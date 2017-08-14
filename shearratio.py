####################
# calculate shear ratio test for clusters
####################

import numpy as np
import scipy.optimize as optimize
import nfwutils, nfwmodeltools
import compare_masses as cm
import intrinsicscatter_grid as isg
import kde

####################

def calcZBinWeights(scaledZ, shear, zbins):

    if isinstance(zbins, int):
        zbins = np.logspace(np.log10(np.min(pdzrange)), np.log10(np.max(pdzrange)), zbins)
    nzbins = len(zbins) - 1

    ngals = shear.shape[0]

    weights = np.zeros((ngals, nzbins))
    aveShear = np.zeros((ngals, nzbins))

    for i in range(nzbins):

        inbin = np.logical_and(scaledZ >= zbins[i], scaledZ < zbins[i+1])

        if not inbin.any():            
            weights[:,i] = np.nan
            aveShear[:,i] = np.nan
            #check for Nan before stacking
        else:
            weights[:,i][inbin] = 1.
            aveShear[:,i][inbin] = shear[inbin]


    return zbins, weights, aveShear

#######################


#######################

def scaleShear(controller, rs, concen = 4., cosmology = nfwutils.std_cosmology):
    #assumes BentVoigt3Shapedistro 

    inputcat = controller.inputcat
    z_b = inputcat['z_b']
    zcluster = controller.zcluster

    cluster_exclusion = np.logical_and(zcluster-0.05 < z_b, z_b < zcluster + 0.1)
    inputcat = inputcat.filter(np.logical_not(cluster_exclusion))
    r_mpc = inputcat['r_mpc']
    ghats = inputcat['ghats']
    size = inputcat['size']
    z_b = inputcat['z_b']


    comovingdist = nfwutils.ComovingDistMemoization(cosmology)

    pivot, m_slope, m_b, m_cov, c = controller.modelbuilder.psfDependence('interp', controller.psfsize)

    betainf = nfwutils.beta([1e6], zcluster, comovingdist = comovingdist)

    #matching definitions with Taylor et al 2011 -> need to get rid of beta_inf in shear amp
    shear = nfwmodeltools.NFWShear(r_mpc, concen, rs, zcluster, comovingdist = comovingdist) / betainf
    
    kappa = nfwmodeltools.NFWKappa(r_mpc, concen, rs, zcluster,  comovingdist = comovingdist)
    


    m = np.zeros_like(size)
    m[size >= pivot] = m_b
    m[size < pivot] = m_slope*(size[size < pivot] - pivot) + m_b

    beta_s = nfwutils.beta_s(z_b, zcluster, comovingdist = comovingdist)


    
    estimators = (ghats - c)*(1-beta_s*kappa)/((1+m)*shear)



    comoving_cluster = comovingdist(zcluster)
    scaledZ = np.array([comovingdist(zi)/comoving_cluster for zi in z_b])

    estimators[scaledZ < 1] = ((ghats - c)/(1+m))[scaledZ < 1]

    

    return scaledZ, estimators

#############################


def calcBinDistro(zbins, weights, shears):

    nzbins = weights.shape[1]

    maxlike_est = np.zeros(nzbins)

    for curz in range(nzbins):

        if np.sum(weights[:,curz], axis=-1) == 0:
            continue

        inBin = np.logical_and(weights[:,curz] > 0., np.isfinite(weights[:,curz]))

        if np.sum(weights[:,curz][inBin]) == 0:
            continue

        wkde = kde.weightedKDE(shears[:,curz][inBin], weights[:,curz][inBin])

        def func2min(x):
            return -wkde(x)

        maxlike_est[curz] = optimize.fmin(func2min, np.zeros(1), disp = False)


    return maxlike_est

###################

def bootstrapBinDistro(zbins, weights, shears, nbootstraps = 500):

    nzbins = weights.shape[1]




    maxlike_ests = np.zeros((nzbins, nbootstraps))



    ngals = shears.shape[0]

    for i in range(nbootstraps):
        
        if (i % 100) == 0:
            print i


        current_draw = np.random.randint(0, ngals, ngals)
        
        maxlike_ests[:,i] = calcBinDistro(zbins, weights[current_draw], shears[current_draw])


    point_est = np.zeros(nzbins)
    sig1 = np.zeros((2, nzbins))
    sig2 = np.zeros((2, nzbins))

    for i in range(nzbins):
        
        sorted_ests = np.sort(maxlike_ests[i,:])
        point_est[i] = sorted_ests[int(0.5*nbootstraps)]
        sig1_low  = sorted_ests[int(0.16*nbootstraps)]
        sig1_high = sorted_ests[int(0.84*nbootstraps)]
        sig2_low  = sorted_ests[int(0.025*nbootstraps)]         
        sig2_high = sorted_ests[int(0.975*nbootstraps)]  

        sig1[0,i] = point_est[i] - sig1_low
        sig1[1,i] = sig1_high - point_est[i]
        sig2[0,i] = point_est[i] - sig2_low
        sig2[1,i] = sig2_high - point_est[i]


        
    return point_est, sig1, sig2, maxlike_ests
    

    

###################


def calcCovariance(median_ghat_sets):

    
    ghats = np.array(median_ghat_sets).T

    mean_ghats = np.mean(median_ghat_sets, axis=0)

    covar = np.cov(ghats)

    return mean_ghats, covar


#######################


def shearScaling(x):

    res = 1. - 1./x
    
    res[x <= 1] = 0.

    return res

######################

    

    


    
    

    
