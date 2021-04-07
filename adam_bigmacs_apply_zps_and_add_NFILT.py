#!/usr/bin/env python
#adam-use# put bigmacs zps in cats and headers of coadd.fits and calculate NFILT
#adam-example# ipython -i -- adam_bigmacs_apply_zps_and_add_NFILT.py -i /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.unstacked.split_apers.cat -o /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.cat -z /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.bigmacs_cleaned_offsets.list
#adam-example# ipython -i -- adam_bigmacs_apply_zps_and_add_NFILT.py -i /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.unstacked.split_apers.cat -o /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.calibrated_PureStarCalib.cat -z /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.bigmacs_cleaned_offsets-PureStarCalib.list
#adam-example# ipython -i -- adam_bigmacs_apply_zps_and_add_NFILT.py -i /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.stars.split_apers.cat -o /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.stars.calibrated_PureStarCalib.cat -z /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.bigmacs_cleaned_offsets-PureStarCalib.list
#####################

# Manually set a zeropoint for a fitid, such as from SLR

#####################

import sys, os, re,glob
sys.path.append('/u/ki/awright/quick/pythons/')
import imagetools, cattools
import header_key_add
import ldac, utilities
import astropy.io.fits as pyfits
import numpy
ns=globals()

######################

def calc_NFILT_with_numobs(catinput,filt_zp_err):
    mag_aper1_keys=filt_zp_err.keys()
    mag_aper1_sdr={} #get a system of distinct representatives (SDR)
    for mag_key in mag_aper1_keys:
        filt=mag_key[mag_key.find('W-'):]
        if mag_aper1_sdr.has_key(filt):
                mag_aper1_sdr[filt].append(mag_key)
        else:
                mag_aper1_sdr[filt]=[mag_key]

    #catinput=ldac.openObjectFile(mag_fl)
    catshape=catinput[mag_aper1_sdr.values()[0][0]].shape
    NFILT_corrected=numpy.zeros(catshape,dtype=numpy.float32)
    for filt in mag_aper1_sdr.keys():
        mag_aper1_keys_clean=mag_aper1_sdr[filt]
        observed_in_filt=numpy.zeros(catshape,dtype=bool)
	printstr=[]
        for mag_key in mag_aper1_keys_clean:
            flux_key=mag_key.replace("MAG_APER1","FLUX_APER1")
            fluxerr_key=flux_key.replace("FLUX","FLUXERR")
            ef=catinput[fluxerr_key].copy()
            observed=(ef>0.)
            observed_in_filt+=observed
            if len(mag_aper1_keys_clean)>1:
                if mag_key.find('10_3')>0:
                        mag_key_10_3=mag_key
                        observed_10_3=observed.copy()
                if mag_key.find('10_2')>0:
                        mag_key_10_2=mag_key
                        observed_10_2=observed.copy()
            	printstr+=['\t%s\t## observed: %i  (of %i). Percentage: %.1f  ## ' % (mag_key,observed.sum(),observed.__len__(),100*observed.mean())]
        NFILT_corrected+=numpy.array(observed_in_filt,dtype=numpy.float32)

        ## check how the data looks
        print '\n%s\n## observed_in_filt: %i  (of %i). Percentage: %.1f  ## ' % (filt,observed_in_filt.sum(),observed_in_filt.__len__(),100*observed_in_filt.mean())
        ## combine the different mags
        if len(mag_aper1_keys_clean)>1:
	    print '\n'.join(printstr)
            #mag_both=numpy.where(observed_10_2,catinput[mag_key_10_2],catinput[mag_key_10_3])
            #flux_both=numpy.where(observed_10_2,catinput[mag_key_10_2.replace("MAG_APER1","FLUX_APER1")],catinput[mag_key_10_3.replace("MAG_APER1","FLUX_APER1")])
            #emag_both=numpy.where(observed_10_2,catinput[mag_key_10_2.replace("MAG_APER1","MAGERR_APER1")],catinput[mag_key_10_3.replace("MAG_APER1","MAGERR_APER1")])
            #eflux_both=numpy.where(observed_10_2,catinput[mag_key_10_2.replace("MAG_APER1","FLUXERR_APER1")],catinput[mag_key_10_3.replace("MAG_APER1","FLUXERR_APER1")])

    return NFILT_corrected

######################

def getZP(zpfile):
	try:
	    zpf = open(zpfile).readlines()
	    zps = {}
	    for line in zpf:
		if line.startswith('#') or line.startswith('psf'):continue
		tokens = line.split()
		fitFilter = tokens[0]
		zpoffset = float(tokens[1])
		zperr = float(tokens[2])
		zps[fitFilter] = (zpoffset, zperr)
	    return zps
	except:
	    ns.update(locals())
	    raise

#######################

def main(flinput,flzps,flnew):
	try:

		filt_zp_err=getZP(flzps)
		catinput=ldac.openObjectFile(flinput)
		NFILT=calc_NFILT_with_numobs(catinput,filt_zp_err)
		flproto=flinput.replace(".cat",".proto-tmp.cat")

		mag_aper1_keys=filt_zp_err.keys()
		other_keys_del=[] #this will get built up in the loop
		ncs=[]
		zp_tab_cols=[]
		for mag_key in mag_aper1_keys:
			zp,err_zp=filt_zp_err[mag_key]

			col_zp=pyfits.Column(name='ZP_'+mag_key, format='E', array = numpy.array([zp]))
			col_err_zp=pyfits.Column(name='ZPERR_'+mag_key, format='E', array = numpy.array([err_zp]))
			zp_tab_cols.append( col_zp )
			zp_tab_cols.append( col_err_zp )
			## add zp,err_zp to image headers and get background/background_rms for this filter
			filt=mag_key[mag_key.find('W-'):]
			directory='/'.join([os.environ['SUBARUDIR'],os.environ['cluster'],filt,'SCIENCE','coadd_'+os.environ['cluster']+'_*'])
			dirs=glob.glob(directory)
			for dir in dirs:
				if 'OLD' in dir:
					continue
				if not os.path.isfile(dir+"/coadd.fits"):
					raise Exception("there is no file: "+dir+"/coadd.fits")
				header_key_add.add_key_val(dir+"/coadd.fits",['ZP_BM','ZPERR_BM'],[zp,err_zp])

			##adam-old get background_rms for this filter
			##flcatcoadd='/'.join([os.environ['SUBARUDIR'],os.environ['cluster'],filt,'SCIENCE','coadd_'+os.environ['cluster']+'_all','coadd.stars.cat'])
			##catcoadd=ldac.openObjectFile(flcatcoadd,"FIELDS")
			##back_level=catcoadd["SEXBKGND"][0]
			##back_rms=catcoadd["SEXBKDEV"][0]

			## calibrate the catalog and conform to bpz input cat setup
			#adam# now that I've determined how to distinguish sextractor non-detections and non-observations, apply that here
			#adam# main  thing I'd like to do is make MAGERR/FLUXERR, where MAG_APER1-*==-99 acceptable to bpz
			#adam# My Hypthesis Confirmed by: ds9e ~/data/MACS1226+21/W-J-V/SCIENCE/coadd_MACS1226+21_all/coadd.fits & #load in ~/wtgpipeline/influx_m99_W-J-V.tsv

			## calibrate and fix MAG_APER1- and FLUX_APER1-
			flux_key=mag_key.replace("MAG_APER1","FLUX_APER1")
			magerr_key=mag_key.replace("MAG","MAGERR")
			fluxerr_key=flux_key.replace("FLUX","FLUXERR")

			m=catinput[mag_key].copy()
			if not m.ndim==1: raise Exception("this column doesn't seem to need to be split (shape is "+str(inmag.shape)+"), but it has APER- in the name. Thats weird and contradictory")
			f=catinput[flux_key].copy()
			em=catinput[magerr_key].copy()
			ef=catinput[fluxerr_key].copy()
			#mask=f<=0 ## m==-99 ## (mask==nondetected+nonobserved)=True
			detected=(f>0.)
			nondetected=(f<=0.)*(ef>0) #Flux <=0, meaningful phot. error
			nonobserved=(ef<=0.) #Negative errors

			frac_zp=10**(-.4*zp)
			flux_newcol=f*frac_zp #((f==-99)==nonobserved).all()=True
			flux_newcol[nonobserved]=-99
			#adam-correct# I did think, briefly, that this was a mistake, but it's correct, the frac_zp is a multiplicative factor, so it get's multiplied to the error as well (that's not the case with the mags, because for them it's an additive factor, hence not affecting the uncertainty)
			eflux_newcol=numpy.where(nonobserved,ef,ef*frac_zp)

			# using mag=-2.5*numpy.log10(flux) after calibrating flux even though m+zp gives the same thing, because I should just use fluxes always since magnitudes cannot be trusted!
			mag_newcol=-2.5*numpy.log10(flux_newcol) #=m+zp
			# for sextractor, both nonobs and nondet are -99 (for bpz unobs=-99 and undet=+99)
			mag_newcol[nonobserved+nondetected]=-99

			f_bpz=flux_newcol.copy()
			ef_bpz=eflux_newcol.copy()
			# previously I'd had f_bpz[nonobserved+nondetected]=0, and that was wrong!
			f_bpz[nonobserved]=0
			ef_bpz[nonobserved]=0
			#m_bpz=mag_newcol.copy()
			#em_bpz=em.copy()
			#m_bpz[nonobserved+nondetected]=0
			#em_bpz[nonobserved]=0

			#adam-new# do this check on the calculations to put my mind at ease
			m_check=m.copy()+zp
			m_check[nonobserved+nondetected]=-99
			close_enough=numpy.array([imagetools.isclose(a,b,abs_tol=1e-5) for a,b in zip(mag_newcol,m_check)])
			assert(close_enough.all())

			#adam-old# Calculate NFILT
			#detected=numpy.logical_not(nondetected+nonobserved)
			#if len(ncs)==0: NFILT=numpy.zeros(detected.shape,dtype=numpy.float32)
			#NFILT+=numpy.array(detected,dtype=numpy.float32)

			## check how the data looks
			print '\n%s\n## detected: %i  ##  nondetected: %i  ## nonobserved: %i  ## ' % (filt,detected.sum(),nondetected.sum(),nonobserved.sum())
			print mag_key,' min,mean,max : ',mag_newcol[detected].min(),mag_newcol[detected].mean(),mag_newcol[detected].max()
			print flux_key,' min,mean,max : ',flux_newcol[detected].min(),flux_newcol[detected].mean(),flux_newcol[detected].max()
			print magerr_key,' min,mean,max : ',em[detected].min(),em[detected].mean(),em[detected].max()
			print fluxerr_key,' min,mean,max : ',ef[detected].min(),ef[detected].mean(),ef[detected].max()
			ncs.append(pyfits.Column(name=mag_key,format='1E',array=mag_newcol))
			ncs.append(pyfits.Column(name=flux_key,format='1E',array=flux_newcol))
			ncs.append(pyfits.Column(name=fluxerr_key,format='1E',array=eflux_newcol))
			ncs.append(pyfits.Column(name=flux_key+"_bpz_inputs",format='1E',array=f_bpz))
			ncs.append(pyfits.Column(name=fluxerr_key+"_bpz_inputs",format='1E',array=ef_bpz))
			## no longer needed: fluxerr_newcol magerr_newcol
			other_keys_del+=[ mag_key.replace("APER1-","APER-"), flux_key.replace("APER1-","APER-"), magerr_key.replace("APER1-","APER-"), fluxerr_key.replace("APER1-","APER-")]

			### adam-old
			##inmag=catinput[mag_key].copy()
			##influx=catinput[flux_key].copy()
			##magerr_newcol=catinput[magerr_key].copy()
			##fluxerr_newcol=catinput[fluxerr_key].copy()
			##mask=inmag==-99
			##mag_newcol=inmag+zp
			##non_obs=influx==-99
			##non_det=(influx<0)*logical_not(non_obs)
			##mag_newcol[non_det]=99
			##mag_newcol[non_obs]=-99
			##flux_newcol=10.0**(-.4*mag_newcol)# make FLUX_APER1- agree with MAG_APER1-
			##flux_newcol[mask]=0 # all(mask==logical_or(non_det,non_obs)) = True
			### calibrate and fix FLUXERR_APER1- and MAGERR_APER1-
			##fluxerr_newcol[non_det]=back_rms*10**(-.4*zp) #since flux is background subtracted, 1sigma det lim = back_rms
			##magerr_newcol[non_det]=-2.5*log10(back_rms)+zp #since flux is background subtracted, 1sigma det mag lim = -2.5*log10(back_rms)
			##fluxerr_newcol[non_obs]=0
			##magerr_newcol[non_obs]=0
			##ncs.append(pyfits.Column(name=magerr_key,format='1E',array=magerr_newcol))
			##ncs.append(pyfits.Column(name=fluxerr_key,format='1E',array=fluxerr_newcol))
			### print out some of the details here:
			##unmasked=logical_not(mask)
			##print "\n"+filt+" background RMS=",back_rms," mag of 1sigma det lim =",-2.5*log10(back_rms)+zp

		## now add NFILT to ncs and save flproto
		ncs.append(pyfits.Column(name='NFILT', format = '1J', array = numpy.array(NFILT,dtype=numpy.int32)))
		hdu = pyfits.PrimaryHDU()
		hduSTDTAB = pyfits.BinTableHDU.from_columns(ncs)
		hduZPSTAB = pyfits.BinTableHDU.from_columns(zp_tab_cols)
		hdulist = pyfits.HDUList([hdu,hduSTDTAB,hduZPSTAB])
		hdulist[1].header['EXTNAME']='OBJECTS'
		hdulist[2].header['EXTNAME']='BIGMACS'
		print "\n...temporarily saving to flproto=",flproto
		hdulist.writeto(flproto,overwrite=True)

		## make a version of flinput with the keys in flproto deleted so that it doesn't give an error in the ldacjoinkey command
		## ALSO remove MAG_APER-/FLUX_APER-/MAGERR_APER-/FLUXERR_APER- so I don't confuse it for MAG_APER1-/... later
		keys_del=[col.name for col in ncs if not col.name.endswith("_bpz_inputs") and not col.name=="NFILT"]+other_keys_del
		flinput2cp=flinput.replace(".cat",".input-tmp.cat")
		ooo=os.system("ldacdelkey -i "+flinput+" -o "+flinput2cp+" -k "+' '.join(keys_del))
		if ooo!=0: raise Exception("the line os.system(ldacdelkey...) failed")

		flnew2cp=flnew.replace(".cat",".new-tmp.cat")
		keys_add=[col.name for col in ncs]
		print "\nnow running: ldacjoinkey -p "+flproto+" -i "+flinput2cp+" -o "+flnew2cp+" -t OBJECTS -k "+' '.join(keys_add)
		ooo=os.system("ldacjoinkey -p "+flproto+" -i "+flinput2cp+" -o "+flnew2cp+" -t OBJECTS -k "+' '.join(keys_add))
		if ooo!=0: raise Exception("the line os.system("+"ldacjoinkey -p "+flproto+" -i "+flinput2cp+" -o "+flnew2cp+" -t OBJECTS -k "+" ".join(keys_add)+") failed")

		## OK, now make the zps table and add it to the cat. example from photocalibrate_cat.py below
		#adam-new# new table with ZPs
                str_addtab="ldacaddtab -i "+flnew2cp+" -o "+flnew+" -p "+flproto+" -t BIGMACS"
		print "\nnow running: "+str_addtab
		ooo=os.system(str_addtab)
		if ooo!=0: raise Exception("the line os.system("+str_addtab+") failed")
		
		print "\nsaving to "+flnew
		os.system("rm -f "+flproto)
		os.system("rm -f "+flinput2cp)
		os.system("rm -f "+flnew2cp)

		ns.update(locals())
		return
		
	except:
		ns.update(locals())
		raise

#######################

if __name__ == '__main__':
	import optparse
	parser = optparse.OptionParser()
	#example:
	#    parser.add_option('-3', '--threesec',
	#                  dest='threesec',
	#                  action='store_true',
	#                  help='Treat as a 3second exposure',
	#                  default=False)
	#parser.add_option('-c', '--cluster', dest='cluster', help='Cluster name')
	#parser.add_option('-f', '--filtername', dest='filter', help='Filter to calibrate')
	#parser.add_option('-m', '--maindir', dest='maindir', help='subaru directory')
	parser.add_option('-i', '--inputcat',
	                  dest='input_fl',
	                  help='input catalog with vector ldac objects.')
	parser.add_option('-o', '--outputcat',
	                  dest='output_fl',
	                  help='output catalog name. ')
	parser.add_option('-z', '--zeropoints',
	                  dest='zeropoints_fl',
	                  help='cleaned zeropoints list name. ')

	from adam_quicktools_ArgCleaner import ArgCleaner
	argv=ArgCleaner()
	options, args = parser.parse_args(argv)
	#if options.cluster is None:
	#    parser.error('Need to specify cluster!')

	print "Called with:"
	print options

	if options.input_fl is None:
	    parser.error('Need to specify input catalog file!')
	if options.output_fl is None:
	    parser.error('Need to specify output catalog file!')
	if options.zeropoints_fl is None:
	    parser.error('Need to specify zeropoints catalog file!')
	main(flinput=options.input_fl,flzps=options.zeropoints_fl,flnew=options.output_fl)
