#! /usr/bin/env python
import sys, os, glob
sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
import imagetools
import astropy.io.fits as pyfits

def date_to_run(imdate):
    if imdate.startswith("2013-06"):return '2013-06-12'
    elif imdate.startswith("2014-08"):return '2014-08-02'
    elif imdate.startswith("2016-07"):return '2016-07-05'
    elif imdate.startswith("2005-05"):return '2005-05-09'
    else:
        print "ERROR!"


filters=["g","r"]
for filter in filters:
	#fnames=glob.glob("/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/"+filter+"/SCIENCE/79*.fits")
	fnames=glob.glob("/nfs/slac/g/ki/ki05/anja/SUBARU/A2204/"+filter+"/SCIENCE/79*_1C.fits")
	for fname in fnames:
		#fitfl=pyfits.open(fname,'update')
		fitfl=pyfits.open(fname)
		header=fitfl[0].header
		date=header["DATE-OBS"]
		pprun=filter+"_"+date_to_run(date)
		print pprun, fname

fnames=glob.glob("/gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/g_DECam//single_V0.0.2A/dec41*_62OXCLFS.*.fits")
for fname in fnames:
	print fname
	fitfl=pyfits.open(fname,'update')
	header=fitfl[0].header
	header["BADCCD"]=1
	fitfl.verify(option="ignore")
	fitfl.flush()
	fitfl.close()
