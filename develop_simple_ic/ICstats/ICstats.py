#! /usr/bin/env python
import pyfits
from matplotlib.pyplot import *
from numpy import *
from glob import glob
from copy import deepcopy
import scipy
import itertools
import sys ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
import time
import os
import shutil
import pdb
import re
import pickle
from fitter import Gauss
from UsefulTools import names, FromPick_data_true, FromPick_data_spots, GetMiddle, GetSpots_bins_values, ShortFileString, num2str
import imagetools
from scipy.stats import *
from scipy.ndimage import *
conn8=array([[1,1,1],[1,1,1],[1,1,1]])
conn4=array([[0,1,0],[1,1,1],[0,1,0]])
tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec,tm_wday, tm_yday,tm_isdst=time.localtime()
DateString=str(tm_mon)+'/'+str(tm_mday)+'/'+str(tm_year)
FileString=ShortFileString(sys.argv[0])
#AFTER PLOTTING:
#NameString=('pltNAME')
#figtext(.003,.003,"Made By:"+FileString,size=10)
#figtext(.303,.003,"Date:"+DateString,size=10)
#figtext(.503,.003,"Named:"+NameString,size=10)
#savefig(NameString)

import astropy
from astropy.io import ascii

fls=["ICstats-fit_goodness.txt", "ICstats-stars_exps.txt", "ICstats-zp_vals_poly.txt"]
for fl in fls:
	tab = ascii.read(fl)
	print "# ",fl.replace(".txt",": "),tab.colnames
ppruns=["W-C-IC_2010-02-12","W-C-IC_2011-01-06","W-C-RC_2006-03-04","W-C-RC_2010-02-12","W-J-B_2010-02-12","W-J-V_2010-02-12","W-S-I+_2010-04-15","W-S-Z+_2011-01-06"]
filters=["W-C-IC","W-C-IC","W-C-RC","W-C-RC","W-J-B","W-J-V","W-S-I+","W-S-Z+"]
prun2ind={}
for i,PPRUN in enumerate(ppruns):
	pprun2ind[PPRUN]=i

zp_names={"W-C-IC_2010-02-12":[],"W-C-IC_2011-01-06":[],"W-C-RC_2006-03-04":[],"W-C-RC_2010-02-12":[],"W-J-B_2010-02-12":[],"W-J-V_2010-02-12":[],"W-S-I+_2010-04-15":[],"W-S-Z+_2011-01-06":[]}
zp_vals={"W-C-IC_2010-02-12":[],"W-C-IC_2011-01-06":[],"W-C-RC_2006-03-04":[],"W-C-RC_2010-02-12":[],"W-J-B_2010-02-12":[],"W-J-V_2010-02-12":[],"W-S-I+_2010-04-15":[],"W-S-Z+_2011-01-06":[]}

zp_names["W-C-IC_2010-02-12"]=["zp_SUPA0118297",  "zp_SUPA0118300",  "zp_SUPA0118301",  "zp_SUPA0118302",  "zp_SUPA0118303",  "zp_SUPA0118304",  "zp_SUPA0118305",  "zp_SUPA0118306",  "zp_SUPA0118307",  "zp_SUPA0118309"]
zp_names["W-C-IC_2011-01-06"]=["zp_SUPA0128329",  "zp_SUPA0128330",  "zp_SUPA0128331",  "zp_SUPA0128333",  "zp_SUPA0128334",  "zp_SUPA0128335",  "zp_SUPA0128336",  "zp_SUPA0128337",  "zp_SUPA0128338"]
zp_names["W-C-RC_2006-03-04"]=["zp_SUPA0046908",  "zp_SUPA0046909",  "zp_SUPA0046910",  "zp_SUPA0046911",  "zp_SUPA0046912",  "zp_SUPA0046913",  "zp_SUPA0046914"]
zp_names["W-C-RC_2010-02-12"]=["zp_SUPA0118331",  "zp_SUPA0118332",  "zp_SUPA0118333",  "zp_SUPA0118334",  "zp_SUPA0118335",  "zp_SUPA0118336"]
zp_names["W-J-B_2010-02-12"]= ["zp_SUPA0118315",  "zp_SUPA0118316",  "zp_SUPA0118317",  "zp_SUPA0118318",  "zp_SUPA0118319",  "zp_SUPA0118320",  "zp_SUPA0118321",  "zp_SUPA0118322",  "zp_SUPA0118323"]
zp_names["W-J-V_2010-02-12"]= ["zp_SUPA0118325",  "zp_SUPA0118326",  "zp_SUPA0118327",  "zp_SUPA0118328",  "zp_SUPA0118329",  "zp_SUPA0118330"]
zp_names["W-S-I+_2010-04-15"]=["zp_SUPA0121389",  "zp_SUPA0121390",  "zp_SUPA0121391",  "zp_SUPA0121392",  "zp_SUPA0121402",  "zp_SUPA0121404",  "zp_SUPA0121405",  "zp_SUPA0121406",  "zp_SUPA0121407",  "zp_SUPA0121408",  "zp_SUPA0121409",  "zp_SUPA0121410",  "zp_SUPA0121411",  "zp_SUPA0121412",  "zp_SUPA0121413",  "zp_SUPA0121414",  "zp_SUPA0121415"]
zp_names["W-S-Z+_2011-01-06"]=["zp_SUPA0128341",  "zp_SUPA0128342",  "zp_SUPA0128343",  "zp_SUPA0128345",  "zp_SUPA0128346",  "zp_SUPA0128347"]
zp_vals["W-C-IC_2010-02-12"]=[-0.01059,-0.00242,-0.00000,0.00034,0.00024,0.00397,0.00299,0.00364,0.00336,0.00609]
zp_vals["W-C-IC_2011-01-06"]=[0.01006,0.01198,0.01596,0.00979,0.00873,0.00861,-0.00000,0.00068,0.00236]
zp_vals["W-C-RC_2006-03-04"]=[-0.15870,-0.15087,-0.13411,-0.00000,0.64629,-0.06292,-0.05157]
zp_vals["W-C-RC_2010-02-12"]=[-0.02550,-0.01579,-0.02184,-0.00000,-0.00481,-0.01709]
zp_vals["W-J-B_2010-02-12"]=[0.00487,-0.00000,0.00577,0.00725,0.00680,-0.00113,-0.00140,-0.00528,0.00208]
zp_vals["W-J-V_2010-02-12"]=[-0.00419,0.00326,0.00021,-0.00000,-0.00053,-0.00059]
zp_vals["W-S-I+_2010-04-15"]=[-0.00000,-0.48899,-0.58830,0.20158,1.20176,1.63501,1.44470,0.79232,1.18102,1.86363,0.76494,0.55156,0.99959,0.71543,0.48740,0.58061,0.86257]
zp_vals["W-S-Z+_2011-01-06"]=[0.00748,0.00661,0.00533,-0.00000,0.00094,0.00420]

zp_chip={}
zp_chip["W-C-IC_2010-02-12"]=[-0.00072,-0.00437,-0.00497,-0.00691,-0.00784,0.00329, 0.00222, 0.00474, 0.00478 ]
zp_chip["W-C-IC_2011-01-06"]=[-0.01577,-0.01398,-0.00791,-0.00209,-0.00437,-0.00702,-0.00554,0.00049, 0.00309 ]
zp_chip["W-C-RC_2006-03-04"]=[-0.00919,-0.01420,-0.01123,-0.00787,-0.00422,-0.00430,-0.00100,-0.00524,-0.00056]
zp_chip["W-C-RC_2010-02-12"]=[-0.00082,-0.00424,-0.00500,-0.00583,-0.00398,0.00466, 0.00370, 0.00395, 0.00955 ]
zp_chip["W-J-B_2010-02-12"]=[-0.00216,-0.00295,-0.00114,-0.00128,-0.00563,-0.00019,0.00354, 0.00395, 0.00946 ]
zp_chip["W-J-V_2010-02-12"]=[0.00151, -0.00112,-0.00490,-0.00101,-0.00532,0.00391, 0.00564, 0.00628, 0.01405 ]
zp_chip["W-S-I+_2010-04-15"]=[-0.00014,-0.00347,-0.00497,-0.00446,-0.00598,-0.00146,-0.00263,-0.00175,-0.00116]
zp_chip["W-S-Z+_2011-01-06"]=[-0.02985,-0.02923,-0.02057,-0.01247,-0.01218,-0.00917,-0.00825,-0.00617,-0.00711]
chips=range(1,10)

SDSS_color=[ 0.38239 , 0.35664 , 0.20142 , 0.18728 , 0.12801 , 0.01103 , 0.13940 , -0.12406]
zp_SDSS =[ 5.87690 , 6.41962 , 7.11604 , 6.68551 , 5.56807 , 6.50241 , 5.75833 , 6.25362]
#W-C-RC_2006-03-04  1$0x1y    1$0x2y    1$0x3y    1$1x0y    1$1x1y    1$1x2y    1$1x3y    1$2x0y    1$2x1y    1$2x2y    1$2x3y    1$3x0y    1$3x1y    1$3x2y    1$3x3y    0$0x1y    0$0x2y    0$0x3y   0$1x0y    0$1x1y   0$1x2y   0$1x3y   0$2x0y    0$2x1y   0$2x2y    0$2x3y   0$3x0y   0$3x1y   0$3x2y   0$3x3y
#W-C-RC_2006-03-04  0.00023   -0.02755  0.00179   0.00439   0.01514   -0.01005  0.00291   -0.03235  0.00241   -0.00172  0.00775   -0.00463  0.00716   0.00025   0.00052   -0.01351  -0.01988  0.00577  -0.00291  0.02605  0.00046  0.00257  -0.04459  0.01248  -0.00410  0.00002  0.00032  0.00853  0.00268  0.00119

poly_coeffs=['0x1y', '0x2y', '1x0y', '1x1y', '1x2y', '2x0y', '2x1y', '2x2y']
#	tab = ascii.read("ICstats-fit_goodness.txt")
#	tab = ascii.read("ICstats-stars_exps.txt")
tab = ascii.read("ICstats-zp_vals_poly.txt")
#fit_coeffs=array(list(tab[0].data)[1:])



filter_color  = { 'W-J-B'  : 'purple',
                'W-S-G+'   : 'blue',
                'W-J-V'    : 'green',
                'W-C-RC'   : 'yellow',
                'W-S-I+'   : 'orange',
                'W-C-IC'   : 'red',
                'W-S-Z+'   : 'black'}
band2color=filter_color

last_filter="none"
f=figure(figsize=(12,16))
title('zp_chip from IC fit')
xlabel('chip number (#)')
ylabel('zp_#')
for FILTER,PPRUN in zip(filters,ppruns): 
	if FILTER==last_filter:marker='x';ls='--'
	else:marker='o';ls='-'
	plot(chips,zp_chip[PPRUN],color=band2color[FILTER],label=FILTER,ls=ls,marker=marker)
	last_filter=FILTER
legend()
f.savefig('pltICzp_fitvals-zp_chip')

poly_coeffs=['0x1y', '0x2y', '1x0y', '1x1y', '1x2y', '2x0y', '2x1y', '2x2y']

last_filter="none"
f=figure(figsize=(15,18))
ax1=f.add_subplot(2,1,1)
ax1.set_title('cheby poly coeffs from IC fit to ROT=0 data')
ax1.set_xlabel('coeff')
ax2=f.add_subplot(2,1,2)
ax2.set_title('cheby poly coeffs from IC fit to ROT=1 data')
ax2.set_xlabel('coeff')
coeff_inds=range(0,8)
for FILTER,PPRUN in zip(filters,ppruns): 
	if FILTER==last_filter:
		marker='x';ls='--'
	else:
		marker='o';ls='-'
	ind=pprun2ind[PPRUN]
	print  "ind=", ind
	coeffs_r0=array(list(tab[ind].data)[9:]) #rot0
	coeffs_r1=array(list(tab[ind].data)[1:9]) #rot1
	ax1.plot(coeff_inds,coeffs_r0,color=band2color[FILTER],label=FILTER,ls=ls,marker=marker)
	ax2.plot(coeff_inds,coeffs_r1,color=band2color[FILTER],label=FILTER,ls=ls,marker=marker)
	last_filter=FILTER
ax1.legend()
ax1.set_xticklabels(poly_coeffs)
ax2.set_xticklabels(poly_coeffs)
f.savefig('pltICzp_fitvals-cheby_coeff')


xx,yy=[],[]
zz=[]
for FILTER,PPRUN in zip(filters,ppruns): 
	ind=pprun2ind[PPRUN]
	zp_images=zp_vals[PPRUN]
	inds=[ind]*len(zp_images)
	xx+=inds
	yy+=zp_images
	zz.append(sum(array(zp_images))/(len(zp_images)-1))


f=figure(figsize=(15,18))
ax1=f.add_subplot(3,1,1)
ax1.set_title('zero-points from the IC fit at this PPRUN')
ax1.set_ylabel('zp_image for each image (red line=mean)')
ax1.scatter(xx,yy,c='k',marker='d')
ax1.plot(coeff_inds,zz,c='r',marker='',ls='--')
ax1.set_xlim(-.2,7.2)
ax1.set_xticks(coeff_inds)
ax1.set_xticklabels([])
ax2=f.add_subplot(3,1,2)
ax2.set_ylabel('SDSS_color')
ax2.plot(coeff_inds,SDSS_color,label="SDSS_color")
ax2.set_xlim(-.2,7.2)
ax2.set_xticks(coeff_inds)
ax2.set_xticklabels([])
ax3=f.add_subplot(3,1,3)
ax3.set_ylabel('zp_SDSS')
ax3.plot(coeff_inds,zp_SDSS,label="zp_SDSS")
ax3.set_xlabel('PPRUN')
ax3.set_xticklabels(ppruns)
ax3.set_xlim(-.2,7.2)
ax3.set_xticks(coeff_inds)
f.subplots_adjust(hspace=.03)
f.savefig('pltICzp_fitvals-SDSS_and_zp_image')
show()
