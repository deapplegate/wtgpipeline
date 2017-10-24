#! /usr/bin/env python
from __future__ import division
import pickle
import astropy.io.fits as pyfits
import astropy
from matplotlib.pyplot import *
from numpy import *
from glob import glob
import sys ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
import os
#import BartStar
namespace=globals()

SEXDIR='/u/ki/awright/InstallingSoftware/pythons/sextractimtools/'
def Star_Rad_Mag_Range(catfl,Nstars=None,ELLIPTICITY=None,**kwargs):
	'''this runs preanisotropy and gets a range of values in Radius-Magnitude space that you can consider stars!
	default CLASS_STAR minimum = .65, but you can change this
	IF YOU SET CLASS_STAR=None, then preanisotropy will run without a cut on CLASS_STAR, but instead with a cut on ellipticity!'''
	#print "Star_Rad_Mag_Range kwargs=",kwargs
	try:
		if 'ELLIPTICITY' in kwargs.keys():
			print "\nIT WORKED\n"*20
			ELLIPTICITY=kwargs['ELLIPTICITY']
			
		#(1)#getting the ldac CATALOG files
		#Pnum0   /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/coadds-pretty_for_10_3_cr.2/MACS0018+16_W-C-RC_sub1.fits   14.7568	 0.787
		#adam-remove# cosmic_fl="/u/ki/awright/InstallingSoftware/pythons/sextractimtools/CATALOG.fits_ldac-%s.fits" % (imagetools.id_generator(10),)
		outfl="/u/ki/awright/InstallingSoftware/pythons/sextractimtools/prean_out-%s.log" % (imagetools.id_generator(10),)
		#default sextractor#print "**ANTI-REMINDER** for now I'm using the default (2.8.6) even though it gives non-sensical values of FWHM! rather than the theli version of sextractor (2.2.2)"
		#default sextractor#sex_command="/afs/slac/g/ki/software/local/bin/sex"
		#adam-remove# print "**REMINDER** for now I'm using the theli version of sextractor (2.2.2) rather than the default (2.8.6) since it gives sensible values of FWHM!"
		#adam-remove# sex_command="/afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/sex_theli"
		#adam-remove# config=SEXDIR+'stars.sex.config'
		#adam-remove# getcat=sex_command+" %s -c %s -SEEING_FWHM %s -FILTER N -DETECT_THRESH 10 -ANALYSIS_THRESH 10 -DETECT_MINAREA 2 -CATALOG_NAME %s -CATALOG_TYPE FITS_LDAC" % (fl,config,cosmic_fl)
		#adam-remove# print "Star_Rad_Mag_Range get star catalog command:",getcat
		#getcat=sex_command+" %s -c /u/ki/awright/thiswork/eyes/config-sex.10_3_cr.2.1 -SEEING_FWHM %s -FILTER N -DETECT_THRESH 10 -ANALYSIS_THRESH 10 -DETECT_MINAREA 1 -CATALOG_NAME %s -CATALOG_TYPE FITS_LDAC" % (fl,cosmic_fl)
		#adam-remove# catout=os.system(getcat) #cosmic.fits
		#(2)#Run preanisotropy on the pretty files to get stars
		getrange_begin="/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/preanisotropy -i %s -t LDAC_OBJECTS -k FLUX_RADIUS MAG_AUTO -s 0.05 -c FLUX_RADIUS 0.7 7.0" % (catfl,)
		getrange_end="2>&1 | tee -a %s" % (outfl,)
		#getrange="/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/preanisotropy -i %s -t LDAC_OBJECTS -k FLUX_RADIUS MAG_AUTO -s 0.05 -c FLUX_RADIUS 0.5 8.0 ELLIPTICITY 0 %s 2>&1 | tee -a %s" % (catfl,ELLIPTICITY,outfl)
		getrange_middles=[]
		if ELLIPTICITY:
			getrange_middles.append("ELLIPTICITY 0.0 %s" % (ELLIPTICITY))
		getrange=[getrange_begin]+getrange_middles+[getrange_end]
		getrangecmd=" ".join(getrange)
		#FLUX_MAX 10.0 100000.0
		print 'Star_Rad_Mag_Range getrangecmd: %s' % (getrangecmd)
		rangeout=os.system(getrangecmd)
		out=open(outfl)
		txt=out.read()
		keyline='propose the following range for stars: '
		skiplines=txt.index(keyline)+len(keyline)
		endtxt=txt[skiplines:]
		txt2=endtxt.partition('\n')[0]
		txt2.partition(' and ')
		radtxt,junk,magtxt=txt2.partition(' and ')
		radsplit=radtxt.split(' ')
		magsplit=magtxt.split(' ')
		magmin=float(magsplit[0])
		magmax=float(magsplit[-1])
		radmin=float(radsplit[0])
		radmax=float(radsplit[-1])
		os.system('rm '+outfl)
		#get the number of stars
		if Nstars:
			starline='Preselected '
			txt.index(starline)
			txt.index(starline)+len(starline)
			skiplines=txt.index(starline)+len(starline)
			endtxt=txt[skiplines:]
			endtxt.index(' objects')
			Nstars=int(endtxt[:endtxt.index(' objects')])
			return (radmin,radmax,magmin,magmax),Nstars
		else:
			return radmin,radmax,magmin,magmax
	except:
		namespace.update(locals())
		raise


def improved_star_mag_rad_range(star_catfl,ex=1.0,**kwargs):
	'''my finely tuned star magnitude and radius box finder
	returns radmin,radmax,magmin,magmax'''
	#print "improved_star_mag_rad_range kwargs=",kwargs
	#define tuneing parameters
	cs_candidate_cut_low=.3
	cs_candidate_cut_high=.3
	#run the function imagetools.Star_Rad_Mag_Range
	try:
		radmin_low,radmax_low,magmin_low,magmax_low=Star_Rad_Mag_Range(star_catfl,ELLIPTICITY=cs_candidate_cut_low,**kwargs)
	except ValueError:
		namespace.update(locals())
		print "Hit ValueError on Low ELLIPTICITY Cut! Must have a very crappy image!"
		raise
	try:
		radmin_high,radmax_high,magmin_high,magmax_high=Star_Rad_Mag_Range(star_catfl,ELLIPTICITY=cs_candidate_cut_high,**kwargs)
	except ValueError:
		print "Hit ValueError on High ELLIPTICITY Cut\n"*100
		namespace.update(locals())
		radmin_high,radmax_high,magmin_high,magmax_high=radmin_low,radmax_low,magmin_low,magmax_low #tmp
	if radmin_high<radmin_low:radmin_high=radmin_low
	if radmax_high<radmax_low:radmax_high=radmax_low
	if magmin_high<magmin_low:magmin_high=magmin_low
	if magmax_high<magmax_low:magmax_high=magmax_low
	radmin,radmax,magmin,magmax=min([radmin_low,radmin_high]),max([radmax_low,radmax_high]),min([magmin_low,magmin_high]),max([magmax_low,magmax_high])
	radmid=(radmin+radmax)/2.0
	radhalf=radmid-radmin
	if type(ex)==tuple:
		radmin-=ex[0]*radhalf
		radmax+=ex[1]*radhalf
	else:
		radmin-=ex*radhalf
		radmax+=ex*radhalf
	#magmid=(magmin+magmax)/2.0
	#maghalf=magmid-magmin
	#magmin-=ex*maghalf
	#magmax+=ex*maghalf
	##magmin-=.5
	#print "radmin,radmax,magmin,magmax=",radmin,radmax,magmin,magmax
	return radmin,radmax,magmin,magmax


def getstar(star_catfl,radmagrange=None,unsat_cut=None,ex=(1.5,2.2),cs_star_cut=.65,ellcut=.25,**kwargs):
	'''Get the stars from this catalog by using improved_star_mag_rad_range function to get cuts on radius and magnitude and then use selective cuts to get the stars. Return the table and a list of bools that will select stars from the table.
	unsat_cut=None: use this to explicitly include saturated stars!'''

	#print "**REMINDER** for now I'm using the theli version of sextractor (2.2.2) rather than the default (2.8.6) since it gives sensible values of FWHM!"
	## if in ascii, then next line doesn't work# star_table = ascii.read(star_catfl,Reader=ascii.sextractor.SExtractor)
	fo=pyfits.open(star_catfl)[-1]
	star_table=fo.data
	if radmagrange==None:
		#print "\ngetstar #2 (getting radmin,radmax,magmin,magmax):\n\t%s\n-----END #2-----\n" % ('radmin,radmax,magmin,magmax=improved_star_mag_rad_range(star_catfl,,**kwargs)',)
		radmin,radmax,magmin,magmax=improved_star_mag_rad_range(star_catfl,ex=ex,**kwargs)
	else:
		radmin,radmax,magmin,magmax=radmagrange
	mag=star_table['MAG_AUTO']
	rad=star_table['FLUX_RADIUS']
	ellipticity=star_table['ELLIPTICITY']
	##flux=star_table['FLUX_MAX']
	rad_star_box = (rad>radmin) * (rad<radmax)
	mag_star_box =  (mag>magmin) * (mag<magmax)
	star_box = rad_star_box * mag_star_box
	
	round_box=ellipticity<ellcut
	good_box=star_box * round_box
	print "Final Number of stars is %s of a total %s detections" % (good_box.sum(),len(good_box))
	#I delete star_catfl and star_fitsfl in stars2block.py, but if I'm calling this function from another place then I will need to remember to delete them!
	cuts={'ELLIPTICITY':ellcut,'MAG_AUTO':(magmin,magmax),'FLUX_RADIUS':(radmin,radmax)}
	return star_table,good_box,cuts

def get_seeing_backrms(fl):

	kwargs={"SEEING_FWHM":.7,"CATALOG_TYPE":"FITS_LDAC","DETECT_MINAREA":2, "ANALYSIS_THRESH":8.0, "DETECT_THRESH":8.0,"PARAMETERS_NAME":"/u/ki/awright/data/BFcorr/2017_test/sex.params_stars"}
	#tmp#kwargs={"SEEING_FWHM":.7,"CATALOG_TYPE":"FITS_LDAC","DETECT_MINAREA":2, "ANALYSIS_THRESH":5.0, "DETECT_THRESH":5.0,"PARAMETERS_NAME":"/u/ki/awright/data/BFcorr/2017_test/sex.params_stars"}
	if type(fl)==list:
		Ndets,Nstars=0,0
		fls=fl
		backrmss=[]
		seeings=[]
		for fl in fls:
			#os.system('./adam_simplecat_from_image.sh %s %s' % (fl,fl.replace('.fits','.cat')))
			catfl=fl.replace('.fits','.cat')
			res,RMS_back_fl=sextract.sextractor(fl,CATALOG_NAME=catfl,c="/u/ki/awright/InstallingSoftware/pythons/sextractimtools/seeing_clearly.sex.config",RMS_back=True,**kwargs)
			backrms,backlevel=RMS_back_fl
			star_table , good_box , cuts= getstar(catfl,radmagrange=None,ex=(1.5,3.0))
			startab=star_table[good_box]
			Nstars+=len(startab);Ndets+=len(star_table)
			seeing=median(startab["FWHM_IMAGE"])*.202
			seeings.append(seeing)
			backrmss.append(backrms)
			print os.path.basename(fl)," seeing=", seeing," arcsec"

		med_seeing=median(seeings)
		print "#adam-look# final median seeing = %4.2f arcsec (#stars=%s , #dets=%s)" % (med_seeing,Ndets,Nstars)
		for fl in fls:
			fo=astropy.io.fits.open(fl)
			fo[0].header["MYSEEING"]=med_seeing
			fo.close()
			catfl=fl.replace('.fits','.cat')
			os.remove(catfl)
		return med_seeing,backrmss
	if type(fl)==str:
		if fl.endswith(".fits"):
			#os.system('./adam_simplecat_from_image.sh %s %s' % (fl,fl.replace('.fits','.cat')))
			catfl=fl.replace('.fits','.cat')
			kwargs={"SEEING_FWHM":.7,"CATALOG_TYPE":"FITS_LDAC","DETECT_MINAREA":2, "ANALYSIS_THRESH":5.0, "DETECT_THRESH":5.0,"PARAMETERS_NAME":"/u/ki/awright/data/BFcorr/2017_test/sex.params_stars"}
			res,RMS_back_fl=sextract.sextractor(fl,CATALOG_NAME=catfl,c="/u/ki/awright/InstallingSoftware/pythons/sextractimtools/seeing_clearly.sex.config",RMS_back=True,**kwargs)
			backrms,backlevel=RMS_back_fl
			star_table , good_box , cuts= getstar(catfl,radmagrange=None,ex=(1.5,3.0))
			startab=star_table[good_box]
			seeing=median(startab["FWHM_IMAGE"])*.202
			print "seeing=", seeing," arcsec"
			fo=astropy.io.fits.open(fl)
			fo[0].header["MYSEEING"]=seeing
			fo.close()
			return seeing,backrms
		else:
			raise Exception("fl=",fl," isn't a fits image file")

os.system('. /u/ki/awright/wtgpipeline/SUBARU.ini')
os.system('. /u/ki/awright/wtgpipeline/progs.ini')
from astropy.io import ascii
import imagetools
import sextract
if __name__=='__main__':
	args=imagetools.ArgCleaner(sys.argv)
	print "args=", args
	fl=args[0]
	if fl.endswith(".fits"):
		if len(args)>1:
			seeing,backrms=get_seeing_backrms(args)
		else:
			seeing,backrms=get_seeing_backrms(fl)
