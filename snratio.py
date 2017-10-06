from __future__ import with_statement
import astropy.io.fits as pyfits
from numpy import *
from pylab import *
import cPickle, sys, os


imagefile = sys.argv[1]
outfile = sys.argv[2]



hdulist = pyfits.open(imagefile)
image = hdulist[0].data

base, ext = os.path.splitext(imagefile)

weightimage = pyfits.open('%s.weight.fits' % base)[0].data

weight_thresh = 0.85*amax(weightimage)

accept = weightimage > weight_thresh


xbounds = (0,image.shape[0])
ybounds = (0, image.shape[1])

image = image - mean(image[accept], dtype=float128)
sigma_1 = std(image[accept], dtype=float128)

def calcSNBox(image, weightimage, xbounds, ybounds, boxsize):

    pixsums = []

    for xi in (arange(xbounds[0], xbounds[1], boxsize) + boxsize/2):
        for yi in (arange(ybounds[0], ybounds[1], boxsize) + boxsize/2):

            cutout = image[xi-boxsize/2:xi+boxsize/2+1, yi-boxsize/2:yi+boxsize/2+1]
            weight_cutout = weightimage[xi-boxsize/2:xi+boxsize/2+1, yi-boxsize/2:yi+boxsize/2+1]

            if len(cutout[weight_cutout < weight_thresh]) > 0.95*len(cutout) or \
                    len(cutout[weight_cutout == 0]) > 0.01*boxsize**2:
                continue

            pixsum = sum(cutout, dtype=float128)
            pixsums.append(pixsum)

    pixsums = array(pixsums)

    print 'Num Points: %d' % len(pixsums)

    clippedpixsums = pixsums
    for counter in range(20):
        sigma = sqrt(mean(clippedpixsums**2, dtype=float128))
        clippedpixsums = clippedpixsums[abs(clippedpixsums) < 5*sigma]
        

    return pixsums, sigma

boxsizes = array([2, 4, 6,10,20,60,100,200, 400, 600, 800, 1000])
#

pixsums = []
sigmas = []
ratios = []

for boxsize in boxsizes:
    
    print 'Current Box Size: %d' % boxsize
    pixsum, sigma = calcSNBox(image, weightimage,xbounds, ybounds, boxsize)
    pixsums.append(pixsum)
    sigmas.append(sigma)
    ratios.append( sigma/(boxsize*sigma_1) )


with open(outfile, 'wb') as output:
    cPickle.dump((boxsizes, sigmas, ratios), output)
