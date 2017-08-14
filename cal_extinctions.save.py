import threading

def ebv_list(list_submit,list_dict,i,ppid): 
	import os
	lineindex = 0
        timehold = time.time()
	list_out = []

	out = open('/tmp/tmpf_' + str(i) + '_' + str(ppid),'w')
        for line in list_submit:
		tt = re.split('\s+',line)
        	ra = float(tt[0])
        	dec = float(tt[1])
        	EBV = calc_EBV(float(ra),float(dec),i)
		list_out.append(EBV)
		#print EBV
		lineindex += 1
		out.write(str(EBV) + '\n')
        	if lineindex % 100 == 0: 
        		print 'thread ' + str(i), lineindex, len(list_submit), time.time() - timehold
        		timehold = time.time()
	list_dict[str(i)]['list_out'] = list_out
	out.close()

def calc_EBV(coord_in_ra,coord_in_dec,i):
	
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
        
        output = commands.getoutput('dust_getval ' + str(gallong) + ' ' + str(gallat) + ' interp=y ipath=/nfs/slac/g/ki/ki03/xoc/pkelly/DUST/maps_' + str(i) ) 
        spt = re.split('\s',output)
	#print spt
        EBV = spt[-1]
	#print EBV, float(coord_in_ra), float(coord_in_dec)
	return EBV

class MyThread ( threading.Thread ):
	def __init__ ( self, list_submit,list_dict, i, ppid):
		self.i = i
		self.list_submit = list_submit 
		self.list_dict = list_dict
		self.ppid = ppid
		threading.Thread.__init__(self)	

	def run ( self ):
		ebv_list(self.list_submit,list_dict,self.i,self.ppid)
	        return 

#add E(B-V) to ldac table
import re, commands, sys, bashreader, os
from ephem import *

dict = bashreader.parseFile('progs.ini')

table = sys.argv[1]

import time
tempfile = '/tmp/outkey'
ebvfile = '/tmp/outebv'
os.system('rm ' + ebvfile)
ppid = os.getppid()
print ppid
command = "ldactoasc -b  -i " + table + " -t OBJECTS -k ALPHA_J2000 DELTA_J2000 > " + ebvfile 
print command
os.system(command)
list = []
import re
outkey=open(tempfile,'w')
lines = open(ebvfile,'r').readlines()
number_interval = 4
length_int = len(lines)/number_interval
start = 0
my_threads = []
list_dict = {}
for i in range(number_interval):
	end = start + length_int
	if i + 1 == number_interval:
		list_submit = lines[start:]
	else:
		list_submit = lines[start:end]
	start = end
	list_dict[str(i)] = {'list_submit':list_submit}
	#s = MyThread(list_submit,list_dict,i,ppid)

	#stat = os.fork()
	print i, 'started'
	s = os.fork()
	if not s:
		ebv_list(list_submit,list_dict,i,ppid)
		sys.exit()
	#s.start()	
	my_threads.append(s)

print my_threads
#print threading.enumerate()
for s in my_threads: 
 	os.waitpid(s,0)

print 'done'

list_out = []
for i in range(number_interval):
	list_out = list_out + list_dict[str(i)]['list_out']

print len(lines), len(list_out)
print lines[0:2], list_out[0:2]
	
	



# READ IN COLUMN INFO











for val in list_out:
	outkey.write(str(val) + '\n')


outkey.close()

command = "asctoldac -i " + tempfile + " -o " + tempfile + ".cat -c " + dict['photconf'] + "/EBV.conf -t OBJECTS  "
os.system(command)

command = "ldacjoinkey -o test -i " + table + " -p " + tempfile + ".cat -t OBJECTS -k EBV" 
os.system(command)

