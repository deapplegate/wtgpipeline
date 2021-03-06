#! /usr/bin/env python
#adam-does# runs SeeingClearly to get the seeing and rms of the image, then uses those to get sextractor thresholds for CR detection
#adam-use# use with CRNitschke pipeline
#adam-call_example# call it like ./get_sextract_thresholds.py /path/flname.fits output_file.txt

#IO stuff:
import sys ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
sys.path.append('/u/ki/awright/wtgpipeline/CRNitschke/')
###saveout = sys.stdout
saveout = sys.stdout
###logout = open('SeeingClearly_stdout.log','w')
###sys.stdout = logout
saveerr = sys.stderr
###logerr = open('SeeingClearly_stderr.log','w')
###sys.stderr = logerr
sys.stdout = sys.stderr

#the basics
import hashlib
import os
import SeeingClearly
from copy import deepcopy

def seeing_to_ft_dt(x):
	y1_dt,m_dt,x1_dt= 5900, -16551.7, 0.48
	min_dt= 3500
	max_dt= 6000
	yy_dts=y1_dt+m_dt*(x-x1_dt)
	if yy_dts<min_dt:yy_dts=min_dt
	if yy_dts>max_dt:yy_dts=max_dt
	y1_ft,m_ft,x1_ft,min_ft= 850, -7000.0, 0.48, 450
	min_ft= 450
	max_ft= 1000
	yy_fts=y1_ft+m_ft*(x-x1_ft)
	if yy_fts<min_ft:yy_fts=min_ft
	if yy_fts>max_ft:yy_fts=max_ft
	return yy_fts,yy_dts

	
import imagetools
import glob
import astropy
from astropy.io import ascii
from numpy import asarray
if __name__ == "__main__":
	args=deepcopy(sys.argv[1:])
	for false_arg in ['-i', '--']:
		if false_arg in args: args.remove(false_arg)
	if len(args)<1:
		sys.exit()
	if not os.path.isfile(args[0]):
		print "sys.argv[1]=",args[0]
		raise Exception(args[0]+" is not a file!")
	else:
		fl=args[0]
		fl2save=args[1]
	#start tmp
	print "Using SeeingClearly to get seeing for: "+fl
	print "saving output to: " +fl2save
	try:
		FILTER=astropy.io.fits.open(fl)[0].header['FILTER']
	except:
		FILTER="UnknownFilt"
	basename=os.path.basename(fl)
	#CCDnum=imagetools.GetCCD(fl)
	#globthis='_'+str(CCDnum)
	#glob_basename=basename.replace(globthis,'_*')
	#adam-old# seeing,back_rms=SeeingClearly.seeing_clearly_withplot(fls,checkplots=1,saveas='pltSeeingClearly_%s_%s' % (FILTER,BASE[:-1]+"ALL"))
	import adam_stars_from_cat
	import numpy
	seeing,back_rms=adam_stars_from_cat.get_seeing_backrms(fl)
	back_rms=numpy.array(back_rms)
	ft,dt=seeing_to_ft_dt(seeing)
	detect_thresh=dt/back_rms #convert to S2N ratio
	filter_thresh=ft/back_rms #convert to S2N ratio
	if FILTER=='W-J-B':
		detect_thresh=asarray([min(170.0,detect_thresh[i]) for i in range(len(detect_thresh))])
		filter_thresh=asarray([min(20.0,filter_thresh[i]) for i in range(len(filter_thresh))])
	elif (detect_thresh>170.0).any() or (filter_thresh>20.0).any():
		print 'checkit: filter=%s and %.2f %% of the detection thresholds are above 170.0 and %.2f %% of the filter thresholds are above 20.0' % (FILTER,(detect_thresh>170.0).mean()*100, (filter_thresh>20.0).mean()*100)
	dict_out={}
	dict_out['seeing']=[seeing]
	dict_out['rms']=[back_rms]
	dict_out['dt']=[detect_thresh]
	dict_out['ft']=[filter_thresh]
	dict_out['#files']=[fl]
	t=astropy.table.Table(data=dict_out,names=['#files','rms','seeing','dt','ft'],dtype=[str,float,float,float,float])
	t.write(fl2save,format="ascii.basic")
	#adam-2014#detect_thresh_cap=min(detect_thresh,150.0) #cap is now set in the function seeing_to_ft_dt
	#PIXSCALE=float(os.environ['PIXSCALE'])
	#if seeing>PIXSCALE*2.5: #I have no check for being undersampled, should I?
	#if seeing>.4:
	#	sys.stdout=saveout #back to printing to terminal
	#	###sys.stdout.write(str(seeing))
	#	print "'0 "+str(back_rms)+" "+str(seeing)+" "+str(detect_thresh)+" "+str(filter_thresh)+"'"
	#	
	#else:
	#	#print "exit 1;"
	#	#raise Exception('Seeing less than 2.5xPIXSCALE. The image is undersampled')
	#	#sys.stderr=saveerr #back to printing to terminal
	#	#sys.stderr.write('1')
	#	sys.stdout=saveout #back to printing to terminal
	#	print "0 "+str(back_rms)+" "+str(seeing)+" "+str(detect_thresh)+" "+str(filter_thresh)
