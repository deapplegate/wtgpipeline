#!/usr/bin/env python
#adam-use# put bigmacs zps in cats and headers of coadd.fits
#adam-example# ipython -i -- adam_bigmacs-apply_zps.py -i /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.unstacked.split_apers.cat -o /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.cat -z /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.bigmacs_cleaned_offsets.list
#####################

# Manually set a zeropoint for a fitid, such as from SLR

#####################

import sys, os, re,glob
from numpy import *
sys.path.append('~/InstallingSoftware/pythons/')
import header_key_add
import ldac, utilities
import astropy.io.fits as pyfits
ns=globals()
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
		flproto=flinput.replace(".cat",".proto-tmp.cat")

		mag_aper1_keys=filt_zp_err.keys()
		all_aper1_keys=[] #this will get built up in the loop
		ncs=[]
		for mag_key in mag_aper1_keys:
			#print ' mag_key=',mag_key
			zp,err=filt_zp_err[mag_key]

			## add zp,err to image headers and get background/background_rms for this filter
			filt=mag_key[mag_key.find('W-'):]
			directory='/'.join([os.environ['SUBARUDIR'],os.environ['cluster'],filt,'SCIENCE','coadd_*'])
			dirs=glob.glob(directory)
			for dir in dirs:
				if not os.path.isfile(dir+"/coadd.fits"):
					raise Exception("there is no file: "+dir+"/coadd.fits")
				header_key_add.add_key_val(dir+"/coadd.fits",['ZP_BM','ZPERR_BM'],[zp,err])

			## get background_rms for this filter
			flcatcoadd='/'.join([os.environ['SUBARUDIR'],os.environ['cluster'],filt,'SCIENCE','coadd_'+os.environ['cluster']+'_all','coadd.stars.cat'])
			catcoadd=ldac.openObjectFile(flcatcoadd,"FIELDS")
			#back_level=catcoadd["SEXBKGND"][0]
			back_rms=catcoadd["SEXBKDEV"][0]

			## calibrate the catalog and conform to bpz input cat setup
			#adam# now that I've determined how to distinguish sextractor non-detections and non-observations, apply that here
			#adam# main  thing I'd like to do is make MAGERR/FLUXERR, where MAG_APER1-*==-99 acceptable to bpz
			#adam# My Hypthesis Confirmed by: ds9e ~/data/MACS1226+21/W-J-V/SCIENCE/coadd_MACS1226+21_all/coadd.fits & #load in ~/wtgpipeline/influx_m99_W-J-V.tsv

			## calibrate and fix MAG_APER1- and FLUX_APER1-
			inmag=catinput[mag_key]
			if not inmag.ndim==1:
				raise Exception("this column doesn't seem to need to be split (shape is "+str(inmag.shape)+"), but it has APER- in the name. Thats weird and contradictory")
			flux_key=mag_key.replace("MAG_APER1","FLUX_APER1")
			influx=catinput[flux_key]
			mask=inmag==-99
			mag_newcol=inmag+zp
			non_obs=influx==-99
			non_det=(influx<0)*logical_not(non_obs)
			mag_newcol[non_det]=99
			mag_newcol[non_obs]=-99
			#adam-old# mag_newcol[mask]=99 #treat it as non-DETECTIONS for now
			flux_newcol=10.0**(-.4*mag_newcol)# make FLUX_APER1- agree with MAG_APER1-
			flux_newcol[mask]=0 # all(mask==logical_or(non_det,non_obs)) = True
			ncs.append(pyfits.Column(name=mag_key,format='1E',array=mag_newcol))
			ncs.append(pyfits.Column(name=flux_key,format='1E',array=flux_newcol))

			## calibrate and fix FLUXERR_APER1- and MAGERR_APER1-
			magerr_key=mag_key.replace("MAG","MAGERR")
			magerr_newcol=catinput[magerr_key].copy()
			fluxerr_key=flux_key.replace("FLUX","FLUXERR")
			fluxerr_newcol=catinput[fluxerr_key].copy()
			fluxerr_newcol[non_det]=back_rms*10**(-.4*zp) #since flux is background subtracted, 1sigma det lim = back_rms
			magerr_newcol[non_det]=-2.5*log10(back_rms)+zp #since flux is background subtracted, 1sigma det mag lim = -2.5*log10(back_rms)
			fluxerr_newcol[non_obs]=0
			magerr_newcol[non_obs]=0
			ncs.append(pyfits.Column(name=magerr_key,format='1E',array=magerr_newcol))
			ncs.append(pyfits.Column(name=fluxerr_key,format='1E',array=fluxerr_newcol))

			## print out some of the details here:
			unmasked=logical_not(mask)
			print "\n"+filt+" background RMS=",back_rms," mag of 1sigma det lim =",-2.5*log10(back_rms)+zp
			print mag_key,' min,mean,max : ',mag_newcol[unmasked].min(),mag_newcol[unmasked].mean(),mag_newcol[unmasked].max()
			print flux_key,' min,mean,max : ',flux_newcol[unmasked].min(),flux_newcol[unmasked].mean(),flux_newcol[unmasked].max()
			print magerr_key,' min,mean,max : ',magerr_newcol[unmasked].min(),magerr_newcol[unmasked].mean(),magerr_newcol[unmasked].max()
			print fluxerr_key,' min,mean,max : ',fluxerr_newcol[unmasked].min(),fluxerr_newcol[unmasked].mean(),fluxerr_newcol[unmasked].max()
			all_aper1_keys+=[ mag_key, flux_key, magerr_key, fluxerr_key]

		print "\nsaving to "+flnew
		hdu = pyfits.PrimaryHDU()
		hduSTDTAB = pyfits.BinTableHDU.from_columns(ncs)
		hdulist = pyfits.HDUList([hdu])
		hdulist.append(hduSTDTAB)
		hdulist[1].header['EXTNAME']='OBJECTS'
		print "\nflproto=",flproto
		hdulist.writeto(flproto,overwrite=True)


		## make a version of flinput with the all_aper1_keys deleted so that it doesn't give an error in the ldacjoinkey command
		fl2cp=flinput.replace(".cat",".input-tmp.cat")
		ooo=os.system("ldacdelkey -i "+flinput+" -o "+fl2cp+" -k "+' '.join(all_aper1_keys))
		if ooo!=0: raise Exception("the line os.system(ldacdelkey...) failed")
		
		print "\nnow running: ldacjoinkey -p "+flproto+" -i "+fl2cp+" -o "+flnew+" -t OBJECTS -k "+' '.join(all_aper1_keys)
		ooo=os.system("ldacjoinkey -p "+flproto+" -i "+fl2cp+" -o "+flnew+" -t OBJECTS -k "+' '.join(all_aper1_keys))
		if ooo!=0: raise Exception("the line os.system("+"ldacjoinkey -p "+flproto+" -i "+fl2cp+" -o "+flnew+" -t OBJECTS -k "+" ".join(all_aper1_keys)+") failed")
		
		os.system("rm -f "+flproto)
		os.system("rm -f "+fl2cp)

		#adam-SHNT# I'd like to remove MAG_APER- so I don't confuse it for MAG_APER1- later (see #example# below)
		#adam-later## make a version of flnew with the old MAG_APER- keys (as opposed to MAG_APER1-) deleted so that it doesn't accidentally use the wrong thing later
		#adam-later# del_keys=[k.replace('_APER1-','_APER-') for k in all_aper1_keys]
		#fl2cp=flnew.replace(".cat",".output-tmp.cat")
		#del_keys=[k.replace('MAG_APER1-','MAG_APER-') for k in all_aper1_keys]
		#ooo=os.system("ldacdelkey -i "+flnew+" -o "+fl2cp+" -k "+' '.join(del_keys))
		#if ooo!=0: raise Exception("the line os.system(ldacdelkey...) failed")
		#os.system("rm -f "+flnew)

		## OK, now make the zps table and add it to the cat. example from photocalibrate_cat.py below
		#example# zp_cols = [pyfits.Column(name = 'filter',
		#example# 	format= '60A',
		#example# 	array=filters),
		#example# pyfits.Column(name = 'zeropoints',
		#example# 	format= 'E',
		#example# 	array=array(zp_list)),
		#example# pyfits.Column(name = 'errors',
		#example# 	format = 'E',
		#example# 	array = array(zperr_list))]
		#example# zpCat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(zp_cols)))
		#example# zpCat.hdu.header['EXTNAME']= 'ZPS'
		#example# hdus = [pyfits.PrimaryHDU(), calibratedCat.hdu, zpCat.hdu]
		#example# hdus.extend(_transferOtherHDUs(options.incatfile))
		#example# hdulist = pyfits.HDUList(hdus)
		#example# hdulist.writeto(options.outcatfile, overwrite=True)

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
