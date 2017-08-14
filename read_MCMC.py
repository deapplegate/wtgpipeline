#! /usr/bin/env python

from dappleutils import *
import shearprofile as sp
from optparse import OptionParser
import sys
import os

if len(sys.argv) != 5:
    print "wrong number of arguments!"
    sys.exit(1)

catfile=  sys.argv[1]
mcmcfile= sys.argv[2]
clusterz= float(sys.argv[3])
beta=     float(sys.argv[4])

mcmc = sp.readMCMC(mcmcfile)
mcmc.drop(10000)
masses = sp.AdamMass(mcmc.c, mcmc.rs, beta, clusterz)
peak,low,upp=sp.ConfidenceRegion(masses)

filebase,ext=os.path.splitext(catfile)
output = open(filebase+"_nfwfit.dat", 'w')
output.write("mass: %g  %g  %g\n" % (peak[0], low[0], upp[0]))
output.close()
