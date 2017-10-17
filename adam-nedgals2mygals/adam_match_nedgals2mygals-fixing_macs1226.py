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
nedcat=astropy.io.ascii.read(ned_file)
bpzcat=astropy.io.fits.open(bpz_file)
outtag="fixing_macs1226"

nedcoords=SkyCoord(nedcat["ra"],nedcat["dec"],frame="fk5")
ned_gmag=nedcat['g'].data
ned_imag=nedcat['i'].data
ned_rmag=nedcat['r'].data
ned_z=nedcat['z'].data
ned_zerr=nedcat['zerr'].data
## now sdss file
sdss_file= "/u/ki/awright/bonnpipeline/adam-nedgals2mygals/cat_sdss_zspecs.tsv"
sdsscat=astropy.io.ascii.read(sdss_file)
sdsscoords=SkyCoord(sdsscat["RA"].data*u.degree,sdsscat["Dec"].data*u.degree,frame="fk5")
idxned,idxsdss, d2d, d3d = sdsscoords.search_around_sky(nedcoords,2*u.arcsec)
sdssmatches=sdsscoords[idxsdss]
matched=zeros((30,),dtype=bool)
matched[idxsdss]=1
d2d_arcsec=d2d*3600*u.arcsec/u.degree

sdss_ra,sdss_dec=sdsscat["RA"].data,sdsscat["Dec"].data
sdss_z=sdsscat["Redshift"].data
Msdss_z=sdss_z[idxsdss]
Msdss_ra=sdss_ra[idxsdss]
Msdss_dec=sdss_dec[idxsdss]
#check if small
Mned_z=ned_z[idxned]
Zned_sdss_diff=Mned_z-Msdss_z
print "max z offset is small:", Zned_sdss_diff.max()
print "max dist[arcsec] is small:", d2d_arcsec.max()

## get unmatched quantities
unmatched=logical_not(matched)
unMsdss_z=sdss_z[unmatched]
unMsdss_ra=sdss_ra[unmatched]
unMsdss_dec=sdss_dec[unmatched]
outtable=astropy.table.table.Table(data=[Msdss_ra,Msdss_dec,Msdss_z,d2d_arcsec],names=["ra","dec","z","d2d_arcsec"])
outtable.write("cat_sdss_matched_zspecs.tsv",format="ascii.commented_header")
outtable=astropy.table.table.Table(data=[unMsdss_ra,unMsdss_dec,unMsdss_z],names=["ra","dec","z"])
outtable.write("cat_sdss_unmatched_zspecs.tsv",format="ascii.commented_header")
## make a catalog from those sdss spec-z's that were missing
addcat=sdsscat[unmatched]
outtable=astropy.table.table.Table(data=[addcat["RA"].data, addcat["Dec"].data, addcat["Redshift"].data, addcat["SN"].data, addcat["Class"].data], names=["RA", "Dec", "Redshift", "SN", "Class"])
outtable.write("cat_additions_from_sdss_zspecs.tsv",format="ascii.commented_header")

##match unmatched things to my cat
unMsdsscoords=SkyCoord(unMsdss_ra*u.degree,unMsdss_dec*u.degree,frame="fk5")

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
objtab=bpzcat[1]
bpzdat=bpztab.data
raw_bpz_z=bpzdat.field("BPZ_Z_B")
raw_bpz_z_min=bpzdat.field("BPZ_Z_B_MIN")
raw_bpz_z_max=bpzdat.field("BPZ_Z_B_MAX")
raw_bpz_odds=bpzdat.field("BPZ_ODDS")
objdat=objtab.data
raw_bpz_ra=objdat.field('ALPHA_J2000')
raw_bpz_dec=objdat.field('DELTA_J2000')
raw_bpz_rmag=objdat.field("MAG_APER1-SUBARU-10_3-1-W-C-RC")
raw_bpz_imag=objdat.field("MAG_APER1-SUBARU-10_3-1-W-C-IC")
raw_bpz_rmagerr=objdat.field("MAGERR_APER1-SUBARU-10_3-1-W-C-RC")
raw_bpz_imagerr=objdat.field("MAGERR_APER1-SUBARU-10_3-1-W-C-IC")
#raw_bpz_bmag=objdat.field("MAG_APER1-SUBARU-10_3-1-W-J-B")
raw_r_ok=raw_bpz_rmag>0
raw_i_ok=raw_bpz_imag>0

#tmp print "ra min/max=",raw_bpz_ra.min(),raw_bpz_ra.max()
#tmp print "dec min/max=",raw_bpz_dec.min(),raw_bpz_dec.max()

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
## SHNT: ok, going from the "Matching Catalog" section here: http://docs.astropy.org/en/stable/coordinates/matchsep.html#matching-catalogs
## get the appropriate matches and plot ned_z vs. z_bpz
#unique matches# idx, d2d, d3d = nedcoords.match_to_catalog_sky(mycoords)
seps=arange(.2,2.2,.1)
Nmatches=[]
Nmatch0s=[]
Nmatch1s=[]
Nmatch2s=[]
Nmatch3orMOREs=[]
for sep in seps:
	idxned,idxmy, d2d, d3d = mycoords.search_around_sky(nedcoords,sep*u.arcsec) #find all matches within 5"
	Nnedmatches=array([(idxned==i).sum() for i in xrange(len(nedcoords))])
	Nnedmatchmean=Nnedmatches.mean()
	Nmatch0=(Nnedmatches==0).sum()
	Nmatch1=(Nnedmatches==1).sum()
	Nmatch2=(Nnedmatches==2).sum()
	Nmatch3orMORE=(Nnedmatches>=3).sum()
	Nmatch2orMORE=(Nnedmatches>=2).sum()
	Nmatches.append(Nnedmatchmean)
	Nmatch0s.append(Nmatch0)
	Nmatch1s.append(Nmatch1)
	Nmatch2s.append(Nmatch2)
	Nmatch3orMOREs.append(Nmatch3orMORE)
	print 'separation=%.1f" : <matches>= %s' % (sep,Nnedmatchmean)

f=figure(figsize=(10,10))
plot(seps,Nmatch0s,label='# matches=0')
plot(seps,Nmatch1s,label='# matches=1')
plot(seps,Nmatch2s,label='# matches=2')
plot(seps,Nmatch3orMOREs,label='# matches>=3')
xlabel('separation [arcsec]')
ylabel('# of objects with 0,1,2,>=3 matches at this separation')
xlim(.2,2.1)
legend()
f.savefig('plt_clip23_cat_NumMatches_vs_separation-narrow')

f=figure(figsize=(10,10))
title('solid black line is probably the key one here (blue dashed+red dashed=solid black).\nStatistics are obviously small, but I would guess 1.2" is a good cutoff distance?')
plot(seps,Nmatch2s,'b--',label='# matches=2')
plot(seps,Nmatch0s,'g-',label='# matches=0')
Nmatch2orMOREs=array(Nmatch3orMOREs)+array(Nmatch2s)
plot(seps,Nmatch2orMOREs,'k-',label='# matches>=2')
plot(seps,Nmatch3orMOREs,'r--',label='# matches>=3')
xlabel('separation [arcsec]')
ylabel('# of objects with 2,>=2, and >=3 matches at this separation')
xlim(.2,2.1)
legend()
f.savefig('plt_clip23_cat_NumMatches2orMORE_vs_separation-narrow')
# separation=0.2" : <matches>=0.567460317
# separation=0.3" : <matches>=0.623015873
# separation=0.4" : <matches>=0.726190476
# separation=0.5" : <matches>=0.813492063
# separation=0.6" : <matches>=0.869047619
# separation=0.7" : <matches>=0.892857142
# separation=0.8" : <matches>=0.896825396
# separation=0.9" : <matches>=0.908730158
# separation=1.0" : <matches>=0.928571428
# separation=1.1" : <matches>=0.936507936
# separation=1.2" : <matches>=0.944444444
# separation=1.3" : <matches>=0.944444444
# separation=1.4" : <matches>=0.952380952
# separation=1.5" : <matches>=0.960317460
# separation=1.6" : <matches>=0.964285714
# separation=1.7" : <matches>=0.972222222
# separation=1.8" : <matches>=0.976190476
# separation=1.9" : <matches>=0.984126984
# separation=2.0" : <matches>=1.007936507
# separation=2.1" : <matches>=1.019841269

idx, d2d, d3d = nedcoords.match_to_catalog_sky(mycoords)
matches=mycoords[idx]
d2d_arcsec=d2d*u.deg.to(u.arcsec)*u.arcsec/u.deg
d2d_pix=d2d_arcsec.value/.2
Mbpz_z=bpz_z[idx]
Mbpz_z_min=bpz_z_min[idx]
Mbpz_z_max=bpz_z_max[idx]
Mbpz_odds=bpz_odds[idx]
Mbpz_rmag=bpz_rmag[idx]
Mbpz_imag=bpz_imag[idx]

## save catalog with all relevent matched information
from astropy.io import ascii
Mbpz_ra=matches.ra.deg
Mbpz_dec=matches.dec.deg
nedra_match=nedcoords.ra.deg
neddec_match=nedcoords.dec.deg
outtable=astropy.table.table.Table(data=[Mbpz_ra,Mbpz_dec,nedra_match,neddec_match,ned_z,Mbpz_z, Mbpz_odds, d2d_pix,d2d_arcsec],names=["Mbpz_ra","Mbpz_dec","nedra_match","neddec_match","ned_z","Mbpz_z"," Mbpz_odds"," d2d_pix","d2d_arcsec"])
outtable.write("matches_nedgals2mygals-%s.tsv" % (outtag),format="ascii.commented_header")

#adam-newplot#
# d2d_arcsec_cap5=where(d2d_arcsec>5*u.arcsec,5,d2d_arcsec)
# f=figure()
# hist(d2d_arcsec_cap5,arange(0,5.2,.1))
# xlim(0,5.2)
# xlabel('separation [arcsec]')
# title('hist of separations capped at 5"')
# savefig('plt_clip23_separations_hist_unique_matches_capped_at5')

#matchdat=bpzdat[idx].copy()
#matchdat.columns.add_col(astropy.io.fits.Column(name="ned_z",array=ned_z,format="1D")) #
#matchdat.columns.add_col(astropy.io.fits.Column(name="d2d_pix",array=d2d_pix,format="1D")) #,format=""
#matchdat.columns.add_col(astropy.io.fits.Column(name="d2d_arcsec",array=d2d_arcsec.value,format="1D")) #,format=""

## SHNT: change to fit mag range
Mbpz_i_ok=i_ok[idx]
Mbpz_r_ok=r_ok[idx]
## now look ddat magnitude differences for 1.2" matches
f=figure(figsize=(10,10))
ax=f.add_subplot(2,1,1)
plot(ned_imag[Mbpz_i_ok],Mbpz_imag[Mbpz_i_ok],'ko',label='mag_i')
ax.set_xlabel('ned i band mag')
ax.set_ylabel('bpz i band mag')
xmin,xmax=ax.get_xlim();ymin,ymax=ax.get_ylim()
minmin=min([xmin,ymin])
maxmax=max([xmax,ymax])
ax.plot([minmin,maxmax],[minmin,maxmax],'k.-')
ax.fill([minmin,minmin,maxmax,maxmax,minmin],[minmin-2,minmin+2,maxmax+2,maxmax-2,minmin-2],'g',alpha=.5)
ax.set_xlim(minmin,maxmax);ax.set_ylim(minmin,maxmax)
ax=f.add_subplot(2,1,2)
plot(ned_rmag[Mbpz_r_ok],Mbpz_rmag[Mbpz_r_ok],'ko',label='mag_r')
ax.set_xlabel('ned r band mag')
ax.set_ylabel('bpz r band mag')
xmin,xmax=ax.get_xlim();ymin,ymax=ax.get_ylim()
minmin=min([xmin,ymin])
maxmax=max([xmax,ymax])
ax.plot([minmin,maxmax],[minmin,maxmax],'k.-')
ax.fill([minmin,minmin,maxmax,maxmax,minmin],[minmin-2,minmin+2,maxmax+2,maxmax-2,minmin-2],'g',alpha=.5)
ax.set_xlim(minmin,maxmax);ax.set_ylim(minmin,maxmax)
f.savefig('plt_clip23_macs1226_correlation_mags')

## check and see how things look if I exclude detections that have a -99 anywhere
allok=Mbpz_i_ok*Mbpz_r_ok
Mbpz_ok_imag=Mbpz_imag[allok]
ned_ok_imag=ned_imag[allok]
Mbpz_ok_rmag=Mbpz_rmag[allok]
ned_ok_rmag=ned_rmag[allok]
bpzMned_imag=Mbpz_ok_imag-ned_ok_imag
bpzMned_rmag=Mbpz_ok_rmag-ned_ok_rmag

## plot hists of ned/bpz i/r mags
f=figure(figsize=(10,10))
suptitle("Hatching is distribution you get when removing all galaxies with -99 in bpz cat\n(in R or I mag) and the ned galaxies matched to them.")
magbins=arange(15,28)-.5
ax=f.add_subplot(2,2,1)
title('ned i band mag')
hist(ned_imag,magbins)
hist(ned_imag[allok],magbins,facecolor=None,hatch="//")
ax=f.add_subplot(2,2,2)
title('ned r band mag')
hist(ned_rmag,magbins)
hist(ned_rmag[allok],magbins,facecolor=None,hatch="//")
ax=f.add_subplot(2,2,3)
title('bpz i band mag')
hist(Mbpz_imag,magbins)
hist(Mbpz_imag[allok],magbins,facecolor=None,hatch="//")
ax=f.add_subplot(2,2,4)
title('bpz r band mag')
hist(Mbpz_rmag,magbins)
hist(Mbpz_rmag[allok],magbins,facecolor=None,hatch="//")
f.savefig('plt_clip23_macs1226_hist_mags')

## ned z distn
#f=figure()
#hist(ned_z,bins=arange(-.1,2.7,.02)+.001)
#savefig('plt_clip23_zspec-all')


## matches are "good" if they are less than 6 pixels apart and BPZ_ODDS>.5
#adam-SHNT# this should be 1.2 arcsec, or 6 pixels now
lt6pix_apart=d2d_pix<6
Mbpz_odds_gtHALF=Mbpz_odds>.5
match_goodenough=lt6pix_apart*Mbpz_odds_gtHALF
goodmatch={}
goodmatch['dist']= d2d_pix[match_goodenough]
goodmatch['Mbpz_z']= Mbpz_z[match_goodenough]
goodmatch['Mbpz_z_min']= Mbpz_z_min[match_goodenough]
goodmatch['Mbpz_z_max']= Mbpz_z_max[match_goodenough]
goodmatch['Mbpz_odds']= Mbpz_odds[match_goodenough]
#tmp goodmatch['unMsdss_z']= unMsdss_z[match_goodenough]
goodmatch['ned_z']= ned_z[match_goodenough]

## save catalog of the good matches
outtable=astropy.table.table.Table( data=[Mbpz_ra[match_goodenough],Mbpz_dec[match_goodenough],nedra_match[match_goodenough],neddec_match[match_goodenough],ned_z[match_goodenough],Mbpz_z[match_goodenough], Mbpz_odds[match_goodenough], d2d_pix[match_goodenough],d2d_arcsec[match_goodenough]], \
		names=["Mbpz_ra","Mbpz_dec","nedra_match","neddec_match","ned_z","Mbpz_z"," Mbpz_odds"," d2d_pix","d2d_arcsec"])
outtable.write("matches_nedgals2mygals-%s_goodmatches.tsv" % (outtag),format="ascii.commented_header")

## plot the good matches
f=plt.figure(figsize=(14,14))
f.suptitle('for matches less than 6 pixels apart with BPZ_ODDS>.5')
ax=f.add_subplot(121)
ax.plot(goodmatch['ned_z'],(goodmatch['Mbpz_z']-goodmatch['ned_z']),'ro')
#tmp plot(goodmatch['unMsdss_z'],(goodmatch['Mbpz_z']-goodmatch['unMsdss_z']),'ro')
ax.set_xlabel('ned_z')
ax.set_ylabel('Mbpz_z-ned_z')
ax.hlines(0,ax.get_xlim()[0],ax.get_xlim()[1])
ax=f.add_subplot(122)
ax.plot(goodmatch['ned_z'],goodmatch['Mbpz_odds'],'bo',label='Mbpz_odds')
ax.plot(goodmatch['ned_z'],goodmatch['dist'],'ko',label='dist')
ax.legend()
#ax.set_title('dist/Mbpz_odds vs. Z ned\n(for matches less than 6 pixels apart with BPZ_ODDS>.5)')
ax.set_xlabel('ned_z')
ax.set_ylabel('dist/Mbpz_odds')
f.savefig('plt_clip23_match_nedgals2mygals-%s-z_compare' % (outtag))

## first plot btwn z=0-.55
f=plt.figure(figsize=(14,14))
f.suptitle('for matches less than 6 pixels apart with BPZ_ODDS>.5')
ax=f.add_subplot(121)
ax.plot(goodmatch['ned_z'],(goodmatch['Mbpz_z']-goodmatch['ned_z']),'ro')
ax.set_xlabel('ned_z')
ax.set_ylabel('Mbpz_z-ned_z')
ax.hlines(0,ax.get_xlim()[0],ax.get_xlim()[1])
ax.set_xlim(0,.55)#;ax.set_ylim(0,.55)
ax=f.add_subplot(122)
ax.plot(goodmatch['ned_z'],goodmatch['Mbpz_odds'],'bo',label='Mbpz_odds')
ax.plot(goodmatch['ned_z'],goodmatch['dist'],'ko',label='dist')
ax.legend()
#ax.set_title('dist/Mbpz_odds vs. Z ned\n(for matches less than 6 pixels apart with BPZ_ODDS>.5)')
ax.set_xlabel('ned_z')
ax.set_ylabel('dist/Mbpz_odds')
ax.set_xlim(0,.55)
f.savefig('plt_clip23_match_nedgals2mygals-%s-z_compare-zoomed' % (outtag))


## first plot btwn z=0-.55
order=goodmatch['ned_z'].argsort()
odds=goodmatch['Mbpz_odds'][order]
uncertain=(odds<.9)
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.errorbar(x=goodmatch['ned_z'][order],y=goodmatch['Mbpz_z'][order],yerr=[goodmatch['Mbpz_z_max'][order]-goodmatch['Mbpz_z'][order],goodmatch['Mbpz_z'][order]-goodmatch['Mbpz_z_min'][order]],fmt='o',mfc='b')
ax.plot(goodmatch['ned_z'][order][uncertain],goodmatch['Mbpz_z'][order][uncertain],'ro')
ax.set_xlabel('ned_z')
ax.set_ylabel('Mbpz_z')
ax.plot([0,1],[0,1],'k.-')
ax.set_xlim(0,.65);ax.set_ylim(0,.65)
ax.set_title('Z bpz vs. Z ned (red marks have BPZ_ODDS<.9)\n(for matches less than 6 pixels apart with BPZ_ODDS>.5)')
f.savefig('plt_clip23_match_nedgals2mygals-%s-z_correlation-zoomed' % (outtag))

## now plot entire range
f=plt.figure(figsize=(14,14))
ax=f.add_subplot(111)
ax.errorbar(x=goodmatch['ned_z'][order],y=goodmatch['Mbpz_z'][order],yerr=[goodmatch['Mbpz_z_max'][order]-goodmatch['Mbpz_z'][order],goodmatch['Mbpz_z'][order]-goodmatch['Mbpz_z_min'][order]],fmt='o',mfc='b')
ax.plot(goodmatch['ned_z'][order][uncertain],goodmatch['Mbpz_z'][order][uncertain],'ro')
xmin,xmax=ax.get_xlim();ymin,ymax=ax.get_ylim()
minmin=min([xmin,ymin])
maxmax=max([xmax,ymax])
ax.set_xlabel('ned_z')
ax.set_ylabel('Mbpz_z')
ax.plot([0,maxmax],[0,maxmax],'k.-')
ax.set_xlim(minmin,maxmax);ax.set_ylim(minmin,maxmax)
ax.set_title('Z bpz vs. Z ned (red marks have BPZ_ODDS<.9)\n(for matches less than 6 pixels apart with BPZ_ODDS>.5)')
f.savefig('plt_clip23_match_nedgals2mygals-%s-z_correlation' % (outtag))

#ymin,ymax=ax.get_ylim()
#xmin,xmax=ax.get_xlim()
#minmin=np.min([xmin,ymin])
#maxmax=np.max([xmax,ymax])
#ax.set_ylim([minmin,maxmax])
#ax.set_xlim([minmin,maxmax])
ned_z_good=goodmatch['ned_z'][order];Mbpz_z_good=goodmatch['Mbpz_z'][order]
good_zoff=goodmatch['Mbpz_z'][order]-goodmatch['ned_z'][order]
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
f.savefig('plt_clip23_match_nedgals2mygals-%s-z_offset_hist-clipped_stats' % (outtag))

Mbpz_i_ok_dcut=Mbpz_i_ok*lt6pix_apart
Mbpz_r_ok_dcut=Mbpz_r_ok*lt6pix_apart
f=figure(figsize=(10,10))
ax=f.add_subplot(2,1,1)
plot(ned_imag[Mbpz_i_ok_dcut],Mbpz_imag[Mbpz_i_ok_dcut],'ko',label='mag_i')
ax.set_xlabel('ned i band mag')
ax.set_ylabel('bpz i band mag')
xmin,xmax=ax.get_xlim();ymin,ymax=ax.get_ylim()
minmin=min([xmin,ymin])
maxmax=max([xmax,ymax])
ax.plot([minmin,maxmax],[minmin,maxmax],'k.-')
ax.fill([minmin,minmin,maxmax,maxmax,minmin],[minmin-2,minmin+2,maxmax+2,maxmax-2,minmin-2],'g',alpha=.5)
ax.set_xlim(minmin,maxmax);ax.set_ylim(minmin,maxmax)
ax=f.add_subplot(2,1,2)
plot(ned_rmag[Mbpz_r_ok_dcut],Mbpz_rmag[Mbpz_r_ok_dcut],'ko',label='mag_r')
ax.set_xlabel('ned r band mag')
ax.set_ylabel('bpz r band mag')
xmin,xmax=ax.get_xlim();ymin,ymax=ax.get_ylim()
minmin=min([xmin,ymin])
maxmax=max([xmax,ymax])
ax.plot([minmin,maxmax],[minmin,maxmax],'k.-')
ax.fill([minmin,minmin,maxmax,maxmax,minmin],[minmin-2,minmin+2,maxmax+2,maxmax-2,minmin-2],'g',alpha=.5)
ax.set_xlim(minmin,maxmax);ax.set_ylim(minmin,maxmax)
f.savefig('plt_clip23_macs1226_correlation_mags-1pt2arcsec_cut')

show()
