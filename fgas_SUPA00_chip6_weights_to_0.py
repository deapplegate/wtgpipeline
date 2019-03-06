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
fgas_clusters =['RXJ2129', 'Zw2089']
fgas_clusters =['A2204']
for cluster in fgas_clusters:

	newdir=data_root+"/"+cluster+"/"

	print '\n######## '+cluster+' #########'
	for filt in filters:

		if os.path.isdir(newdir+"/"+filt+"/"):
			new_sci_dir=newdir+filt+"/WEIGHTS"
			sciims7=glob(new_sci_dir+"/SUPA00*_7*I.weight.fits")
			sciims6=glob(new_sci_dir+"/SUPA00*_6*I.weight.fits")
		else:
			continue
		filtstr="    "+filt+": "
		newcalibs=glob(newdir+"/"+filt+"*CALIB/WEIGHTS/")
		for new_sci_dir in newcalibs:
			print cluster,filt,' HAS CALIBS!'
			sciims6+=glob(new_sci_dir+"/SUPA00*_6*I.weight.fits")
			sciims7+=glob(new_sci_dir+"/SUPA00*_7*I.weight.fits")
		#print ' len(sciims7)=',len(sciims7)
		#print ' len(sciims6)=',len(sciims6)
		print ' len(sciims7)==len(sciims6): ',len(sciims7)==len(sciims6)
		if len(sciims7)!=len(sciims6):
			print 'NOT SAME # of chip6 and chip7 here: '+ newdir+filt+"/WEIGHTS/ ( or maybe "+newdir+"/"+filt+"*CALIB/WEIGHTS/ ) "
		continue
		#sciims=filter( lambda x: not x.endswith('sub.fits') ,sciims)
		#for fl7 in sciims7:
		#	fl6=fl7.replace('_7OCF','_6OCF')
		for fl6 in sciims6:
			print "openning: "+fl6
			try:
				fitfl=astropy.io.fits.open(fl6,'update')
			except:
				fl7=fl6.replace('_6OCF','_7OCF')
				ooo=os.system('cp %s %s' % (fl7,fl6))
				if ooo>0:
					raise Exception('could execute command: '+'cp %s %s' % (fl7,fl6))
				fitfl=astropy.io.fits.open(fl6,'update')
			#fitfl.verify('fix')
			# fitfl[0].data.shape == ( fitfl[0].header['NAXIS2'] , fitfl[0].header['NAXIS1'])
			try:
				if not fitfl[0].data.shape==(4080,2000):
					print 'fl=',fl6,' has: fitfl[0].data.shape=',fitfl[0].data.shape
					raise Exception('not the expected shape!')
			except:
				fl7=fl6.replace('_6OCF','_7OCF')
				ooo=os.system('cp %s %s' % (fl7,fl6))
				if ooo>0:
					raise Exception('could execute command: '+'cp %s %s' % (fl7,fl6))
				fitfl=astropy.io.fits.open(fl6,'update')
			fitfl[0].data= np.zeros(fitfl[0].data.shape,dtype=np.float32)
			fitfl[0].header['BITPIX']=-32
			#del fitfl[0].header['BYTEORDR']
			try:
				fitfl.flush()
				fitfl.close()
			except:
				print "adam-look TRY VERIFYING!"
				fitfl.flush('fix')
				fitfl.close()
			print "set "+fl6+" to zeros"

