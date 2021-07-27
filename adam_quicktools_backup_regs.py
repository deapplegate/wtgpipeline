#! /usr/bin/env python
#adam-does# backs up the region files that I've slaved over night and day and never want to have to redo EVER!
#adam-use# use along with stellar suppression rings, by-hand masking regions, backmasking areas. asteroid and star masks, any region files at all
#adam-example# ipython -i -- adam_quicktools_backup_regs.py /u/ki/awright/data/MACS0416-24/W-C-RC/SCIENCE/autosuppression/
#adam-example# ipython -i -- adam_quicktools_backup_regs.py /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-C-RC/SCIENCE/autosuppression/
import sys
sys.path.append('/u/ki/awright/InstallingSoftware/pythons/')
from import_tools import *
backup_main="/u/ki/awright/data/backup_regions/"
SUBARUDIR1="/u/ki/awright/data/"
SUBARUDIR2="/gpfs/slac/kipac/fs1/u/awright/SUBARU/"

def backup_regions(dir2backup):
	if os.path.isdir(dir2backup):
		pass
	else:
		raise Exception('directory youre backing up (%s) doesnt exist!' % (dir2backup))
	if dir2backup.startswith(SUBARUDIR1):
		SUBARUDIR=SUBARUDIR1
	elif dir2backup.startswith(SUBARUDIR2):
		SUBARUDIR=SUBARUDIR2
	else:
		raise Exception('directory youre backing up (%s) isnt within the SUBARUDIR directory' % (dir2backup,))

	backup_locators=dir2backup.replace(SUBARUDIR,'').split('/')
	try:
		backup_locators.remove('')
	except ValueError:
		pass
	backup_datetime="%.2i-%.2i-%.4i_at_%.2i-%.2i" % (tm_mon,tm_mday,tm_year,tm_hour,tm_min)
	backup_location=backup_main+'_'.join(backup_locators)+"_"+backup_datetime
	os.mkdir(backup_location)
	regs2backup=glob(dir2backup+"/*.reg")
	num_copied=0
	for reg in regs2backup:
		out=os.system('cp %s %s' % (reg,backup_location))
		if out==0:
			num_copied+=1
		else:
			raise Exception('attempt to copy this file: %s has failed!' % (reg))
	print "backed up %s region files from %s to %s" % (num_copied,dir2backup,backup_location)

if __name__=='__main__':
	dir2backup=sys.argv[-1]
	backup_regions(dir2backup)
