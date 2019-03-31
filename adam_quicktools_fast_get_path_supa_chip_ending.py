#! /usr/bin/env python
#adam-does# when given a glob of files, will return the number of images in the glob, the path, SUPA, chip number, and ending of the files/file
#adam-example# for im='/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-S-Z+/SCIENCE/SUPA0128347_10OCFI.fits'
#		get_path_supa_chip_ending(im)= ('/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-S-Z+/SCIENCE', 'SUPA0128347', '10', 'OCFI')
#adam-SHNT# this actually only works for a single file now. Not sure how to make it useful for multiple files
import sys
import os,re

def get_path_supa_chip_ending(im):
	'''example: im='/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-S-Z+/SCIENCE/SUPA0128347_10OCFI.fits'
	get_path_supa_chip_ending(im)= ('/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-S-Z+/SCIENCE', 'SUPA0128347', '10', 'OCFI')'''
	path=os.path.dirname(im)
	basename=os.path.basename(im)
	name_match=re.match("SUPA([0-9]*)_([0-9]{1,2})([A-Z]*).fits",basename)
	supa="SUPA"+name_match.group(1)
	chip=name_match.group(2)
	ending=name_match.group(3)
	return path,supa,chip,ending

def get_supa_chip_endings_dict(ims):
        '''
	give a list of fits image files, return 2 dictionarys:
		paths: 1st-keys are directories of those images, 2nd-keys are SUPA####### , third are endings (OCF, OCFS, etc.), final values are a list of the chip numbers
		endings: 1st-keys are endings (OCF, OCFS, etc.), values are number of files with that ending
	example: im='/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-S-Z+/SCIENCE/SUPA0128347_10OCFI.fits'
        get_path_supa_chip_ending(im)= ('/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-S-Z+/SCIENCE', 'SUPA0128347', '10', 'OCFI')'''
        paths={}
        endings={}
        for im in ims:
                path=os.path.dirname(im)                                                                                                                                                                                   
                basename=os.path.basename(im)
                basename=basename.split('.')[0]
                name_match=re.match("SUPA([0-9]*)_([0-9]{1,2})([A-Z]*)",basename)
                supa="SUPA"+name_match.group(1)
                chip=name_match.group(2)
                ending=name_match.group(3)
                if not paths.has_key(path):
                        paths[path]={}
                if not paths[path].has_key(supa):
                        paths[path][supa]={}
                if not paths[path][supa].has_key(ending):
                        paths[path][supa][ending]=[]
                paths[path][supa][ending].append(chip)
                if not ending in endings.keys():
                        endings[ending]=0
                endings[ending]+=1
        return paths,endings

if __name__ == "__main__":
	im=sys.argv[-1]
	im_isfile=os.path.isfile(im)
	im_isfits=im.endswith(".fits")
	all_images=(im_isfile*im_isfits)

	if not all_images:
		raise Exception("adam-Error: Not all of the inputs were images. You must modify this file or fix your inputs")


	path,supa,chip,ending=get_path_supa_chip_ending(im)
	sys.stdout.write("%s %s %s %s" % (path,supa,chip,ending))
