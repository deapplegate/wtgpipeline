#! /usr/bin/env python
import sys,os
sys.path.append('/u/ki/awright/InstallingSoftware/pythons/')
from adam_quicktools_ArgCleaner import ArgCleaner
args=ArgCleaner(sys.argv)
print "args=", args

