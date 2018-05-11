#! /usr/bin/env python
#adam-does# plots comparison between the bpz redshifts and external reference spectroscopic redshifts

import sys,os,inspect ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
from import_tools import *
curfile=os.path.abspath(inspect.getfile(inspect.currentframe()))
FileString=os.path.basename(curfile)
args=imagetools.ArgCleaner(sys.argv)
import numpy as np
import matplotlib.pyplot as plt
import astropy
from astropy.coordinates import SkyCoord
from astropy import units as u

## From match_specz_and_bpz.py
#outtable=astropy.table.table.Table( data=[good['zspec_ra'],good['zspec_dec'],good['ref_z'],good['bpz_z'],good['bpz_ra'],good['bpz_dec'],good['bpz_SeqNr'],good['bpz_z_min'],good['bpz_z_max'],good['bpz_odds'],good['bpz_imag'],good['bpz_rmag'],good['bpz_imagerr'],good['bpz_rmagerr'],good['bpz_i_ok'],good['bpz_r_ok'],good['bpz_allok'],good['dist']], \
#				                names=['ref_ra','ref_dec','ref_z','bpz_z','bpz_ra','bpz_dec','bpz_SeqNr','bpz_z_min','bpz_z_max','bpz_odds','bpz_I','bpz_R','bpz_Ierr','bpz_Rerr','bpz_I_ok','bpz_R_ok','bpz_allok','dist'])
#outtable.write("match_specz_and_bpz_cats.tsv",format="ascii.commented_header")

## From codes that open up the other files i dont need
########ned_file= "/u/ki/awright/bonnpipeline/adam-nedgals2mygals/sdssj1226_redshifts_converted.tsv"
########bpz_file= "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.bpztab.cat"
########sdss_file="/u/ki/awright/bonnpipeline/adam-nedgals2mygals/cat_additions_from_sdss_zspecs.tsv" #'Survey', 'RA', 'Dec', 'Redshift', 'SN', 'Class'
########sdsscat=astropy.io.ascii.read(sdss_file)
########nedcat=astropy.io.ascii.read(ned_file)
########bpzcat=astropy.io.fits.open(bpz_file)
######### primary OBJECTS PHOTINFO FIELDS BPZTAB
########bpztab=bpzcat[-1]
########objtab=bpzcat[1]
########bpzdat=bpztab.data
########objdat=objtab.data
########raw_bpz_z=bpzdat.field("BPZ_Z_B")
########raw_bpz_ra=objdat.field('ALPHA_J2000')

cat=astropy.io.ascii.read("match_specz_and_bpz_cats.tsv") #,format="ascii.commented_header")
names=['ref_ra','ref_dec','ref_z','bpz_z','bpz_ra','bpz_dec','bpz_SeqNr','bpz_z_min','bpz_z_max','bpz_odds','bpz_I','bpz_R','bpz_Ierr','bpz_Rerr','bpz_I_ok','bpz_R_ok','bpz_allok','dist']
from numpy import *
cat['bpz_allok'].dtype=bool
#sys.exit()
### PLOTS

#adam-SHNT# ok, start plotting here
order=cat['ref_z'].argsort()
odds=cat['bpz_odds'][order]
uncertain_mags=logical_not(cat['bpz_allok'][order])
uncertain_odds=(odds<.9)
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.errorbar(x=cat['ref_z'][order][odds>.5],y=cat['bpz_z'][order][odds>.5],yerr=[cat['bpz_z_max'][order][odds>.5]-cat['bpz_z'][order][odds>.5],cat['bpz_z'][order][odds>.5]-cat['bpz_z_min'][order][odds>.5]],fmt='o',mfc='b')
ax.plot(cat['ref_z'][order][(odds>.5) * uncertain_mags],cat['bpz_z'][order][(odds>.5) * uncertain_mags],'ys',label="mag=-99")
ax.plot(cat['ref_z'][order][(odds>.5) * uncertain_odds],cat['bpz_z'][order][(odds>.5) * uncertain_odds],'ro',label="odds<.9")
ax.set_xlabel('zspec')
ax.set_ylabel('bpz_z')
ax.plot([0,1],[0,1],'k.-')
ax.set_xlim(0.3,.65);ax.set_ylim(0.3,.65)
ax.set_title('Z bpz vs. Z spec (for matches with BPZ_ODDS>.5)')
legend(loc="upper left")
f.savefig('plot_specz_and_bpz_correlation-zoomed-clipped_ODDS_gt_pt5' )

## now plot entire range
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.errorbar(x=cat['ref_z'][order][odds>.5],y=cat['bpz_z'][order][odds>.5],yerr=[cat['bpz_z_max'][order][odds>.5]-cat['bpz_z'][order][odds>.5],cat['bpz_z'][order][odds>.5]-cat['bpz_z_min'][order][odds>.5]],fmt='o',mfc='b')
ax.plot(cat['ref_z'][order][(odds>.5) * uncertain_mags],cat['bpz_z'][order][(odds>.5) * uncertain_mags],'ys',label="mag=-99")
ax.plot(cat['ref_z'][order][(odds>.5) * uncertain_odds],cat['bpz_z'][order][(odds>.5) * uncertain_odds],'ro',label="odds<.9")
xmin,xmax=ax.get_xlim();ymin,ymax=ax.get_ylim()
minmin=min([xmin,ymin])
if minmin<-.01:minmin=-.01
maxmax=max([xmax,ymax])
ax.set_xlabel('zspec')
ax.set_ylabel('bpz_z')
ax.plot([-0.2,maxmax],[-0.2,maxmax],'k.-')
ax.set_xlim(minmin,maxmax);ax.set_ylim(minmin,maxmax)
ax.set_title('Z bpz vs. Z spec (for matches with BPZ_ODDS>.5)')
legend(loc="upper left")
f.savefig('plot_specz_and_bpz_correlation-clipped_ODDS_gt_pt5' )

## first plot btwn z=0-.55
order=cat['ref_z'].argsort()
odds=cat['bpz_odds'][order]
uncertain_mags=logical_not(cat['bpz_allok'][order])
uncertain_odds=(odds<.9)
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.errorbar(x=cat['ref_z'][order],y=cat['bpz_z'][order],yerr=[cat['bpz_z_max'][order]-cat['bpz_z'][order],cat['bpz_z'][order]-cat['bpz_z_min'][order]],fmt='o',mfc='b')
ax.plot(cat['ref_z'][order][uncertain_mags],cat['bpz_z'][order][uncertain_mags],'ys',label="mag=-99")
ax.plot(cat['ref_z'][order][uncertain_odds],cat['bpz_z'][order][uncertain_odds],'ro',label="odds<.9")
ax.set_xlabel('zspec')
ax.set_ylabel('bpz_z')
ax.plot([0,1],[0,1],'k.-')
ax.set_xlim(0.3,.65);ax.set_ylim(0.3,.65)
ax.set_title('Z bpz vs. Z spec')
legend(loc="upper left")
f.savefig('plot_specz_and_bpz_correlation-zoomed' )

## now plot entire range
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.errorbar(x=cat['ref_z'][order],y=cat['bpz_z'][order],yerr=[cat['bpz_z_max'][order]-cat['bpz_z'][order],cat['bpz_z'][order]-cat['bpz_z_min'][order]],fmt='o',mfc='b')
ax.plot(cat['ref_z'][order][uncertain_mags],cat['bpz_z'][order][uncertain_mags],'ys',label="mag=-99")
ax.plot(cat['ref_z'][order][uncertain_odds],cat['bpz_z'][order][uncertain_odds],'ro',label="odds<.9")
xmin,xmax=ax.get_xlim();ymin,ymax=ax.get_ylim()
minmin=min([xmin,ymin])
if minmin<-.01:minmin=-.01
maxmax=max([xmax,ymax])
ax.set_xlabel('zspec')
ax.set_ylabel('bpz_z')
ax.plot([-0.2,maxmax],[-0.2,maxmax],'k.-')
ax.set_xlim(minmin,maxmax);ax.set_ylim(minmin,maxmax)
ax.set_title('Z bpz vs. Z spec')
legend(loc="upper left")
f.savefig('plot_specz_and_bpz_correlation' )

from fitter import Gauss
ref_z_good=cat['ref_z'][order];bpz_z_good=cat['bpz_z'][order]
good_zoff=(cat['bpz_z'][order]-cat['ref_z'][order])/(1+cat['ref_z'][order])
print "cat matches offset mean:",good_zoff.mean()
print "cat matches offset std:",good_zoff.std()

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
ax.set_title('(Z bpz - Z spec)/(1 + Z spec)')
ax.set_xlabel('stats for values excluding outliers with |Z bpz - Z zspec|/(1 + Z spec) >.1 (%s of %s passed clip)\n   mean:%.3f  sigma:%.3f  rms: %.3f' % (z_clipper.sum(),z_clipper.__len__(),mu,sigma,clipped_zoff.std()))
ax.set_xlim(-.305 ,.305)
f.savefig('plot_specz_and_bpz_offset_hist' )

## now look at clipped Z offset dist'n
oddsGT9=odds>.9
better_zoff=good_zoff[oddsGT9]
z_clipper=better_zoff.__abs__()<.1
clipped_zoff=better_zoff[z_clipper]
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.set_ylabel('galaxies')
ax.hist(better_zoff,bins=np.arange(-.305 ,.315,.01))
N,bins=histogram(clipped_zoff,bins=np.arange(-.105 ,.115,.01))
gauss_bins=GetMiddle(bins)
better_gauss=Gauss(gauss_bins,N,threshold=.08)
mu=better_gauss.mean
sigma=better_gauss.sigma
xx,yy=better_gauss.getfitline(100)
ax.plot(xx,yy,'r-')
ax.set_title('(Z bpz - Z spec)/(1 + Z spec) (for matches with BPZ_ODDS>.9)')
ax.set_xlabel('stats for values excluding outliers with |Z bpz - Z zspec|/(1 + Z spec) >.1 (%s of %s passed clip)\n   mean:%.3f  sigma:%.3f  rms: %.3f' % (z_clipper.sum(),z_clipper.__len__(),mu,sigma,clipped_zoff.std()))
ax.set_xlim(-.305 ,.305)
f.savefig('plot_specz_and_bpz_offset_hist-clipped_ODDS_gt_pt9' )

show()
