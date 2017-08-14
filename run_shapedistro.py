#!/usr/bin/env python
######################

import sys
import numpy as np, pymc
import ldac, shapedistro

######################

inputcatfile = sys.argv[1]
outputcatfile = sys.argv[2]
modelname = sys.argv[3]
nsamples = float(sys.argv[4])

######

cat = ldac.openObjectFile(inputcatfile)

######

model = getattr(shapedistro, modelname)

mcmc = None
for i in range(10):
    try:
        mcmc = pymc.MCMC(model(cat['size'],
                               cat['snratio'],
                               cat['g'],
                               cat['true_g']),
                         db = 'pickle',
                         dbname=outputcatfile)
        break
    except pymc.ZeroProbability:
        pass

if mcmc is None:
    print 'Cannot Init MCMC'
    sys.exit(1)

print 'sampling'
mcmc.sample(nsamples)
print 'done'

mcmc.db.close()
