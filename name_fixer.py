#! /usr/bin/env python
import os,sys,glob
import pyfits
import adam_quicktools_ArgCleaner
args=adam_quicktools_ArgCleaner.ArgCleaner(sys.argv)
directory=args[0]
if not os.path.isdir(directory):
	print 'directory=',directory
	print "this isn't a directory. try again next time!"
	raise Exception("input arg isn't a directory")

fls=glob.glob(directory+'/SUPA011*')

for fl in fls:
    fo=pyfits.open(fl,'update')
    for ext in range(len(fo)):
	    if " " in fo[ext].header["OBJECT"]:
		obj=fo[ext].header["OBJECT"]
		objnew=obj.replace(" ","_")`
		fo[ext].header["OBJECT"]=objnew
		fo.flush()
	    elif
		print "adam-look: replace this space!?",fo[0].header["OBJECT"],fl
    fo.close()
