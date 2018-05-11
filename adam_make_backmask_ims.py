#! /usr/bin/env python
#adam-call_example# call it like: ./adam_make_backmask_ims.py ~/my_data/SUBARU/${cluster}/${filter}/SCIENCE/ ${ending}
#adam-does# makes BACKMASK directory with images used to mask reflections, cross-talk, areas of coherent offsets in astrometry, and maybe even asteroids
#        mask in difference coadds, but place regions in SUPA*_[0-9]OCF.fits images, so regions are placed on individual chip exposures with backmask.py
# 	SUPAXXXXXXX-all.coadd.fits         : difference images for each exposure ("coadd_cluster_SUPAXXXXXXX"-"coadd_cluster_all")
# 	SUPAXXXXXXX-all.coadd.smoothed.fits: smoothed difference images
#adam-call_example# adam_make_backmask_ims.py /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/
#adam-comments# very useful

#BEFORE RUNNING CODE (1): set make_smoothed if you want smoothed images for all types of coadd differences (all, gabodsid, gabrot)
#BEFORE RUNNING CODE (2): set make_gabodsid and make_gabrot to determine the types of coadd differences you want to make (makes "all" always), can make gabodsid & gabrot as well
make_smoothed=1
make_gabodsid=1
make_gabrot=0

from numpy import *
import scipy.ndimage as ndimage
import matplotlib.pyplot as plt
import glob
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


dir_backmask=input_dir+'BACKMASK/'
if not os.path.exists(dir_backmask):
	os.makedirs(dir_backmask)


supa_fls=glob.glob(input_dir+'coadd_'+cluster+'_SUPA*/coadd.fits')
regex_cluster=imagetools.getRegex(cluster)
if make_gabodsid==1:
	gabodsid_fls=glob.glob(input_dir+'coadd_'+cluster+'_gabodsid[0-9][0-9][0-9][0-9]/coadd.fits')
	gabodsid_dict={}
	for fl in gabodsid_fls:
		coadd_gabodsid_dir=fl.split('/')[-2]
		fl_match=re.match('coadd_'+regex_cluster+'_gabodsid([0-9][0-9][0-9][0-9])',coadd_gabodsid_dir)
		gabodsid=fl_match.group(1)
		gabodsid_dict[gabodsid]=fl

if make_gabrot==1:
	gabrot_fls=glob.glob(input_dir+'coadd_'+cluster+'_gab[0-9][0-9][0-9][0-9]-rot[0-1]/coadd.fits')
	gabrot_dict={}
	for fl in gabrot_fls:
		coadd_gabrot_dir=fl.split('/')[-2]
		fl_match=re.match('coadd_'+regex_cluster+'_gab([0-9][0-9][0-9][0-9])-rot([0-1])',coadd_gabrot_dir)
		gab=fl_match.group(1)
		rot=fl_match.group(2)
		gabrot='gab'+gab+'-rot'+rot
		gabrot_dict[gabrot]=fl

#SHNT: now make a dict that matches keys I'll get from the coadd_fl's I'm looping over
# to the matching gabrot_fl and gabodsid_fl
all_fls=glob.glob(input_dir+'coadd_'+cluster+'_all/coadd.fits')
all_fl=all_fls[0]
all_head=pyfits.open(all_fl)[0].header
all_img=imagetools.GetImage(all_fl)
all0s=all_img==0
smoothed_fls=[]
place_reg_fls=[]
orig_dir=input_dir.replace('/SCIENCE/','')+"_*/SCIENCE/"
for supa_fl in supa_fls:
	supa_dir=os.path.dirname(supa_fl)
	supa=supa_dir[-11:]
	split_fl_str=input_dir+supa+'_[0-9]*%s*.fits' % (ending)
	#adam-old# split_fl_str=orig_dir+supa+'_[0-9]*%s*.fits' % (ending)
	split_fls=glob.glob(split_fl_str)
	split_fl=split_fls[0]
	if len(split_fls)<10:
		raise Exception("split_fl: "+split_fl+" isn't returning 10 matches")
	split_head=pyfits.open(split_fl)[0].header
	gab=str(split_head['GABODSID'])
	rot=str(split_head['ROTATION'])
	gabrot='gab'+gab+'-rot'+rot
	supa_img=imagetools.GetImage(supa_fl)
	supa0s=supa_img==0

	#make exposure-all images
	im0s=logical_or(supa0s,all0s)
	difference_img=supa_img-all_img
	difference_img[im0s]=0
	diffim=difference_img.copy()
	diffim[im0s]=nan
	hdu=pyfits.PrimaryHDU(asarray(diffim,dtype=float32))
	hdu.header=all_head
	difference_fl=dir_backmask+supa+'-all.coadd.fits'
	hdu.writeto(difference_fl,overwrite=True,output_verify='ignore')
	# make smoothed image
	if make_smoothed!=0:
		smooth_img = ndimage.gaussian_filter(difference_img, sigma=3)
		smooth_img[im0s]=nan
		hdu=pyfits.PrimaryHDU(asarray(smooth_img,dtype=float32))
		hdu.header=all_head
		smoothed_fl=difference_fl.replace('coadd','coadd.smoothed')
		hdu.writeto(smoothed_fl,overwrite=True,output_verify='ignore')
		print 'wrote 2 files: '+smoothed_fl+'\n\tand '+difference_fl
		smoothed_fls.append(smoothed_fl)
		place_reg_fls.append(split_fl_str)
	else: print 'wrote file: '+difference_fl

	#make gabodsid-all images
	if make_gabodsid==1:
		if gabodsid_dict.has_key(gab):
			gabodsid_fl=gabodsid_dict[gab]
			gabodsid_img=imagetools.GetImage(gabodsid_fl)
			gabodsid0s=gabodsid_img==0
			im0s=logical_or(supa0s,gabodsid0s)
			difference_img=supa_img-gabodsid_img
			difference_img[im0s]=0
			diffim=difference_img.copy()
			diffim[im0s]=nan
			hdu=pyfits.PrimaryHDU(asarray(diffim,dtype=float32))
			hdu.header=all_head
			difference_fl=dir_backmask+supa+'-gabodsid'+gab+'.coadd.fits'
			hdu.writeto(difference_fl,overwrite=True,output_verify='ignore')
			# make smoothed image
			if make_smoothed!=0:
				smooth_img = ndimage.gaussian_filter(difference_img, sigma=3)
				smooth_img[im0s]=nan
				hdu=pyfits.PrimaryHDU(asarray(smooth_img,dtype=float32))
				hdu.header=all_head
				smoothed_fl=difference_fl.replace('coadd','coadd.smoothed')
				hdu.writeto(smoothed_fl,overwrite=True,output_verify='ignore')
				print 'wrote 2 files: '+smoothed_fl+'\n\tand '+difference_fl
				smoothed_fls.append(smoothed_fl)
				place_reg_fls.append(split_fl_str)
			else: print 'wrote file: '+difference_fl
		else: print "gabodsid "+gab+" not found!"

	#make gabodsid_rot-all images
	if make_gabrot==1:
		if gabrot_dict.has_key(gabrot):
			gabrot_fl=gabrot_dict[gabrot]
			gabrot_img=imagetools.GetImage(gabrot_fl)
			gabrot0s=gabrot_img==0
			im0s=logical_or(supa0s,gabrot0s)
			difference_img=supa_img-gabrot_img
			difference_img[im0s]=0
			diffim=difference_img.copy()
			diffim[im0s]=nan
			hdu=pyfits.PrimaryHDU(asarray(diffim,dtype=float32))
			hdu.header=all_head
			difference_fl=dir_backmask+supa+'-'+gabrot+'.coadd.fits'
			hdu.writeto(difference_fl,overwrite=True,output_verify='ignore')
			# make smoothed image
			if make_smoothed!=0:
				smooth_img = ndimage.gaussian_filter(difference_img, sigma=3)
				smooth_img[im0s]=nan
				hdu=pyfits.PrimaryHDU(asarray(smooth_img,dtype=float32))
				hdu.header=all_head
				smoothed_fl=difference_fl.replace('coadd','coadd.smoothed')
				hdu.writeto(smoothed_fl,overwrite=True,output_verify='ignore')
				print 'wrote 2 files: '+smoothed_fl+'\n\tand '+difference_fl
				smoothed_fls.append(smoothed_fl)
				place_reg_fls.append(split_fl_str)
			else: print 'wrote file: '+difference_fl
		else: print "gabrot "+gabrot+" not found!"


if make_smoothed!=0:
	for place_reg_fl,smoothed_fl in zip(place_reg_fls,smoothed_fls):
		print "ipython -i -- backmask.py %s %s" % (smoothed_fl,place_reg_fl)
