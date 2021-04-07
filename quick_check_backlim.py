#! /usr/bin/env python
#adam-does# this code makes and pickles dictionaries needed in make_inputs_and_models.py
#adam-use# saves CRbads_info to CRbads_info.pkl and Prettys_info to Prettys_info.pkl
#the basics
from numpy import *
from matplotlib.pyplot import *
from glob import glob
from copy import deepcopy
import scipy
import itertools

#unlikely to need, so comment them out:
#from collections import Counter
#import cosmolopy
#import shutil
import hashlib
import astropy
import astropy.io.fits
pyfits=astropy.io.fits
from astropy.io import ascii

#shell/non-python related stuff
import sys ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
import time
import os
import shutil
import pdb
import re
import pickle

#my stuff!
from fitter import Gauss
from UsefulTools import names, FromPick_data_true, FromPick_data_spots, GetMiddle, GetSpots_bins_values, ShortFileString, num2str
import imagetools
import cattools

#super useful image packages
#import ds9
from scipy.stats import *
from scipy.ndimage import *
conn8=array([[1,1,1],[1,1,1],[1,1,1]])
conn4=array([[0,1,0],[1,1,1],[0,1,0]])

#BEFORE PLOTTING
import time
tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec,tm_wday, tm_yday,tm_isdst=time.localtime()
DateString=str(tm_mon)+'/'+str(tm_mday)+'/'+str(tm_year)
FileString=ShortFileString(sys.argv[0])

#AFTER PLOTTING:
#NameString=('pltNAME')
#figtext(.003,.003,"Made By:"+FileString,size=10)
#figtext(.303,.003,"Date:"+DateString,size=10)
#figtext(.503,.003,"Named:"+NameString,size=10)
#savefig(NameString)

#sex_theli /nfs/slac/g/ki/ki05/anja/SUBARU/A521/W-C-RC/SCIENCE/SUPA0006184_3OCFSI.fits -c sex_simple.conf -CATALOG_NAME mycat.cat -FLAG_IMAGE /nfs/slac/g/ki/ki05/anja/SUBARU/A521/W-C-RC/WEIGHTS/SUPA0006184_3OCFSI.flag.fits -WEIGHT_IMAGE /nfs/slac/g/ki/ki05/anja/SUBARU/A521/W-C-RC/WEIGHTS/SUPA0006184_3OCFSI.weight.fits -WEIGHT_TYPE MAP_WEIGHT
#sex_theli /nfs/slac/g/ki/ki05/anja/SUBARU/A521/W-C-RC/SCIENCE/SUPA0006184_3OCFSI.fits -c sex_simple.conf -CATALOG_NAME mycat.cat3 -FLAG_IMAGE /nfs/slac/g/ki/ki05/anja/SUBARU/A521/W-C-RC/WEIGHTS/SUPA0006184_3OCFSI.flag.fits -WEIGHT_IMAGE /nfs/slac/g/ki/ki05/anja/SUBARU/A521/W-C-RC/WEIGHTS/SUPA0006184_3OCFSI.weight.fits -WEIGHT_TYPE MAP_WEIGHT -FILTER Y -FILTER_NAME ${DATACONF}/gauss_4.0_7x7.conv

import ldac
f=figure()
title('SExtractor run on SUPA0006184_3OCFSI.fits with LOCAL sky background subtraction\nDETECTION/ANALYSIS thresholds at 2')
for fl in glob('mycat.cat*'):
	tab=ldac.openObjectFile(fl,'LDAC_OBJECTS')
	xx=tab['FLUX_APER']
	yy=tab['FLUXERR_APER']
	uncal_mag=tab['MAG_APER']
	## RZP from external header in the coadd directory
	RZP = 0.003672
	GAIN=2.5

	## (astroconda) /nfs/slac/g/ki/ki05/anja/SUBARU/A521/PHOTOMETRY_W-C-RC_aper$ ldactoasc -i A521.slr.cat -t ZPS -s 
	#   1 filter                                                             
	#  61 zeropoints                                                         
	#  62 errors                                                             
	#SUBARU-10_1-1-W-C-RC                                         27.6
	AZP=27.6
	#plot(-2.5*log10(xx),yy,'k.')
	scatter(uncal_mag+RZP+AZP,yy)
xlim(10,25.5)
xlabel('MAG_APER (uncalibrated mag + REL_ZP + ABS_ZP (SUBARU-10_1-1-W-C-RC from SLR cat)')
ylabel('FLUXERR_APER')
savefig('plt_quick_check_backlim_sextractor_fluxerr_vs_mag')

show()

