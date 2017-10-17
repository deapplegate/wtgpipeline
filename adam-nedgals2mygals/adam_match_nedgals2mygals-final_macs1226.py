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
outtable=astropy.table.table.Table(data=[Mbpz_ra,Mbpz_dec,zspec_ra,zspec_dec,zspec_z,Mbpz_z, Mbpz_odds, d2d_arcsec],names=["Mbpz_ra","Mbpz_dec","zspec_ra","zspec_dec","zspec_z","Mbpz_z"," Mbpz_odds","d2d_arcsec"])
outtable.write("matches_uncut_final_zspecgals2mygals-%s.tsv" % (outtag),format="ascii.commented_header")

## check and see how things look if I exclude detections that have a -99 anywhere
Mbpz_i_ok=i_ok[idx]
Mbpz_r_ok=r_ok[idx]
allok=Mbpz_i_ok*Mbpz_r_ok

## matches are "good" if they are less than 6 pixels apart and BPZ_ODDS>.5
lt6pix_apart=d2d_arcsec<1.2
Mbpz_odds_gtHALF=Mbpz_odds>.5
match_badenough=logical_not(lt6pix_apart*Mbpz_odds_gtHALF)
bad={}
bad['dist']= d2d_arcsec[match_badenough]
bad['Mbpz_z']= Mbpz_z[match_badenough]
bad['Mbpz_z_min']= Mbpz_z_min[match_badenough];bad['Mbpz_z_max']= Mbpz_z_max[match_badenough]
bad['Mbpz_odds']= Mbpz_odds[match_badenough]
bad['zspec_z']= zspec_z[match_badenough]
bad['Mbpz_r_ok']= Mbpz_r_ok[match_badenough]
bad['lt6pix_apart']= lt6pix_apart[match_badenough]
bad['Mbpz_odds_gtHALF']= Mbpz_odds_gtHALF[match_badenough]
## save catalog of the bad matches
outtable=astropy.table.table.Table( data=[Mbpz_ra[match_badenough],Mbpz_dec[match_badenough],zspec_ra[match_badenough],zspec_dec[match_badenough],zspec_z[match_badenough],Mbpz_z[match_badenough], Mbpz_odds[match_badenough], d2d_arcsec[match_badenough],Mbpz_r_ok[match_badenough],lt6pix_apart[match_badenough],Mbpz_odds_gtHALF[match_badenough]], \
		names=["Mbpz_ra","Mbpz_dec","zspec_ra","zspec_dec","zspec_z","Mbpz_z","Mbpz_odds","d2d_arcsec","Mbpz_r_ok","lt6pix_apart","Mbpz_odds_gtHALF"])
outtable.write("matches_FailedCut_d2dcut_oddscutpt5_zspecgals2mygals-%s.tsv" % (outtag),format="ascii.commented_header")
match_goodenough=lt6pix_apart
good={}
good['dist']= d2d_arcsec[match_goodenough]
good['Mbpz_z']= Mbpz_z[match_goodenough]
good['Mbpz_z_min']= Mbpz_z_min[match_goodenough];good['Mbpz_z_max']= Mbpz_z_max[match_goodenough]
good['Mbpz_odds']= Mbpz_odds[match_goodenough]
good['zspec_z']= zspec_z[match_goodenough]
good['allok']= allok[match_goodenough]
## save catalog of the good matches
outtable=astropy.table.table.Table( data=[Mbpz_ra[match_goodenough],Mbpz_dec[match_goodenough],zspec_ra[match_goodenough],zspec_dec[match_goodenough],zspec_z[match_goodenough],Mbpz_z[match_goodenough], Mbpz_odds[match_goodenough], d2d_arcsec[match_goodenough]], \
		names=["Mbpz_ra","Mbpz_dec","zspec_ra","zspec_dec","zspec_z","Mbpz_z","Mbpz_odds","d2d_arcsec"])
outtable.write("matches_FinalCat_d2dcut_zspecgals2mygals-%s.tsv" % (outtag),format="ascii.commented_header")
match_goodenough=lt6pix_apart*Mbpz_odds_gtHALF
good={}
good['dist']= d2d_arcsec[match_goodenough]
good['Mbpz_z']= Mbpz_z[match_goodenough]
good['Mbpz_z_min']= Mbpz_z_min[match_goodenough];good['Mbpz_z_max']= Mbpz_z_max[match_goodenough]
good['Mbpz_odds']= Mbpz_odds[match_goodenough]
good['zspec_z']= zspec_z[match_goodenough]
good['allok']= allok[match_goodenough]
## save catalog of the good matches
outtable=astropy.table.table.Table( data=[Mbpz_ra[match_goodenough],Mbpz_dec[match_goodenough],zspec_ra[match_goodenough],zspec_dec[match_goodenough],zspec_z[match_goodenough],Mbpz_z[match_goodenough], Mbpz_odds[match_goodenough], d2d_arcsec[match_goodenough]], \
		names=["Mbpz_ra","Mbpz_dec","zspec_ra","zspec_dec","zspec_z","Mbpz_z","Mbpz_odds","d2d_arcsec"])
outtable.write("matches_d2dcut_oddscutpt5_zspecgals2mygals-%s.tsv" % (outtag),format="ascii.commented_header")

### PLOTS

## first plot btwn z=0-.55
order=good['zspec_z'].argsort()
odds=good['Mbpz_odds'][order]
uncertain_mags=logical_not(good['allok'][order])
uncertain_odds=(odds<.9)
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.errorbar(x=good['zspec_z'][order],y=good['Mbpz_z'][order],yerr=[good['Mbpz_z_max'][order]-good['Mbpz_z'][order],good['Mbpz_z'][order]-good['Mbpz_z_min'][order]],fmt='o',mfc='b')
ax.plot(good['zspec_z'][order][uncertain_mags],good['Mbpz_z'][order][uncertain_mags],'yo',label="mag=-99")
ax.plot(good['zspec_z'][order][uncertain_odds],good['Mbpz_z'][order][uncertain_odds],'ro',label="odds<.9")
ax.set_xlabel('zspec')
ax.set_ylabel('Mbpz_z')
ax.plot([0,1],[0,1],'k.-')
ax.set_xlim(0.3,.65);ax.set_ylim(0.3,.65)
ax.set_title('Z bpz vs. Z spec (for matches less than 6 pixels apart with BPZ_ODDS>.5)')
legend(loc="upper left")
f.savefig('plt_match_zspecgals2mygals-%s-z_correlation-zoomed' % (outtag))

## now plot entire range
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.errorbar(x=good['zspec_z'][order],y=good['Mbpz_z'][order],yerr=[good['Mbpz_z_max'][order]-good['Mbpz_z'][order],good['Mbpz_z'][order]-good['Mbpz_z_min'][order]],fmt='o',mfc='b')
ax.plot(good['zspec_z'][order][uncertain_mags],good['Mbpz_z'][order][uncertain_mags],'yo',label="mag=-99")
ax.plot(good['zspec_z'][order][uncertain_odds],good['Mbpz_z'][order][uncertain_odds],'ro',label="odds<.9")
xmin,xmax=ax.get_xlim();ymin,ymax=ax.get_ylim()
minmin=min([xmin,ymin])
if minmin<-.01:minmin=-.01
maxmax=max([xmax,ymax])
ax.set_xlabel('zspec')
ax.set_ylabel('Mbpz_z')
ax.plot([0,maxmax],[0,maxmax],'k.-')
ax.set_xlim(minmin,maxmax);ax.set_ylim(minmin,maxmax)
ax.set_title('Z bpz vs. Z spec (for matches less than 6 pixels apart with BPZ_ODDS>.5)')
legend(loc="upper left")
f.savefig('plt_match_zspecgals2mygals-%s-z_correlation' % (outtag))

from fitter import Gauss
zspec_z_good=good['zspec_z'][order];Mbpz_z_good=good['Mbpz_z'][order]
good_zoff=(good['Mbpz_z'][order]-good['zspec_z'][order])/(1+good['zspec_z'][order])
print "good matches offset mean:",good_zoff.mean()
print "good matches offset std:",good_zoff.std()

## now look at clipped Z offset dist'n
z_clipper=good_zoff.__abs__()<.1
clipped_zoff=good_zoff[z_clipper]
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.set_ylabel('galaxies')
ax.hist(good_zoff,bins=np.arange(-.305 ,.315,.01))
N,bins=histogram(clipped_zoff,bins=np.arange(-.105 ,.115,.01))
gauss_bins=GetMiddle(bins)
good_gauss=Gauss(gauss_bins,N,threshold=.08)
mu=good_gauss.mean
sigma=good_gauss.sigma
xx,yy=good_gauss.getfitline(100)
ax.plot(xx,yy,'r-')
ax.set_title('(Z bpz - Z spec)/(1 + Z spec) (for matches less than 6 pixels apart with BPZ_ODDS>.5)')
ax.set_xlabel('stats for values excluding outliers with |Z bpz - Z zspec|/(1 + Z spec) >.1 (%s of %s passed clip)\n   mean:%.3f  sigma:%.3f  rms: %.3f' % (z_clipper.sum(),z_clipper.__len__(),mu,sigma,clipped_zoff.std()))
ax.set_xlim(-.305 ,.305)
f.savefig('plt_match_zspecgals2mygals-%s-z_offset_hist-clipped_stats' % (outtag))

## matches are "good" if they are less than 6 pixels apart and BPZ_ODDS>.5
lt6pix_apart=d2d_arcsec<1.2
Mbpz_odds_gtHALF=Mbpz_odds>.9
match_goodenough=lt6pix_apart*Mbpz_odds_gtHALF
good={}
good['dist']= d2d_arcsec[match_goodenough]
good['Mbpz_z']= Mbpz_z[match_goodenough]
good['Mbpz_z_min']= Mbpz_z_min[match_goodenough];good['Mbpz_z_max']= Mbpz_z_max[match_goodenough]
good['Mbpz_odds']= Mbpz_odds[match_goodenough]
good['zspec_z']= zspec_z[match_goodenough]
good['allok']= allok[match_goodenough]
## save catalog of the good matches
outtable=astropy.table.table.Table( data=[Mbpz_ra[match_goodenough],Mbpz_dec[match_goodenough],zspec_ra[match_goodenough],zspec_dec[match_goodenough],zspec_z[match_goodenough],Mbpz_z[match_goodenough], Mbpz_odds[match_goodenough], d2d_arcsec[match_goodenough]], \
		names=["Mbpz_ra","Mbpz_dec","zspec_ra","zspec_dec","zspec_z","Mbpz_z","Mbpz_odds","d2d_arcsec"])
outtable.write("matches_d2dcut_oddscutpt9_zspecgals2mygals-%s.tsv" % (outtag),format="ascii.commented_header")

## first plot btwn z=0-.55
order=good['zspec_z'].argsort()
uncertain_mags=logical_not(good['allok'][order])
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.errorbar(x=good['zspec_z'][order],y=good['Mbpz_z'][order],yerr=[good['Mbpz_z_max'][order]-good['Mbpz_z'][order],good['Mbpz_z'][order]-good['Mbpz_z_min'][order]],fmt='o',mfc='b')
ax.plot(good['zspec_z'][order][uncertain_mags],good['Mbpz_z'][order][uncertain_mags],'yo',label="mag=-99")
ax.set_xlabel('zspec')
ax.set_ylabel('Mbpz_z')
ax.plot([0,1],[0,1],'k.-')
ax.set_xlim(0.3,.65);ax.set_ylim(0.3,.65)
ax.set_title('Z bpz vs. Z spec (for matches less than 6 pixels apart with BPZ_ODDS>.9)')
legend(loc="upper left")
f.savefig('plt_match_zspecgals2mygals-%s-z_correlation_oddsGTpt9-zoomed' % (outtag))

## now plot entire range
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.errorbar(x=good['zspec_z'][order],y=good['Mbpz_z'][order],yerr=[good['Mbpz_z_max'][order]-good['Mbpz_z'][order],good['Mbpz_z'][order]-good['Mbpz_z_min'][order]],fmt='o',mfc='b')
ax.plot(good['zspec_z'][order][uncertain_mags],good['Mbpz_z'][order][uncertain_mags],'yo',label="mag=-99")
xmin,xmax=ax.get_xlim();ymin,ymax=ax.get_ylim()
minmin=min([xmin,ymin])
if minmin<-.01:minmin=-.01
maxmax=max([xmax,ymax])
ax.set_xlabel('zspec')
ax.set_ylabel('Mbpz_z')
ax.plot([0,maxmax],[0,maxmax],'k.-')
ax.set_xlim(minmin,maxmax);ax.set_ylim(minmin,maxmax)
ax.set_title('Z bpz vs. Z spec (for matches less than 6 pixels apart with BPZ_ODDS>.9)')
legend(loc="upper left")
f.savefig('plt_match_zspecgals2mygals-%s-z_correlation_oddsGTpt9' % (outtag))

zspec_z_good=good['zspec_z'][order];Mbpz_z_good=good['Mbpz_z'][order]
good_zoff=(good['Mbpz_z'][order]-good['zspec_z'][order])/(1+good['zspec_z'][order])
print "good matches offset mean:",good_zoff.mean()
print "good matches offset std:",good_zoff.std()

## now look at clipped Z offset dist'n
z_clipper=good_zoff.__abs__()<.1
clipped_zoff=good_zoff[z_clipper]
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.set_ylabel('galaxies')
ax.hist(good_zoff,bins=np.arange(-.305 ,.315,.01))
N,bins=histogram(clipped_zoff,bins=np.arange(-.105 ,.115,.01))
gauss_bins=GetMiddle(bins)
good_gauss=Gauss(gauss_bins,N,threshold=.08)
mu=good_gauss.mean
sigma=good_gauss.sigma
xx,yy=good_gauss.getfitline(100)
ax.plot(xx,yy,'r-')
ax.set_title('(Z bpz - Z spec)/(1 + Z spec) (for matches less than 6 pixels apart with BPZ_ODDS>.9)')
ax.set_xlabel('stats for values excluding outliers with |Z bpz - Z zspec|/(1 + Z spec) >.1 (%s of %s passed clip)\n   mean:%.3f  sigma:%.3f  rms: %.3f' % (z_clipper.sum(),z_clipper.__len__(),mu,sigma,clipped_zoff.std()))
ax.set_xlim(-.305 ,.305)
f.savefig('plt_match_zspecgals2mygals-%s-z_offset_hist-clipped_oddsGTpt9_stats' % (outtag))

show()
