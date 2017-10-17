#! /usr/bin/env python
#adam-does# matches the redshifts from our pipeline/bpz to external reference redshifts
#adam-example# ipython -i -- ./adam_match_nedgals2mygals.py nedcat bpzcat =astropy.io.ascii.read("/u/ki/awright/bonnpipeline/adam_ned_MACS1226+21_galaxies.tsv")
#adam-example# ipython -i -- ./adam_match_nedgals2mygals.py /u/ki/awright/bonnpipeline/adam_ned_MACS1226+21_galaxies.tsv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.bpztab.cat
#adam-example# ipython -i -- ./adam_match_nedgals2mygals.py /u/ki/awright/bonnpipeline/adam-nedgals2mygals/sdssj1226_redshifts_converted.tsv  /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.bpztab.cat

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

ned_file=args[0]
bpz_file=args[1]
nedcat=astropy.io.ascii.read(ned_file)
bpzcat=astropy.io.fits.open(bpz_file)

if len(args)>2:
	outtag=args[-1]
else:
	outtag="tagless"


nedcoords=SkyCoord(nedcat["ra"],nedcat["dec"],frame="fk5")
ned_z=nedcat['z'].data
ned_zerr=nedcat['zerr'].data
#adam-SHNT#

#adam-example# nedcat=astropy.io.ascii.read("/u/ki/awright/bonnpipeline/adam_ned_MACS1226+21_galaxies.tsv")
#adam-example# nedcoords=SkyCoord(nedcat["RA_deg"],nedcat["DEC_deg"],frame="fk5")
#adam-example# ned_z=nedcat['Redshift'].data
## ran this to make an ldaccat with bpz redshifts and MACS1226+21.calibrated.cat coordinates
#ldacaddtab -i MACS1226+21.calibrated.cat -p all_bpzAPER1CWWSB_capak.list1_0.bpz.tab -t STDTAB -o MACS1226+21.calibrated.bpztab.cat.tmp
#ldacrentab -i MACS1226+21.calibrated.bpztab.cat.tmp -t STDTAB BPZTAB -o MACS1226+21.calibrated.bpztab.cat
#rm MACS1226+21.calibrated.bpztab.cat.tmp

#adam-example# bpzcat=astropy.io.fits.open("/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.bpztab.cat")
# os.system("ldacdesc -i /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.bpztab.cat")
# primary OBJECTS PHOTINFO FIELDS BPZTAB
bpztab=bpzcat[-1]
objects=bpzcat[1]
objdat=objects.data
bpzdat=bpztab.data
myra=objdat.field('ALPHA_J2000')
mydec=objdat.field('DELTA_J2000')
#fk5 is J2000 by default!
mycoords=SkyCoord(myra*u.degree,mydec*u.degree,frame="fk5")
## SHNT: ok, going from the "Matching Catalog" section here: http://docs.astropy.org/en/stable/coordinates/matchsep.html#matching-catalogs
## get the appropriate matches and plot ned_z vs. z_bpz
idx, d2d, d3d = nedcoords.match_to_catalog_sky(mycoords)
matches=mycoords[idx]
d2d_arcsec=d2d*u.deg.to(u.arcsec)*u.arcsec/u.deg
d2d_pix=d2d_arcsec.value/.2
bpz_z=bpztab.data.field("BPZ_Z_B")[idx]
bpz_z_min=bpztab.data.field("BPZ_Z_B_MIN")[idx]
bpz_z_max=bpztab.data.field("BPZ_Z_B_MAX")[idx]
bpz_odds=bpztab.data.field("BPZ_ODDS")[idx]

## save catalog with all relevent matched information
from astropy.io import ascii
myra_match=matches.ra.deg
mydec_match=matches.dec.deg
nedra_match=nedcoords.ra.deg
neddec_match=nedcoords.dec.deg
outtable=astropy.table.table.Table(data=[myra_match,mydec_match,nedra_match,neddec_match,ned_z,bpz_z, bpz_odds, d2d_pix,d2d_arcsec],names=["myra_match","mydec_match","nedra_match","neddec_match","ned_z","bpz_z"," bpz_odds"," d2d_pix","d2d_arcsec"])
outtable.write("matches_nedgals2mygals-%s.tsv" % (outtag),format="ascii.commented_header")
#matchdat=bpzdat[idx].copy()
#matchdat.columns.add_col(astropy.io.fits.Column(name="ned_z",array=ned_z,format="1D")) #
#matchdat.columns.add_col(astropy.io.fits.Column(name="d2d_pix",array=d2d_pix,format="1D")) #,format=""
#matchdat.columns.add_col(astropy.io.fits.Column(name="d2d_arcsec",array=d2d_arcsec.value,format="1D")) #,format=""


## matches are "good" if they are less than 5 pixels apart and BPZ_ODDS>.5
lt5pix_apart=d2d_pix<5
bpz_odds_gtHALF=bpz_odds>.5
match_goodenough=lt5pix_apart*bpz_odds_gtHALF
goodmatch={}
goodmatch['dist']= d2d_pix[match_goodenough]
goodmatch['bpz_z']= bpz_z[match_goodenough]
goodmatch['bpz_z_min']= bpz_z_min[match_goodenough]
goodmatch['bpz_z_max']= bpz_z_max[match_goodenough]
goodmatch['bpz_odds']= bpz_odds[match_goodenough]
goodmatch['ned_z']= ned_z[match_goodenough]

## save catalog of the good matches
outtable=astropy.table.table.Table( data=[myra_match[match_goodenough],mydec_match[match_goodenough],nedra_match[match_goodenough],neddec_match[match_goodenough],ned_z[match_goodenough],bpz_z[match_goodenough], bpz_odds[match_goodenough], d2d_pix[match_goodenough],d2d_arcsec[match_goodenough]], \
		names=["myra_match","mydec_match","nedra_match","neddec_match","ned_z","bpz_z"," bpz_odds"," d2d_pix","d2d_arcsec"])
outtable.write("matches_nedgals2mygals-%s_goodmatches.tsv" % (outtag),format="ascii.commented_header")

## plot the good matches
f=plt.figure(figsize=(14,14))
f.suptitle('for matches less than 5 pixels apart with BPZ_ODDS>.5')
ax=f.add_subplot(121)
ax.plot(goodmatch['ned_z'],(goodmatch['bpz_z']-goodmatch['ned_z']),'ro')
ax.set_xlabel('ned_z')
ax.set_ylabel('bpz_z-ned_z')
ax.hlines(0,ax.get_xlim()[0],ax.get_xlim()[1])
ax=f.add_subplot(122)
ax.plot(goodmatch['ned_z'],goodmatch['bpz_odds'],'bo',label='bpz_odds')
ax.plot(goodmatch['ned_z'],goodmatch['dist'],'ko',label='dist')
ax.legend()
#ax.set_title('dist/bpz_odds vs. Z ned\n(for matches less than 5 pixels apart with BPZ_ODDS>.5)')
ax.set_xlabel('ned_z')
ax.set_ylabel('dist/bpz_odds')
f.savefig('plt_match_nedgals2mygals-%s-z_compare' % (outtag))

## first plot btwn z=0-.55
f=plt.figure(figsize=(14,14))
f.suptitle('for matches less than 5 pixels apart with BPZ_ODDS>.5')
ax=f.add_subplot(121)
ax.plot(goodmatch['ned_z'],(goodmatch['bpz_z']-goodmatch['ned_z']),'ro')
ax.set_xlabel('ned_z')
ax.set_ylabel('bpz_z-ned_z')
ax.hlines(0,ax.get_xlim()[0],ax.get_xlim()[1])
ax.set_xlim(0,.55)#;ax.set_ylim(0,.55)
ax=f.add_subplot(122)
ax.plot(goodmatch['ned_z'],goodmatch['bpz_odds'],'bo',label='bpz_odds')
ax.plot(goodmatch['ned_z'],goodmatch['dist'],'ko',label='dist')
ax.legend()
#ax.set_title('dist/bpz_odds vs. Z ned\n(for matches less than 5 pixels apart with BPZ_ODDS>.5)')
ax.set_xlabel('ned_z')
ax.set_ylabel('dist/bpz_odds')
ax.set_xlim(0,.55)
f.savefig('plt_match_nedgals2mygals-%s-z_compare-zoomed' % (outtag))


## first plot btwn z=0-.55
order=goodmatch['ned_z'].argsort()
odds=goodmatch['bpz_odds'][order]
uncertain=(odds<.9)
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.errorbar(x=goodmatch['ned_z'][order],y=goodmatch['bpz_z'][order],yerr=[goodmatch['bpz_z_max'][order]-goodmatch['bpz_z'][order],goodmatch['bpz_z'][order]-goodmatch['bpz_z_min'][order]],fmt='o',mfc='b')
ax.plot(goodmatch['ned_z'][order][uncertain],goodmatch['bpz_z'][order][uncertain],'ro')
ax.set_xlabel('ned_z')
ax.set_ylabel('bpz_z')
ax.plot([0,1],[0,1],'k.-')
ax.set_xlim(0,.65);ax.set_ylim(0,.65)
ax.set_title('Z bpz vs. Z ned (red marks have BPZ_ODDS<.9)\n(for matches less than 5 pixels apart with BPZ_ODDS>.5)')
f.savefig('plt_match_nedgals2mygals-%s-z_correlation-zoomed' % (outtag))

## now plot entire range
order=goodmatch['ned_z'].argsort()
odds=goodmatch['bpz_odds'][order]
uncertain=(odds<.9)
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.errorbar(x=goodmatch['ned_z'][order],y=goodmatch['bpz_z'][order],yerr=[goodmatch['bpz_z_max'][order]-goodmatch['bpz_z'][order],goodmatch['bpz_z'][order]-goodmatch['bpz_z_min'][order]],fmt='o',mfc='b')
ax.plot(goodmatch['ned_z'][order][uncertain],goodmatch['bpz_z'][order][uncertain],'ro')
xmin,xmax=ax.get_xlim();ymin,ymax=ax.get_ylim()
minmin=min([xmin,ymin])
maxmax=max([xmax,ymax])
ax.set_xlabel('ned_z')
ax.set_ylabel('bpz_z')
ax.plot([0,maxmax],[0,maxmax],'k.-')
ax.set_xlim(minmin,maxmax);ax.set_ylim(minmin,maxmax)
ax.set_title('Z bpz vs. Z ned (red marks have BPZ_ODDS<.9)\n(for matches less than 5 pixels apart with BPZ_ODDS>.5)')
f.savefig('plt_match_nedgals2mygals-%s-z_correlation' % (outtag))

#ymin,ymax=ax.get_ylim()
#xmin,xmax=ax.get_xlim()
#minmin=np.min([xmin,ymin])
#maxmax=np.max([xmax,ymax])
#ax.set_ylim([minmin,maxmax])
#ax.set_xlim([minmin,maxmax])
ned_z_good=goodmatch['ned_z'][order];bpz_z_good=goodmatch['bpz_z'][order]
good_zoff=goodmatch['bpz_z'][order]-goodmatch['ned_z'][order]
print "good matches offset mean:",good_zoff.mean()
print "good matches offset std:",good_zoff.std()

## now look at clipped Z offset dist'n
z_clipper=good_zoff.__abs__()<.1
clipped_zoff=good_zoff[z_clipper]
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.set_ylabel('galaxies')
ax.hist(good_zoff,bins=np.arange(-.305 ,.315,.01))
ax.set_title('Z bpz - Z ned')
ax.set_xlabel('stats for values excluding outliers with |Z bpz - Z ned|>.1 (%s of %s passed clip)\n   mean:%.3f    rms: %.3f' % (z_clipper.sum(),z_clipper.__len__(),clipped_zoff.mean(),clipped_zoff.std()) )
ax.set_xlim(-.305 ,.305)
f.savefig('plt_match_nedgals2mygals-%s-z_offset_hist-clipped_stats' % (outtag))
plt.show()

