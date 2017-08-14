#######################
# Toy Model For Shear Recovery
########################

import numpy as np, scipy.stats as stats, scipy.integrate as integrate
import pymc
import shearprofile as sp
import fitmodel as fm

########################

__cvs_id__ = "$Id: shearmodel.py,v 1.1 2010-07-02 23:08:47 dapple Exp $"

########################

shape_sigma = 0.001

def single_z_contamination_model(measured_g, alphaRange = 0.1):

    g = pymc.Uniform('g', -0.5, 0.5)

    sigma = shape_sigma

    if hasattr(alphaRange, '__len__'):
        alpha = pymc.Uniform('alpha', alphaRange[0], alphaRange[1])
    else:
        alpha = alphaRange

    @pymc.stochastic(observed=True)
    def data(value = measured_g, g = g, alpha = alpha, sigma = sigma):

        return np.sum(np.log( (1-alpha)*stats.norm.pdf(measured_g, g, sigma) + \
                        alpha*stats.norm.pdf(measured_g, 0, sigma) ))

    return locals()


#############

def pdz_model(measured_g, dz, pdz, betas):

    #assumes SIS model in that gamma == kappa

    nzbins = len(betas)
    ghat = np.column_stack(nzbins*[measured_g])

    ngals = len(measured_g)
    beta_z = np.vstack(ngals*[betas])

    assert(ghat.shape == beta_z.shape == pdz.shape)

    sigma = shape_sigma
       
    ################


    ginf = pymc.Uniform('ginf', 0.045, 0.055)

    @pymc.stochastic(observed=True)
    def data(value = measured_g, ginf = ginf, sigma = sigma):

        gamma = beta_z * ginf
        g = gamma / ( 1 - gamma )
        deltas = ghat - g

        return np.sum(np.log(np.sum(dz*pdz*stats.norm.pdf(deltas, 0, sigma), axis=-1)))


    ##################

    return locals()



##################

def create_pdzmodel_data(ginf, ngals, z0, sigmaz, clusterz):

    trueZ = sigmaz * np.random.standard_normal(ngals) + z0
#    peakPDZs = sigmaz * np.random.standard_normal(ngals) + z0

    dz = 0.01
    pdzs = []
    betas = []

    probs = []
    zs = np.arange(0, 3, dz)
    for z in zs:
#        probs.append( stats.norm.pdf( z, peakPDZs, sigmaz) )
        probs.append( stats.norm.pdf( z, z0, sigmaz) )

    pdz = np.column_stack(probs)

    beta = sp.beta_s(zs, clusterz)

#    realBeta = sp.beta_s([z0], clusterz)
    realBeta = sp.beta_s(trueZ, clusterz)

    gamma = realBeta*ginf
    g = gamma / ( 1 - gamma )

    ghats = shape_sigma*np.random.standard_normal(ngals) + g

#    return ghats, dz, pdz, beta, z0*np.ones(ngals), peakPDZs
    return ghats, dz, pdz, beta, trueZ

    
###################


def beta_method(ghat, beta_s, beta_s2):

    #SIS style -> gamma == kappa

    B = beta_s2 / beta_s**2

    g_est = np.mean(ghat)

    a = -(1+g_est)
    b = np.sqrt((1+g_est)**2 + 4*g_est*(B-1))
    c = 2*(B-1)

    gamma = (a + b) / c

    ginf = gamma / beta_s

    return ginf

def bootstrap_beta_method(ghat, beta_s, beta_s2, nbootstraps = 500):

    ginfs = []
    for i in xrange(nbootstraps):

        cat = ghat[np.random.randint(0, len(ghat), len(ghat))]

        ginfs.append(beta_method(cat, beta_s, beta_s2))

    return ginfs

                 
