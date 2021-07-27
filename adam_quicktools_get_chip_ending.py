#! /usr/bin/env python
#adam-does# when given a glob of files, will return the number of files in the glob, the path, SUPA, chip number, and ending of the files/file
#adam-example# for im='/u/ki/awright/data/MACS1226+21/W-S-Z+/SCIENCE/SUPA0128347_10OCFI.fits'
#		get_path_supa_chip_ending(im)= ('/u/ki/awright/data/MACS1226+21/W-S-Z+/SCIENCE', 'SUPA0128347', '10', 'OCFI')
#adam-SHNT# this actually only works for a single file now. Not sure how to make it useful for multiple files
import sys
import os

allnums=[str(i) for i in range(10)]
fl=sys.argv[-1]
path=os.path.dirname(fl)
basename=os.path.basename(fl)
baseshort=basename.rsplit('.')[0]
numext=baseshort.rsplit('_')[-1]
chip=''
ending=''
for char in numext:
    if char in allnums:
	chip+=char
    else:
	ending+=char
sys.stdout.write("%s %s" % (chip,ending))
