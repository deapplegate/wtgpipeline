#! /usr/bin/env python
from glob import glob
import astropy
import astropy.io.fits
import os,sys
from adam_quicktools_ArgCleaner import ArgCleaner
args=ArgCleaner(sys.argv)
flag_fls=filter( lambda x: x.endswith('flag.fits') ,args)
if not len(args)==len(flag_fls):
	raise Exception('Some of the files you entered arent flag.fits files!')

for fl in flag_fls:
	wtfl=fl.replace('flag','weight')
	os.system('cp %s /u/ki/awright/data/MACS1115+01/W-C-RC/WEIGHTS/pre_ring_backup/' % (fl))
	flag=astropy.io.fits.open(fl)[0].data
	wtfo=astropy.io.fits.open(wtfl,'update')
	flag0s=(flag==0.0).mean()
	if flag0s<.05:
		scifl=fl.replace('flag.','')
		scifl=scifl.replace('WEIGHTS','SCIENCE')
		scifo=astropy.io.fits.open(scifl)
		if scifo[0].header['BADCCD']!=1:
			raise Exception('FLAGS are all positive, yet BADCCD!=1')
	flag_mask=(flag>0)
	wtfo[0].data[flag_mask]=0.0
	wtfo.flush()
	wtfo.close()
