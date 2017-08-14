##########
# For mass recon using Voigt model
############

import cPickle, numpy as np
import nfwmodeltools, maxlike_masses as maxlike

##############

samplefile ='/nfs/slac/g/ki/ki06/anja/SUBARU/shapedistro/voigt_posterior.pkl'
nsamples = 10000

###

likelihood_func = nfwmodeltools.voigt_like

###


def bin_selectors(cat):

    bins = [cat['snratio'] < 4, 
            np.logical_and(cat['snratio'] >= 4, cat['snratio'] < 5),
            np.logical_and(cat['snratio'] >= 5, cat['snratio'] < 6),
            np.logical_and(cat['snratio'] >= 6, cat['snratio'] < 8),
            np.logical_and(cat['snratio'] >= 8, cat['snratio'] < 10),
            np.logical_and(cat['snratio'] >= 10, cat['snratio'] < 20),
            cat['snratio'] > 20]

    return bins



###

input = open(samplefile, 'rb')

shape_params = cPickle.load(input)

input.close()

makeShapePrior = maxlike.makeSampledPrior

