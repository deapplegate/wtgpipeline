#! /usr/bin/env python
#adam-does# this has most of the generalized useful functions I've written since the start of grad school
#adam-use# use with anything and everything
import sys

def ArgCleaner(args=sys.argv,FileString=None,pythons_remove=True): #re-write (generalize) 
	'''takes command line inputs and cleans out the garbage and picks out the useful stuff'''
	py_index=0
	for arg in args:
		if arg.endswith(".py"):
			py_index=args.index(arg)
			break
	args_pre_py=args[:py_index]
	args_post_py=args[py_index:]
	arg0=args[0]
	if "python" in arg0: args.pop(0)
	if "-i" in args_pre_py:args.remove("-i")
	if "--pylab" in args:args.remove("--pylab")
	if "--" in args:args.remove("--")
	if FileString:
		if FileString in args[0]:
			args.pop(0)
	if pythons_remove:
		for arg in args:
			if arg.endswith(".py"):
				args.remove(arg)
	return args

args=ArgCleaner(args=sys.argv)
import numpy as np
gabodsids=np.sort([int(arg) for arg in args])
gab_group=[]
for gab in gabodsids:
    gab_group.append([gab-1,gab,gab+1])
import itertools
gabpairs=np.array(list(itertools.combinations(gabodsids,2)))
neighbors= lambda a,b: a+1==b or a+2==b
gabneighbors=[]
for gabpair in gabpairs:
    gabneighbortest=neighbors(gabpair[0],gabpair[1])
    if gabneighbortest: gabneighbors.append(gabpair)

for gabpair in gabneighbors:
    gab1=gabpair[0]
    gab2=gabpair[1]
    gabkey=str(gab1)+'_AND_'+str(gab2)
    #print gabkey,gabcond
    gabcond="((GABODSID=%s)OR(GABODSID=%s))" % (str(gab1),str(gab2))
    print gabkey,'\t',gabcond

for gab in gabodsids:
    gabcond="(GABODSID=%s)" % (str(gab))
    print gab,'\t',gabcond
