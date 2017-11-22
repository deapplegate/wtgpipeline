#!/usr/bin/env python
####################

import sys
import numpy as np
import compare_masses as cm, intrinsicscatter as isc
import scatter_sims as ss, nfwutils
from readtxtfile import readtxtfile

workdir = sys.argv[1]
subdir = sys.argv[2]
outfile = sys.argv[3]
nsamples = int(sys.argv[4])

items = readtxtfile('simclusterlist')
clusters = clusters = [ x[0] for x in items]

redshifts = cm.readClusterRedshifts()
properredshifts = np.array([redshifts[x] for x in clusters])


masses, errs, massgrid, scale_radii = ss.readMLMasses(workdir, subdir, clusters)
truemasses = {}
for cluster in clusters:
    truemasses[cluster] = nfwutils.massInsideR(scale_radii[cluster], 4., redshifts[cluster], 1.5)

x = np.hstack([len(masses[c])*[truemasses[c]] for c in clusters])
y = np.hstack([masses[c] for c in clusters])
yerr = np.hstack([errs[c] for c in clusters])



calibmodel = isc.IntrinsicScatter(x, y, yerr)
calibMCMC = calibmodel.buildMCMC(outfile)
calibMCMC.m_angle.value = np.pi / 4.

calibMCMC.sample(nsamples)

calibMCMC.db.close()

