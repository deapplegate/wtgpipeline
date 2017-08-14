import os, sys
filter = sys.argv[1] 

script = open(filter + '_superflat','w')

if filter == 'b': #ready
	#flatdir = os.environ['subdir'] + '2003-09-25_W-J-B/DOMEFLAT/'
	flatdir = os.environ['subdir'] + '2004-06-20_COSMOS_B/DOMEFLAT/'
	flatprefix = 'DOMEFLAT'
	sciencedir = os.environ['subdir'] + '2004-06-20_COSMOS_B/SCIENCE/'

if filter == 'i': #ready
	#flatdir = os.environ['subdir'] + '2002-06-04_W-C-IC/DOMEFLAT/'
	flatdir = os.environ['subdir'] + '2004-06-20_DEEP_I/DOMEFLAT/'
	flatprefix = 'DOMEFLAT'
	sciencedir = os.environ['subdir'] + '2004-06-20_DEEP_I/SCIENCE/'

if filter == 'z':
	#flatdir = os.environ['subdir'] + '2004-02-23_W-S-Z+/DOMEFLAT/'
	flatdir = os.environ['subdir'] + '2004-06-20_COSMOS_Z/DOMEFLAT/'
	flatprefix = 'DOMEFLAT'
	sciencedir = os.environ['subdir'] + '2004-06-20_COSMOS_Z/SCIENCE/'

script.write('setenv INSTRUMENT SUBARU\n')
for chip in range(1,11):
	from glob import glob
	if len(glob(flatdir + 'SCIENCE_' + str(chip) + ".fits")) == 0:
		script.write('bsub -R rhel40 -q long -e ' + str(chip) + '_' + str(filter) + '_script_out -o ' + str(chip) + '_' + str(filter) + '_script_out ./make_superflat_batch.sh ' + flatdir + ' ' + flatprefix + ' ' + sciencedir + ' ' + str(chip) + ' \n')
