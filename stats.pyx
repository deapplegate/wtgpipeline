########################
# Common statistics functions that need to run quickly
#######################
# Compiling info: gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I /u/ki/dapple/include/python2.7/ -I /u/ki/dapple/lib/python2.7/site-packages/numpy/core/include/ -o stats.so stats.c


########################

# cython: profile=False

import numpy as np
cimport numpy as np
cimport cython


cdef extern from "math.h":
    double exp(double)
    double log(double)
    double sqrt(double)

sqrt2pi = sqrt(2*np.pi)


#########################

@cython.boundscheck(False)
@cython.wraparound(False)
def Gaussian(np.ndarray[np.double_t, ndim=1, mode='c'] x,
             double mu,
             double sig):

    cdef Py_ssize_t i, nmax

    nmax = x.shape[0]
    
    cdef np.ndarray[np.double_t, ndim=1, mode='c'] result = np.zeros(nmax, dtype = np.float64)

    for i from nmax > i >= 0:
        result[i] = exp(-0.5*(x[i]-mu)**2/sig**2)/(sqrt2pi*sig)

    return result

#########################



@cython.boundscheck(False)
@cython.wraparound(False)
def LogSumGaussian(np.ndarray[np.double_t, ndim=1, mode='c'] x,
             double mu,
             double sig):

    cdef Py_ssize_t i, nmax

    nmax = x.shape[0]
    
    cdef double sum = 0.

    for i from nmax > i >= 0:
        sum += exp(-0.5*(x[i]-mu)**2/sig**2)/(sqrt2pi*sig)

    return log(sum)

#####################

@cython.boundscheck(False)
@cython.wraparound(False)
def LogSumLogNormal(np.ndarray[np.double_t, ndim=1, mode='c'] x,
                    np.ndarray[np.double_t, ndim=1, mode='c'] logx,
                    double mu,
                    double sig):

    cdef Py_ssize_t i, nmax

    nmax = x.shape[0]
    
    cdef double sum = 0.

    for i from nmax > i >= 0:
        sum += exp(-0.5*(logx[i]-mu)**2/sig**2)/(sqrt2pi*sig*x[i])


    return log(sum)
