import os, sys, commands, re
from glob import glob

datadir = '/nfs/slac/g/ki/ki05/anja/SUBARU/'

if len(sys.argv) < 2: 
	print "python calcset.py run kind"
	print "python calcset.py 2002-12-03_W-J-V SKYFLAT"

run = sys.argv[1]
kind = sys.argv[2] # DOMEFLAT or SKYFLAT
if len(sys.argv) > 3: 
	instrument = sys.argv[3]
else: instrument = 'SUBARU_10_2'

path = datadir + run + '/SCIENCE/ORIGINALS/'
gl = glob(path + '*fits')

if len(gl) == 0:
	path = datadir + run + '/STANDARD/ORIGINALS/'
	gl = glob(path + '*fits')

file = gl[0]
print file
output = commands.getoutput('dfits -x 1 ' + file + ' | fitsort FILTER01 MJD OBJECT')

print output

outputre = re.split('\s+',re.split('\n',output)[1])
if outputre[0] == '': outputre = outputre[1:]

FILTER = outputre[1]
MJD = outputre[2]

print FILTER, MJD

output = commands.getoutput( "/afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/nightid -t  22:00:00 -d 31/12/1998 -m " + MJD)
outputre = re.split('\:',re.split('\n',output)[1].replace(' ',''))
GABODSID = outputre[-1]
print output, GABODSID


path = datadir + instrument + '_' + FILTER + '_' + kind

print path
gl = glob(path + '/SET*')


print '\n'

list = {}
for set in gl:
	jj = open(set + '/gabodsid','r').readlines()	
	MIN = re.split('=',jj[1].replace('\n',''))[1]
	MAX = re.split('=',jj[2].replace('\n',''))[1]
	setname = re.split('SET',set)[1] 
	#if float(MIN) < float(GABODSID) < float(MAX):
	#	setfound = 'SET' + setname 

	list['SET' + setname] = {'MIN':MIN,'MAX':MAX}
	
for r in range(1,len(list)+1):	
	print 'SET' + str(r), list['SET' + str(r)]['MIN'],  list['SET' + str(r)]['MAX']

print 'GABODSID', GABODSID

	
	

