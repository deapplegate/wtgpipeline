#! /usr/bin/env python
#adam-call_example# call it like: ./adam_make_poly_masks_chip1_and_6.py ~/my_data/SUBARU/${cluster}/${filter}/SCIENCE/ ${ending}
# set make_smoothed if you want to MAKE smoothed images
make_smoothed=0
make_regs=0

from numpy import *
import scipy.ndimage as ndimage
import matplotlib.pyplot as plt
from glob import glob
import sys ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
import imagetools
import astropy, astropy.io.fits as pyfits
import os
import re
from adam_quicktools_ArgCleaner import ArgCleaner
args=ArgCleaner(sys.argv)

input_dir=args[0]
ending=args[1]

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

dir_smooth_chip=input_dir+'autosuppression_smoothed_chips/'
if not os.path.exists(dir_smooth_chip):
	os.makedirs(dir_smooth_chip)
dir_template=input_dir+'autosuppression/chip1_and_6_masks/'
dir_reg=dir_template


supa_fls=[]
supa_groups={1:[1,6,2,7],2:[3,8,4,9,5,10]}
chip2group={}
for chip in range(1,11):
    for group in supa_groups.keys():
        if chip in supa_groups[group]:
		chip2group[chip]=group

supa_chips={}
supa_only=glob(input_dir+'SUPA0*_%s%s.fits' % (1,ending))
supas=[os.path.basename(ss).replace('_1'+ending+'.fits','') for ss in supa_only]
for chip in range(1,11):
	supa_fls+=glob(input_dir+'SUPA0*_%s%s.fits' % (chip,ending))
	supa_chips[chip]=glob(input_dir+'SUPA0*_%s%s.fits' % (chip,ending))


#SHNT: now make a dict that matches keys I'll get from the coadd_fl's I'm looping over
# to the matching gabrot_fl and gabodsid_fl
smoothed_fls=[]
place_reg_fls=[]
ds9str={}
chips=[3,4]
for chip in [2,3,8]:
	ds9str[chip]="ds9 -zoom to fit -geometry 2000x2000 -cmap bb -zscale -lock frame wcs "

for supa in supas:
    for chip in [2,3,8]:
	supa_fl=input_dir+supa+'_'+str(chip)+ending+'.fits'
	supa_fitsfl=astropy.io.fits.open(supa_fl)
	supa_header=supa_fitsfl[0].header
	# make smoothed image
	smoothed_fl=os.path.basename(supa_fl).replace('.fits','_smoothed.fits')
	smoothed_fl=dir_smooth_chip+os.path.basename(supa_fl).replace('.fits','_smoothed.fits')
	if make_smoothed!=0:
		supa_image=supa_fitsfl[0].data
		smooth_img = ndimage.gaussian_filter(supa_image, sigma=4)
		hdu=pyfits.PrimaryHDU(asarray(smooth_img,dtype=float32))
		hdu.header=supa_header
		hdu.writeto(smoothed_fl,overwrite=True,output_verify='ignore')
		print 'wrote smoothed file: '+smoothed_fl
	supa_fitsfl.close()
	smoothed_fls.append(smoothed_fl)
	## use this part to get starting templates and make a ds9 call printout
	rot=str(supa_header['ROTATION'])
	config=str(supa_header['CONFIG'])
	if config=="10_3": continue ##adam-tmp
	if rot=="1": continue ##adam-tmp
	place_reg_fl='%s/%s' % (dir_reg,os.path.basename(supa_fl).replace(ending+'.fits','.reg'))
	if chip==8:
		print 'cp -n %s/starmask_%s.reg %s' % (dir_template,6,place_reg_fl)
		os.system('cp -n %s/starmask_%s.reg %s' % (dir_template,6,place_reg_fl))
	else:
		os.system('echo "" >> %s' % (place_reg_fl))
	place_reg_fls.append(place_reg_fl)
	group=chip2group[chip]
	ds9str[chip]+= " %s -region load %s" % (smoothed_fl,place_reg_fl)

for chip in [2,3,8]:
    ds9str[chip]+=" &"
    print ds9str[chip]
