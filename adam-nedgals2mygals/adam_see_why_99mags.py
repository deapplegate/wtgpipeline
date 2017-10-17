#! /usr/bin/env python
#adam-does# matches the redshifts from our pipeline/bpz to external reference redshifts
#adam-example# ipython -i -- ./adam_match_nedgals2mygals.py nedcat bpzcat =astropy.io.ascii.read("/u/ki/awright/bonnpipeline/adam_ned_MACS1226+21_galaxies.tsv")
#adam-example# ipython -i -- ./adam_match_nedgals2mygals.py /u/ki/awright/bonnpipeline/adam_ned_MACS1226+21_galaxies.tsv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.bpztab.cat

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

ned_file= "/u/ki/awright/bonnpipeline/adam-nedgals2mygals/sdssj1226_redshifts_converted.tsv"
bpz_file= "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.bpztab.cat"
sdss_file="/u/ki/awright/bonnpipeline/adam-nedgals2mygals/cat_additions_from_sdss_zspecs.tsv" #'Survey', 'RA', 'Dec', 'Redshift', 'SN', 'Class'
sdsscat=astropy.io.ascii.read(sdss_file)
nedcat=astropy.io.ascii.read(ned_file)
bpzcat=astropy.io.fits.open(bpz_file)
outtag="final_macs1226_clip23"

#adam-example# bpzcat=astropy.io.fits.open("/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.bpztab.cat")
# os.system("ldacdesc -i /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.bpztab.cat")
# primary OBJECTS PHOTINFO FIELDS BPZTAB
bpztab=bpzcat[-1]
objtab=bpzcat[1]
bpzdat=bpztab.data
objdat=objtab.data
raw_bpz_z=bpzdat.field("BPZ_Z_B")
raw_bpz_z_min=bpzdat.field("BPZ_Z_B_MIN")
raw_bpz_z_max=bpzdat.field("BPZ_Z_B_MAX")
raw_bpz_odds=bpzdat.field("BPZ_ODDS")
raw_bpz_ra=objdat.field('ALPHA_J2000')
raw_bpz_dec=objdat.field('DELTA_J2000')
raw_bpz_rmag=objdat.field("MAG_APER1-SUBARU-10_3-1-W-C-RC")
raw_bpz_imag=objdat.field("MAG_APER1-SUBARU-10_3-1-W-C-IC")
raw_bpz_rmagerr=objdat.field("MAGERR_APER1-SUBARU-10_3-1-W-C-RC")
raw_bpz_imagerr=objdat.field("MAGERR_APER1-SUBARU-10_3-1-W-C-IC")
raw_r_ok=raw_bpz_rmag>0
raw_i_ok=raw_bpz_imag>0

## now clip down to the bpz catalog that actually has a similar magnitude range:
ok_bpz=(raw_bpz_rmag<23)*(raw_bpz_imag<23)
if ok_bpz.any():
	bpz_z=raw_bpz_z[ok_bpz]
	bpz_z_min=raw_bpz_z_min[ok_bpz]
	bpz_z_max=raw_bpz_z_max[ok_bpz]
	bpz_odds=raw_bpz_odds[ok_bpz]
	bpz_ra=raw_bpz_ra[ok_bpz]
	bpz_dec=raw_bpz_dec[ok_bpz]
	bpz_rmag=raw_bpz_rmag[ok_bpz]
	bpz_imag=raw_bpz_imag[ok_bpz]
	bpz_rmagerr=raw_bpz_rmagerr[ok_bpz]
	bpz_imagerr=raw_bpz_imagerr[ok_bpz]
	r_ok=raw_r_ok[ok_bpz]
	i_ok=raw_i_ok[ok_bpz]

#fk5 is J2000 by default!
mycoords=SkyCoord(bpz_ra*u.degree,bpz_dec*u.degree,frame="fk5")

## now get ned/sdss info
sdsscoords=SkyCoord(sdsscat["RA"].data*u.degree,sdsscat["Dec"].data*u.degree,frame="fk5")
nedcoords=SkyCoord(nedcat["ra"],nedcat["dec"],frame="fk5")
# ned_gmag=nedcat['g'].data ned_imag=nedcat['i'].data ned_rmag=nedcat['r'].data
sdss_z=sdsscat["Redshift"].data
ned_z=nedcat['z'].data

##combine ned and sdss info
zspec_dec=append(nedcoords.dec.deg,sdsscoords.dec.deg)
zspec_ra=append(nedcoords.ra.deg,sdsscoords.ra.deg)
zspec_z=append(ned_z,sdss_z)
zspeccoords=SkyCoord(zspec_ra*u.degree,zspec_dec*u.degree,frame="fk5")

idx, d2d, d3d = zspeccoords.match_to_catalog_sky(mycoords)
d2d_arcsec=d2d.deg*3600
matches=mycoords[idx]
Mbpz_ra=matches.ra.deg
Mbpz_dec=matches.dec.deg
Mbpz_z=bpz_z[idx]
Mbpz_z_min=bpz_z_min[idx];Mbpz_z_max=bpz_z_max[idx] #Mbpz_rmag=bpz_rmag[idx] Mbpz_imag=bpz_imag[idx]
Mbpz_odds=bpz_odds[idx]

## save catalog with all relevent matched information
from astropy.io import ascii
I_file="cat_all_I_mags.tsv"
Icat=astropy.io.ascii.read(I_file)
R_file="cat_all_R_mags.tsv"
Rcat=astropy.io.ascii.read(R_file)


## isolate the -99 mags
minus99=Rcat["MAG_APER1-10_3"].data==-99.0
Rcat_minus99=Rcat[minus99]
Icat_minus99=Icat[minus99]

for col in Rcat.colnames:
	print "                             W-C-RC: ",col,Rcat[col].data.min(),Rcat[col].data.max()
	print "(MAG_APER1-10_3-W-C-RC==-99) W-C-RC: ",col,Rcat_minus99[col].data.min(),Rcat_minus99[col].data.max()
	print "                             W-C-IC: ",col,Icat[col].data.min(),Icat[col].data.max()
	print "(MAG_APER1-10_3-W-C-IC==-99) W-C-IC: ",col,Icat_minus99[col].data.min(),Icat_minus99[col].data.max()

f=figure()
names=Rcat.colnames[1:]
nums=[1,3,5,7,9]
bins=arange(14,101)-.5
for i,col in zip(nums,Rcat.colnames):
    f.add_subplot(5,2,i)
    title(col+"-1-W-C-RC")
    hist(Rcat[col].data,bins=bins)
    f.add_subplot(5,2,i+1)
    title(col+"-1-W-C-IC")
    hist(Icat[col].data,bins=bins)
f.suptitle("Mag distribution in general")


f=figure()
names=Rcat.colnames[1:]
nums=[1,3,5,7]
bins=arange(14,101)-.5
for i,col in zip(nums,names):
    f.add_subplot(4,2,i)
    title(col+"-1-W-C-RC")
    hist(Rcat_minus99[col].data,bins=bins)
    f.add_subplot(4,2,i+1)
    title(col+"-1-W-C-IC")
    hist(Icat_minus99[col].data,bins=bins)
f.suptitle("Other mags where MAG_APER1-10_3-SUBARU-1-W-C-RC=-99")
show()
