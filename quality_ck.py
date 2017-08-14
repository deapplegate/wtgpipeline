# figure out which files should go into the SUPERFLAT!

from retrieve_images import *

import os, sys, commands, re, commands
from glob import glob

run = sys.argv[1]

gluniq,glnobackup,kill_delete = collect_files(run)

datadir = '/nfs/slac/g/ki/ki05/anja/SUBARU/'
path = datadir + run + '/SCIENCE/ORIGINALS/'
pathaux = datadir + '/auxiliary/' + run  + '/'
pathdownload = path + 'SMOKA/'

superflat_file = open(datadir + run + '/superflat_exclusion','a')

rejectlist = []
superflat_exclude = []
deletelist = []

print glnobackup

gluniq.sort(compare)

for im in gluniq:
	os.system('xpaset -p ds9 file ' + pathdownload + im['file'] + '.fits')
	reject = raw_input(im['OBJECT'] + ' reject? (no is default, "exit" to exit) ')
	if len(reject) > 0:
		if reject[0] == 'y' or reject[0] == 'Y' or reject[0] == 'r':	
	        	rejectlist.append(im)
	        if reject[0] == 'e':
	        	break

print rejectlist	

if not kill_delete:
	for im in rejectlist:
                yes = 1
        	for imnobackup in glnobackup:
        		if imnobackup['file'] == im['file']:
        			yes = 0
        	if yes == 1:	
        		deletelist.append([im['file'],im['OBJECT']])
        	else:
        		superflat_exclude.append([im['file'],im['OBJECT']])
else: 
	print "will not delete because there is no 'nobackup' directory to find originals in\n to exclude from deletion"

print deletelist	
for file in deletelist:
	print file
print superflat_exclude

delete = raw_input('do you want to delete your files?')
if delete[0] == 'y' or delete[0] == 'n':
	for file in deletelist:
		#remove from ORIGINALS directory
		os.system('rm ' + path + file[0] + ".fits")
		#remove from AUXILIARY directory
		for i in range(10):
			os.system('rm ' + pathaux + file[0] + str(i) + '.fits')

super= raw_input('do you want to APPEND to superflat exclusion file?')
if super[0] == 'y' or super[0] == 'n':
	for file in (superflat_exclude+deletelist):
        	for i in range(10):
        		superflat_file.write(file[0] + '_' + str(i) + '\n')
