#####################
# Tools for smoothing distributions
#####################


import numpy as np
from scipy.stats.kde import gaussian_kde

####################


def weightedKDE(sample, weights, h = None):

    totalweight = np.sum(weights)
    weightedMean = np.average(sample, weights = weights)
    stddev = np.sqrt(np.sum(weights*(sample - weightedMean)**2)/totalweight)
    if h is None:
        h = 1.06*stddev*(len(sample)**(-0.2))  #silverman's rule of thumb, simplified slightly
        print h

    def kde(x):

        if isinstance(x, float):
            x = np.array([x])

        training = np.column_stack(len(x)*[sample])
        delta = (training - x)/h
        
        pdf = np.sum(weights*np.exp(-0.5*delta.T**2)/np.sqrt(2*np.pi), axis=-1)/totalweight

        return pdf

    return kde

    


