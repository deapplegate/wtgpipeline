#! /usr/bin/env python
from glob import glob
coadd_masterdir='/gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-C-RC/SCIENCE/'
supa_coadds=glob(coadd_masterdir+'SUPA0*_8OCFSI.fits')
median_coadd=coadd_masterdir+'coadd_RXJ2129_all/coadd.fits'
medianfitsfl=astropy.io.fits.open(median_coadd)
median_image=medianfitsfl[0].data
median_header=medianfitsfl[0].header
medianfitsfl.close()
for supa in supa_coadds:

	supa_fitsfl=astropy.io.fits.open(supa)
	#supa_image=supa_fitsfl[0].data
	supa_header=supa_fitsfl[0].header
	supa_fitsfl.close()
	## 
