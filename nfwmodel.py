##########################
# Implements an NFW model for investigation 
# of redshift and contamination effects
###########################

import pymc, numpy as np, scipy.stats as stats
import shearprofile as sp
#import fitmodel as fm
import leastsq
import nfwmodeltools as tools
import cPickle


########################

__cvs_id__ = "$Id: nfwmodel.py,v 1.6 2010-12-22 22:20:02 dapple Exp $"

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

        nfw_shear = beta_s*tools.NFWShear(r, concentration, r_scale, zcluster, D_lens)
        nfw_kappa = beta_s*tools.NFWKappa(r, concentration, r_scale, zcluster, D_lens)

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


def ML_NFW_Model(r_mpc, ghats, betas, pdz, concentration, zcluster, likelihood_func, shapedistro_samples):

    #r_mpc, ghats, pdz, and shapedistro_samples may be either arrays or lists of arrays
    # if lists of arrays, then each entry is associated across the lists and will be passed
    # to likelihood_func seperately, with the logProbs summed together

    #######
    # Data Prep
    #######

    if not isinstance(r_mpc, list):
        r_mpc = [r_mpc]
        ghats = [ghats]
        pdz = [pdz]
        shapedistro_samples = [shapedistro_samples]

    r_mpc = [ np.ascontiguousarray(x) for x in r_mpc ]
    pdz = [ np.ascontiguousarray(x) for x in pdz ]
    
    shapedistro_samples = [ np.ascontiguousarray(x) for x in shapedistro_samples ]

    D_lens = sp.angulardist(zcluster)

    nzbins = len(betas)
    ghats = [ np.ascontiguousarray(x) for x in ghats ]

    betas = np.ascontiguousarray(betas)

    nshapebins = len(shapedistro_samples)



    #######
    # Model
    #######

    ## shape parameter priors

    shape_sample_index = [pymc.DiscreteUniform('shape_index_%d' % i, 0, len(x)) for i, x in enumerate(shapedistro_samples)]

    shape_params = np.empty(nshapebins, dtype=object)
    for i, index, samples in zip(range(len(shapedistro_samples)), shape_sample_index, shapedistro_samples):

        @pymc.deterministic(name = 'shape_params_%d' % i)
        def shape_param_func(index = index, samples = samples):
            return samples[:,index]

        shape_params[i] = shape_param_func

    ## r_scale is log-uniform
    log_r_scale = pymc.Uniform('log_r_scale', np.log(.01), np.log(1.))

    
    @pymc.stochastic(observed=True)
    def data(value = ghats, log_r_scale = log_r_scale, shape_params = shape_params):

        logprobs = np.array([likelihood_func(log_r_scale, cur_r_mpc, 
                               cur_ghats, betas, 
                               cur_pdz, cur_shapedistro_samples,
                               concentration, zcluster, D_lens) \
                                       for (cur_r_mpc, cur_ghats, cur_pdz, cur_shapedistro_samples) \
                                       in zip(r_mpc, ghats, pdz, shape_params)])


        return np.sum(logprobs)


    ########
        
    return locals()




#######

def scan_model(rs, r_mpc, ghats, betas, pdz, concentration, zcluster, likelihood_func, shapedistro_samples):

    model = None
    for i in range(10):
        try:
            model = pymc.Model(ML_NFW_Model(r_mpc, ghats, betas, pdz, concentration, 
                                            zcluster, likelihood_func, shapedistro_samples))


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
    
