#!/usr/bin/env python

import sys, astropy.io.fits as pyfits
from numpy import *

image_name = sys.argv[1]
weight_name = sys.argv[2]
out_name = sys.argv[3]

image_hdu = pyfits.open(image_name)[0]
image = image_hdu.data
header = image_hdu.header
weight = pyfits.open(weight_name)[0].data

goodpix = weight > 0

sigma = std(image[goodpix], dtype=float128)

print 'Number of good pixels: %d     Sigma = %f' % (len(image[goodpix]),
                                                    sigma)

shape = image.shape

noise = sigma*random.standard_normal(shape)

out_hdu = pyfits.PrimaryHDU(noise, header=header)
out_hdu.writeto(out_name, output_verify='ignore')


