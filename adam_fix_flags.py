#! /usr/bin/env python                                                                                                                                                             
#adam-does# removes the effect of the regions on the flag images
#adam-use# use only in combination with adam_fix_regweights.sh when you've removed some regions and need to change the weight files accordingly
import sys,os,inspect
sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
from import_tools import *
curfile=os.path.abspath(inspect.getfile(inspect.currentframe()))
FileString=os.path.basename(curfile)
args=imagetools.ArgCleaner(sys.argv,FileString)
fl=args[0]
fo=pyfits.open(fl,mode="update")
im=fo[0].data
fixreg=im>=128
im[fixreg]-=128
fo.flush()
fo.close()
