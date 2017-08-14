def calibrate_magnitudes(zps,coeffs,mag):
	import numpy

import sys, os, re
cluster = sys.argv[1]
pipelinedir = sys.argv[2]
caldir = '/nfs/slac/g/ki/ki02/xoc/anja/SUBARU/' + cluster + '/CALIBRATION/'
PHOTOCONF = pipelinedir + os.environ['PHOTCONF'][1:]
# need to read in the color used in the fit for each band i.e. (B-V) for B band
colors = ['B','V','R','I','z']
colors_iter = ['','B','V','R','I','z']

os.system('source progs.ini')

#move to processed cluster directory
for color in colors:
	os.chdir(caldir)
	os.chdir(color)
	#need to paste together catalogs after astrometry has been applied -- this is catalog cat5
	os.system('rm merge_*.cat5')
       	os.system('ldacpaste -i *cat5 -o merge_chips.cat5')
        #now need to join together the OBJECTS and FIELDS tables with make_join
	command = 'make_join -i merge_chips.cat5 -o merge_temp_join.cat5 -c ' + PHOTOCONF + '/make_join_std.conf'
	print command
      	os.system(command) 
       	os.system('ldacrentab -i merge_temp_join.cat5 -o merge_join.cat5 -t OBJECTS STDTAB')


os.chdir(caldir)
	 
#then need to ASSOCIATE and MAKE_SSC
filelist = [ caldir + '/'+y+'/merge_join.cat5' for y in colors[0:2]]
filelist_assoc = [caldir + '/'+y+'/merge_assoc.cat5' for y in colors[0:2]]
for file in filelist_assoc: os.system('rm ' + file)
filelist = reduce(lambda x,y: x + ' ' + y,filelist)
filelist_assoc = reduce(lambda x,y: x + ' ' + y,filelist_assoc)
print filelist 

command = 'associate -i ' + filelist + ' -t STDTAB -o ' + filelist_assoc + ' -c ' + PHOTOCONF + '/fullastrom.conf.associate' #/std.conf.associate'
print command

print '\n\n\n\n'
os.system(command)
os.system('rm pairs.cat')
command = 'make_ssc -i ' + filelist_assoc + ' -o pairs.cat -t STDTAB ' # -c ' + PHOTOCONF + '/test_ssc' #'/fullastrom.make_ssc.pairs'
print command
os.system(command)


#then read out



#now need to read 

#os.system("ldactoasc -o ./tmp_ldac -i FIELDS " + + " -t -k " )
#
#os.system("ldactoasc -o ./tmp_ldac -i " + + " -t -k " )
#
#import re
#
#lines = open('tmp_ldac','r').readlines()
#for line in lines:
#	resplit = re.split('\s+',line)		
#	
#
#
#
#import numarray
#
#os.system("asctoldac -o ")
#
#
#
#
#
