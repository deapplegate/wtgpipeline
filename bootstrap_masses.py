##########################
# Implements an NFW model for investigation 
# of redshift and contamination effects
###########################

import pymc, numpy as np
import shearprofile as sp
#import fitmodel as fm
import leastsq
import nfwmodeltools as tools, nfwutils



########################

__cvs_id__ = "$Id: bootstrap_masses.py,v 1.1 2011-02-11 02:55:04 dapple Exp $"

#########################

__DEFAULT_OMEGA_M__ = 0.3
__DEFAULT_OMEGA_L__ = 0.7
__DEFAULT_h__ = 0.7
__DEFAULT_PIXSCALE__ = 0.2  #arcsec / pix
__DEFAULT_SIZE__ = np.array([10000,10000]) #pixels
__DEFAULT_CENTER__ = np.array([5000,5000])  #cluster location

v_c = 299792.458 #km/s

#########################

                              

########################
# BETA RECONSTRUCTION
########################

def beta_method(r_pix, r_mpc, ghat, beta_s, beta_s2, concentration, zcluster,
                pixscale = __DEFAULT_PIXSCALE__, fitrange=(0.5, 3.), Omega_m = 0.3, Omega_l = 0.7):

    cosmology = nfwutils.Cosmology(Omega_m, Omega_l)
    comovingdist = nfwutils.ComovingDistMemoization(cosmology = cosmology)

    
    def NFWModel(r, r_scale):

        nfw_shear = beta_s*tools.NFWShear(r, concentration, r_scale, zcluster, comovingdist)
        nfw_kappa = beta_s*tools.NFWKappa(r, concentration, r_scale, zcluster, comovingdist)

        g = (1 + (beta_s2 / beta_s**2 - 1)*nfw_kappa)*nfw_shear/(1 - nfw_kappa)

        return g

    
    minPix = fitrange[0] * 3600. * (180./np.pi) / ( pixscale * D_lens )
    maxPix = fitrange[1] * 3600. * (180./np.pi) / ( pixscale * D_lens )

    profile = sp.shearprofile(np.zeros_like(r_pix), r_pix, ghat, np.zeros_like(ghat), sigma2 = None, 
                              range = (minPix, maxPix), bins=15, center=(0,0), logbin=True)
    
    profile_r_mpc = profile.r * pixscale * (1./3600.) * (np.pi / 180. ) * D_lens

    keepBins = np.logical_and(np.isfinite(profile.E), np.isfinite(profile.Eerr))


    rs, isCon = leastsq.leastsq(NFWModel, [0.4], profile_r_mpc[keepBins], 
                                profile.E[keepBins], profile.Eerr[keepBins], 
                                fullOutput=False)    

    if not isCon:
        return None

    return rs

#    print profile_r_mpc.shape
#    print profile.E.shape
#    print profile.Eerr.shape
#    
#    fit = fm.FitModel(profile_r_mpc, profile.E, profile.Eerr, NFWModel, fm.ChiSqStat, guess=[0.4])
#    fit.fit()
#   
#    if fit.have_fit:
#        return fit.par_vals['r_scale']
#    else:
#        return None

######################

def bootstrap_beta_method(r_pix, r_mpc, ghat, actualBetas, concentration, zcluster, 
                          nbootstraps=2000):

    scale_radii = []
    nfail = 0
    for i in xrange(nbootstraps):

        curBootstrap = np.random.randint(0, len(r_mpc), size=len(r_mpc))
        
        curR_pix = r_pix[curBootstrap]
        curR_mpc = r_mpc[curBootstrap]
        curGhat = ghat[curBootstrap]
        curBetas = actualBetas[curBootstrap]

        beta_s = np.mean(curBetas)
        beta_s2 = np.mean(curBetas**2)

        scale_radius = beta_method(curR_pix, curR_mpc, curGhat, beta_s, beta_s2, 
                                   concentration, zcluster)
        if scale_radius is None or not np.isfinite(scale_radius):
            nfail += 1
        else:
            scale_radii.append(scale_radius)

    return scale_radii, nfail

#########################

###########
# Newman method of ignoring P(z)
############

def newman_method(r_mpc, ghat, betas, sigma, m, concentration, zcluster,
                pixscale = __DEFAULT_PIXSCALE__, fitrange=(0.75, 3.)):

    
    def NFWModel(coords, r_scale):

        r = coords[:,0]
        beta_s = coords[:,1]

        nfw_shear = beta_s*tools.NFWShear(r, concentration, r_scale, zcluster)
        nfw_kappa = beta_s*tools.NFWKappa(r, concentration, r_scale, zcluster)

        g = nfw_shear/(1 - nfw_kappa)

        return g


    tokeep = np.logical_and(r_mpc >= fitrange[0], r_mpc < fitrange[1])

    coords = np.column_stack([r_mpc[tokeep], betas[tokeep]])
    

    rs, isCon = leastsq.leastsq(NFWModel, [0.4], coords, ghat[tokeep] / m, 
                                (sigma/m)*np.ones(coords.shape[0]), fullOutput=False)    

    if not isCon:
        return None

    return rs


######################

def bootstrap_newman_method(r_mpc, ghat, actualBetas, sigma, concentration, zcluster, 
                          nbootstraps=2000, msigma = 0.05):

    scale_radii = []
    nfail = 0
    for i in xrange(nbootstraps):

        curBootstrap = np.random.randint(0, len(r_mpc), size=len(r_mpc))
        
        curR_mpc = r_mpc[curBootstrap]
        curGhat = ghat[curBootstrap]
        curBetas = actualBetas[curBootstrap]

        m = msigma*np.random.standard_normal() + 1.

        scale_radius = newman_method(curR_mpc, curGhat, curBetas, 
                                   sigma, m, concentration, zcluster)
        if scale_radius is None or not np.isfinite(scale_radius):
            nfail += 1
        else:
            scale_radii.append(scale_radius)

    return scale_radii, nfail


######################
# Beta method with contamination
#####################

def beta_contamination(x, y, g1, g2, mag, useInContam,                             
                       areamap,                                                    
                       zdist,                                                      
                       zcluster,                                                   
                       norm_radii,                                                 
                       concentration_prior = 4.,                                   
                       density_prior = [0, 30],                                    
                       contam_prior = [0, 10],                                     
                       fitrange = (0.4, 4.),                                       
                       bins = 15,                                                  
                       logbin = False,                                             
                       pixscale = __DEFAULT_PIXSCALE__, center = __DEFAULT_CENTER__):

    #######
    # save config setting
    #######

    momento = {'x'                    :  x,                                
               'y,'                   :  y,                                        
               'g1'                   :  g1,                                      
               'g2'                   :  g2,                                      
               'mag'                  :  mag,                                     
               'useInContam'          :  useInContam,                      
               'areamap'              :  areamap,                                                       
               'zdist'                :  zdist,                                                           
               'zcluster'             :  zcluster,                                                          
               'norm_radii'           :  norm_radii,                                                        
               'concentration_prior'  :  concentration_prior,                                     
               'density_prior'        :  density_prior,                                 
               'contam_prior'         :  contam_prior,                                  
               'fitrange'             :  fitrange,                                  
               'bins'                 :  bins,                                                    
               'logbin'               :  logbin,                                            
               'pixscale'             :  pixscale,  
               'center'               :  center
               }      


                       

    #######
    # Data Prep
    #######

    D_lens =nfwutils.angulardist(zcluster)

    cat = {'Xpos' : x, 'Ypos' : y, 'gs1' : g1, 'gs2' : g2}
    r_arcsec, E, B = sp.calcTangentialShear(cat, center, pixscale)
    r_mpc = r_arcsec * (1./3600.) * (np.pi / 180. ) * D_lens 
        
    if logbin:
        dr = log(dr)
        rmin = log(rmin)
        rmax = log(rmax)
        
        leftedges, binwidth = linspace(rmin, rmax, bins+1, endpoint=True, retstep=True)

        rbin = exp(leftedges)

        rbin = (rbin[1:] + rbin[:-1])/2.


    else:
        leftedges, binwidth = linspace(rmin, rmax, bins, endpoint=False, retstep=True)
        rbin = leftedges + binwidth/2.


    # Set up binning grid:
    

    Ebin = zeros(bins, dtype=float64)
    Ebinerr = zeros(bins, dtype=float64)
    Bbin = zeros(bins)
    Bbinerr = zeros(bins)
    nbin = zeros(bins)

    index = ((dr - rmin) / binwidth).astype(int)
    
    goodentry = logical_and(index >= 0, index < bins)




    #######
    # Model
    #######

    ## r_scale is log-uniform
    log_r_scale = pymc.Uniform('log_r_scale', np.log(.01), np.log(1.))

    normgal_density = pymc.Uniform('n_normgals', density_prior[0], density_prior[1])

    contam_amp = pymc.Uniform('A_contam', contam_prior[0], contam_prior[1])

    raise Exception("Out of date function -- discovered & ignored 2012-04-01; no jobke")

    @pymc.stochastic(observed=True)
    def shear(value = ghats, 
             log_r_scale = log_r_scale, 
             normgal_density = normgal_density, 
             contam_amp = contam_amp):

        return tools.likelihood(log_r_scale, r_mpc, ghat_matrix, beta_matrix, pdz, concentration, zcluster, D_lens, shape_sigma)

    @pymc.stochastic(observed=True)
    def numcounts(value = ngals,
                  normgal_density = normgal_density,
                  contam_amp = contam_amp):

        pass


    ########
        
    return locals()





def alteredCosmology(cat, om):

    cosmology = nfwutils.Cosmology(om, 1.-om)
    comovingdist = nfwutils.ComovingDistMemoization(cosmology)

    betas = nfwutils.beta_s(cat['z'], 0.3, comovingdist)
    dl = nfwutils.angulardist(0.3, comovingdist = comovingdist)

    r_mpc = cat['r_pix'] * 0.2 * (1./3600.) * (np.pi / 180. ) * dl

    shears = tools.NFWShear(r_mpc, 4.0, 0.5, 0.3, dl, Omega_m = om, Omega_l = 1 - om)
    kappa = tools.NFWKappa(r_mpc, 4.0, 0.5, 0.3, dl, Omega_m = om, Omega_l = 1 - om)
    g = betas*shears / (1 - betas*kappa)
    scale_radii = beta_method(cat['r_pix'], r_mpc, 
                              g, np.mean(betas), np.mean(betas**2), 
                              4, 0.3, Omega_m = om, Omega_l = 1 - om)
    mass = nfwutils.massInsideR(scale_radii, 4.0, 0.3, 1, cosmology)

    return mass
