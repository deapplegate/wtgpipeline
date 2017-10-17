#! /usr/bin/env python
import sys,os,glob
maindir="/nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/"
backdir="/nfs/slac/g/ki/ki18/anja/SUBARU/compare_astrom_offsets/backup_MACS0416-24_refcat_good5_wt10_STABILITY_INSTRUMENT/"
if not os.path.isdir(backdir):
	os.makedirs(backdir)

#for filter in ["W-C-RC","W-J-B","W-S-Z+"]:
for filter in ["W-C-RC"]:
	# COPY BACKMASK
	if os.path.isdir('%s/%s/SCIENCE/BACKMASK/' % (maindir,filter)):
		command="cp -R %s/%s/SCIENCE/BACKMASK/ %s/BACKMASK_%s/" % (maindir,filter,backdir,filter)
		ooo=os.system(command)
		print ooo,command

	# COPY COADDS
	coadds=glob.glob('%s/%s/SCIENCE/coadd_*/coadd.fits' % (maindir,filter))
	for coadd in coadds:
		if coadd.endswith("weight.fits"): coadd_type=".weight"
		elif coadd.endswith("flag.fits"): coadd_type=".flag"
		else: coadd_type=""
		coadd_rename=coadd.split('/')[-2]
		coadd_rename+="_"+filter
		command="cp %s %s/%s%s.fits" % (coadd,backdir,coadd_rename,coadd_type)
		ooo=os.system(command)
		print ooo,command

	# COPY HEADERS
	headers_path=backdir+filter+"_headers_scamp_photom_2MASS"
	if not os.path.isdir(headers_path):
		os.makedirs(headers_path)
	headers=glob.glob('%s/%s/SCIENCE/headers_scamp_photom_2MASS/*.head' % (maindir,filter))
	for header in headers:
		command='cp %s %s' % (header,headers_path)
		ooo=os.system(command)
		print ooo,command
	
	headers_path=backdir+filter+"_headers_scamp_2MASS"
	if not os.path.isdir(headers_path):
		os.makedirs(headers_path)
	headers=glob.glob('%s/%s/SCIENCE/headers_scamp_2MASS/*.head' % (maindir,filter))
	for header in headers:
		command='cp %s %s' % (header,headers_path)
		ooo=os.system(command)
		print ooo,command

# COPY astrom_photom dir
astromdir=maindir+"W-J-B/SCIENCE/astrom_photom_scamp_2MASS/"
backdirastrom=backdir+"astrom_photom_scamp_2MASS/"
os.system('cp -R %s %s' % (astromdir,backdirastrom))
