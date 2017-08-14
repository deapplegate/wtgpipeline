##########################
# Implements an NFW model for investigation 
# of redshift and contamination effects
###########################

import pymc, numpy as np, scipy.stats as stats
import shearprofile as sp
#import fitmodel as fm
import leastsq
import nfwmodeltools_contam as tools
import cPickle


########################

__cvs_id__ = "$Id: nfwmodel_contam.py,v 1.1 2010-12-14 18:58:24 dapple Exp $"

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
                pixscale = __DEFAULT_PIXSCALE__, fitrange=(0.3, 5.)):

    D_lens = sp.angulardist(zcluster)

    
    def NFWModel(r, r_scale):

        nfw_shear = beta_s*tools.NFWShear(r, concentration, r_scale, zcluster)
        nfw_kappa = beta_s*tools.NFWKappa(r, concentration, r_scale, zcluster)

        g = (1 + (beta_s2 / beta_s**2 - 1)*nfw_kappa)*nfw_shear/(1 - nfw_kappa)

        return g

    
    minPix = fitrange[0] * 3600. * (180./np.pi) / ( pixscale * D_lens )
    maxPix = fitrange[1] * 3600. * (180./np.pi) / ( pixscale * D_lens )

    profile = sp.shearprofile(np.zeros_like(r_pix), r_pix, ghat, np.zeros_like(ghat), sigma2 = None, 
                              range = (minPix, maxPix), bins=15, center=(0,0), logbin=True)
    
    profile_r_mpc = profile.r * pixscale * (1./3600.) * (np.pi / 180. ) * D_lens

    rs, isCon = leastsq.leastsq(NFWModel, [0.4], profile_r_mpc, profile.E, profile.Eerr, fullOutput=False)    

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

    D_lens = sp.angulardist(zcluster)

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

    @pymc.stochastic(observed=True)
    def shear(value = ghats, 
             log_r_scale = log_r_scale, 
             normgal_density = normgal_density, 
             contam_amp = contam_amp):

        raise Exception("Out of Date Function -- discovered & abandoned 2012-04-01; no joke")

        return tools.likelihood(log_r_scale, r_mpc, ghat_matrix, beta_matrix, pdz, concentration, zcluster, D_lens, shape_sigma)

    @pymc.stochastic(observed=True)
    def numcounts(value = ngals,
                  normgal_density = normgal_density,
                  contam_amp = contam_amp):

        pass


    ########
        
    return locals()




######################
# ML Reconstruction
######################


def ML_NFW_Model(r_mpc, ghats, betas, pdz, dz, concentration, zcluster, shape_sigma):

    #######
    # Data Prep
    #######

    r_mpc = np.ascontiguousarray(r_mpc)
    pdz = np.ascontiguousarray(pdz)

    D_lens = sp.angulardist(zcluster)

    nzbins = len(betas)
    ghat_matrix = np.ascontiguousarray(np.column_stack(nzbins*[ghats]))

    ngals = len(ghats)
    beta_matrix = np.ascontiguousarray(np.vstack(ngals*[betas]))

    assert(ghat_matrix.shape == beta_matrix.shape == pdz.shape)


    #######
    # Model
    #######

    ## r_scale is log-uniform
    log_r_scale = pymc.Uniform('log_r_scale', np.log(.01), np.log(1.))

    ##contamination
    contam_fraction = pymc.Uniform('contam_fraction', 0.0, 0.3)
    contam_mu = pymc.Uniform('contam_mu', -1.0, 1.0)
    contam_sig = pymc.Uniform('contam_sig', shape_sigma, 10*shape_sigma)

    #assuming dz is constant over range!!!
    #assuming sigma is the same for all galaxies!

    @pymc.stochastic(observed=True)
    def data(value = ghats, log_r_scale = log_r_scale, contam_fraction = contam_fraction, contam_mu = contam_mu, contam_sig = contam_sig):

        raise Exception("Out of date function; discovered & abandoned 2012-04-01; no joke")

        return tools.likelihood(log_r_scale, 
                                r_mpc, 
                                ghat_matrix, 
                                beta_matrix, 
                                pdz, 
                                concentration, 
                                zcluster, 
                                D_lens, 
                                shape_sigma, 
                                dz,
                                contam_fraction, 
                                contam_mu, 
                                contam_sig)


    ########
        
    return locals()


#######

def scan_model(rs, r_mpc, ghats, betas, pdz, dz, concentration, zcluster, shape_sigma):

    model = None
    for i in range(10):
        try:
            model = pymc.Model(ML_NFW_Model(r_mpc, ghats, betas, pdz, dz, concentration, 
                                            zcluster, shape_sigma))
            break
        except pymc.ZeroProbability:
            pass
        
    if model is None:
        return rs, np.zeros_like(rs)


    scan = []
    for r in rs:
        try:
            model.log_r_scale.value = np.log(r)
            scan.append(model.logp)
        except pymc.ZeroProbability:
            scan.append(pymc.PyMCObjects.d_neg_inf)

    return rs, scan

#######

def sample_model(r_mpc, ghats, betas, pdz, dz, concentration, zcluster, shape_sigma, samples = 10000):

    model = None
    for i in range(10):
        try:
            model = pymc.Model(ML_NFW_Model(r_mpc, ghats, betas, pdz, dz, concentration, 
                                            zcluster, shape_sigma))
            break
        except pymc.ZeroProbability:
            pass
        
    if model is None:
        return np.array([])

    
    mcmc = pymc.MCMC(model)

    return mcmc
    
