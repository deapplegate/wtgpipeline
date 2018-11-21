#! /usr/bin/env python
#adam-example# ./adam_tmp_add_GAIN_to_header.py RXJ2129
import sys,os,re
from glob import glob

from my_cluster_params import ic_cldata,clusters_refcats
data_root=os.environ['SUBARUDIR']
filters=["W-J-B","W-J-V","W-C-RC","W-S-I+","W-C-IC","W-S-Z+"]
import astropy
import astropy.io.fits

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
			newppruns=glob(newdir+"/"+filt+"_20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]")
			newpprun=' '.join([ pprundirstr.rsplit('/')[-1] for pprundirstr in newppruns])
			new_sci_dir=newdir+filt+"/SCIENCE"
			sciims=glob(new_sci_dir+"/SUPA*I.fits")
		#oldcalibs=glob(olddir+"/"+filt+"*CALIB/")
		newcalibs=glob(newdir+"/"+filt+"*CALIB/")
		for new_sci_dir in newcalibs:
			sciims+=glob(new_sci_dir+"/SUPA*I.fits")
		sciims=filter( lambda x: not x.endswith('sub.fits') ,sciims)
		for fl in sciims:
			fitfl=astropy.io.fits.open(fl,'update')
			fitfo=fitfl[0]
			config=fitfo.header['CONFIG']
			if not fitfo.header.__contains__('GAIN'):
				print cluster,filter,'lacks gain',fl
				if config=='10_3':
					fitfo.header['GAIN']=3.0
				elif config=='10_2':
					fitfo.header['GAIN']=2.5
				elif config=='10_1':
					fitfo.header['GAIN']=2.5
				else:
					raise Exception('CONFIG isnt 10_3 10_2 or 10_1 for fl='+fl)
			else:
				print 'adam-look',cluster,filter,'HAS GAIN',fl
			try:
				fitfl.close()
			except:
				print "adam-look TRY VERIFYING!"
				fitfo.verify('fix')
				fitfl.close()
