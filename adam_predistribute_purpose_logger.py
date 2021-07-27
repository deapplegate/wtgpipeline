#! /usr/bin/env python
#adam-does# this code takes undistributed sets (with names similar to .../CLUSTER_DETAILS/TYPE_OF_DATA/*.fits) and puts the purpose and type of data into the headers so that it will be there after the sets have been distributed

## these files are in folders that bare names of their purposes. Log this in a txt file and in the image headers
## then distribute sets

#/u/ki/awright/data/from_archive/newdarks/
import sys,os,re,string
import imagetools
from glob import glob
dirs=[] ## FILL THIS!
#dirs=["/u/ki/awright/data/from_archive/Abell2744_2008/SUPERFLAT_2008-07-30_W-S-I+/",
#"/u/ki/awright/data/from_archive/Abell2744_2008/SUPERFLAT_2008-08-24-2008-08-28_W-S-I+/",
#"/u/ki/awright/data/from_archive/Abell2744_2013/FLAT/",
#"/u/ki/awright/data/from_archive/Abell2744_2013/OBJECT/",
#"/u/ki/awright/data/from_archive/Abell2744_2013/BIAS/",
#"/u/ki/awright/data/from_archive/Abell2744_2013/SUPERFLAT_2013-11-29_W-J-B/",
#"/u/ki/awright/data/from_archive/Abell2744_2013/SUPERFLAT_2013-02-06_2013-06-10_W-J-B/",
#"/u/ki/awright/data/from_archive/Abell2744_2013/SUPERFLAT_2013-06-09-2013-06-11_W-S-Z+/",
#"/u/ki/awright/data/from_archive/Abell2744_2013/SUPERFLAT_2013-12-01_W-S-Z+/"]
#dirs=["/u/ki/awright/data/from_archive/Abell2744_2013/SUPERFLAT_2013-02-06_W-C-RC/",
#"/u/ki/awright/data/from_archive/Abell2744_2013/SUPERFLAT_2013-06-10_W-C-RC/",
#"/u/ki/awright/data/from_archive/Abell2744_2013/SUPERFLAT_2013-12-01_W-C-RC/",
#"/u/ki/awright/data/from_archive/Z2089/BIAS_2007-02-13-2007-02-16/",
#"/u/ki/awright/data/from_archive/Z2089/BIAS_2009-03-27-2009-03-29/",
#"/u/ki/awright/data/from_archive/Z2089/BIAS_2010-03-12-2010-03-16/",
#"/u/ki/awright/data/from_archive/Z2089/BIAS_2010-12-04-2010-12-06/",
#"/u/ki/awright/data/from_archive/Z2089/FLAT/",
#"/u/ki/awright/data/from_archive/Z2089/SCIENCE/",
#"/u/ki/awright/data/from_archive/Z2089/SUPERFLAT2_2007-02-13_W-S-I+/",
#"/u/ki/awright/data/from_archive/Z2089/SUPERFLAT2_2009-03-28_W-S-I+/",
#"/u/ki/awright/data/from_archive/Z2089/SUPERFLAT2_2010-03-15_W-J-V/",
#"/u/ki/awright/data/from_archive/Z2089/SUPERFLAT2_2010-12-05_W-J-V/",
#"/u/ki/awright/data/from_archive/Z2089/SUPERFLAT_2007-02-13_W-S-I+/",
#"/u/ki/awright/data/from_archive/Z2089/SUPERFLAT_2009-03-28_W-S-I+/",
#"/u/ki/awright/data/from_archive/Z2089/SUPERFLAT_2010-03-15_W-J-V/",
#"/u/ki/awright/data/from_archive/Z2089/SUPERFLAT_2010-12-05_W-J-V/",
#"/u/ki/awright/data/from_archive/Z2701/FLAT/",
#"/u/ki/awright/data/from_archive/Z2701/SCIENCE/",
#"/u/ki/awright/data/from_archive/Z2701/SUPERFLAT2_2010-03-15_W-S-I+/",
#"/u/ki/awright/data/from_archive/Z2701/SUPERFLAT_2010-03-15_W-S-I+/"]
import header_key_add
for dir in dirs:
	splits=dir.split("/")
	purpose=splits[-2]
	cluster=splits[-3]
	fls=glob(dir+"*.fits")
	print ' dir=',dir , ' len(fls)=',len(fls) , ' purpose=',purpose , ' cluster=',cluster
	for fl in fls:
		header_key_add.add_key_val(fl,["DOTHIS","TOTHIS"],[purpose,cluster])

