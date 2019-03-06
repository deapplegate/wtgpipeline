#! /usr/bin/env python
import os,sys
from glob import glob
import astropy, astropy.io.fits
import numpy as n
coadd_masterdir='/gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-C-RC/SCIENCE/'+'coadd_RXJ2129_all/'

resamp_mask_dir='/gpfs/slac/kipac/fs1/u/anja//ricardo_needs_more_space/manmasking/RXJ2129/masks/'
mask_fls=glob(resamp_mask_dir+'SUPA*REMSmask.fits')
for mask_fl in mask_fls:
	mf1,mf2=os.path.basename(mask_fl).split('OCFSRI')
	weight2mask=coadd_masterdir+mf1+'OCFSRI.sub.RXJ2129_all.resamp.weight.fits'
	flag2mask=coadd_masterdir+mf1+'OCFSRI.sub.flag.RXJ2129_all.resamp.fits'
	print flag2mask
	print os.path.isfile(flag2mask)

	# now mask the flag/weight
	maskfo=astropy.io.fits.open(mask_fl)
	maskim=maskfo[0].data
	## mask the weight 1st

	os.system('cp %s %s' % (weight2mask,'/u/ki/awright/my_data/SUBARU/RXJ2129/W-C-RC/SCIENCE/coadds_before_REMS/'+mf1+'OCFSRI.sub.RXJ2129_all.resamp.weight.B4REMS2.fits'))
	weightfo=astropy.io.fits.open(weight2mask,mode='update')
	weightim=weightfo[0].data
	weighthead=weightfo[0].header
	weightfo[0].data=n.asarray(weightim*maskim,dtype=weightim.dtype)
	weighthead['REMS']='mask_applied'
	weightfo.verify()
	weightfo.flush()
	weightfo.close()

	## mask the flag 2nd

	os.system('cp %s %s' % (flag2mask,'/u/ki/awright/my_data/SUBARU/RXJ2129/W-C-RC/SCIENCE/coadds_before_REMS/'+mf1+'OCFSRI.sub.flag.RXJ2129_all.resamp.B4REMS2.fits'))
	flagfo=astropy.io.fits.open(flag2mask,mode='update')
	flagim=flagfo[0].data
	flaghead=flagfo[0].header
	flagim[maskim==0]=17 #flag 17 will be 
	flagfo[0].data=n.asarray(flagim,dtype=flagim.dtype)
	flaghead['REMS']='mask_applied'
	flagfo.verify()
	flagfo.flush()
	flagfo.close()
	print 'wrote out new:', flag2mask

sys.exit()

## RXJ2129 applying masks
#
#apply masks to flag files here:
#/u/ki/awright/my_data/SUBARU/RXJ2129/W-C-RC/SCIENCE/coadd_RXJ2129_all/SUPA01351*sub.flag.*resamp*.fits
#and weight files here:
#/u/ki/awright/my_data/SUBARU/RXJ2129/W-C-RC/SCIENCE/coadd_RXJ2129_all/SUPA01351*sub*resamp*weight.fits
#
#Then re-run perform_coadd_swarp.sh to re-make the coadd.fits/coadd.weight.fits/coadd.flag.fits files here:
#(astroconda) ~/my_data/SUBARU/RXJ2129/W-C-RC/SCIENCE$ \ls -d coadd_RXJ2129_SUPA01351*
#coadd_RXJ2129_SUPA0135155  coadd_RXJ2129_SUPA0135158  coadd_RXJ2129_SUPA0135161  coadd_RXJ2129_SUPA0135164  coadd_RXJ2129_SUPA0135167  coadd_RXJ2129_SUPA0135170
#coadd_RXJ2129_SUPA0135156  coadd_RXJ2129_SUPA0135159  coadd_RXJ2129_SUPA0135162  coadd_RXJ2129_SUPA0135165  coadd_RXJ2129_SUPA0135168  coadd_RXJ2129_SUPA0135171
#coadd_RXJ2129_SUPA0135157  coadd_RXJ2129_SUPA0135160  coadd_RXJ2129_SUPA0135163  coadd_RXJ2129_SUPA0135166  coadd_RXJ2129_SUPA0135169
#(astroconda) ~/my_data/SUBARU/RXJ2129/W-C-RC/SCIENCE$ \ls -d coadd_RXJ2129_[a-z]*    
#coadd_RXJ2129_all  coadd_RXJ2129_gabodsid2025  coadd_RXJ2129_gabodsid4952  coadd_RXJ2129_good
#
#Which I've already moved out of the way here:
#for fl in `\ls coadd_RXJ2129_SUPA01351*/coadd.*fits` ; do dir=`dirname $fl` ; base=`basename $fl ` ; mv $fl coadds_before_REMS/${dir}_${base} ; done
#for fl in `\ls coadd_RXJ2129_[a-z]*/coadd.*fits` ; do dir=`dirname $fl` ; base=`basename $fl ` ; mv $fl coadds_before_REMS/${dir}_${base} ; done
#
#Then I should compare the two sets to make sure it works!
