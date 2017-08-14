#! /usr/bin/env python
#adam-does# moves a certain class of files so that it's not in the way screwing up pipeline scripts, but keeping them somewhere in case I need them
#adam-use# for example, after running the stellar suppression you can remove the *OCF.fits files so they don't confuse the processing of the *OCFR.fits files. But you can save the *OCF.fits files in case you add more stellar rings in later.
#adam-example# ipython -i -- adam_backup_and_rm_files.py /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/*OCF.fits
import sys
sys.path.append('/u/ki/awright/InstallingSoftware/pythons/')
from import_tools import *
SUBARUDIR="/nfs/slac/g/ki/ki18/anja/SUBARU/"
backup_main="/nfs/slac/g/ki/ki18/anja/SUBARU/backup_files/"
files2backup=imagetools.ArgCleaner(sys.argv)
fl0= files2backup[0]
backup_from_dir=fl0[:fl0.rfind('/')]
if os.path.isdir(backup_from_dir):
	if backup_from_dir.startswith(SUBARUDIR):
		backup_locators=backup_from_dir.replace(SUBARUDIR,'').split('/')
		try:
			backup_locators.remove('')
		except ValueError:
			pass
		backup_datetime="%.2i-%.2i-%.4i_at_%.2i-%.2i" % (tm_mon,tm_mday,tm_year,tm_hour,tm_min)
		backup_location=backup_main+'_'.join(backup_locators)+"_"+backup_datetime
		os.mkdir(backup_location)
		num_copied=0
		for fl in files2backup:
			if os.path.islink(fl):
				raise Exception('cannot do this backup, at least one file (%s) is a symlink\nmust copy link dest to links filename in order to do this!')
		for fl in files2backup:
			print 'mv %s %s' % (fl,backup_location)
			out=os.system('mv %s %s' % (fl,backup_location))
			if out==0:
				num_copied+=1
			else:
				raise Exception('attempt to copy this file: %s has failed!' % (fl))
		print "\n\nbacked up %s files from %s to %s\none example is: %s" % (num_copied,backup_from_dir,backup_location,fl0)
	else:
		raise Exception('directory youre backing up (%s) isnt within the SUBARUDIR (%s) directory' % (backup_from_dir,SUBARUDIR))
else:
	raise Exception('directory youre backing up (%s) doesnt exist!' % (backup_from_dir))

