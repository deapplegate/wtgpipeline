#! /usr/bin/env python
import os,sys,commands

os.system('\ls -rt1 *.py *.sh > bonnpipeline_scripts-all.log')
os.system('grep "adam" bonnpipeline_scripts-all.log > bonnpipeline_scripts-adam.log')
os.system('grep -v "adam" bonnpipeline_scripts-all.log > bonnpipeline_scripts-non-adam.log')
print "got scriptlogs"
dir='/u/ki/awright/bonnpipeline/'
fl_adam=open('bonnpipeline_scripts-adam.log')
fl_non=open('bonnpipeline_scripts-non-adam.log')
ls_adam=fl_adam.readlines()
ls_non=fl_non.readlines()
for line in ls_adam:
	if not line.startswith('adam_'): continue
	tryline=line.replace('adam_','')
	if tryline in ls_non:
		command='ls -lrth %s %s' % (tryline.strip(),line.strip())
		print "command=",command
		out = commands.getoutput(command)
		print out
	#myscript=tryline.strip()
	#for nonline in ls_non:
	#	nonscript=nonline.strip()
	#	if myscript in nonscript: print myscript,nonscript
        #
