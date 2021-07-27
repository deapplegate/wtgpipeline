#! /usr/bin/env python
'''
this file will flatten a directory with as many (and as complicated) a directory structure as there is.
It links everything into a single dir, except the things you don't want it to, in this case .fits,.cat,.pkl files i don't really need.
'''
#adam-example# ./adam_flattened_linkable_dir.py /u/ki/awright/thiswork/eyes/
import sys
sys.path.append('/u/ki/awright/quick/pythons/')
from adam_quicktools_ArgCleaner import ArgCleaner
args=ArgCleaner(sys.argv)
#from import_tools import *
#SUBARUDIR="/u/ki/awright/data/"
#backup_main="/u/ki/awright/data/backup_files/"
import os,shutil
#os.walk
#adam_flattened_linkable_dir.py
maindir=args[0]
if not os.path.isdir(maindir):
	print 'maindir='+maindir
	raise Exception('you have to input a directory as an argument, not maindir='+maindir)

flatdir=maindir+'adam_flatten_linkable/'
flatdirplots=maindir+'adam_flatten_linkable/plots/'
justplots=1
if not justplots:
	if os.path.isdir(flatdir):
		os.system('rm -r %s' % (flatdir))
	os.mkdir(flatdir)
os.mkdir(flatdirplots)

num_copied=0
num_plots_copied=0
followlinks=True
for root, dirs, files in os.walk(maindir,topdown=False, followlinks=followlinks):
	if 'adam_flatten_linkable' in root:
		continue
	elif '.svn' in root:
		continue
	print '\n##### ', root,' #####'
	#print dirs
	fitsfiles=[]
	catfiles=[]
	pklfiles=[]
	pngfiles=[]
	files2link=[]
	for fl in files:
		if fl.endswith('.fits'):
			fitsfiles.append(fl)
		elif fl.endswith('.pkl'):
			pklfiles.append(fl)
		elif fl.endswith('.cat'):
			catfiles.append(fl)
		elif fl.endswith('.png'):
			pngfiles.append(fl)
		#elif os.path.islink(fl):
		else:
			files2link.append(fl)
	link_locators=root.replace(maindir,'').split('/')
	try:
		link_locators.remove('')
	except ValueError:
		pass
	#link_datetime="%.2i-%.2i-%.4i_at_%.2i-%.2i" % (tm_mon,tm_mday,tm_year,tm_hour,tm_min)
	if not justplots:
		link_location=flatdir+'__'.join(link_locators) #+"_"+link_datetime
		for fl in files2link:
			source_fl=os.path.join(root,fl)
			dest_fl=link_location+'_NAME_'+fl
			if os.path.islink(dest_fl):
				print 'already exists:',dest_fl
			print 'ln -s %s %s' % (source_fl,dest_fl)
			num_copied+=1
			os.symlink(source_fl,dest_fl)
	link_location=flatdirplots+'__'.join(link_locators) #+"_"+link_datetime
	for fl in pngfiles:
		source_fl=os.path.join(root,fl)
		dest_fl=link_location+'_NAME_'+fl
		if os.path.islink(dest_fl):
			print 'already exists:',dest_fl
		print 'ln -s %s %s' % (source_fl,dest_fl)
		num_plots_copied+=1
		os.symlink(source_fl,dest_fl)
print 'copied:',num_copied,' to ',flatdir
print 'copied:',num_plots_copied,' to ',flatdirplots
