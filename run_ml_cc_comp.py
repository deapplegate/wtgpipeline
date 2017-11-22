#!/usr/bin/env python
####################

import sys
import numpy as np
import compare_masses as cm, intrinsicscatter2 as isc2
from readtxtfile import readtxtfile
import pymc

outfile = sys.argv[1]
nsamples = int(sys.argv[2])

items = readtxtfile('worklist')
clusters = clusters = [ x[0] for x in items]

mlbootstraps, mlmasks = cm.readMLBootstraps('/u/ki/dapple/ki06/bootstrap_2011-12-14/', items)
ccbootstraps, ccbootmask = cm.readCCSummary('/u/ki/dapple/ki06/bootstrap_2011-12-14/', clusters, 100)

reducedML = {}
reducedCC = {}

for cluster in clusters:
    totalmask = np.logical_and(mlmasks[cluster] == 1, ccbootmask[cluster] == 1)
    reducedML[cluster] = mlbootstraps[cluster][totalmask]
    reducedCC[cluster] = ccbootstraps[cluster][totalmask]

calibmodel = isc2.IntrinsicScatter2(reducedML, reducedCC)
calibMCMC = calibmodel.buildMCMC(outfile)

#calibMCMC.use_step_method(pymc.Metropolis, calibMCMC.m_angle, proposal_sd = 0.1)
#calibMCMC.use_step_method(pymc.Metropolis, calibMCMC.log10_intrinsic_scatter, proposal_sd = 0.8)

calibMCMC.sample(nsamples)

calibMCMC.db.close()

