#! /usr/bin/env python
#adam-does# makes autosuppression directory with images that can be used to place stellar halos
# 	SUPAXXXXXXX.coadd.smoothed.fits: smoothed images
#adam-call_example# call it like: adam_make_autosuppression_ims.py /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/
#adam-comments# not useful
from numpy import *
import scipy.ndimage as ndimage
import matplotlib.pyplot as plt
import glob
import sys ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
import imagetools
import pyfits
import os
input_dir=sys.argv[1]
input_dir=input_dir.replace('//','/')
if not input_dir.endswith('/'):
	input_dir+='/'
if not os.path.exists(input_dir):
	raise Exception("input_dir=sys.argv[1]:" +input_dir+ " isn't a directory")

dir_splits=input_dir.split('/')
try:
	dir_splits.remove('')
	dir_splits.remove('')
except ValueError:
	pass
cluster=dir_splits[-3]
filter=dir_splits[-2]


dir_autosuppression=input_dir+'autosuppression/'
if not os.path.exists(dir_autosuppression):
	os.makedirs(dir_autosuppression)

coadd_fls=glob.glob(input_dir+'coadd_'+cluster+'_SUPA*/coadd.fits')
orig_dir=input_dir.replace('/SCIENCE/','')+"_*/SCIENCE/"
for coadd_fl in coadd_fls:
	coadd_img=imagetools.GetImage(coadd_fl)
	# make difference image
	im0s=coadd_img==0
	head=pyfits.open(coadd_fl)[0].header
	coadd_dir=os.path.dirname(coadd_fl)
	supa=coadd_dir[-11:]
	split_fl=orig_dir+supa+'_[0-9]*OCF.fits'
	if len(glob.glob(split_fl))!=10:
		raise Exception("split_fl: "+split_fl+" isn't returning 10 matches")
	# make smoothed image
	smooth_img = ndimage.gaussian_filter(coadd_img, sigma=4)
	smooth_img[im0s]=nan
	hdu=pyfits.PrimaryHDU(asarray(smooth_img,dtype=float32))
	hdu.header=head
	smoothed_fl =dir_autosuppression+supa+'.coadd.smoothed.fits'
	hdu.writeto(smoothed_fl,clobber=True,output_verify='ignore')
	print 'wrote file: '+smoothed_fl
