#! /usr/bin/env python
import astropy, sys, os
import astropy.io.fits
from adam_quicktools_ArgCleaner import ArgCleaner
args=ArgCleaner(sys.argv)
for arg in args:
	assert os.path.isfile(arg)
	assert arg.endswith('.fits')
	fo=astropy.io.fits.open(arg,mode='update')
	fo.verify('fix')
	fo.flush()
	fo.close()
		

