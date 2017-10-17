#! /usr/bin/env python
#adam-does# backs up the region files that I've slaved over night and day and never want to have to redo EVER!
#adam-use# use along with stellar suppression rings, by-hand masking regions, backmasking areas. asteroid and star masks, any region files at all
#adam-example# ipython -i -- adam_backup_regs.py /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/autosuppression/
import sys
sys.path.append('/u/ki/awright/InstallingSoftware/pythons/')
from import_tools import *
SUBARUDIR="/nfs/slac/g/ki/ki18/anja/SUBARU/"
backup_main="/nfs/slac/g/ki/ki18/anja/SUBARU/backup_regions/"
dir2backup=sys.argv[-1]
if os.path.isdir(dir2backup):
	if dir2backup.startswith(SUBARUDIR):
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
	else:
		raise Exception('directory youre backing up (%s) isnt within the SUBARUDIR (%s) directory' % (dir2backup,SUBARUDIR))
else:
	raise Exception('directory youre backing up (%s) doesnt exist!' % (dir2backup))

