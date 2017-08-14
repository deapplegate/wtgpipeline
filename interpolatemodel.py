#!/usr/bin/env python
#########################
# Make Illumination correction images
##########################

import pyfits, illummodels, os.path, sys, re
from numpy import *

########################

__cvs_id__ = "$Id: interpolatemodel.py,v 1.3 2009-04-20 23:09:43 dapple Exp $"

#######################


#first axis in pyfits is y axis
#model passed in is in physical x,y params


def interpolateModel(model, xvals, yvals):
    X,Y = meshgrid(xvals, yvals)
    return model(X,Y)

def makeCorrection(filename):

    base, ext = os.path.splitext(filename)

    header = pyfits.getheader(filename)
    xsize = header['NAXIS1']
    ysize = header['NAXIS2']
    

    model = illummodels.findChipModel(filename)
        
    correction = interpolateModel(model, xrange(xsize), xrange(ysize))

    if correction.dtype != float32:
        hdu = pyfits.PrimaryHDU(correction.astype(float32))
    else:
        hdu = pyfits.PrimaryHDU(correction)
    

    hdu.writeto('%s.illumcor.fits' % base, clobber = True)

if __name__ == '__main__':
    
    files = sys.argv[1:]
    for file in files:
        print 'Processing %s' % file
        try:
            makeCorrection(file)
        except illummodels.UnreadableException, e:
            sys.stderr.write(e.message)
            continue

