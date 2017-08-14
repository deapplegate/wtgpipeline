#!/usr/bin/env python
#######################
# Run a henk style analysis through the batch queue
########################

import numpy as np
import sys, ldac, pyfits
import bootstrap_masses as bm
import process_cosmos_sims as pcs
import os, cPickle

#########################


inputCatFile = sys.argv[1]

nBootstraps = int(sys.argv[2])

bpzcut = float(sys.argv[3])

outputFile = sys.argv[4]

##########################

inputcat = ldac.openObjectFile(inputCatFile)

concentration = inputcat.hdu.header['CONCEN']
zcluster = inputcat.hdu.header['Z']
true_scale_radius = inputcat.hdu.header['R_S']

goodObjs = np.logical_and(inputcat['z_odds'] > bpzcut,
                          np.logical_and(inputcat['z_b'] > zcluster + 0.1,
                                         inputcat['z_b'] < 1.25))




betas = sp.beta_s(inputcat['z_b'], zcluster)


rss, nfails = bm.bootstrap_beta_method(inputcat['r_pix'][goodObjs], 
                                    inputcat['r_mpc'][goodObjs], 
                                    inputcat['ghats'][goodObjs], 
                                    betas[goodObjs], 
                                    concentration, 
                                    zcluster, 
                                    nBootstraps)



r500 = sp.NFWRdelta(500, 4.0, true_scale_radius)

masses = np.array([sp.AdamMass(4.0, x, r500, zcluster) for x in rss])

mu = np.mean(masses)
sig = np.std(masses)

chisq = ((masses - mu)/sig)**2
    
massdist = pcs.MassDist(zcluster, true_scale_radius, mu, sig, chisq)

cols = [ pyfits.Column(name = 'Rs', format = 'E', array = rss),
         pyfits.Column(name = 'masses', format = 'E', array = masses)]

cat = pyfits.new_table(cols)
cat.header.update('EXTNAME', 'OBJECTS')
cat.header.update('NFAILS', nfails)

cat.writeto(outputFile, clobber=True)

base, ext = os.path.splitext(outputFile)
output = open('%s.pkl' % base, 'wb')
cPickle.dump(massdist, output)
output.close()
