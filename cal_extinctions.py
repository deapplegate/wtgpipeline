def calc_EBV(coord_in_ra,coord_in_dec):
	
	#coord_in_ra='12:51:26.28'
        #coord_in_dec='27:07:42.'
        coord = Equatorial( str(coord_in_ra*(24./360.)), str(coord_in_dec), epoch='2000') # input needs to be in HOURS as a STRING
        g = Galactic(coord, epoch='2000') # output is in degrees not hours--it's latitude/longitude
 
        spt = re.split('\:',str(g.lat))
        #print spt, abs(float(spt[0])), float(spt[1])/60.
        gallat = float(spt[0]) / abs(float(spt[0])) * (abs(float(spt[0])) + float(spt[1])/60. + float(spt[2])/3600. )
        #print gallat
        #print g.long
        spt = re.split('\:',str(g.long))
        #print spt
        gallong = float(spt[0]) / abs(float(spt[0])) *  (abs(float(spt[0])) + float(spt[1])/60. + float(spt[2])/3600. )
        #print gallong
        
        #coordtest = Equatorial(Galactic(g.long,g.lat, epoch='2000'), epoch='2000')
        
        output = commands.getoutput('dust_getval ' + str(gallong) + ' ' + str(gallat) + ' interp=y ipath=/nfs/slac/g/ki/ki03/xoc/pkelly/DUST/maps') 
        spt = re.split('\s',output)
	#print spt
        EBV = spt[-1]
	#print EBV, float(coord_in_ra), float(coord_in_dec)
	return EBV


#add E(B-V) to ldac table
import re, commands, sys, bashreader, os
from ephem import *

ppid = os.getppid()
dict = bashreader.parseFile('progs.ini')

table = sys.argv[1]

import time
tempfile = '/tmp/outkey'
ebvfile = '/tmp/outebv'
os.system('rm ' + ebvfile)
command = "ldactoasc -b  -i " + table + " -t OBJECTS -k ALPHA_J2000 DELTA_J2000 > " + ebvfile 
print command
os.system(command)
print 'done'
tempmap = '/tmp/map' + str(ppid)
os.system('dust_getval ' + str(gallong) + ' ' + str(gallat) + ' interp=y ipath=/nfs/slac/g/ki/ki03/xoc/pkelly/DUST/maps infile=' + ebvfile + ' outfile=' + tempmap + ' noloop=y') 




raw_input()
list = []
import re
outkey=open(tempfile,'w')
lines = open(ebvfile,'r').readlines()
# READ IN COLUMN INFO
lineindex = 0
timehold = time.time()
for line in lines:
	tt = re.split('\s+',line)
	ra = float(tt[0])
	dec = float(tt[1])
	EBV = calc_EBV(float(ra),float(dec))
	outkey.write(str(EBV) + '\n')
	lineindex += 1
	
	
	if lineindex % 1000 == 0: 
		print lineindex, len(lines), time.time() - timehold
		timehold = time.time()
outkey.close()

command = "asctoldac -i " + tempfile + " -o " + tempfile + ".cat -c " + dict['photconf'] + "/EBV.conf -t OBJECTS  "
os.system(command)

command = "ldacjoinkey -o test -i " + table + " -p " + tempfile + ".cat -t OBJECTS -k EBV" 
os.system(command)




























