#!/usr/bin/env python
#####################

import sys, glob
import pymc, numpy as np
import shapedistro, shapedistro_residuals as sdr, ldac

#####################


trainingfile = sys.argv[1]
testingfile = sys.argv[2]
resfile = sys.argv[3]
modelname = sys.argv[4]
burn = int(sys.argv[5])
outfile = sys.argv[6]


training_cat = ldac.openObjectFile(trainingfile)

testing_cat = ldac.openObjectFile(testingfile)

shapemodel = getattr(shapedistro, modelname)

mcmc = sdr.loadResult(training_cat, resfile, shapemodel)

postpred_dist = mcmc.trace('postpred_g')[burn:]

logp = sdr.calcPostPredLogProb(testing_cat, mcmc.unique_g_true, postpred_dist)

output = open(outfile, 'w')
output.write('%f\n' % logp)
output.close()
