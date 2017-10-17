#! /usr/bin/env python
if 0:
	fl1="adam_svnlogger.log"
	fl2="adam_notes-svn_not_under_version_control_files.log"
	## this particular example is meant to take all of the lines in fl1 that are NOT in fl2 and put them in fl_out
	fl_out="adam_notes-svn_useful.log"
	fo1=open(fl1,'r')
	fo2=open(fl2,'r')
	lines1=fo1.readlines()
	lines2=fo2.readlines()
	lines_out=[]
	for l1 in lines1:
	    if not l1 in lines2:
		lines_out.append(l1)
	fo_out=open(fl_out,'w')
	fo_out.writelines(lines_out)
	fo_out.close()


	import commands 
	import string
	fl1="adam_notes-potentially_useful_files.log"
	fo1=open(fl1,'r')
	lines1=fo1.readlines()
	lines1=map(string.strip,lines1)
	photoz_or_bpz_files=[]
	for l1 in lines1:
		if "photoz" in l1 or "bpz" in l1:
			photoz_or_bpz_files.append(l1)
			command="wc -l "+l1
			out = commands.getoutput(command)
			print l1,out
	print photoz_or_bpz_files


fl1="APER0-1_files_quick.log"
fl2="APER-files_quick.log"
## this particular example is meant to take all of the lines in fl1 and fl2 and put them in fl_out
fl_out="adam_notes-APER0-1_and_APER.log"
fo1=open(fl1,'r')
fo2=open(fl2,'r')
lines1=fo1.readlines()
lines2=fo2.readlines()
lines_out=[]
for l1 in lines1:
    if l1 in lines2:
	lines_out.append(l1)
fo_out=open(fl_out,'w')
fo_out.writelines(lines_out)
fo_out.close()
