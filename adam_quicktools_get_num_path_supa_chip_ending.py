#! /usr/bin/env python
#adam-does# when given a glob of files, will return the number of images in the glob, the path, SUPA, chip number, and ending of the files/file
#adam-example# for im='/u/ki/awright/data/MACS1226+21/W-S-Z+/SCIENCE/SUPA0128347_10OCFI.fits'
#		get_path_supa_chip_ending(im)= ('/u/ki/awright/data/MACS1226+21/W-S-Z+/SCIENCE', 'SUPA0128347', '10', 'OCFI')
#adam-SHNT# this actually only works for a single file now. Not sure how to make it useful for multiple files
import sys
import os
sys.path.append('/u/ki/awright/InstallingSoftware/pythons/')
import imagetools
images=imagetools.ArgCleaner(sys.argv)

all_images=True
for im in images:
	im_isfile=os.path.isfile(im)
	im_isfits=im.endswith(".fits")
	all_images*=(im_isfile*im_isfits)


if not all_images:
	raise Exception("adam-Error: Not all of the inputs were images. You must modify this file or fix your inputs")

num=len(images)

if num==1:
	path,supa,chip,ending=imagetools.get_path_supa_chip_ending(images[0])
	sys.stdout.write("%s %s %s %s %s" % (num,path,supa,chip,ending))
else:
	raise Exception("adam-Error: There was more than 1 file given. Not sure how I want to handle that yet.")
