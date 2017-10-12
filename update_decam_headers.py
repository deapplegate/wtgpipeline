#! /usr/bin/env python
filters=['u','g','r','i','z','Y']
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


## put PPRUN, MYFILT (short version of filter name), INSTRUM=DECam, ROTATION=0, CONFIG=DECam in for all images
for filter in filters:
	fnames=glob.glob("/gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/"+filter+"_DECam//single_V0.0.2A/dec*.sub.fits")
	for fname in fnames:
		fitfl=pyfits.open(fname,'update')
		header=fitfl[0].header
		date=header["DATE-OBS"]
		pprun=filter+"_"+date_to_run(date)
		header['PPRUN']=pprun
		header['MYFILT']=filter
		header['INSTRUM']="DECam"
		header['ROTATION']=0
		header['CONFIG']="DECam"
		fitfl.verify(option="ignore")
		fitfl.flush()
		fitfl.close()
	print filter,len(fnames)
