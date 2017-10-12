#! /usr/bin/env python
#adam-does# work in progress, eventually will take out the junk in the output logs that comes from printing out environment or something, but right now it only looks at how successful this process would be with the current basic scheme
#adam-use# change this, maybe have it parse outputs or something? The parallel manager makes this more difficult. It might end up being a huge waste of time!
import sys
sys.path.append('/u/ki/awright/InstallingSoftware/pythons/')
from import_tools import *

#tmp: sys.argv
fl='/u/ki/awright/bonnpipeline/scratch/OUT-do_coadd_batch-MACS0416-24_W-J-B.log'
fo=open(fl,'rw')
lines=fo.readlines()
startNumLines=len(lines)
lines_ar=array(lines)

# loop over output log templates and remove them

rm_files=["/u/ki/awright/bonnpipeline/adam_parse_bash_logs/bash_printout.log","/u/ki/awright/bonnpipeline/adam_parse_bash_logs/bash_starting_template.log","/u/ki/awright/bonnpipeline/adam_parse_bash_logs/olines.log","/u/ki/awright/bonnpipeline/adam_parse_bash_logs/subaru_ini_starting_template.log"]
rmNumLines=0
rmLines=[]
rmLinesDict={}
for bfl in rm_files:
	bfl_basename=os.path.basename(bfl)
	rmLinesDict[bfl_basename]=[]
	print "\n"+bfl_basename+":"
	bfo=open(bfl,'r')
	blines=bfo.readlines()
	bNumLines=len(blines)
	bl0=blines[0]
	starting_lines=lines_ar==bl0
	starting_spots=nonzero(starting_lines)[0]
	for ss in starting_spots:
		if lines[ss:ss+bNumLines]==blines:
			rmLines+=range(ss,ss+bNumLines)
			rmLinesDict[bfl_basename]+=range(ss,ss+bNumLines)
			rmNumLines+=bNumLines
			print "\t%s-%s: True" % (ss,ss+bNumLines)
		else:
			print "\t%s-%s: False" % (ss,ss+bNumLines)
	bfo.close()

for bfl1,bfl2 in itertools.combinations(rm_files,2):
	bfl1_basename=os.path.basename(bfl1)
	bfl2_basename=os.path.basename(bfl2)
	rmLinesDict[bfl1_basename]=set( rmLinesDict[bfl1_basename])
	rmLinesDict[bfl2_basename]=set( rmLinesDict[bfl2_basename])
	overlap=rmLinesDict[bfl1_basename].difference(rmLinesDict[bfl2_basename])
	if overlap:
		print bfl1_basename,bfl2_basename, "overlap in lines:",overlap

print "\n\noverlap if nums different: len(rmLines)=%s , len(unique(rmLines))=%s" % (len(rmLines),len(unique(rmLines)))
print "removed %s lines, of a possible %s, making it %.2f percent of original length" % (rmNumLines,startNumLines,(startNumLines-rmNumLines)/float(startNumLines)*100)
fo.close()

#lines_fixed=lines
#shabang=lines[952]
#shabang_lines=lines_ar==shabang
#shabang_spots=nonzero(shabang_lines)[0]

#    0 : 952		952
# 2194 : 3138		944
#14083 : 14599		516
#65032 : 66232		1200
#65136 : 66232		1096
#65377 : 66232		855
#93070 : 94014		944
#98890 : 99834		944
#112449 : 113393 	944
#114694 : 114967 	273
#121236 : 122180 	944
#127431 : 127690 	259
#130112 : 130330 	218
#130141 : 130330 	189
#279439 : 280383 	944
#284541 : 285485 	944
#288318 : 289262 	944

#olines len=944 , fl00='/u/ki/awright/bonnpipeline/adam_parse_bash_logs/olines.log'
