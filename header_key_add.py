#! /usr/bin/env python
import sys # ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
#from import_tools import *
from numpy import array
import copy
import astropy
import astropy.io.fits
import os

def ArgCleaner(allargs=sys.argv): #re-write (generalize) 
        '''takes command line inputs and cleans out the garbage and picks out the useful stuff'''
        args=[]
        for arg in allargs:
                if arg.endswith(".py"):continue
                if arg.startswith("-"):continue
                if arg=='python':continue
                else:
                        args.append(arg)
        return args

#def add_key_val(fl,keys,vals):
#	fitfl=astropy.io.fits.open(fl,'update')
#	head=fitfl[0].header
#	for k,v in zip(keys,vals):	
#		head[k]=v
#	fitfl.verify(option="ignore")
#	fitfl.flush()
#	fitfl.close()

def add_key_val(fl,keys,vals):
	fitfl=astropy.io.fits.open(fl,'update')
	for fitfo in fitfl:
		head=fitfo.header
		for k,v in zip(keys,vals):	
			head[k]=v
	fitfl.verify(option="ignore")
	fitfl.flush()
	fitfl.close()

if __name__ == "__main__":
	args=copy.deepcopy(ArgCleaner(sys.argv))
	#args_dashed=array([s.startswith('-') and not s.replace('.','0').isdigit() for s in args])
	#keep=args_dashed.cumsum()
	#keys_vals=args[keep]
	#NN=len(keys_vals)
	#keys=keys_vals[0:NN:2]
	#vals=keys_vals[1:NN:2]
	args=array(args)
	keys_vals_spots=array(['=' in s for s in args])
	keys_vals=args[keys_vals_spots]
	if keys_vals_spots[0]==False:
		fl=args[0]
	else:
		raise("what the deal is?")
	keys=[]
	vals=[]
	for p in keys_vals:
		k,v=p.split('=')
		v_negative_bool=v.startswith('-')
		v_decimal_bool='.' in v
		if v.isdigit() or (v_negative_bool and v[1:].isdigit()):
			v=int(v)
		elif v_decimal_bool and v.replace('.','0').replace('-','0').isdigit(): #then it's a number with decimals or negatives in it
			v=float(v)
		keys.append(k)
		vals.append(v)
	print "fl=",fl
	print "keys=",keys
	print "vals=",vals
	add_key_val(fl,keys,vals)
