#!/usr/bin/env python
######################

# Recompute the cluster mass statistics 

import sys, pymc
import numpy as np
import maxlike_masses as mm, maxlike_secure_floatvoigt_driver as msfd, nfwutils

workdir = sys.argv[1]
outdir = sys.argv[2]
cluster = sys.argv[3]
filter = sys.argv[4]
image = sys.argv[5]



controller = msfd.makeController()
handler = controller.filehandler
options, args = handler.createOptions(workdir = workdir, 
                                      incatalog = '%s/%s.%s.%s.cut_lensing.cat' % (workdir, cluster, filter, image),
                                      cluster = cluster,
                                      filter = filter,
                                      image = image)
options, args = controller.modelbuilder.createOptions(options = options, args = args)

options.outputFile = '%s/%s.%s.%s.out' % (outdir, cluster, filter, image)
controller.load(options, args)


db = pymc.database.pickle.load(options.outputFile)

controller.mcmc = pymc.MCMC(controller.model, db = db)

controller.masses = np.array([nfwutils.massInsideR(rs, controller.mcmc.concentration, controller.mcmc.zcluster, controller.r500) for rs in np.exp(controller.mcmc.trace('log_r_scale')[3000:])])


mm.dumpMasses(controller.masses, options.outputFile)
