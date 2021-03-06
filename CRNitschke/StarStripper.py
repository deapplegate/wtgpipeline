#! /usr/bin/env python
import sys ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons/')
import imagetools
from import_tools import *
import numpy
numpy.warnings.filterwarnings('ignore') #adam-tmp#
warnings.simplefilter("ignore", DeprecationWarning)
fl=sys.argv[-1]
ending=""
#fl='/nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-S-Z+_2010-11-04/SCIENCE/SUPA0125892_7OCF.fits'
#crfl='/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_BB_CRN-cosmics_MACS0416-24_W-S-Z+.SUPA0125892_7.fits'
header=astropy.io.fits.open(fl)[0].header
OBJECT=header['MYOBJ']
FILTER=header['FILTER']
CCDnum=header['IMAGEID']

flname=os.path.basename(fl).split('.')[0]
if 'OCF' in fl:
	BASE=os.path.basename(fl).split('OCF')[0]
else:
	BASE=flname
OFB='%s_%s_%s' % (OBJECT,FILTER,BASE,)
image=imagetools.GetImage(fl)
compare_dir='/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_compare/'
plot_dir='/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/plot_SCIENCE_SS/'
BBCRfl='/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_BB_CRN-cosmics_%s_%s.%s%s.fits' % (OBJECT,FILTER,BASE,ending)
CR_segfl='/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_CRN-cosmics_%s_%s.%s%s.fits' % (OBJECT,FILTER,BASE,ending)
CR_filtfl='/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/FILTERED_CRN-cosmics_%s_%s.%s%s.fits' % (OBJECT,FILTER,BASE,ending)
#fl_original=compare_dir+'BBout_ORIGINAL_%s_%s.%s.fits' % (OBJECT,FILTER,BASE)
fl_woblend=compare_dir+'BBout_WOblend_%s_%s.%s%s.fits' % (OBJECT,FILTER,BASE,ending)
fl_revised=compare_dir+'BBrevised_*_BBCR_%s_%s.%s%s.fits' % (OBJECT,FILTER,BASE,ending)
#fl_erase=compare_dir+'BB_ERASED_'+bthresh1_tag+'_BBCR_%s_%s.%s.fits' % (OBJECT,FILTER,BASE)
#fl_revised=compare_dir+'BBrevised_'+bthresh1_tag+'_BBCR_%s_%s.%s.fits' % (OBJECT,FILTER,BASE)
#im_erased=astropy.io.fits.open(fl_erased)[0].data
#im_erased.max()
BBCRseg=imagetools.GetImage(BBCRfl)
BBCRseg=asarray(BBCRseg,dtype=int)
crheader=astropy.io.fits.open(BBCRfl)[0].header
SEEING=crheader['MYSEEING']
SEEING_str=('%.3f' % (SEEING)).replace('.','pt')
OFB_SEEING=OFB.replace('SUPA',SEEING_str+'_SUPA')
filtim=imagetools.GetImage(CR_filtfl)

#put SEEING and FILTER dependent kmax cut in here:
import os
CONFIG=os.environ['config']
if CONFIG=="10_3":
	if FILTER=="W-C-RC":
		if SEEING<0.50: kmax=3.50 #based on GUESSING
		elif SEEING<0.60: kmax=2.85 #based on GUESSING
		elif SEEING<0.70: kmax=2.70 #based on MACS1226 data
		else: kmax=2.70
	elif FILTER=="W-S-I+":
		if SEEING<0.50: kmax=3.50 #based on GUESSING
		elif SEEING<0.60: kmax=2.85 #based on GUESSING
		elif SEEING<0.77: kmax=2.70 #based on MACS1226 data
		elif SEEING<0.90: kmax=2.55 #based on MACS1226 data
		else: kmax=2.55
	elif FILTER=="W-C-IC":
		if SEEING<0.50: kmax=3.50 #based on GUESSING
		elif SEEING<0.60: kmax=2.85 #based on GUESSING
		elif SEEING<0.80: kmax=2.70 #based (loosely) on MACS1226 data
		else: kmax=2.70
	elif FILTER=="W-S-Z+":
		if SEEING<0.60: kmax=4.10 #based on MACS0416 data
		elif SEEING<0.70: kmax=3.30 #based on GUESSING
		elif SEEING<0.85: kmax=2.75 #based on MACS1226 data
		elif SEEING<1.2: kmax=2.55 #based (loosely) on MACS1226 data
		else: kmax=2.55
	else:
		kmax=3.00

elif CONFIG=="10_2":
	if SEEING<0.50: kmax=4.10 #based on GUESSING
	elif SEEING<0.70: kmax=3.30 #based on GUESSING
	elif SEEING<1.00: kmax=2.85 #based on MACS1226 data
	else: kmax=2.85
else:
	raise Exception("SUBARU configuration isn't defined")

## get properties of the masks
import skimage
from skimage import measure
cr_regs=skimage.measure.regionprops(label_image=BBCRseg, intensity_image=image)
cr_labels=arange(BBCRseg.max(),dtype=int)+1
cr_e=asarray([cr_regs[i-1].eccentricity for i in cr_labels])
cr_diam=asarray([cr_regs[i-1].equivalent_diameter for i in cr_labels])
cr_solidity=asarray([cr_regs[i-1].solidity for i in cr_labels])
cr_max=asarray([cr_regs[i-1].max_intensity for i in cr_labels])
cr_mean=asarray([cr_regs[i-1].mean_intensity for i in cr_labels])
cr_area=asarray([cr_regs[i-1].area for i in cr_labels])
conn8=ones((3,3),dtype=bool)
CRslices=scipy.ndimage.find_objects(BBCRseg)


def cr_any_label(labels):
	boolim=zeros(BBCRseg.shape,dtype=bool)
	for l in labels:
		boolim+=BBCRseg==l
	return boolim

## see if skewness and kurtosis does anything
def skew_kurt_2D(Z):
	h,w = np.shape(Z)
	x = range(w)
	y = range(h)
	X,Y = np.meshgrid(x,y)
	#Centroid (mean)
	cx = np.sum(Z*X)/np.sum(Z)
	cy = np.sum(Z*Y)/np.sum(Z)
	###Standard deviation
	x2 = (range(w) - cx)**2
	y2 = (range(h) - cy)**2
	X2,Y2 = np.meshgrid(x2,y2)
	#Find the variance
	vx = np.sum(Z*X2)/np.sum(Z)
	vy = np.sum(Z*Y2)/np.sum(Z)
	#SD is the sqrt of the variance
	sx,sy = np.sqrt(vx),np.sqrt(vy)
	###Skewness
	x3 = (range(w) - cx)**3
	y3 = (range(h) - cy)**3
	X3,Y3 = np.meshgrid(x3,y3)
	#Find the thid central moment
	m3x = np.sum(Z*X3)/np.sum(Z)
	m3y = np.sum(Z*Y3)/np.sum(Z)
	#Skewness is the third central moment divided by SD cubed
	skx = m3x/sx**3
	sky = m3y/sy**3
	###Kurtosis
	x4 = (range(w) - cx)**4
	y4 = (range(h) - cy)**4
	X4,Y4 = np.meshgrid(x4,y4)
	#Find the fourth central moment
	m4x = np.sum(Z*X4)/np.sum(Z)
	m4y = np.sum(Z*Y4)/np.sum(Z)
	#Kurtosis is the fourth central moment divided by SD to the fourth power
	kx = m4x/sx**4
	ky = m4y/sy**4
	#Centroid x: cx  #Centroid y: cy
	#StdDev x:   sx  #StdDev y:   sy
	#Skewness x: skx #Skewness y: sky
	#Kurtosis x: kx  #Kurtosis y: ky
	return skx,sky,kx,ky

cr_skxs,cr_skys,cr_kxs,cr_kys=[],[],[],[]
## make the final cuts
MaxInside8s=[]
removed_labels=[]
for i,sl in enumerate(CRslices):
	l=i+1
	spots=BBCRseg[sl]==l
	patch=image[sl]
	max_pos_pt=scipy.ndimage.measurements.maximum_position(patch,spots)
	max_spot=zeros(patch.shape,dtype=bool)
	max_spot[max_pos_pt]=1
	#now make sure max isn't on the edge and is in an open8 portion
	insides_spots=scipy.ndimage.binary_erosion(spots,conn4)
	open8_spots=scipy.ndimage.binary_opening(spots,conn8)
	MaxInside8=(max_spot*insides_spots*open8_spots).any()
	MaxInside8s.append(MaxInside8)
	#now get clipped eccentricity
	clip_spots=binary_propagation(max_spot,mask=spots)
	clip_spots=asarray(clip_spots,dtype=int16)
	try:
		reg=skimage.measure.regionprops(clip_spots)[0]
	except TypeError:
		if 1 in clip_spots.shape:
			cr_skxs.append(nan);cr_skys.append(nan);cr_kxs.append(nan);cr_kys.append(nan)
			continue
	e_clip=reg.eccentricity
	e_orig=cr_e[i]
	#now get skewness and kurtosis
	skx,sky,kx,ky=skew_kurt_2D(patch-patch.min())
	cr_skxs.append(skx);cr_skys.append(sky);cr_kxs.append(kx);cr_kys.append(ky)
	if e_clip>e_orig:
		cr_e[i]=e_clip
	if e_clip>.8 and e_orig<.8:
		removed_labels.append(l)

#######Xspots_starlike=cr_any_label(cr_labels[starlike])
#######Xspots_not_starlike=cr_any_label(cr_labels[logical_not(starlike)])
#######CLIPseg,CLIPseg_Nlabels=scipy.ndimage.label(Xspots_starlike,conn8)
#######CLIPslices=scipy.ndimage.find_objects(CLIPseg)

########f=figure()
########skx,sky,kx,ky=skew_kurt_2D(sp);f.add_subplot(321);title('sp: skx=%.2f,sky=%.2f,kx=%.2f,ky=%.2f' % (skx,sky,kx,ky));imshow(sp,interpolation='nearest',origin='lower left')
########skx,sky,kx,ky=skew_kurt_2D(sp);f.add_subplot(322);title('sp: skx=%.2f,sky=%.2f,kx=%.2f,ky=%.2f' % (skx,sky,kx,ky));imshow(sp,interpolation='nearest',origin='lower left')
########skx,sky,kx,ky=skew_kurt_2D(p);f.add_subplot(323);title('p: skx=%.2f,sky=%.2f,kx=%.2f,ky=%.2f' % (skx,sky,kx,ky));imshow(p,interpolation='nearest',origin='lower left')
########skx,sky,kx,ky=skew_kurt_2D(pppp);f.add_subplot(324);title('pppp: skx=%.2f,sky=%.2f,kx=%.2f,ky=%.2f' % (skx,sky,kx,ky));imshow(pppp,interpolation='nearest',origin='lower left')
########skx,sky,kx,ky=skew_kurt_2D(pp);f.add_subplot(325);title('pp: skx=%.2f,sky=%.2f,kx=%.2f,ky=%.2f' % (skx,sky,kx,ky));imshow(pp,interpolation='nearest',origin='lower left')
########skx,sky,kx,ky=skew_kurt_2D(ppp);f.add_subplot(326);title('ppp: skx=%.2f,sky=%.2f,kx=%.2f,ky=%.2f' % (skx,sky,kx,ky));imshow(ppp,interpolation='nearest',origin='lower left')
########show()

cr_skxs=asarray(cr_skxs).__abs__();cr_skys=asarray(cr_skys).__abs__();cr_kxs=asarray(cr_kxs).__abs__();cr_kys=asarray(cr_kys).__abs__()
cr_kmax=asarray([max(ky,kx) for ky,kx in zip(cr_kys,cr_kxs)])
cr_skmax=asarray([max(sky,skx) for sky,skx in zip(cr_skys,cr_skxs)])
MaxInside8s=asarray(MaxInside8s)
removed_labels=asarray(removed_labels)
starlike=(cr_e<.8)*(cr_area>9)*(cr_area<50)*(cr_max<30000)*MaxInside8s*(cr_kmax<kmax)*(cr_skmax<.88)
starlike_labels=cr_labels[starlike]
Xspots_starlike=cr_any_label(starlike_labels)
Xspots_not_starlike=cr_any_label(cr_labels[logical_not(starlike)])

## save plots of star postage stamps and things that missed the cut
#params=['e=%.2f , area=%i' % (cr_e[i],cr_area[i]) for i in cr_labels-1]
#params=['skxy=%.2f/%.2f|kxy=%.2f/%.2f' % (cr_skxs[i],cr_skys[i],cr_kxs[i],cr_kys[i]) for i in cr_labels-1]
params=['sk=%.2f|k=%.2f' % (cr_skmax[i],cr_kmax[i]) for i in cr_labels-1]

import img_scale
zmin,zmax,ziter=img_scale.range_from_zscale(image,contrast=.25)
fig=imagetools.plotlabels(ll=starlike_labels,segments=BBCRseg,slices=CRslices,params=params,background=image,zscale=(zmin,zmax))
fig.suptitle('Possible Stars Picked from blocked_blender.2.2.py Masks\neccentricity<.8 & 9<area<50 & max intensity<30,000 & 3x3 inside mask shape')
fig.savefig(plot_dir+'pltSS_Stars_'+OFB_SEEING)

if len(removed_labels):
	fig=imagetools.plotlabels(ll=removed_labels,segments=BBCRseg,slices=CRslices,params=params,background=image,zscale=(zmin,zmax))
	fig.suptitle('Not Starlike: eccentricity<.8 & when clipped eccentricity>.8')
	fig.savefig(plot_dir+'pltSS_NotStars-Clip_e_raise_'+OFB_SEEING)

starlike_not8=(cr_e<.8)*(cr_area>5)*(cr_area<50)*(cr_max<30000)*logical_not(MaxInside8s)*(cr_kmax<kmax)*(cr_skmax<.88)
if starlike_not8.any():
	fig=imagetools.plotlabels(cr_labels[starlike_not8],segments=BBCRseg,slices=CRslices,params=params,background=image,zscale=(zmin,zmax))
	fig.suptitle('Not Starlike: Would be starlike, but no conn8 in the shape')
	fig.savefig(plot_dir+'pltSS_NotStars-open8_'+OFB_SEEING)

kmax_ul=5.0
starlike_k=(cr_e<.8)*(cr_area>9)*(cr_area<50)*(cr_max<30000)*MaxInside8s*(cr_kmax>kmax)*(cr_kmax<kmax_ul)*(cr_skmax<.88)
if starlike_k.sum()>40:
	kmax_ul=4.1
	starlike_k=(cr_e<.8)*(cr_area>9)*(cr_area<50)*(cr_max<30000)*MaxInside8s*(cr_kmax>kmax)*(cr_kmax<kmax_ul)*(cr_skmax<.88)

if starlike_k.sum()>40:
	kmax_ul=max(kmax+.3,3.0)
	starlike_k=(cr_e<.8)*(cr_area>9)*(cr_area<50)*(cr_max<30000)*MaxInside8s*(cr_kmax>kmax)*(cr_kmax<kmax_ul)*(cr_skmax<.88)

if starlike_k.any():
	fig=imagetools.plotlabels(ll=cr_labels[starlike_k],segments=BBCRseg,slices=CRslices,params=params,background=image,zscale=(zmin,zmax))
	fig.suptitle('Not Starlike: k>kmax=%.2f' % kmax)
	fig.savefig(plot_dir+'pltSS_NotStars-k_gt_kmax_'+OFB_SEEING)

starlike_gt30000=(cr_e<.8)*(cr_area>9)*(cr_area<50)*MaxInside8s*(cr_max>30000)*(cr_kmax<kmax)*(cr_skmax<.88)
if starlike_gt30000.any():
	fig=imagetools.plotlabels(ll=cr_labels[starlike_gt30000],segments=BBCRseg,slices=CRslices,params=params,background=image,zscale=(zmin,zmax))
	fig.suptitle('Not Starlike: Greater than 30,000')
	fig.savefig(plot_dir+'pltSS_NotStars-gt_than_30000_'+OFB_SEEING)

starlike_skew_kurt=(cr_e<.8)*(cr_area>9)*(cr_area<50)*(cr_max<30000)*MaxInside8s*((cr_kmax>=kmax)+(cr_skmax>=.88))
if starlike_skew_kurt.any():
	print 'skewness and kurtosis cut removed: ',starlike_skew_kurt.sum()
	fig=imagetools.plotlabels(ll=cr_labels[starlike_skew_kurt],segments=BBCRseg,slices=CRslices,params=params,background=image,zscale=(zmin,zmax))
	fig.suptitle('Not Starlike: too skewed or large kurtosis')
	fig.savefig(plot_dir+'pltSS_NotStars-skew_kurt'+OFB_SEEING)

#f=imagetools.ImageWithSpots([image,filtim],Xspots_starlike,name1='image',name2='filtered image',nameX='Possible Stars',ignore_scale=True,mode='box')
#f.savefig(plot_dir+'pltSS_Star_Candidates-full_image_'+OFB_SEEING)

## Save KeepOrRM image and the final image with masks included
KeepOrRM=zeros(Xspots_starlike.shape,dtype=int)
KeepOrRM[Xspots_starlike]=-1
KeepOrRM[Xspots_not_starlike]=1
hdu=astropy.io.fits.PrimaryHDU(asarray(KeepOrRM,dtype=int))
hdu.header=crheader
fl_KeepOrRM=BBCRfl.replace('SEGMENTATION_BB_CRN-cosmics','SEGMENTATION_KeepOrRM-starlike_cosmics')
hdu.writeto(fl_KeepOrRM,overwrite=True)

final_im=image.copy()
final_im[Xspots_not_starlike]=0
hdu=astropy.io.fits.PrimaryHDU(asarray(final_im,dtype=float))
hdu.header=crheader
fl_final=BBCRfl.replace('SEGMENTATION_BB_CRN-cosmics','StarRMout_KeepOrRM-purified_cosmics')
hdu.writeto(fl_final,overwrite=True)
files2check=[fl,fl_woblend,fl_revised,fl_KeepOrRM,fl_final]
print '\nds9 -zscale -tile mode column '+' '.join(files2check)+' -zscale -lock frame image -lock crosshair image -geometry 2000x2000 &'

## plot star column in eccentricity vs. diameter space
from matplotlib import collections
fig, ax_d = subplots(figsize=(14,11))
ax_d.plot(cr_e, cr_diam, 'b.')
ax_d.plot(cr_e[starlike], cr_diam[starlike], 'bo')
star_e,star_diam,star_area=(cr_e[starlike], cr_diam[starlike], cr_area[starlike])
median_star_area=median(star_area)
median_star_diam=median(star_diam)
fwhm=SEEING/.202 #convert to pixels
star_diam_fwhm_ratio=median_star_diam/fwhm
fig.suptitle('Plot of eccentricity vs. effective diameter (blue) or vs. area (red) \n SEEING=%.2f" & FWHM Star = %.2f pixels & Median Diameter = %.2f & Ratio FWHM/Median(Diam)=%.2f' % (SEEING,fwhm,median_star_diam,star_diam_fwhm_ratio))
ax_d.set_xlabel('eccentricity')
# Make the y-axis label and tick labels match the line color.
ax_d.set_ylabel(r'Effective Diameter = $\sqrt{4/\pi \times area}$', color='b')
for tl in ax_d.get_yticklabels():
	tl.set_color('b')

ax_a = ax_d.twinx()
ax_a.plot(cr_e, cr_area, 'r.')
ax_a.plot(cr_e[starlike], cr_area[starlike], 'ro')
ax_a.set_ylabel('Area [pixels]', color='r')
for tl in ax_a.get_yticklabels():
	tl.set_color('r')
collection_a = collections.BrokenBarHCollection(xranges=[(0,.8)],yrange=[9,50],facecolor='red', alpha=0.5)
collection_d = collections.BrokenBarHCollection(xranges=[(0,.8)],yrange=[sqrt(4/pi*9),sqrt(4/pi*50)],facecolor='blue', alpha=0.5)
ax_a.add_collection(collection_a)
ax_d.add_collection(collection_d)
fig.savefig(plot_dir+'pltSS_e_vs_diam_and_area_'+OFB_SEEING)

## print stats
print "\nfor fl: %s \n\tSEEING=%.2f" % (fl,SEEING)
CRseg_tot_num=BBCRseg.max()
CRseg_removed_stars=starlike.sum()
print "\t# CR masks started with: %s\n\t# CR masks finished with: %s\n\t# CR masks deleted/starlike: %s"  % (CRseg_tot_num,CRseg_tot_num-CRseg_removed_stars,CRseg_removed_stars)
print "\nBBSSCR_stats-SS",BASE,CRseg_removed_stars

## save SEGMENTATION_BBSS_CRN-cosmics (the new file that replaces SEGMENTATION_BB_CRN-cosmics in the pipeline)
BBSSCRseg,BBSSCRseg_Nlabels=scipy.ndimage.label(Xspots_not_starlike,conn8)
hdu=astropy.io.fits.PrimaryHDU(data=BBSSCRseg,header=crheader)
BBSSCRfl=BBCRfl.replace('SEGMENTATION_BB_CRN-cosmics','SEGMENTATION_BBSS_CRN-cosmics')
hdu.writeto(BBSSCRfl,overwrite=True)
