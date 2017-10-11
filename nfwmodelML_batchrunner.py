#!/usr/bin/env python
#######################
# Run a ML pdz fit for an nfw model
########################

import numpy as np
import sys, ldac, astropy, astropy.io.fits as pyfits, cPickle
import shearprofile as sp
import nfwmodel



#########################

def matchById(smallcat, bigcat, smallid='SeqNr', bigid=None):
    if bigid is None:
        bigid = smallid

    seqnr = {}
    for i, x in enumerate(bigcat[bigid]):
        seqnr[x] = i
        
    keep = []
    for x in smallcat[smallid]:
        keep.append(seqnr[x])
            
    keep = np.array(keep)
    matched = bigcat.filter(keep)
    return matched


################################


inputCatFile = sys.argv[1]
inputPDZ = sys.argv[2]
outputFile = sys.argv[3]

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


pdzfile = open(inputPDZ, 'rb')
pdzrange, pdz = cPickle.load(pdzfile)
pdzrange = pdzrange.astype(np.float64)
pdz = pdz.astype(np.float64)


betas = sp.beta_s(pdzrange, zcluster)

rs = np.arange(0.01, 1.0, 0.0005)

rs, scan = nfwmodel.scan_model(rs, 
                               inputcat['r_mpc'][goodObjs].astype(np.float64),
                               inputcat['ghats'][goodObjs].astype(np.float64),
                               betas,
                               pdz[goodObjs],
                               concentration,
                               zcluster,
                               np.array([0.25])[0])



cols = [ pyfits.Column(name = 'Rs', format = 'E', array = rs),
         pyfits.Column(name = 'prob', format = 'E', array = scan)]
cat = pyfits.BinTableHDU.from_columns(cols)
cat.header['EXTNAME']= 'OBJECTS'

cat.writeto(outputFile, overwrite=True)
