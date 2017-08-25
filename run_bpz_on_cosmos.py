#! /usr/bin/env python
oldcat = '/u/ki/dapple/nfs12/cosmos/cosmos.cat'
newcat="/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.cat"
DETECT_FILTER="r_s"
M_0_filt="r_s"
M_0_filt2="i_c"

ns=globals()
import os,sys
env_vars=os.environ.keys()
vars_ok=True
if not os.environ['BPZPATH']: 
	print "BPZPATH isn't defined!"
	vars_ok=False
subarudir = os.environ['subdir']

import re, string, numpy,scipy
from glob import glob
import astropy.io.fits as pyfits

##all keys in this cat: 'gp      ' 'dIB484  ' 'F814W   ' 'i_max   ' 'dIB527  ' 'dH1     ' 'K_uv    ' 'NB816   ' 'z_s     ' 'IB738   ' 'ID_2006 ' 'i_auto  ' 'dH_uv   ' 'i_star  ' 'H       ' 'du_s    ' 'F814W_star' 'J_uv    ' 'dch3    ' 'dIB738  ' 'du      ' 'dIB827  ' 'IB427   ' 'dJ      ' 'dH      ' 'dB      ' 'H_uv    ' 'IB505   ' 'J3      ' 'dch2    ' 'dV      ' 'x       ' 'dip     ' 'IB624   ' 'FUV     ' 'dIB505  ' 'dJ3     ' 'dJ2     ' 'dKs     ' 'di_s    ' 'Eb-v    ' 'J2      ' 'g_s     ' 'J1      ' 'dIB624  ' 'dK_uv   ' 'dKc     ' 'di_c    ' 'zp      ' 'rp      ' 'dKnf    ' 'dH2     ' 'appflag ' 'ra      ' 'photflag' 'dF814W  ' 'dNUV    ' 'auto_offset' 'ID_2008 ' 'acs_mask' 'dNB816  ' 'di_auto ' 'H2      ' 'drp     ' 'H1      ' 'dIB427  ' 'dzp     ' 'dFUV    ' 'deep_mask' 'V_mask  ' 'dJ1     ' 'dIB767  ' 'z_mask  ' 'dg_s    ' 'i_mask  ' 'IB574   ' 'dzpp    ' 'NUV     ' 'zpp     ' 'blendflag' 'mask_NUV' 'IB679   ' 'Kc      ' 'B       ' 'J       ' 'F814W_fwhm' 'Ks      ' 'dIB574  ' 'det_fwhm' 'dIB679  ' 'V       ' 'i_fwhm  ' 'IB709   ' 'ch1     ' 'ch2     ' 'ch3     ' 'ch4     ' 'IB767   ' 'mask_FUV' 'dec     ' 'IRAC2_mask' 'ip      ' 'i_c     ' 'i_s     ' 'dIB709  ' 'dz_s    ' 'dJ_uv   ' 'r_s     ' 'dY_uv   ' 'u_s     ' 'Kc_mask ' 'B_mask  ' 'auto_flag' 'tile    ' 'flags   ' 'dch1    ' 'IRAC1_mask' 'dch4    ' 'acsdata_mask' 'dNB711  ' 'Knf     ' 'y       ' 'dgp     ' 'IB827   ' 'ID      ' 'NB711   ' 'IB464   ' 'Y_uv    ' 'IB527   ' 'u       ' 'objID   ' 'dr_s    ' 'IB484   ' 'dIB464  '

## BVRIZ or ugriz or ugrizY
#u u_s
#i_c and i_s
filterlist = ['B','V','r_s','i_c','z_s']

cluster="cosmos_ultravista"
## make the bpz columns and bpz input file
photdir=os.environ['PWD']
inputcat_alter_ldac= photdir + cluster + '.bpz_input.txt'
os.system('cp %s %s' % (newcat,inputcat_alter_ldac))
columns_fl= photdir + cluster + '.bpz.columns'
columns_fo= open(columns_fl,'w')
columns_num=2
ascii_cat_keys=["ID"]
M_0_key=None #this gets set in the loopM_0_key2=None #this gets set in the loop
M_0_key2=None #this gets set in the loop
for filt in filterlist:
	filt_col=[filt,'%i,%i' % (columns_num,1+columns_num),'AB','0.02','0.0\n']
	columns_fo.write('\t'.join(filt_col))
	ascii_cat_keys.append(filt)
	ascii_cat_keys.append('d'+filt)
	columns_num+=2
	if M_0_filt in filt:
		M_0_key=filt
	if M_0_filt2 in filt:
		M_0_key2=filt

if M_0_key==None:
	raise Exception("the filter %s used for M_0 didn't show up in filterlist" % (M_0_filt))
else:
	ascii_cat_keys.append("MAG_APER1-"+M_0_key)
if M_0_key2==None: #raise exception for now, but in practice this backup filter isn't needed
	raise Exception("the backup filter %s used for M_0 didn't show up in filterlist, can change it to something else or drop it alltogether" % (M_0_filt2))
	print "the backup filter %s used for M_0 didn't show up in filterlist, can change it to something else or drop it alltogether" % (M_0_filt2)
else:
	ascii_cat_keys.append("MAG_APER1-"+M_0_key2)

columns_fo.write('\t'.join(['ID','1\n']))
columns_fo.write('\t'.join(['M_0',str(columns_num)+'\n']))
columns_fo.close()

command="ldactoasc -i %s -t OBJECTS -s -b -k %s > %s" % (inputcat_alter_ldac,' '.join(ascii_cat_keys),inputcat_alter_ldac)
print "command=",command

