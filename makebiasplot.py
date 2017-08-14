#!/usr/bin/env python 
#########################

import sys
import matplotlib
matplotlib.use('PS')
import publication_plots as pp
import process_cosmos_sims as pcs, process_cosmos_sims_plots as pcsp
import pylab

#########################

dir = sys.argv[1]
contamdir = sys.argv[2]
output = sys.argv[3]

######################

consol = pcs.consolidate(pcs.processSummaryDir(dir))
contamconsol = pcs.consolidate(pcs.processSummaryDir(contamdir))

pcsp.publicationBias(consol, contamconsol)


pylab.savefig(output)
