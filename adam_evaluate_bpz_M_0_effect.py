#! /usr/bin/env python
#adam-does# matches the redshifts from our pipeline/bpz to external reference redshifts
#adam-example# ipython -i -- ./match_specz_and_bpz_cats.py nedcat bpzcat =astropy.io.ascii.read("/u/ki/awright/wtgpipeline/adam_ned_MACS1226+21_galaxies.tsv")
#adam-example# ipython -i -- ./match_specz_and_bpz_cats.py /u/ki/awright/wtgpipeline/adam_ned_MACS1226+21_galaxies.tsv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.bpztab.cat

import sys,os,inspect ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
from import_tools import *
curfile=os.path.abspath(inspect.getfile(inspect.currentframe()))
FileString=os.path.basename(curfile)
args=imagetools.ArgCleaner(sys.argv,FileString)
import numpy as np
import matplotlib.pyplot as plt
import astropy
from astropy.coordinates import SkyCoord
from astropy import units as u
from astropy.io import ascii
import string

bpz_file= "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.APER1.1.CWWSB_capak.list.all.input_and_bpz.tab"
final_file= "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.APER1.1.CWWSB_capak.list.all.EVERY.cat"
def ldac_opener(cat_file):
	cat=astropy.io.fits.open(cat_file)
	print "%s tables in %s opening 1st one" % (len(cat),cat_file)
	tab=cat[1].data
	return tab


cat0=ldac_opener(bpz_file)
cat1=ldac_opener(final_file)
R_filt="MAG_APER1-SUBARU-10_3-1-W-C-RC"
I_filt="MAG_APER1-SUBARU-10_3-1-W-C-IC"
Rm=cat0.field(R_filt)
Rme=cat0.field(R_filt.replace("MAG","MAGERR"))
Rf=cat0.field(R_filt.replace("MAG","FLUX"))
Rfe=cat0.field(R_filt.replace("MAG","FLUXERR"))
Im=cat0.field(I_filt)
Ime=cat0.field(I_filt.replace("MAG","MAGERR"))
If=cat0.field(I_filt.replace("MAG","FLUX"))
Ife=cat0.field(I_filt.replace("MAG","FLUXERR"))
print "min,max,min(Rm>0):",Rm.min(),Rm.max(),Rm[Rm>0].min()
Rf=cat0.field(R_filt.replace("MAG","FLUX"))
Rfe=cat0.field(R_filt.replace("MAG","FLUXERR"))
If=cat0.field(I_filt.replace("MAG","FLUX"))
Ife=cat0.field(I_filt.replace("MAG","FLUXERR"))
filt_bpz_keys=[]
filts=[]
for key in cat0.columns.names:
	if key.endswith("_bpz"):
		if key.startswith("FLUX_"):
			filt=key[string.find(key,"W-"):-4]
			if filt=='W-C-RC':
				Rfilt=filt
				Rkey=key
				continue
			filt_bpz_keys.append(key)
			filts.append(filt)

filt_bpz_keys.append(Rkey)
filts.append(Rfilt)
## want R band to be last in the list
Hkeys={}
Hkeys['W-J-B']='HYBRID_MAG_APER1-SUBARU-10_3-1-W-J-B' 
Hkeys['W-S-I+']='HYBRID_MAG_APER1-SUBARU-10_3-1-W-S-I+'
Hkeys['W-C-RC']='HYBRID_MAG_APER1-SUBARU-10_3-1-W-C-RC'
Hkeys['W-S-Z+']='HYBRID_MAG_APER1-SUBARU-10_3-1-W-S-Z+'
Hkeys['W-C-IC']='HYBRID_MAG_APER1-SUBARU-10_3-1-W-C-IC'
Hkeys['W-J-V']='HYBRID_MAG_APER1-SUBARU-10_3-1-W-J-V' 

qual={} #determine quality of detection in each band (+1=detection, 0=non-obs, -1=non-detection)
for filt,key in zip(filts,filt_bpz_keys):
	f=cat0.field(key)
	ef=cat0.field(key.replace("FLUX","FLUXERR"))
	qual[filt]=zeros(f.shape,dtype=int32)
	#determine quality of detection in each band (+1=detection)
	fpos=f>0
	fneg=logical_not(fpos)
	efpos=ef>0
	efneg=logical_not(efpos)
	dets,nonobs,nondet=fpos,(fneg)*(efneg),(fneg)*(efpos)
	qual[filt][fpos]=1
	#determine quality of detection in each band (0=non-obs)
	qual[filt][nonobs]=0
	#determine quality of detection in each band (-1=non-detection)
	qual[filt][nondet]=-1
	#print "in band %s, # detections=%s, # non-obs=%s, # non-det=%s" % (filt,dets.sum(),(nonobs).sum(),(nondet).sum())
	Hm=cat1.field(Hkeys[filt])
	Hm_dets=Hm[dets]
	Hm_nondet=Hm[nondet]
	Hm_nonobs=Hm[nonobs]
	print "in band %s ave HYBRID MAG for detections / non-obs / non-det = %.1f / %.1f / %.1f" % (filt,Hm_dets.mean(),(Hm_nonobs).mean(),(Hm_nondet).mean())
	#f=figure()
	f, ax = plt.subplots(3, figsize=(8,10), sharex=True)
	f.add_subplot(2,2,1)
	hist(Hm_dets)
	title(Hkeys[filt]+" distribution for detections")
	f.add_subplot(2,2,2)
	hist(Hm_nonobs)
	title(Hkeys[filt]+" distribution for non-obs")
	f.add_subplot(2,2,3)
	hist(Hm_nondet)
	title(Hkeys[filt]+" distribution for non-det")
	#f.savefig
	#Hm_dets.mean(),(Hm_nonobs).mean(),(Hm_nondet).mean())
	#adam-SHNT#ok, still need to plot the distribution of HYBRID mags for non-dets and non-obs!

## put R band last in the list, so these will be the R-band stats!
Hm_nondet_fix=Hm_nondet[Hm_nondet>-99]
print "in band %s fixed %s of %s nondets" % (filt,len(Hm_nondet_fix),len(Hm_nondet))
print "in band %s HYBRID MAG of the fixed nondets have min/mean/max= %.1f / %.1f / %.1f" % (filt,Hm_nondet_fix.min(),Hm_nondet_fix.mean(),Hm_nondet_fix.max())
Hm_nonobs_fix=Hm_nonobs[Hm_nonobs>-99]
print "in band %s fixed %s of %s nonobss" % (filt,len(Hm_nonobs_fix),len(Hm_nonobs))
print "in band %s HYBRID MAG of the fixed nonobss have min/mean/max= %.1f / %.1f / %.1f" % (filt,Hm_nonobs_fix.min(),Hm_nonobs_fix.mean(),Hm_nonobs_fix.max())

#'BPZ_ODDS', 'BPZ_Z_ML', 'BPZ_T_ML', 'BPZ_CHI-SQUARED', 'BPZ_M_0'
M0=cat0.field('BPZ_M_0')
badM0=(M0<0)
Hm_badM0=Hm[badM0]
(Hm_badM0<0).sum()
#M0=cat0.field('BPZ_M_0')
odds=cat0.field('BPZ_ODDS')
badodds=odds[badM0]
goododds=odds[logical_not(badM0)]
f=figure()
f.add_subplot(121)
hist(goododds,bins=arange(0,1.05,.05))
title('BPZ_ODDS distribution for objects with M_0>0 (ave ODDS[M_0>0]=%.3f)' % (goododds.mean()) )
f.add_subplot(122)
hist(badodds,bins=arange(0,1.05,.05))
title('BPZ_ODDS distribution for objects with M_0<0 (i.e. bad M_0s) (ave ODDS[M_0<0]=%.3f)' % (badodds.mean()) )
f.savefig('plt_bpz_odds_badM0_and_goodM0')
show()

I_goodM0=qual['W-C-IC']>0
V_goodM0=qual['W-J-V']>0
at_least_one=zeros(M0.shape,dtype=bool)
for k in qual.keys():
    at_least_one=at_least_one+(qual[k]>0)
print "There are %s # of detections with R band M_0<0, that's a fraction of %.3f detections" % (badM0.sum(),badM0.mean())
print "for detections with R band M_0<0, we have good mags for %.3f of I band mags, %.3f of either I or V band mags, and %.3f of at least one magnitude" % (I_goodM0[badM0].mean(),(V_goodM0+I_goodM0)[badM0].mean(),(at_least_one)[badM0].mean())

## RESULTING INFORMATION PRINTED OUT
######  min,max,min(Rm>0): -99.0 37.1635 18.0861
######  in band W-S-Z+ ave HYBRID MAG for detections / non-obs / non-det = 24.9 / 11.5 / 20.6
######  in band W-J-B ave HYBRID MAG for detections / non-obs / non-det = 26.1 / 9.8 / 21.2
######  in band W-C-IC ave HYBRID MAG for detections / non-obs / non-det = 25.1 / -15.1 / 19.6
######  in band W-J-V ave HYBRID MAG for detections / non-obs / non-det = 25.8 / -7.7 / 14.3
######  in band W-C-RC ave HYBRID MAG for detections / non-obs / non-det = 25.5 / -5.5 / 0.3
######  in band W-C-RC fixed 1992 of 2589 nondets
######  in band W-C-RC HYBRID MAG of the fixed nondets have min/mean/max= 24.8 / 30.0 / 40.2
######  in band W-C-RC fixed 2162 of 2867 nonobss
######  in band W-C-RC HYBRID MAG of the fixed nonobss have min/mean/max= 15.4 / 25.0 / 34.7
######  There are 5456 # of detections with R band M_0<0, that's a fraction of 0.043 detections
######  for detections with R band M_0<0, we have good mags for 0.398 of I band mags, 0.608 of either I or V band mags, and 0.761 of at least one magnitude
