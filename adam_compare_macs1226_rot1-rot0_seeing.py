#! /usr/bin/env python
#adam-does# calculates seeing, has a plotting option to check if it's right or not 
#adam-use# anything
#the basics
from numpy import *
from matplotlib.pyplot import *
from glob import glob
from copy import deepcopy
import scipy
import itertools
#unlikely to need, so comment them out:
#from collections import Counter
#import cosmolopy
#import shutil
import hashlib
import astropy
import astropy, astropy.io.fits as pyfits
#pyfits=astropy.io.fits
from astropy.io import ascii
#shell/non-python related stuff
import sys ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
import time
import os
import shutil
import pdb
import re
import pickle
#my stuff!
from fitter import Gauss
from UsefulTools import names, FromPick_data_true, FromPick_data_spots, GetMiddle, GetSpots_bins_values, ShortFileString, num2str
import imagetools
import cattools
#super useful image packages
#import ds9
from scipy.stats import *
from scipy.ndimage import *
conn8=array([[1,1,1],[1,1,1],[1,1,1]])
conn4=array([[0,1,0],[1,1,1],[0,1,0]])
#BEFORE PLOTTING
tm_year,tm_mon,tm_mday,tm_hour,tm_min,tm_sec,tm_wday, tm_yday,tm_isdst=time.localtime()
DateString=str(tm_mon)+'/'+str(tm_mday)+'/'+str(tm_year)
FileString=ShortFileString(sys.argv[0])
from numpy import *
namespace=globals()
import scipy.signal as signal
import BartStar
import sextract
SEXDIR='/u/ki/awright/InstallingSoftware/pythons/sextractimtools/'
PLOTDIR='/u/ki/awright/data/eyes/CRNitschke_output/plot_SeeingClearly/'
steps=arange(.3,2.3,.015) #chose this range and step size, could change later

def seeing_clearly_withplot(image,checkplots=1,saveas=None,**kwargs):
	'''SAME AS seeing_clearly, BUT WITH PLOTTING!
	Take input image, which could be one chip or a series of 10 chips and return the seeing value of that image.
	(1) run the sextractor function to make a catalog with the parameters I'll need to identify stars
	(2) Weight detections by how likely they are to be stars
	(3) Step along the FWHM axis of the MAG, FWHM plane and find at which point the weighted sum of the neighboring detections is largest. This point is the seeing of the image.'''
	try:
		try:
			header=pyfits.open(image)[0].header
		except IOError:
			header=pyfits.open(image[0])[0].header
		FILTER=header['FILTER']
		#####DETERMINE CUT PARAMS#####
		number_NN=155 #chose this number of nearest neighbors to consider, could change later #cut#
		dist_cut=.04 #could change later #cut#
		sat_cut=.87 #could change later #cut#
		#if 'DATACONF' in os.environ and 'PIXSCALE' in os.environ and 'SATURATION' in os.environ:
		#	DATACONF=os.environ['DATACONF']
		#	PIXSCALE=float(os.environ['PIXSCALE'])	
		#	SATURATION=os.environ['SATURATION']
		#else:
		#	raise Exception("YOU MUST RUN THIS COMMAND FIRST: . /u/ki/awright/wtgpipeline/SUBARU.ini")
		if 'PIXSCALE' in os.environ:
			PIXSCALE=float(os.environ['PIXSCALE'])	
		else:
			PIXSCALE=.202 #default to SUBARU 10_3 config
		config=SEXDIR+'seeing_clearly.sex.config'
		CATALOG_NAME=SEXDIR+'seeing_clearly-%s.cat' % (imagetools.id_generator(6),)
		#set default sextractor parameters
		if 'DETECT_MINAREA' not in kwargs: kwargs['DETECT_MINAREA']=2
		if 'DETECT_THRESH' not in kwargs:
			#if FILTER=="W-C-RC":
			#	kwargs['DETECT_THRESH']=10.0
			#	s2n_thresh=10.0
			#elif FILTER=="W-J-B":
			#	kwargs['DETECT_THRESH']=7.0
			#	s2n_thresh=7.0
			kwargs['DETECT_THRESH']=10.0
			s2n_thresh=10.0
		else:
			s2n_thresh=kwargs['DETECT_THRESH']
		if 'ANALYSIS_THRESH' not in kwargs:kwargs['ANALYSIS_THRESH']=kwargs['DETECT_THRESH']
		#####RUN SEXTRACTOR#####
		#2.2.2#sextractor(image,CATALOG_NAME=CATALOG_NAME,c=config,**kwargs)
		if type(image)==string_ or type(image)==str:
			res,RMS_back=sextract.sextractor(image,CATALOG_NAME=CATALOG_NAME,c=config,RMS_back=True,SEEING_FWHM=.7,**kwargs)#chose seeing=.7 since 2.2.2 requires a seeing value, could change later
			back_rms,back=RMS_back
			t=ascii.read(CATALOG_NAME,Reader=ascii.sextractor.SExtractor)
		else:
			all_images=image
			all_back_rms=[]
			all_ts=[]
			for image_fl in all_images:
				res,RMS_back_fl=sextract.sextractor(image_fl,CATALOG_NAME=CATALOG_NAME,c=config,RMS_back=True,SEEING_FWHM=.7,**kwargs)#chose seeing=.7 since 2.2.2 requires a seeing value, could change later
				back_rms_fl,back_fl=RMS_back_fl
				t_fl=ascii.read(CATALOG_NAME,Reader=ascii.sextractor.SExtractor)
				all_back_rms.append(back_rms_fl)
				all_ts.append(t_fl)
			back_rms=mean(all_back_rms)
			t=astropy.table.operations.vstack(all_ts)
		#####CUT OUT SATURATED & ELONGATED THINGS#####
		unsaturated=t['FLUX_MAX'].data<(t['FLUX_MAX'].data.max()*sat_cut) #chose sat_cut*100% of the max
		#the ellipticity cut now depends on the number of stars that pass!
		def rounder(min_frac_pass_el_cut=.35,el_cut_start=.1): #could change later #cut#
			el_cut=el_cut_start
			rounder_box=t['ELLIPTICITY'].data<el_cut #get objects that are sufficiently round
			while rounder_box.mean()<min_frac_pass_el_cut: #while the ellipticity cut is removing too many objects 
				el_cut+=.01 #lower the standards on how elliptical the objects have to be in order to be considered as stars
				try:
					print "Hit ellipticity cut change for ",saveas.split('/')[-1]
				except AttributeError:
					pass
				print "\tnow at %s" % (el_cut)
				rounder_box=t['ELLIPTICITY'].data<el_cut
			return rounder_box,el_cut
		round_box,el_cut=rounder()
		if round_box.sum()<200 and round_box.__len__()>300 and el_cut<.3:
			print "Hit the ellipticity changing thing where I decide there needs to be more detections so I artificially change the el_cut...might want to change if I'm just adding in background by doing this!"
			round_box,el_cut=rounder(min_frac_pass_el_cut=.5,el_cut_start=el_cut)
		cut1spots=unsaturated*round_box
		t_better=t[cut1spots]
		#####SET-UP WEIGHTING SCHEME SO THAT LARGER FLUX DETECTIONS CONTRIBUTE MORE TO THE FOM#####
		#weight height in yy about these points!
		yy=log10(t_better['FLUX_MAX'].data)
		#wt_top_range,wt_bottom_range=scoreatpercentile(yy,95),scoreatpercentile(yy,5)
		wt_top_range,wt_bottom_range=yy.max(),scoreatpercentile(yy,10)
		wt_range= wt_top_range-wt_bottom_range
		def wt_pts(x):
			wt_val_at_bottom=.1 #could change later
			wts=(1-wt_val_at_bottom)/wt_range*(x-wt_bottom_range)+wt_val_at_bottom
			wts[wts<wt_val_at_bottom]=wt_val_at_bottom
			wts[wts>1]=1
			return wts
		#####START PLOTTING#####
		if checkplots:
			f=figure(figsize=(16,10))
			ax1=f.add_subplot(2,1,1)
			ax2=f.add_subplot(2,1,2)
			#ax1.set_xlabel('different seeing guesses')
			ax1.set_ylabel('Figure of Merit\nFOM=sum the of weights of objects with |FWHM-seeing|<%s' % (dist_cut),size=10)
			ax1.set_title('"Seeing Clearly" calculation figure of merit vs. seeing')
			#old#ax1.set_title('Plot Checking Seeing calculation\nsolid line=average distance bwtn NN and the seeing guess\ndashed line=1/width of NN flux distribution (normed to fit on these axes)')
			cut2color=['b','g','r','c','m','y','orange','purple','k']
		#####GET DATA AND LISTS NEEDED IN LOOP#####
		s2n=t_better['FLUX_MAX'].data/back_rms
		FWHM_IMAGE=t_better['FWHM_IMAGE'].data*PIXSCALE
		plotspots=[]
		seeings_wted=[]
		Etype=0 #default is no error
		xd,xu=.4,2.0 #xaxis limits
		#####CALCULATE SEEING FOR DIFFERENT S2N CUT LEVELS UNTIL IT CONVERGES!#####
		s2ncut_levels=arange(10,26,3)
		for cut_i,s2ncut in enumerate(s2ncut_levels):
			cut2spots=s2n>s2ncut
			Nstars=cut2spots.sum()
			if Nstars<number_NN:
				try:
					print "%s = Nstars<number_NN = %s" % (Nstars,number_NN)
					if seeings_wted[-2]-seeing_wted<.03: #change back to .02
						Etype=1
						seeing_final_wted=seeing_wted
						break
					else:
						Etype=2
						print "cut2spots.sum()<number_NN without converging, returning nan!"
						seeing_final_wted=nan
						break
				except IndexError:
					##if this happens maybe I should take a 2nd look at the saturation and ellipticity cut?
					raise Exception("if this happens maybe I should take a 2nd look at the saturation and ellipticity cut?")
					#if cut_i==0:
					#	Etype=3
					#	print "cut2spots.sum()<number_NN on first loop, returning nan!"
					#	seeing_final_wted=nan
					#	break
					#elif cut_i==1:
					#	Etype=4
					#	print "cut2spots.sum()<number_NN on 2nd loop, returning value from 1st loop!"
					#	seeing_final_wted=seeing
					#	break
			fwhm=FWHM_IMAGE[cut2spots]
			yy_pc2=yy[cut2spots]
			foms_wted=[]
			for s in steps: 
				diffs=fwhm-s
				#this is the Apr 7th way of doing things: by picking out the closest 200 pts
				#old#negatives=ma.masked_array(diffs,diffs>0)
				#old#positives=ma.masked_array(diffs,diffs<0)
				#old#diffargs=append(negatives.argsort()[-number_NN/2:],positives.argsort()[0:number_NN/2])
				#go out a distance from the bin center and count the number of stars in there, multiplied by their weight
				cut3spots=diffs.__abs__()<dist_cut #IR= In Region
				IR_flux=yy_pc2[cut3spots]
				IR_Y_wts=wt_pts(IR_flux)
				IR_absdiffs=diffs.__abs__()[cut3spots]
				IR_X_wts=1-IR_absdiffs/dist_cut
				IR_wts=IR_X_wts*IR_Y_wts
				IR_fom_wted=(IR_wts).sum() #minmax
				foms_wted.append(IR_fom_wted)
			foms_wted=asarray(foms_wted)
			#get seeing_wted for this s2n iteration from fom_wted min
			seebin_wted=foms_wted.argmax()#tmp #minmax
			seeing_wted=steps[seebin_wted]
			seeings_wted.append(seeing_wted)
			#handle plotting
			if checkplots:
				#lets get the spots for plotting purposes
				diffs=fwhm-seeing_wted
				cut3spots=diffs.__abs__()<dist_cut #IR= In Region
				finalspots=cattools.SpotCutter([cut1spots,cut2spots,cut3spots])
				plotspots.append(finalspots)
				#lets plot the stuff on the top axis
				ax1.plot(steps,foms_wted,cut2color[cut_i],label='SNR>%s' % (s2ncut,))
				ax1.legend();ax1.set_xlim(xd,xu)
			#handle convergence and asigning final measured seeing value
			if cut_i>0:
				#fix: need to make convergence a little more rigorous
				#if converged get final seeing from seeings_wted
				if seeings_wted[-2]==seeing_wted:
					seeing_final_wted=seeing_wted
					#print "would have final seeing after %s loops: SEEING=%s" % (cut_i,seeing)
				elif cut_i==5 and abs(seeings_wted[-2]-seeing_wted)<.02:
					try:seeing_final_wted
					except NameError:
						seeing_final_wted=.5*(seeings_wted[-2]+seeing_wted)
				else:
					try:seeing_final_wted
					except NameError:
						seeing_final_wted=nan
						Etype=6
			###elif cut_i>=5: #runs at end of s2ncut loop!
		#else: this only runs if you don't hit a break, but I want it to run every time!
		try:
			maybe_missed_stars=fwhm<(seeing_final_wted-dist_cut)
			num_mms= maybe_missed_stars.sum()
			frac_mms= maybe_missed_stars.mean()
			localmaxs_wted=signal.argrelmax(foms_wted)[0] #minmax
			vals_at_localmaxs=foms_wted[localmaxs_wted]
			num_minima=len(localmaxs_wted)
			#ismax=vals_at_localmaxs==foms_wted.max()
			#aftermax=logical_not(ismax.cumsum())
			#vals_aftermax=vals_at_localmaxs[aftermax]
			#inds_aftermax=localmaxs_wted[aftermax]
			ss=list(steps);final_ind=ss.index(seeing_final_wted)
			b4max=localmaxs_wted<final_ind
			vals_b4max=vals_at_localmaxs[b4max]
			inds_b4max=localmaxs_wted[b4max]
			#what if I tried to make this a little better! I'll choose the biggest peak, then see if there are others
			fom1=vals_at_localmaxs.max()
			peaks_high_enough=vals_b4max>fom1*.51
			Ncandidates= peaks_high_enough.sum()
			#here I pick out the LARGEST peak b4 the chosen peak. 
			ind_peak_b4max=vals_b4max.argmax()
			seeing2=steps[inds_b4max[ind_peak_b4max]]
			fom2=vals_b4max.max()
			if Ncandidates>1:
				#it picks out the FIRST peak that passes the cut and is also within 80% of the 2nd peak
				fomcut=max([fom2*.8,fom1*.51])
				peaks_high_enough=vals_b4max>fomcut
				ind_peak_b4max= peaks_high_enough.argmax()
				seeing2=steps[inds_b4max[ind_peak_b4max]]
				fom2=vals_b4max[ind_peak_b4max]
				saveas+="-else-not2ndpeak"
			#b4-was-working-fine#fom1=vals_at_localmaxs.max()
			ratio=fom2/fom1
			ind2=inds_b4max[vals_b4max.argmax()]
			ind1=localmaxs_wted[vals_at_localmaxs.argmax()]
			elseinfo=(num_mms,frac_mms,ratio,seeing2,seeing_wted)
			seeoff=seeing_wted-seeing2
			#if all of these conditions are true, then take the first peak instead of the highest peak!
			if (seeoff<.28)*(frac_mms>.1)*(num_mms>39)*(ratio>.51): #maybe r=.4, .45, or .5 instead
				seeing_final_wted=seeing2
				print "maybe_missed_stars.sum() =",maybe_missed_stars.sum()
				print "maybe_missed_stars.mean()=",maybe_missed_stars.mean()
				saveas+="-else-rpt51"
		except ValueError:
			elseinfo=(nan,nan,nan,nan,nan)
		#END s2n cut loop
		namespace.update(locals())
		#tmp#os.system('rm '+CATALOG_NAME)
		try:
			if checkplots:
				t['FWHM_IMAGE']*=PIXSCALE
				ax2=BartStar.ShowStars(t,subsample_bools=tuple([cut1spots]+plotspots),axes=('FWHM_IMAGE','FLUX_MAX'),ax=ax2,subsample_name='ellipticity<%s & flux<%s*max(flux) & w/in %s of bin center' % (el_cut,sat_cut,dist_cut))
				ax2.set_xlim(xd,xu)
				yu2,yd2=ax2.get_ylim()
				ax2.plot([seeing_final_wted,seeing_final_wted],[yu2,yd2],'k--',label='SC wted')
				try:
					head_see=pyfits.open(image)[0].header['SEEING']
					ax2.plot([head_see,head_see],[yu2,yd2],'purple',alpha=.5,label='Header See')
				except:
					print "HEADER SEEING WASN'T THERE!"
					pass
				ax2.plot([xd,xu],[wt_bottom_range,wt_bottom_range],'r',ls=":",label='range')
				ax2.plot([xd,xu],[wt_top_range,wt_top_range],'r',ls=":")
				yu1,yd1=ax1.get_ylim()
				ax1.plot([seeing_final_wted,seeing_final_wted],[yu1,yd1],'k--')
				ax2.text(xd+.03*(xu-xd),yd2+.1*(yu2-yd2),'seeings_wted='+(len(seeings_wted)*'%.2f,' % tuple(seeings_wted))[:-1])
				ax2.legend()
				if saveas:
					if '/' not in saveas: saveas=PLOTDIR+saveas
					f.savefig(saveas)
			if Etype>0:
				errfl=open('/u/ki/awright/InstallingSoftware/pythons/sextractimtools/seeing_clearly_errors.log','a+')
				#errfl=open('/u/ki/awright/InstallingSoftware/pythons/sextractimtools/seeing_clearly_errors-ellcutpt1.log','a+')
				errfl.write('\n#################################################################\n')
				for varname,varval in zip(['image','Etype','cut_i','seeings_wted','el_cut','Nstars','round.mean()','unsaturated.mean()','round.sum()','unsaturated.sum()'],[image,Etype,cut_i,seeings_wted,el_cut,Nstars,round_box.mean(),unsaturated.mean(),round_box.sum(),unsaturated.sum()]):
					errfl.write('%17s = ' % (varname,) + str(varval)+ '\n')
				errfl.write('#################################################################\n')
				errfl.flush()
				errfl.close()
			namespace.update(locals())
			try:
				return seeing_final_wted, array(all_back_rms)
			except NameError:
				return seeing_final_wted,back_rms
			#return seeing_final_wted,seeings_wted,elseinfo
		except NameError:
			#changed things so that convergence should be easier, so if we hit this error it's bad
			print "changed things so that convergence should be easier, so if we hit this error it's bad"
			namespace.update(locals())
			raise
			print "Finished without converging, returning nan!"
			Etype=7
			errfl=open('/u/ki/awright/InstallingSoftware/pythons/sextractimtools/seeing_clearly_errors.log','a+')
			#errfl=open('/u/ki/awright/InstallingSoftware/pythons/sextractimtools/seeing_clearly_errors-ellcutpt1.log','a+')
			errfl.write('\n#################################################################\n')
			for varname,varval in zip(['image','Etype','cut_i','seeings_wted','el_cut','Nstars','round.mean()','unsaturated.mean()','round.sum()','unsaturated.sum()'],[image,Etype,cut_i,seeings_wted,el_cut,Nstars,round_box.mean(),unsaturated.mean(),round_box.sum(),unsaturated.sum()]):
				errfl.write('%17s = ' % (varname,) + str(varval)+ '\n')
			errfl.write('#################################################################\n')
			errfl.flush()
			#tmp: I'm not doing anything here because this hasn't happened yet. I'll cross that bridge later if I come to it
			try:
				return nan,all_back_rms
			except NameError:
				return nan,back_rms
	except:
		namespace.update(locals())
		raise

def seeing_clearly(image,**kwargs):
	'''Take input image, which could be one chip or a series of 10 chips and return the seeing value of that image.
	(1) run the sextractor function to make a catalog with the parameters I'll need to identify stars
	(2) Weight detections by how likely they are to be stars
	(3) Step along the FWHM axis of the MAG, FWHM plane and find at which point the weighted sum of the neighboring detections is largest. This point is the seeing of the image.'''
	#####DETERMINE CUT PARAMS#####
	try:
		header=pyfits.open(image)[0].header
	except IOError:
		header=pyfits.open(image[0])[0].header
	FILTER=header['FILTER']
	number_NN=155 #chose this number of nearest neighbors to consider, could change later #cut#
	dist_cut=.04 #could change later #cut#
	sat_cut=.87 #could change later #cut#
	#if 'DATACONF' in os.environ and 'PIXSCALE' in os.environ and 'SATURATION' in os.environ:
	#	DATACONF=os.environ['DATACONF']
	#	PIXSCALE=float(os.environ['PIXSCALE'])	
	#	SATURATION=os.environ['SATURATION']
	#else:
	#	raise Exception("YOU MUST RUN THIS COMMAND FIRST: . /u/ki/awright/wtgpipeline/SUBARU.ini")
	if 'PIXSCALE' in os.environ:
		PIXSCALE=float(os.environ['PIXSCALE'])	
	else:
		PIXSCALE=.202 #default to SUBARU 10_3 config
	config=SEXDIR+'seeing_clearly.sex.config'
	CATALOG_NAME='/tmp/seeing_clearly-%s.cat' % (imagetools.id_generator(6),)
	#set default sextractor parameters
	if 'DETECT_MINAREA' not in kwargs: kwargs['DETECT_MINAREA']=2
	if 'DETECT_THRESH' not in kwargs:
		#if FILTER=="W-C-RC":
		#	kwargs['DETECT_THRESH']=10.0
		#	s2n_thresh=10.0
		#elif FILTER=="W-J-B":
		#	kwargs['DETECT_THRESH']=7.0
		#	s2n_thresh=7.0
		kwargs['DETECT_THRESH']=10.0
		s2n_thresh=10.0
	else:
		s2n_thresh=kwargs['DETECT_THRESH']
	if 'ANALYSIS_THRESH' not in kwargs:kwargs['ANALYSIS_THRESH']=kwargs['DETECT_THRESH']
	#####RUN SEXTRACTOR#####
	#2.2.2#sextractor(image,CATALOG_NAME=CATALOG_NAME,c=config,**kwargs)
	if type(image)==string_ or type(image)==str:
		res,RMS_back=sextract.sextractor(image,CATALOG_NAME=CATALOG_NAME,c=config,RMS_back=True,SEEING_FWHM=.7,**kwargs)#chose seeing=.7 since 2.2.2 requires a seeing value, could change later
		back_rms,back=RMS_back
		t=ascii.read(CATALOG_NAME,Reader=ascii.sextractor.SExtractor)
	else:
		all_images=image
		all_back_rms=[]
		all_ts=[]
		for image_fl in all_images:
			res,RMS_back_fl=sextract.sextractor(image_fl,CATALOG_NAME=CATALOG_NAME,c=config,RMS_back=True,SEEING_FWHM=.7,**kwargs)#chose seeing=.7 since 2.2.2 requires a seeing value, could change later
			back_rms_fl,back_fl=RMS_back_fl
			t_fl=ascii.read(CATALOG_NAME,Reader=ascii.sextractor.SExtractor)
			all_back_rms.append(back_rms_fl)
			all_ts.append(t_fl)
			t_fl.close()
		back_rms=mean(all_back_rms)
		t=astropy.table.table.operations.vstack(all_ts)
	#####CUT OUT SATURATED & ELONGATED THINGS#####
	unsaturated=t['FLUX_MAX'].data<t['FLUX_MAX'].data.max()*sat_cut #chose sat_cut*100% of the max
	#the ellipticity cut now depends on the number of stars that pass!
	def rounder(min_frac_pass_el_cut=.35,el_cut_start=.1): #could change later #cut#
		el_cut=el_cut_start
		rounder_box=t['ELLIPTICITY'].data<el_cut #get objects that are sufficiently round
		while rounder_box.mean()<min_frac_pass_el_cut: #while the ellipticity cut is removing too many objects 
			el_cut+=.01 #lower the standards on how elliptical the objects have to be in order to be considered as stars
			rounder_box=t['ELLIPTICITY'].data<el_cut
		return rounder_box,el_cut
	round_box,el_cut=rounder()
	if round_box.sum()<200 and round_box.__len__()>300 and el_cut<.3:
		print "Hit the ellipticity changing thing where I decide there needs to be more detections so I artificially change the el_cut...might want to change if I'm just adding in background by doing this!"
		round_box,el_cut=rounder(min_frac_pass_el_cut=.5,el_cut_start=el_cut)
	cut1spots=unsaturated*round_box
	t_better=t[cut1spots]
	#####SET-UP WEIGHTING SCHEME SO THAT LARGER FLUX DETECTIONS CONTRIBUTE MORE TO THE FOM#####
	#weight height in yy about these points!
	yy=log10(t_better['FLUX_MAX'].data)
	#wt_top_range,wt_bottom_range=scoreatpercentile(yy,95),scoreatpercentile(yy,5)
	wt_top_range,wt_bottom_range=yy.max(),scoreatpercentile(yy,10)
	wt_range= wt_top_range-wt_bottom_range
	def wt_pts(x):
		wt_val_at_bottom=.1 #could change later
		wts=(1-wt_val_at_bottom)/wt_range*(x-wt_bottom_range)+wt_val_at_bottom
		wts[wts<wt_val_at_bottom]=wt_val_at_bottom
		wts[wts>1]=1
		return wts
	#####GET DATA AND LISTS NEEDED IN LOOP#####
	s2n=t_better['FLUX_MAX'].data/back_rms
	FWHM_IMAGE=t_better['FWHM_IMAGE'].data*PIXSCALE
	seeings_wted=[]
	Etype=0 #default is no error
	#####CALCULATE SEEING FOR DIFFERENT S2N CUT LEVELS UNTIL IT CONVERGES!#####
	s2ncut_levels=arange(10,26,3)
	for cut_i,s2ncut in enumerate(s2ncut_levels):
		cut2spots=s2n>s2ncut
		Nstars=cut2spots.sum()
		if Nstars<number_NN:
			try:
				print "%s = Nstars<number_NN = %s" % (Nstars,number_NN)
				if seeings_wted[-2]-seeing_wted<.03: #change back to .02
					Etype=1
					seeing_final_wted=seeing_wted
					break
				else:
					Etype=2
					print "cut2spots.sum()<number_NN without converging, returning nan!"
					seeing_final_wted=nan
					break
			except IndexError:
				##if this happens maybe I should take a 2nd look at the saturation and ellipticity cut?
				raise Exception("if this happens maybe I should take a 2nd look at the saturation and ellipticity cut?")
		fwhm=FWHM_IMAGE[cut2spots]
		yy_pc2=yy[cut2spots]
		foms_wted=[]
		for s in steps: 
			diffs=fwhm-s
			#this is the Apr 7th way of doing things: by picking out the closest 200 pts
			#go out a distance from the bin center and count the number of stars in there, multiplied by their weight
			cut3spots=diffs.__abs__()<dist_cut #IR= In Region
			IR_flux=yy_pc2[cut3spots]
			IR_Y_wts=wt_pts(IR_flux)
			IR_absdiffs=diffs.__abs__()[cut3spots]
			IR_X_wts=1-IR_absdiffs/dist_cut
			IR_wts=IR_X_wts*IR_Y_wts
			IR_fom_wted=(IR_wts).sum()
			foms_wted.append(IR_fom_wted)
		foms_wted=asarray(foms_wted)
		#get seeing_wted for this s2n iteration from fom_wted min
		seebin_wted=foms_wted.argmax()
		seeing_wted=steps[seebin_wted]
		seeings_wted.append(seeing_wted)
		#handle convergence and asigning final measured seeing value
		if cut_i>0:
			#if converged get final seeing from seeings_wted
			if seeings_wted[-2]==seeing_wted:
				seeing_final_wted=seeing_wted
				#print "would have final seeing after %s loops: SEEING=%s" % (cut_i,seeing)
			elif cut_i==5 and abs(seeings_wted[-2]-seeing_wted)<.02:
				try:seeing_final_wted
				except NameError:
					seeing_final_wted=.5*(seeings_wted[-2]+seeing_wted)
			else:
				try:seeing_final_wted
				except NameError:
					seeing_final_wted=nan
					Etype=6
	#else: this only runs if you don't hit a break, but I want it to run every time!
	try:
		maybe_missed_stars=fwhm<(seeing_final_wted-dist_cut)
		num_mms= maybe_missed_stars.sum()
		frac_mms= maybe_missed_stars.mean()
		localmaxs_wted=signal.argrelmax(foms_wted)[0] #minmax
		vals_at_localmaxs=foms_wted[localmaxs_wted]
		num_minima=len(localmaxs_wted)
		#ismax=vals_at_localmaxs==foms_wted.max()
		#aftermax=logical_not(ismax.cumsum())
		#vals_aftermax=vals_at_localmaxs[aftermax]
		#inds_aftermax=localmaxs_wted[aftermax]
		ss=list(steps);final_ind=ss.index(seeing_final_wted)
		b4max=localmaxs_wted<final_ind
		vals_b4max=vals_at_localmaxs[b4max]
		inds_b4max=localmaxs_wted[b4max]
		#what if I tried to make this a little better! I'll choose the biggest peak, then see if there are others
		fom1=vals_at_localmaxs.max()
		peaks_high_enough=vals_b4max>fom1*.51
		Ncandidates= peaks_high_enough.sum()
		#here I pick out the LARGEST peak b4 the chosen peak. 
		ind_peak_b4max=vals_b4max.argmax()
		seeing2=steps[inds_b4max[ind_peak_b4max]]
		fom2=vals_b4max.max()
		if Ncandidates>1:
			#it picks out the FIRST peak that passes the cut and is also within 80% of the 2nd peak
			fomcut=max([fom2*.8,fom1*.51])
			peaks_high_enough=vals_b4max>fomcut
			ind_peak_b4max= peaks_high_enough.argmax()
			seeing2=steps[inds_b4max[ind_peak_b4max]]
			fom2=vals_b4max[ind_peak_b4max]
		#b4-was-working-fine#fom1=vals_at_localmaxs.max()
		ratio=fom2/fom1
		ind2=inds_b4max[vals_b4max.argmax()]
		ind1=localmaxs_wted[vals_at_localmaxs.argmax()]
		seeoff=seeing_wted-seeing2
		#if all of these conditions are true, then take the first peak instead of the highest peak!
		if (seeoff<.28)*(frac_mms>.1)*(num_mms>39)*(ratio>.51):
			seeing_final_wted=seeing2
	except ValueError:
		pass
	#END s2n cut loop
	#namespace.update(locals())
	os.system('rm '+CATALOG_NAME)
	try:
		if Etype>0:
			errfl=open('/u/ki/awright/InstallingSoftware/pythons/sextractimtools/seeing_clearly_errors.log','a+')
			errfl.write('\n#################################################################\n')
			for varname,varval in zip(['image','Etype','cut_i','seeings_wted','el_cut','Nstars','round.mean()','unsaturated.mean()','round.sum()','unsaturated.sum()'],[image,Etype,cut_i,seeings_wted,el_cut,Nstars,round_box.mean(),unsaturated.mean(),round_box.sum(),unsaturated.sum()]):
				errfl.write('%17s = ' % (varname,) + str(varval)+ '\n')
			errfl.write('#################################################################\n')
			errfl.flush()
			errfl.close()
		#namespace.update(locals())
		try:
			return seeing_final_wted, array(all_back_rms)
		except NameError:
			return seeing_final_wted,back_rms
	except NameError:
		print "changed things so that convergence should be easier, so if we hit this error it's bad"
		#namespace.update(locals())
		raise

for img_name,plot_name in zip(["/u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_gab4060-rot1/coadd.fits","/u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_gab4060-rot0/coadd.fits"],["plt_seeing_macs1226_rot1","plt_seeing_macs1226_rot0"]):
	print ' img_name=',img_name , ' plot_name=',plot_name
	print "Using SeeingClearly to get seeing for: "+img_name
	seeing,back_rms=seeing_clearly_withplot(img_name,checkplots=1,saveas=plot_name)
	print "RMS of the background in this image is: "+str(back_rms)+"\n\n SeeingClearly.seeing_clearly got (in arcseconds): Seeing="+str(seeing)
	show()

## RESULTS ##
#Hit ellipticity cut change for  plt_seeing_macs1226_rot1
#	now at 0.15
#RMS of the background in this image is: 0.0587957
#
# SeeingClearly.seeing_clearly got (in arcseconds): Seeing=0.6
# img_name= /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_gab4060-rot0/coadd.fits  plot_name= plt_seeing_macs1226_rot0
#Using SeeingClearly to get seeing for: /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_gab4060-rot0/coadd.fits
#/afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/sex_theli /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_gab4060-rot0/coadd.fits -c /u/ki/awright/InstallingSoftware/pythons/sextractimtools/seeing_clearly.sex.config -CATALOG_NAME /u/ki/awright/InstallingSoftware/pythons/sextractimtools/seeing_clearly-EWS8A1.cat -DETECT_MINAREA 2 -SEEING_FWHM 0.7 -ANALYSIS_THRESH 10.0 -DETECT_THRESH 10.0
#called string was:  /afs/slac/u/ki/anja/software/ldacpipeline-0.12.20/bin/Linux_64/sex_theli /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_gab4060-rot0/coadd.fits -c /u/ki/awright/InstallingSoftware/pythons/sextractimtools/seeing_clearly.sex.config -CATALOG_NAME /u/ki/awright/InstallingSoftware/pythons/sextractimtools/seeing_clearly-EWS8A1.cat -DETECT_MINAREA 2 -SEEING_FWHM 0.7 -ANALYSIS_THRESH 10.0 -DETECT_THRESH 10.0 > /u/ki/awright/InstallingSoftware/pythons/sextractimtools/coadd.log 2>&1
#Hit ellipticity cut change for  plt_seeing_macs1226_rot0
#	now at 0.15
#RMS of the background in this image is: 0.0528193
#
# SeeingClearly.seeing_clearly got (in arcseconds): Seeing=0.75
