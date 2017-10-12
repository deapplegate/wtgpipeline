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
