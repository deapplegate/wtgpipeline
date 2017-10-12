#! /usr/bin/env python
#adam-does# this code takes things from /nfs/slac/g/ki/ki18/anja/SUBARU/2013-02-06_W-J-B/SKYFLAT and puts STARTDIR="2013-02-06_W-J-B/SKYFLAT" in header

import sys,os,re,string
import imagetools
from glob import glob
dirs=[] ## FILL THIS!
import header_key_add
dirs=["/nfs/slac/g/ki/ki18/anja/SUBARU/2007-02-13_W-J-V","/nfs/slac/g/ki/ki18/anja/SUBARU/2007-02-13_W-S-I+","/nfs/slac/g/ki/ki18/anja/SUBARU/2007-02-13_BIAS","/nfs/slac/g/ki/ki18/anja/SUBARU/2008-07-30_W-S-I+","/nfs/slac/g/ki/ki18/anja/SUBARU/2009-03-28_W-S-I+","/nfs/slac/g/ki/ki18/anja/SUBARU/2009-03-28_BIAS","/nfs/slac/g/ki/ki18/anja/SUBARU/2010-03-12_W-J-V","/nfs/slac/g/ki/ki18/anja/SUBARU/2010-03-12_W-S-I+","/nfs/slac/g/ki/ki18/anja/SUBARU/2010-03-12_BIAS","/nfs/slac/g/ki/ki18/anja/SUBARU/2010-11-07_W-J-V","/nfs/slac/g/ki/ki18/anja/SUBARU/2010-12-05_W-J-V","/nfs/slac/g/ki/ki18/anja/SUBARU/2010-12-05_BIAS"]
dirs+=["/nfs/slac/g/ki/ki18/anja/SUBARU/2013-11-29_W-J-B", "/nfs/slac/g/ki/ki18/anja/SUBARU/2013-07-13_BIAS", "/nfs/slac/g/ki/ki18/anja/SUBARU/2013-07-15_W-C-RC", "/nfs/slac/g/ki/ki18/anja/SUBARU/2013-07-15_W-S-Z+", "/nfs/slac/g/ki/ki18/anja/SUBARU/2013-07-16_W-J-B", "/nfs/slac/g/ki/ki18/anja/SUBARU/2013-12-01_W-S-Z+", "/nfs/slac/g/ki/ki18/anja/SUBARU/2013-12-01_W-C-RC", "/nfs/slac/g/ki/ki18/anja/SUBARU/2013-02-06_W-J-B", "/nfs/slac/g/ki/ki18/anja/SUBARU/2013-06-10_W-J-B", "/nfs/slac/g/ki/ki18/anja/SUBARU/2013-06-10_W-C-RC", "/nfs/slac/g/ki/ki18/anja/SUBARU/2013-06-09_W-S-Z+", "/nfs/slac/g/ki/ki18/anja/SUBARU/2013-02-06_W-C-RC", "/nfs/slac/g/ki/ki18/anja/SUBARU/2012-07-16_DARK", "/nfs/slac/g/ki/ki18/anja/SUBARU/2012-08-12_DARK", "/nfs/slac/g/ki/ki18/anja/SUBARU/2013-12-03_DARK", "/nfs/slac/g/ki/ki18/anja/SUBARU/2012-07-23_DARK", "/nfs/slac/g/ki/ki18/anja/SUBARU/2013-06-09_DARK"]
for maindir in dirs:
	origdirs=glob(maindir+"/*/ORIGINALS")
	MYPPRUN=maindir.split("/")[-1]
	for origdir in origdirs:
		MYTYPE=origdir.split("/")[-2]
		STARTDIR=MYPPRUN+"/"+MYTYPE
		fls=glob(origdir+"/*.fits")
		print ' MYPPRUN=',MYPPRUN , ' MYTYPE=',MYTYPE, ' len(fls)=',len(fls)
		for fl in fls:
			header_key_add.add_key_val(fl,["MYPPRUN","MYTYPE","STARTDIR"],[MYPPRUN,MYTYPE,STARTDIR])

