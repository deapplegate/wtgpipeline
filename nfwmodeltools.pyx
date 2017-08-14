##########################
# Implements an NFW model for investigation 
# of redshift and contamination effects
###########################
# Compiling info: gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I /u/ki/dapple/include/python2.7/ -I /u/ki/dapple/lib/python2.7/site-packages/numpy/core/include/ -o nfwmodeltools.so nfwmodeltools.c voigt.c

# cython: profile=False

import numpy as np
cimport numpy as np
cimport cython

import nfwutils

cdef extern from "math.h":
    double exp(double)
    double log(double)

cdef extern from "voigt.h":
    double voigt(double, double, double)


########################

__cvs_id__ = "$Id: nfwmodeltools.pyx,v 1.5 2011-02-09 01:59:14 dapple Exp $"

#########################

__DEFAULT_OMEGA_M__ = 0.3
__DEFAULT_OMEGA_L__ = 0.7
__DEFAULT_h__ = 0.7
__DEFAULT_PIXSCALE__ = 0.2

v_c = 299792.458 #km/s

DTYPE = np.double
ctypedef np.double_t DTYPE_T

#########################


############################
# NFW Profile
############################

cdef double deltaC(double c):
    return (200./3.) * c**3 / (log(1+c) - c/(1+c))

##############


def NFWShear(r, c, rs, z, comovingdist = nfwutils.comovingdist):

    cosmology = comovingdist.cosmology

    D_lens = nfwutils.angulardist(z, comovingdist = comovingdist)
    
    rho_c_over_sigma_c = 1.5 * D_lens * nfwutils.beta([1e6], z, comovingdist) * cosmology.hubble2(z) / v_c**2
    
    delta_c = deltaC(c)
    amp = rs*delta_c*rho_c_over_sigma_c

    x = (r/rs).astype(np.float64)

    g = np.zeros(r.shape, dtype=np.float64)

    xless = x[x < 1]
    a = np.arctanh(np.sqrt((1-xless)/(1+xless)))
    b = np.sqrt(1-xless**2)
    c = (xless**2) - 1
    
    g[x<1] = 8*a/(b*xless**2) + 4*np.log(xless/2)/xless**2 - 2/c + 4*a/(b*c)

    xgre = x[x>1]
    a = np.arctan(np.sqrt((xgre-1)/(1+xgre)))
    b = np.sqrt(xgre**2-1)
    
    g[x>1] = 8*a/(b*xgre**2) + 4*np.log(xgre/2)/xgre**2 - 2/b**2 + 4*a/b**3

    g[x == 1] = 10./3 + 4*np.log(.5)

    return amp*g

###################

def NFWKappa(r, c, rs, z, comovingdist = nfwutils.comovingdist):

  cosmology = comovingdist.cosmology
    
  D_lens = nfwutils.angulardist(z, comovingdist = comovingdist)
    
  rho_c_over_sigma_c = 1.5 * D_lens * nfwutils.beta([1e6], z, comovingdist) * cosmology.hubble2(z) / v_c**2

  
  
  delta_c = deltaC(c)
  amp = 2*rs*delta_c*rho_c_over_sigma_c
  
  x = (r/rs).astype(np.float64)

  kappa = np.zeros(r.shape, dtype=np.float64)
    
  xless = x[x<1]
  a = np.arctanh(np.sqrt((1-xless)/(1+xless)))
  b = np.sqrt(1-xless**2)
  c = 1./(xless**2 - 1)
  kappa[x<1] = c*(1 - 2.*a/b)

  xgre = x[x>1]
  a = np.arctan(np.sqrt((xgre-1)/(1+xgre)))
  b = np.sqrt(xgre**2-1)
  c = 1./(xgre**2 - 1)
  kappa[x>1] = c*(1 - 2.*a/b)

  kappa[x == 1] = 1./3.;


  return kappa*amp;


######################
# ML Reconstruction Tools
######################


@cython.boundscheck(False)
@cython.wraparound(False)
def dumbnormal_like(double r_scale, 
                    np.ndarray[DTYPE_T, ndim=1, mode='c'] r_mpc not None, 
                    np.ndarray[DTYPE_T, ndim=1, mode='c'] ghats not None, 
                    np.ndarray[DTYPE_T, ndim=1, mode='c'] betas not None, 
                    np.ndarray[DTYPE_T, ndim=2, mode='c'] pdz not None, 
                    np.ndarray[DTYPE_T, ndim=1, mode='c'] shapedistro_samples not None,
                    double concentration, 
                    double zcluster):

    cdef double shape_sigma = shapedistro_samples[0]

    cdef Py_ssize_t nobjs = pdz.shape[0]
    cdef Py_ssize_t npdz = pdz.shape[1]

    cdef np.ndarray[DTYPE_T, ndim=1, mode='c'] gamma_inf = NFWShear(r_mpc, concentration, r_scale, zcluster)
    cdef np.ndarray[DTYPE_T, ndim=1, mode='c'] kappa_inf = NFWKappa(r_mpc, concentration, r_scale, zcluster)

    cdef double delta = 0.
    cdef double curPDZ = 0.
    cdef double beta = 0.
    cdef Py_ssize_t i, j
    cdef DTYPE_T galProb = 0.
    cdef DTYPE_T logprob = 0.

    for i from nobjs > i >= 0:

        galProb = 0.
        for j from npdz > j >= 0:

            curPDZ = pdz[i,j]
            if curPDZ > 1e-6:

                beta = betas[j]

                delta = ghats[i] - (beta*gamma_inf[i] / (1 - beta*kappa_inf[i]))

                galProb = galProb + curPDZ*exp(-.5*(delta/shape_sigma)**2)

        logprob = logprob + log(galProb)



        
    return logprob



#########################################

@cython.boundscheck(False)
@cython.wraparound(False)
def voigt_like(double r_scale, 
               np.ndarray[DTYPE_T, ndim=1, mode='c'] r_mpc not None, 
               np.ndarray[DTYPE_T, ndim=1, mode='c'] ghats not None, 
               np.ndarray[DTYPE_T, ndim=1, mode='c'] betas not None, 
               np.ndarray[DTYPE_T, ndim=2, mode='c'] pdz not None, 
               np.ndarray[DTYPE_T, ndim=1, mode='c'] shapedistro_samples not None,
               double concentration, 
               double zcluster):

    cdef Py_ssize_t nobjs = pdz.shape[0]
    cdef Py_ssize_t npdz = pdz.shape[1]

    cdef Py_ssize_t nshapesamples = shapedistro_samples.shape[1]

    cdef np.ndarray[DTYPE_T, ndim=1, mode='c'] gamma_inf = NFWShear(r_mpc, concentration, r_scale, zcluster)
    cdef np.ndarray[DTYPE_T, ndim=1, mode='c'] kappa_inf = NFWKappa(r_mpc, concentration, r_scale, zcluster)

    cdef double m = 0.
    cdef double c = 0.
    cdef double sigma = 0.
    cdef double gamma = 0.
    cdef double delta = 0.
    cdef double curPDZ = 0.
    cdef double beta = 0.
    cdef double g = 0.

    cdef Py_ssize_t i, j, s
    cdef DTYPE_T galProb = 0.
    cdef DTYPE_T logProb = 0.

        
    m = shapedistro_samples[0]
    c = shapedistro_samples[1]
    sigma = shapedistro_samples[2]
    gamma = shapedistro_samples[3]

    for i from nobjs > i >= 0:

        galProb = 0.
        for j from npdz > j >= 0:

            curPDZ = pdz[i,j]
            if curPDZ > 1e-6:

                beta = betas[j]

                g = (beta*gamma_inf[i] / (1 - beta*kappa_inf[i]))


                delta = ghats[i] - (1+m)*g - c

                galProb = galProb + curPDZ*voigt(delta, sigma, gamma)




        logProb = logProb + log(galProb)

        
    return logProb




###########################################################################


@cython.boundscheck(False)
@cython.wraparound(False)
def bentvoigt_like(double r_scale, 
               np.ndarray[DTYPE_T, ndim=1, mode='c'] r_mpc not None, 
               np.ndarray[DTYPE_T, ndim=1, mode='c'] ghats not None, 
               np.ndarray[DTYPE_T, ndim=1, mode='c'] betas not None, 
               np.ndarray[DTYPE_T, ndim=2, mode='c'] pdz not None, 
               np.ndarray[DTYPE_T, ndim=1, mode='c'] m not None,
               np.ndarray[DTYPE_T, ndim=1, mode='c'] c not None,
               double sigma,
               double gamma,
               double concentration, 
               double zcluster):

    cdef Py_ssize_t nobjs = pdz.shape[0]
    cdef Py_ssize_t npdz = pdz.shape[1]


    cdef np.ndarray[DTYPE_T, ndim=1, mode='c'] gamma_inf = NFWShear(r_mpc, concentration, r_scale, zcluster)
    cdef np.ndarray[DTYPE_T, ndim=1, mode='c'] kappa_inf = NFWKappa(r_mpc, concentration, r_scale, zcluster)

    cdef double delta = 0.
    cdef double curPDZ = 0.
    cdef double beta = 0.
    cdef double g = 0.

    cdef Py_ssize_t i, j, s
    cdef DTYPE_T galProb = 0.
    cdef DTYPE_T logProb = 0.

        
    for i from nobjs > i >= 0:

        galProb = 0.
        for j from npdz > j >= 0:

            curPDZ = pdz[i,j]
            if curPDZ > 1e-6:

                beta = betas[j]

                g = (beta*gamma_inf[i] / (1 - beta*kappa_inf[i]))


                delta = ghats[i] - (1+m[i])*g - c[i]

                galProb = galProb + curPDZ*voigt(delta, sigma, gamma)




        logProb = logProb + log(galProb)

        
    return logProb





