#!/usr/bin/env python
#######################
# Run a ML pdz fit for an nfw model
########################

import numpy as np
import sys, ldac, pyfits, cPickle
import shearprofile as sp
import nfwmodel



##########################

inputCatFile = sys.argv[1]
inputPDZ = sys.argv[2]
shapedistro_module = sys.argv[3]
outputFile = sys.argv[4]

##########################

inputcat = ldac.openObjectFile(inputCatFile)

concentration = inputcat.hdu.header['CONCEN']
zcluster = inputcat.hdu.header['Z']


D_lens = sp.angulardist(zcluster)
pixscale = 0.2
minPix = 0.3 * 3600. * (180./np.pi) / ( pixscale * D_lens )
maxPix = 5. * 3600. * (180./np.pi) / ( pixscale * D_lens )

goodObjs = np.logical_and(np.logical_and(inputcat['r_pix'] > minPix, 
                                         inputcat['r_pix'] < maxPix),
                          np.logical_and(inputcat['z_b'] > 0,
                                         inputcat['z_b'] < 1.25))


shapedistro = __import__(shapedistro_module)

bin_selectors = [np.logical_and(goodObjs, selector) \
                     for selector in shapedistro.bin_selectors(inputcat)]


pdzfile = open(inputPDZ, 'rb')
pdzrange, pdz = cPickle.load(pdzfile)
pdzrange = pdzrange.astype(np.float64)
pdz = pdz.astype(np.float64)


betas = sp.beta_s(pdzrange, zcluster)

rs = np.arange(0.01, 1.0, 0.0005)

rs, scan = nfwmodel.scan_model(rs, 
                               [inputcat['r_mpc'][x].astype(np.float64) for x in bin_selectors],
                               [inputcat['ghats'][x].astype(np.float64) for x in bin_selectors],
                               betas,
                               [pdz[x] for x in bin_selectors],
                               concentration,
                               zcluster,
                               shapedistro.likelihood_func,
                               shapedistro.samples)




cols = [ pyfits.Column(name = 'Rs', format = 'E', array = rs),
         pyfits.Column(name = 'prob', format = 'E', array = scan)]
cat = pyfits.new_table(cols)
cat.header.update('EXTNAME', 'OBJECTS')

cat.writeto(outputFile, clobber=True)
