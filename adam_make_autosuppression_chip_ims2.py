#! /usr/bin/env python
#adam-call_example# call it like: ./adam_make_autosuppression_chip_ims2.py ~/my_data/SUBARU/${cluster}/${filter}/SCIENCE/ ${ending}
#adam-call_example# call it like: ./adam_make_autosuppression_chip_ims2.py ~/data/MACS1115+01/W-C-RC/SCIENCE/ OCFSI
# set make_smoothed if you want to MAKE smoothed images
make_smoothed=0
make_regs=1

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
dir_template=input_dir+'autosuppression/template_rings_rot'
dir_reg=input_dir+'autosuppression/'


supa_fls=[]
supa_groups={1:[1,6,2,7],2:[3,8,4,9,5,10]}
use_chips=[8,4,5,7,3,9,10]
use_chips+=[2]

supa_chips={}
supa_only=glob(input_dir+'SUPA00*_%s%s.fits' % (1,ending))
supas=[os.path.basename(ss).replace('_1'+ending+'.fits','') for ss in supa_only]
for chip in use_chips:
	supa_fls+=glob(input_dir+'SUPA00*_%s%s.fits' % (chip,ending))
	supa_chips[chip]=glob(input_dir+'SUPA00*_%s%s.fits' % (chip,ending))


#SHNT: now make a dict that matches keys I'll get from the coadd_fl's I'm looping over
# to the matching gabrot_fl and gabodsid_fl
smoothed_fls=[]
place_reg_fls=[]
fo=open('toMask_RXJ2129_rot0_10_2.list','w')
for chip in use_chips:
    ds9str="ds9 -view layout vertical -zoom to fit -geometry 2000x2000 -cmap bb -zscale "
    for supa in supas:
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
	if config!="10_2": continue ##adam-tmp
	if rot!="0": continue ##adam-tmp
	place_reg_fl='%s/%s' % (dir_reg,os.path.basename(supa_fl).replace(ending+'.fits','.reg'))
	if make_regs!=0:
		print 'cp -n %s%s/chip_%s.reg %s' % (dir_template,rot,chip,place_reg_fl)
		os.system('cp -n %s%s/chip_%s.reg %s' % (dir_template,rot,chip,place_reg_fl))
	place_reg_fls.append(place_reg_fl)
	ds9str+= " %s -region load %s" % (smoothed_fl,place_reg_fl)
	fo.write(smoothed_fl+'\n')

    ds9str+=" -frame lock wcs -title 'chip"+str(chip)+"' &\n"
    #adam-tmp# print ds9str
print 'toMask_RXJ2129_rot0_10_2.list'
fo.close()
