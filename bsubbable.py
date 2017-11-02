#! /usr/bin/env python
import sys,os
sys.path.append("~/InstallingSoftware/pythons/")
from adam_quicktools_ArgCleaner import ArgCleaner
args=ArgCleaner(sys.argv)
script=args[0]
if script.startswith("./"):
	script=script[2:]
print "running this:", args[0]
#if os.path.isfile(script):

base=script.split(".")[0]
import time
now=time.localtime()
datestr='-'.join([str(now.tm_year),str(now.tm_mon),str(now.tm_mday)])
outfile="OUT-%s-%s.out" % (datestr,base)
errfile="OUT-%s-%s.err" % (datestr,base)

outdir="/nfs/slac/kipac/fs1/u/awright/batch_files/bsubbable/"

print "IF IT WILL TAKE A WHILE, THEN RUN THIS:"
print "bsub -q long -W 7000 -R rhel60 -o %s/%s -e %s/%s './%s' " % (outdir,outfile,outdir,errfile,script)
