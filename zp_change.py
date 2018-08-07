#! /usr/bin/env python
## new ZPs with (now properly masked) coadds for MACS1115:
#MAG_APER1-SUBARU-10_3-1-W-J-V 26.9987651732 0.0040
#MAG_APER1-SUBARU-10_2-1-W-C-RC 27.3196096636 0.0027
#MAG_APER1-SUBARU-10_3-1-W-S-Z+ 26.9722776062 0.0031
#MAG_APER1-SUBARU-10_3-1-W-C-IC 27.1407420238 0.0029
#MAG_APER1-SUBARU-10_3-1-W-J-B 26.6005197471 0.0082
#MAG_APER1-SUBARU-10_3-1-W-C-RC 27.3118845343 0.0030


## Here are the old ones for comparison:
#MAG_APER1-SUBARU-10_3-1-W-J-V 26.9965711037 0.0048
#MAG_APER1-SUBARU-10_2-1-W-C-RC 27.3177248703 0.0026
#MAG_APER1-SUBARU-10_3-1-W-S-Z+ 26.9695412448 0.0076
#MAG_APER1-SUBARU-10_3-1-W-C-IC 27.1384112708 0.0055
#MAG_APER1-SUBARU-10_3-1-W-J-B 26.6010102601 0.0124
#MAG_APER1-SUBARU-10_3-1-W-C-RC 27.3100587966 0.0028

import astropy.io.fits as pyfits
from matplotlib.pyplot import *
from numpy import *
from glob import glob
from copy import deepcopy
import scipy
import itertools

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
def combine_tables(t1,t2):
	nrows1 = t1.shape[0]                                                                                                                                                                                                       
	nrows2 = t2.shape[0]
	nrows = nrows1 + nrows2
	hdu = astropy.io.fits.BinTableHDU.from_columns(t1.columns, nrows=nrows)
	for colname in t1.columns.names:
	    hdu.data[colname][nrows1:] = t2[colname]
    	#hdu.writeto('newtable.fits')
	return hdu


import astropy
from astropy.io import ascii

flnew = 'MACS1115+01_new_zps.txt'
flold = 'MACS1115+01_old_zps.txt'

told=ascii.read(flold,names=['band','zp','zp_err'],delimiter=' ',format='fixed_width_no_header')
tnew=ascii.read(flnew,names=['band','zp','zp_err'],delimiter=' ',format='fixed_width_no_header')




### make the plots
f=figure(figsize=(14,10))
ax1=f.add_subplot(2,2,1)
title('zp for new & old BIGMACS results')
plot(told['band'],told['zp'],'ko',label='old')
plot(tnew['band'],tnew['zp'],'rx',label='new')
legend()
ax1.set_xticklabels([])

ax1=f.add_subplot(2,2,2)
title('zp_err for new & old BIGMACS results')
plot(told['band'],told['zp_err'],'ko',label='old')
plot(tnew['band'],tnew['zp_err'],'rx',label='new')
legend()
ax1.set_xticklabels([])

ax1=f.add_subplot(2,2,3)
plot(tnew['band'],200*(tnew['zp']-told['zp'])/(tnew['zp']+told['zp']),'bo',label='new')
title('zp % difference btwn new & old')
xticks(rotation=90)
ax1=f.add_subplot(2,2,4)
title('zp_err % difference btwn new & old')
plot(tnew['band'],200*(tnew['zp_err']-told['zp_err'])/(tnew['zp_err']+told['zp_err']),'bo',label='new')
xticks(rotation=90)
f.subplots_adjust(bottom=.35)

#BEFORE PLOTTING
tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec,tm_wday, tm_yday,tm_isdst=time.localtime()
DateString=str(tm_mon)+'/'+str(tm_mday)+'/'+str(tm_year)
FileString=ShortFileString('zp_change.py')

#AFTER PLOTTING:
NameString=('plt_change_zp_MACS1115+01')
figtext(.003,.003,"Made By:"+FileString,size=10)
figtext(.303,.003,"Date:"+DateString,size=10)
figtext(.503,.003,"Named:"+NameString,size=10)
f.savefig(NameString)
