#####
# C implementations for Banff Challenge
#####
# Compiling info: 
#gcc -shared -pthread -fPIC -fwrapv -O2 -Wall -fno-strict-aliasing -I /u/ki/dapple/include/python2.7/ -I /u/ki/dapple/lib/python2.7/site-packages/numpy/core/include/ -I./ -o banff_tools.so banff_tools.c
#

import numpy as np
cimport numpy as np
cimport cython

cdef extern from "math.h":
     double log(double)

################

DTYPE = np.double
ctypedef np.double_t DTYPE_T

################



def computePDF(np.ndarray[DTYPE_T, ndim=1, mode='c'] samples, 
               np.ndarray[DTYPE_T, ndim=1, mode='c'] querypoints, 
               np.ndarray[DTYPE_T, ndim=1, mode='c'] deltas, 
               int npoints = 200):

    cdef int nsamples = len(samples)
    cdef int nquerypoints = len(querypoints)

    assert(len(samples) > npoints)

    cdef np.ndarray[DTYPE_T, ndim=1, mode='c'] probs = np.zeros(nquerypoints)

    cdef double x = 0.
    cdef np.ndarray[DTYPE_T, ndim=1, mode='c'] sample_distances = np.zeros(nsamples)
    
    cdef int min_index
    cdef np.ndarray[np.int32_t, ndim=1, mode='c'] indices = np.zeros(npoints, dtype = np.int32)
    cdef int nfound = 0
    cdef int ilow = 0
    cdef int ihigh = 0

    cdef np.ndarray[DTYPE_T, ndim=1, mode='c'] nearest_samples = np.zeros(npoints)
    cdef double minX = 0.
    cdef double maxX = 0.

    cdef int i = nquerypoints - 1
    for i from nquerypoints > i >= 0:

        x = querypoints[i]
        
        sample_distances[:] = np.abs(samples - x)

        min_index = np.arange(nsamples, dtype=np.int32)[sample_distances == min(sample_distances)][0]

        indices[:] = np.zeros(npoints, dtype=np.int32)
        indices[0] = min_index
        nfound = 1
        ilow = min_index
        ihigh = min_index
        while (nfound < npoints):
            ilow = ilow - 1
            ihigh = ihigh + 1
            if ilow <= -1:
                indices[nfound:] = ihigh + np.arange(npoints - nfound, dtype=np.int32)
                break
            elif ihigh >= nsamples:
                indices[nfound:] = ilow - np.arange(npoints - nfound, dtype=np.int32)
                break
            elif sample_distances[ilow] < sample_distances[ihigh]:
                indices[nfound] = ilow
                nfound += 1
                ilow = ilow - 1
            else:
                indices[nfound] = ihigh
                nfound += 1
                ihigh = ihigh + 1

        

        nearest_samples[:] = samples[indices]

        minX = np.min(nearest_samples)
        maxX = np.max(nearest_samples)

        probs[i] = npoints / (nsamples*(maxX - minX))


    
    
    return probs

    
