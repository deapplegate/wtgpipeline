#! /usr/bin/env python
#adam-example# ./adam_tmp_add_GAIN_to_header.py RXJ2129
import sys,os,re
from glob import glob

from my_cluster_params import ic_cldata,clusters_refcats
data_root=os.environ['SUBARUDIR']
filters=["W-J-B","W-J-V","W-C-RC","W-S-I+","W-C-IC","W-S-Z+"]
import astropy
import astropy.io.fits

import numpy as np

fgas_clusters =['MACS0429-02','RXJ2129', 'Zw2089']
fgas_clusters =['MACS1115+01']
for cluster in fgas_clusters:

	newdir=data_root+"/"+cluster+"/"

	print '\n######## '+cluster+' #########'
	for filt in filters:

		filtstr="    "+filt+": "
		#if os.path.isdir(olddir+"/"+filt+"/"):
		#	oldppruns=glob(olddir+"/"+filt+"_20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]")
		#	oldpprun=' '.join([ pprundirstr.rsplit('/')[-1] for pprundirstr in oldppruns])
		#	filtstr=""+filtstr+" : SCIENCE in OLD"
		#	old_sci_dir=olddir+filt+"/SCIENCE"
		#	sciims=glob(old_sci_dir+"/SUPA*.fits")
		#	sciims=filter( lambda x: not x.endswith('sub.fits') ,sciims)
		#	paths,endings1=get_supa_chip_endings(sciims)
		#	sciendings['old'][filt]=endings1
		#	supas=paths[old_sci_dir].keys()
		#	catfls=[]
		#	for supa in supas:
		#		catfls+=glob(astrom_olddir+'cat_photom/'+supa+'*.ldac')
		#	paths,endings2=get_supa_chip_endings(catfls)
		#	catendings['old'][filt]=endings2
		#	print'old',filt,endings1,endings2,oldpprun
		if os.path.isdir(newdir+"/"+filt+"/"):
			new_sci_dir=newdir+filt+"/WEIGHTS"
			sciims=glob(new_sci_dir+"/SUPA00*_7*I.weight.fits")
		#oldcalibs=glob(olddir+"/"+filt+"*CALIB/")
		newcalibs=glob(newdir+"/"+filt+"*CALIB/WEIGHTS/")
		for new_sci_dir in newcalibs:
			sciims+=glob(new_sci_dir+"/SUPA00*_7*I.weight.fits")
		#sciims=filter( lambda x: not x.endswith('sub.fits') ,sciims)
		for fl7 in sciims:
			fl6=fl7.replace('_7OCF','_6OCF')
			ooo=os.system('cp -n %s %s' % (fl7,fl6))
			#ooo=os.system('cp -n %s %s' % (fl7,fl6))
			print "openning: "+fl6
			fitfl=astropy.io.fits.open(fl6,'update')
			fitfl.verify('fix')
			fitfl[0].data= np.zeros(fitfl[0].data.shape,dtype=np.float32)
			#del fitfl[0].header['BYTEORDR']
			try:
				fitfl.flush()
				fitfl.close()
			except:
				print "adam-look TRY VERIFYING!"
				fitfl.flush('fix')
				fitfl.close()
			print "set "+fl6+" to zeros"

print "imstats /u/ki/awright/data/MACS1115+01/W-C-RC/WEIGHTS/SUPA00*_6OCFSRI.weight.fits"
