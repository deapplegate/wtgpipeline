#!/usr/bin/env python
#######################
# Run a henk style analysis through the batch queue
########################

import numpy as np
import sys, ldac, astropy.io.fits as pyfits
import shearprofile as sp
import bootstrap_masses as bm
import process_cosmos_sims as pcs
import os, cPickle
import pdzfile_utils as pdzutils, nfwutils

#########################


inputCatFile = sys.argv[1]
bpzfile = sys.argv[2]
pdzfile = sys.argv[3]
nBootstraps = int(sys.argv[4])
msigma = float(sys.argv[5])
bpzcut = float(sys.argv[6])
outputFile = sys.argv[7]

##########################

inputcat = ldac.openObjectFile(inputCatFile)

concentration = inputcat.hdu.header['CONCEN']
zcluster = inputcat.hdu.header['Z']
true_scale_radius = inputcat.hdu.header['R_S']

bpz = ldac.openObjectFile(bpzfile, 'STDTAB').matchById(inputcat, 'z_id')

pdzmanager = pdzutils.PDZManager.open(pdzfile)

pdzrange, pdzs = pdzmanager.associatePDZ(inputcat['z_id'])

foregroundprob = pdzs.cumsum(axis=-1).T[pdzrange <= zcluster][-1]


goodObjs = np.logical_and(bpz['BPZ_ODDS'] > bpzcut,
                          np.logical_and(bpz['BPZ_Z_B'] < 1.25,
                                         foregroundprob < 0.25))

#                                         bpz['z_b'] > zcluster + 0.1),

betas = nfwutils.beta_s(bpz['BPZ_Z_B'], zcluster)


sigma = 0.25

print '!!!!!!!!!!!!!!'
print len(inputcat.filter(goodObjs))


rss, nfails = bm.bootstrap_newman_method(inputcat['r_mpc'][goodObjs], 
                                             inputcat['ghats'][goodObjs], 
                                             betas[goodObjs], 
                                             sigma,
                                             concentration, 
                                             zcluster, 
                                             nBootstraps, msigma = msigma)



#r500 = nfwutils.rdelta(true_scale_radius, concentration, 500)
#m500 = nfwutils.Mdelta(true_scale_radius, concentration, zcluster, 500)
m15 = nfwutils.massInsideR(true_scale_radius, concentration, zcluster, 1.5)

masses = np.array([nfwutils.massInsideR(x, concentration, zcluster, 1.5) \
                       for x in rss])

mu = np.mean(masses)
sig = np.std(masses)

chisq = ((masses - mu)/sig)**2
    
massdist = pcs.MassDist(zcluster, true_scale_radius, m15, mu, sig, chisq)

cols = [ pyfits.Column(name = 'Rs', format = 'E', array = rss),
         pyfits.Column(name = 'masses', format = 'E', array = masses)]

cat = pyfits.BinTableHDU.from_columns(cols)
cat.header['EXTNAME']= 'OBJECTS'
cat.header['NFAILS']= nfails

cat.writeto(outputFile, overwrite=True)

base, ext = os.path.splitext(outputFile)
output = open('%s.pkl' % base, 'wb')
cPickle.dump(massdist, output)
output.close()
