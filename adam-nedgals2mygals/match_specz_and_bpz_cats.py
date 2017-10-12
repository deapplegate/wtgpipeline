#! /usr/bin/env python
#adam-does# matches the redshifts from our pipeline/bpz to external reference redshifts
#adam-example# ipython -i -- ./match_specz_and_bpz_cats.py nedcat bpzcat =astropy.io.ascii.read("/u/ki/awright/bonnpipeline/adam_ned_MACS1226+21_galaxies.tsv")
#adam-example# ipython -i -- ./match_specz_and_bpz_cats.py /u/ki/awright/bonnpipeline/adam_ned_MACS1226+21_galaxies.tsv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.bpztab.cat

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
raw_bpz_SeqNr=objdat.field('SeqNr')
raw_bpz_ra=objdat.field('ALPHA_J2000')
raw_bpz_dec=objdat.field('DELTA_J2000')
#raw_bpz_rmag=objdat.field("MAG_AUTO1-SUBARU-10_3-1-W-C-RC")
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
	bpz_SeqNr=raw_bpz_SeqNr[ok_bpz]

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
Mbpz_z_min=bpz_z_min[idx]
Mbpz_z_max=bpz_z_max[idx]
Mbpz_odds=bpz_odds[idx]
Mbpz_rmag=bpz_rmag[idx]
Mbpz_imag=bpz_imag[idx]
Mbpz_rmagerr=bpz_rmagerr[idx]
Mbpz_imagerr=bpz_imagerr[idx]
Mbpz_i_ok=i_ok[idx]
Mbpz_r_ok=r_ok[idx]
Mbpz_SeqNr=bpz_SeqNr[idx]

## save catalog with all relevent matched information
from astropy.io import ascii
#outtable=astropy.table.table.Table(data=[Mbpz_ra,Mbpz_dec,zspec_ra,zspec_dec,zspec_z,Mbpz_z, Mbpz_odds, d2d_arcsec],names=["Mbpz_ra","Mbpz_dec","zspec_ra","zspec_dec","zspec_z","Mbpz_z"," Mbpz_odds","d2d_arcsec"])
#outtable.write("match_specz_and_bpz_cats_uncut_final_zspecgals2mygals.tsv",format="ascii.commented_header")

## check and see how things look if I exclude detections that have a -99 anywhere

## matches are "good" if they are less than 6 pixels apart and z>.01
#adam-SHNT# the below:
## So, I run bpz on a catalog that's got both stars and galaxies in it, but I have ZMIN=.01, so it's safe to say that the BPZ results are going to be meaningless for stars, and I should remove them from the plots evaluating the effectiveness of BPZ.
#also, I've got some doubles, are these by any chance from cat_additions_from_sdss_zspecs.tsv overlapping with the zspecs?
#I think that's it, but I might need to make some of these changes in other adam_match_nedgals2mygals*.py files too!
lt6pix_apart=d2d_arcsec<1.2
gtpt01_z=zspec_z>.01
match_goodenough=lt6pix_apart*gtpt01_z
bpzra=Mbpz_ra[match_goodenough]
bpzdec=Mbpz_dec[match_goodenough]
inds=arange(len(zspec_z))
goodinds=inds[match_goodenough]
goodzspec= zspec_z[match_goodenough]
doubles=[]
doubles_ra=[]
doubles_dec=[]
for i in range(len(bpzra)):
	ra=bpzra[i]
	ra_matches=bpzra==ra
	dec=bpzdec[i]
	dec_matches=bpzdec==dec
	if dec_matches.sum()>1:
		if not i==dec_matches.argmax():
			doubles.append((i,dec_matches.argmax()))
			doubles_ra.append(ra)
			doubles_dec.append(dec)

doubles_zspec_inds=[]
match_goodsingles=match_goodenough.copy()
for (i1,i2) in doubles:
	print goodzspec[i1],goodzspec[i2],goodzspec[i1]-goodzspec[i2]
	doubles_zspec_inds.append((goodinds[i1],goodinds[i2]))
	gi1,gi2=(goodinds[i1],goodinds[i2])
	d2d1=d2d_arcsec[gi1]
	d2d2=d2d_arcsec[gi2]
	if d2d1<d2d2:
		print match_goodenough[gi2]
		match_goodsingles[gi2]=False
	else:
		print match_goodenough[gi1]
		match_goodsingles[gi1]=False

# turns out the doubles (where two zspec objects are matched to the same bpz object) are from zspec having two z's listed for a single object (one side of galaxy and the other side of the galaxy)

Mbpz_ra=matches.ra.deg
Mbpz_dec=matches.dec.deg
Mbpz_z=bpz_z[idx]
Mbpz_z_min=bpz_z_min[idx]
Mbpz_z_max=bpz_z_max[idx]
Mbpz_odds=bpz_odds[idx]
Mbpz_rmag=bpz_rmag[idx]
Mbpz_imag=bpz_imag[idx]
Mbpz_rmagerr=bpz_rmagerr[idx]
Mbpz_imagerr=bpz_imagerr[idx]
Mbpz_i_ok=i_ok[idx]
Mbpz_r_ok=r_ok[idx]
Mbpz_SeqNr=bpz_SeqNr[idx]
good={}
good['dist']= d2d_arcsec[match_goodsingles]
good['Mbpz_ra']= Mbpz_ra[match_goodsingles]
good['Mbpz_dec']= Mbpz_dec[match_goodsingles]
good['Mbpz_z']= Mbpz_z[match_goodsingles]
good['Mbpz_z_min']= Mbpz_z_min[match_goodsingles]
good['Mbpz_z_max']= Mbpz_z_max[match_goodsingles]
good['Mbpz_odds']= Mbpz_odds[match_goodsingles]
good['Mbpz_imag']= Mbpz_imag[match_goodsingles]
good['Mbpz_rmag']= Mbpz_rmag[match_goodsingles]
good['Mbpz_imagerr']= Mbpz_imagerr[match_goodsingles]
good['Mbpz_rmagerr']= Mbpz_rmagerr[match_goodsingles]
good['Mbpz_i_ok']= Mbpz_i_ok[match_goodsingles]
good['Mbpz_r_ok']= Mbpz_r_ok[match_goodsingles]
good['Mbpz_SeqNr']= Mbpz_SeqNr[match_goodsingles]
good['zspec_z']= zspec_z[match_goodsingles]
good['zspec_ra']= zspec_ra[match_goodsingles]
good['zspec_dec']= zspec_dec[match_goodsingles]
allok=Mbpz_i_ok*Mbpz_r_ok
good['Mbpz_allok']= allok[match_goodsingles]
## save catalog of the good matches

outtable=astropy.table.table.Table( data=[good['zspec_ra'],good['zspec_dec'],good['zspec_z'],good['Mbpz_z'],good['Mbpz_ra'],good['Mbpz_dec'],good['Mbpz_SeqNr'],good['Mbpz_z_min'],good['Mbpz_z_max'],good['Mbpz_odds'],good['Mbpz_imag'],good['Mbpz_rmag'],good['Mbpz_imagerr'],good['Mbpz_rmagerr'],good['Mbpz_i_ok'],good['Mbpz_r_ok'],good['Mbpz_allok'],good['dist']], \
		names=['ref_ra','ref_dec','ref_z','bpz_z','bpz_ra','bpz_dec','bpz_SeqNr','bpz_z_min','bpz_z_max','bpz_odds','bpz_I','bpz_R','bpz_Ierr','bpz_Rerr','bpz_I_ok','bpz_R_ok','bpz_allok','dist'])
outtable.write("match_specz_and_bpz_cats.tsv",format="ascii.commented_header")
#outtable=astropy.table.table.Table( data=[Mbpz_ra[match_goodsingles],Mbpz_dec[match_goodsingles],zspec_ra[match_goodsingles],zspec_dec[match_goodsingles],zspec_z[match_goodsingles],Mbpz_z[match_goodsingles], Mbpz_odds[match_goodsingles], d2d_arcsec[match_goodsingles]], \
#		names=["Mbpz_ra","Mbpz_dec","zspec_ra","zspec_dec","zspec_z","Mbpz_z","Mbpz_odds","d2d_arcsec"])
#outtable.write("match_specz_and_bpz_cats.tsv",format="ascii.commented_header")

#adam-SHNT# OK, i've got to save the Z_S to the catalog now, and that's the catalog adam_do_photometry.py has to use!
Z_S_SeqNr=Mbpz_SeqNr[match_goodsingles]
Z_S_z=zspec_z[match_goodsingles]
## save catalog of the good matches
bpz_path=os.path.split(bpz_file)
outtable=astropy.table.table.Table( data=[ Z_S_SeqNr, Z_S_z ], names=['SeqNr','z'])
outtable.write(bpz_path[0]+"/match_specz_and_bpz_cats.txt",format="ascii.commented_header")
