#!/usr/bin/env python

import ldac, astropy.io.fits as pyfits, sys, numpy

subsetcatfile = sys.argv[1]
fullcatfile = sys.argv[2]
outcatfile = sys.argv[3]

def matchById(smallcat, bigcat, smallid='SeqNr', bigid=None):
    if bigid is None:
        bigid = smallid

    seqnr = {}
    for x in bigcat[bigid]:
        seqnr[x] = False
        
    for x in smallcat[smallid]:
        seqnr[x] = True
            
    keep = numpy.array([seqnr[x] for x in bigcat[bigid]])
    matched = bigcat.filter(keep)
    return matched

def _transferOtherHDUs(catfile):

    hdulist = pyfits.open(catfile)
    otherhdus = []
    for hdu in hdulist:
        try:
            if hdu.header['EXTNAME'] != 'OBJECTS':
                otherhdus.append(hdu)
        except KeyError:
            pass

    return otherhdus


subsetcat = ldac.openObjectFile(subsetcatfile)
fullcat = ldac.openObjectFile(fullcatfile)

matchedCat = matchById(subsetcat, fullcat)

hdus = [ pyfits.PrimaryHDU(), matchedCat.hdu]
hdus.extend(_transferOtherHDUs(fullcatfile))

hdulist = pyfits.HDUList(hdus)
hdulist.writeto(outcatfile, overwrite = True)
