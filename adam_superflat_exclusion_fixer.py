#! /usr/bin/env python
#adam-example# ./adam_superflat_exclusion_fixer.py /nfs/slac/g/ki/ki18/anja/SUBARU/2015-12-15_W-C-RC/SCIENCE_SKYFLAT_SET3/superflat_exclusion 0
#adam-example-countonly# ./adam_superflat_exclusion_fixer.py /nfs/slac/g/ki/ki18/anja/SUBARU/2015-12-15_W-C-RC/SCIENCE_SKYFLAT_SET3/superflat_exclusion 1
import sys,os
sys.path.append("~/InstallingSoftware/pythons/")
import imagetools
args=imagetools.ArgCleaner(sys.argv)
print "args=", args

fl=args[0]
if len(args)>1:
	countonly=args[1]

	if countonly=='0':
		print "change the superflat_exclusion file"
	elif countonly=='1':
		print "don't change the superflat_exclusion file, just count the number of images excluded in each ccd"
	else:
		raise Exception("no good  ")
else:
	countonly='0'

if not os.path.isfile(fl):
	raise Exception("not a file")

fl_old="%s.old" % (fl)
os.system("cp %s %s" % (fl,fl_old))

fold=open(fl_old,'rb')
import string,re
ccdnums=[str(i) for i in range(1,11)]
ccdnums9=[str(i) for i in range(1,10)]

SF_rmed={}
for n in ccdnums:
	SF_rmed[n]=0

if countonly=='0':
	f=open(fl,'wb')
else:
	f=open(fl,'rb')

for l in fold.xreadlines():
	l=l.strip()
	if not l: continue
	m=re.match("(SUPA[0-9][0-9][0-9][0-9][0-9][0-9][0-9])(.*)",l)
	if not m: raise Exception("one line isn't empty or a proper SUPA#######!")
	l0,l1=m.groups()
	if l1 in ["","_","_*"," *","*"]:
		for n in ccdnums:
			SF_rmed[n]+=1
			newl=l0+"_"+n+"\n"
			if countonly=='0':
				f.write(newl)
	else:
		if "10" in l1:
			SF_rmed["10"]+=1
			newl=l0+"_10\n"
			if countonly=='0':
				f.write(newl)
			l1=l1.replace('10','')
		for n in ccdnums9:
			if n in l1:
				SF_rmed[n]+=1
				newl=l0+"_"+n+"\n"
				if countonly=='0':
					f.write(newl)


f.close()

from glob import glob
originals=glob(os.path.dirname(fl)+"/SCIENCE/ORIGINALS/SUPA*.fits")
ntotal=originals.__len__()
if ntotal==0:
	originals=glob(os.path.dirname(fl).rpartition('/')[0]+"/SCIENCE/ORIGINALS/SUPA*.fits")
	ntotal=originals.__len__()
Sccd="  CCD |                   "
for n in ccdnums:
	Sccd+="\n%5s | %i (rmed %i of %i)" % (n,ntotal-SF_rmed[n],SF_rmed[n],ntotal)
print Sccd
