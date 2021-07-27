#! /usr/bin/env python
#adam-predecessor# cat_matcher.py does more stuff but is less concise
#adam-useful# document this later, it's helpful! PUT IN cattools.py 
from matplotlib.pylab import *
import astropy.io.fits as pyfits
import astropy
import ldac
sys.path.append('/u/ki/awright/quick/pythons/')
import cattools
import imagetools
from astropy.coordinates import SkyCoord
from astropy import units as u
ns=globals()

oldfls={'cut_lensing': '//nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/good/cut_lensing.cat',
'coadd_filtered': '//nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/good/coadd_filtered.cat',
'coadd_photo': '//nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/good/coadd_photo.cat',
'photometry': '/nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.slr.cat'}

newfls={'cut_lensing': '/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554/cut_lensing.cat',
'coadd_filtered': '/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554/coadd_filtered.cat',
'coadd_photo': '/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554/coadd_photo.cat',
'photometry': '/u/ki/awright/data/fgas_pz_masses/MACS1115+01.W-C-RC.cat'}

import os
for fl in newfls.values()+oldfls.values():
    if not os.path.isfile(fl):
        raise Exception("file does not exist: "+fl)

oldfl=oldfls['coadd_photo']
newfl=newfls['coadd_photo']

# ds9e /u/ki/awright/data/MACS1115+01/W-C-RC/SCIENCE/coadd_MACS1115+01_all/coadd.fits -catalog import tsv /u/ki/awright/data/fgas_pz_masses/compare_MACS1115+01+01_and_explore_NFILT_alpha_delta/old_unmatched_photometry_old2new.cat -catalog import tsv /u/ki/awright/data/fgas_pz_masses/compare_MACS1115+01+01_and_explore_NFILT_alpha_delta/old_unmatched_cut_lensing_old2new.cat &
# -catalog import tsv /u/ki/awright/data/fgas_pz_masses/compare_MACS1115+01+01_and_explore_NFILT_alpha_delta/old_unmatched_photometry_old2new.cat -catalog import tsv /u/ki/awright/data/fgas_pz_masses/compare_MACS1115+01+01_and_explore_NFILT_alpha_delta/old_unmatched_cut_lensing_old2new.cat &
finaldir_in='/u/ki/awright/data/fgas_pz_masses/compare_MACS1115+01_io/inputs_regs_and_annulus_removed/'
finaldir_out='/u/ki/awright/data/fgas_pz_masses/compare_MACS1115+01_io/outputs/'



## get cut_lensing.cat matched
compare_dir='/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/compare_oct24_2018/'
newcatfl='/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554/cut_lensing.cat'
compare_dir='/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/good_from_2011_changed_faintmag_cut_and_masks_matched/'
oldcatfl='/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/good_from_2011_changed_faintmag_cut_and_masks_matched/cut_lensing.cat'
oldcatfl_pre_match=oldcatfl+'-pre_match.cat'
#os.system('mv %s %s' % (oldcatfl,oldcatfl_pre_match))
lensoldfl='/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/good_from_2011_changed_faintmag_cut_and_masks_gscut/cut_lensing.cat'
lensnewWoldRSfl='/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554_gscut_rgcut_rhcut_starcut_oldRScut/cut_lensing.cat'
lensnewWnewRSfl='/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554_gscut_rgcut_rhcut_starcut_newRScut/cut_lensing.cat'
mold,mnew,d2d,unmold,unmnew=cattools.match_pair_stats(lensoldfl,lensnewWoldRSfl,tag='comparison_btwn_old_and_newWoldRScut',output_dir='/u/ki/awright/wtgpipeline/scratch/')
mold,mnew,d2d,unmold,unmnew=cattools.match_pair_stats(lensnewWnewRSfl,lensnewWoldRSfl,tag='comparison_btwn_old_and_newWoldRScut',output_dir='/u/ki/awright/wtgpipeline/scratch/')

sys.exit()


mold,mnew,d2d,unmold,unmnew=cattools.match_unordered(oldcatfl_pre_match,newcatfl)
tag='gabodsid1554'
mnew.saveas(compare_dir+'new_matched_'+tag+'_paired.cat',overwrite=True)
mold.saveas(compare_dir+'old_matched_'+tag+'_paired.cat',overwrite=True)
unmnew.saveas(compare_dir+'new_unmatched_'+tag+'_paired.cat',overwrite=True)
unmold.saveas(compare_dir+'old_unmatched_'+tag+'_paired.cat',overwrite=True)
bothold=unmold.append(mold)
bothnew=unmnew.append(mnew)

f=figure(figsize=(12,8))
suptitle('Comparison of new/old galaxy properties of catalog objects IGNORING MATCHING \n(old has the same faintmag cut and masks as new)')
f.add_subplot(2,3,1) ; x,bins,patch=hist( bothnew['rh'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( bothold['rh'], bins=bins, color='r',label='old', histtype='step',density=True)
title('rh')
f.add_subplot(2,3,2) ; x,bins,patch=hist( bothnew['snratio'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( bothold['snratio'], bins=bins, color='r',label='old', histtype='step',density=True)
title('snratio')
legend()
f.add_subplot(2,3,3) ; x,bins,patch=hist( bothnew['gs'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( bothold['gs'], bins=bins, color='r',label='old', histtype='step',density=True)
title('gs')
f.add_subplot(2,3,4) ; x,bins,patch=hist( bothnew['rg'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( bothold['rg'], bins=bins, color='r',label='old', histtype='step',density=True)
title('rg')
f.add_subplot(2,3,5) ; x,bins,patch=hist( bothnew['MAG_APER1-SUBARU-10_2-1-W-C-RC'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( bothold['MAG_APER1-SUBARU-COADD-1-W-C-RC'], bins=bins, color='r',label='old', histtype='step',density=True)
legend()
title('R mag')
f.add_subplot(2,3,6) ; x,bins,patch=hist( bothnew['Pgs'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( bothold['Pgs'], bins=bins, color='r',label='old', histtype='step',density=True)
title('Pgs')
f.savefig('plt_MACS1115_old_new_difference_hists')

f=figure(figsize=(12,8))
suptitle('Comparison of new/old galaxy properties of UNMATCHED catalog objects \n(old has the same faintmag cut and masks as new)')
f.add_subplot(2,3,1) ; x,bins,patch=hist( unmnew['rh'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( unmold['rh'], bins=bins, color='r',label='old', histtype='step',density=True)
title('rh')
f.add_subplot(2,3,2) ; x,bins,patch=hist( unmnew['snratio'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( unmold['snratio'], bins=bins, color='r',label='old', histtype='step',density=True)
title('snratio')
legend()
f.add_subplot(2,3,3) ; x,bins,patch=hist( unmnew['gs'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( unmold['gs'], bins=bins, color='r',label='old', histtype='step',density=True)
title('gs')
f.add_subplot(2,3,4) ; x,bins,patch=hist( unmnew['rg'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( unmold['rg'], bins=bins, color='r',label='old', histtype='step',density=True)
title('rg')
f.add_subplot(2,3,5) ; x,bins,patch=hist( unmnew['MAG_APER1-SUBARU-10_2-1-W-C-RC'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( unmold['MAG_APER1-SUBARU-COADD-1-W-C-RC'], bins=bins, color='r',label='old', histtype='step',density=True)
legend()
title('R mag')
f.add_subplot(2,3,6) ; x,bins,patch=hist( unmnew['Pgs'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( unmold['Pgs'], bins=bins, color='r',label='old', histtype='step',density=True)
title('Pgs')
f.savefig('plt_MACS1115_old_new_unmatched_difference_hists')

f=figure(figsize=(12,8))
suptitle('Comparison of new/old galaxy properties of MATCHED catalog objects \n(old has the same faintmag cut and masks as new)')
f.add_subplot(2,3,1) ; x,bins,patch=hist( mnew['rh'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( mold['rh'], bins=bins, color='r',label='old', histtype='step',density=True)
title('rh')
f.add_subplot(2,3,2) ; x,bins,patch=hist( mnew['snratio'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( mold['snratio'], bins=bins, color='r',label='old', histtype='step',density=True)
title('snratio')
legend()
f.add_subplot(2,3,3) ; x,bins,patch=hist( mnew['gs'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( mold['gs'], bins=bins, color='r',label='old', histtype='step',density=True)
title('gs')
f.add_subplot(2,3,4) ; x,bins,patch=hist( mnew['rg'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( mold['rg'], bins=bins, color='r',label='old', histtype='step',density=True)
title('rg')
f.add_subplot(2,3,5) ; x,bins,patch=hist( mnew['MAG_APER1-SUBARU-10_2-1-W-C-RC'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( mold['MAG_APER1-SUBARU-COADD-1-W-C-RC'], bins=bins, color='r',label='old', histtype='step',density=True)
legend()
title('R mag')
f.add_subplot(2,3,6) ; x,bins,patch=hist( mnew['Pgs'], color='b',label='new', histtype='step',density=True)
x,bins2,patch=hist( mold['Pgs'], bins=bins, color='r',label='old', histtype='step',density=True)
title('Pgs')
f.savefig('plt_MACS1115_old_new_matched_difference_hists')
show()

sys.exit()


## get RS-new out of cut_lensing_RS_remains.cat
datadir='/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/good_from_2011_changed_faintmag_cut_and_masks_and_RS/'
RSnewfl="/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554/MACS1115+01_redsequence.cat"
#RSnewfl="/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554/coadd_rs.cat"
oldlensfl=datadir+'cut_lensing_RS_remains.cat'
catfl=datadir+'cut_colors.cat'
t=ldac.openObjectFile(catfl)
rglargecut=4.53896
rgcut = t['rg']<rglargecut
clcut = t['cl']<100
#(((snratio_scaled1 > 3.0 AND rh > 2.01774) AND Pgs > 0.1) AND cl=0)
cut3 = (t['snratio_scaled1'] > 3.0) * (t['rh'] > 2.01774) * (t['Pgs'] > 0.1) * (t['cl']==0)
allcuts=clcut*cut3*rgcut
tpassed=t.filter(allcuts)
tpassed.saveas(datadir+'cut_lensing_RS_remains.cat',overwrite=True)

oldfo=pyfits.open(oldlensfl)
newfo=pyfits.open(RSnewfl)
newcat=ldac.LDACCat(newfo['OBJECTS'])
oldcat=ldac.LDACCat(oldfo['OBJECTS'])

ra_key,dec_key='ALPHA_J2000','DELTA_J2000'
new = SkyCoord(ra=newcat[ra_key]*u.degree, dec=newcat[dec_key]*u.degree)
old = SkyCoord(ra=oldcat[ra_key]*u.degree, dec=oldcat[dec_key]*u.degree)

matchmin=0.0 ; matchmax=0.8
ridx, rd2d, rd3d = old.match_to_catalog_sky(new)


match_array=(matchmin<=rd2d.arcsec)*(rd2d.arcsec<matchmax)
print 'matching fraction: ',match_array.mean()
#moldcat=oldcat.filter(match_array)
notmoldcat=oldcat.filter(logical_not(match_array))
print 'of ',len(oldcat),'there are these many left:',sum(logical_not(match_array))
notmoldcat.saveas(datadir+'cut_lensing.cat',overwrite=True)
sys.exit()

##
compare_dir='/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/good_from_2011_changed_faintmag_cut_matched/'
oldcatfl='/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/good_from_2011_changed_faintmag_cut_matched/cut_lensing.cat'
#adam-old# compare_dir='/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/good_from_2011_changed_faintmag_cut_and_masks_matched/'
#adam-old# oldcatfl='/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/good_from_2011_changed_faintmag_cut_and_masks_matched/cut_lensing.cat'
oldcatfl_pre_match=oldcatfl+'-pre_match.cat'
os.system('mv %s %s' % (oldcatfl,oldcatfl_pre_match))

newcatfl='/u/ki/awright/data/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554/cut_lensing.cat'
moldcat,mnewcat,d2d,unmoldcat,unmnewcat=cattools.match_unordered(oldcatfl_pre_match,newcatfl)
tag='gabodsid1554'
mnewcat.saveas(compare_dir+'new_matched_'+tag+'_paired.cat',overwrite=True)
moldcat.saveas(compare_dir+'old_matched_'+tag+'_paired.cat',overwrite=True)
unmnewcat.saveas(compare_dir+'new_unmatched_'+tag+'_paired.cat',overwrite=True)
unmoldcat.saveas(compare_dir+'old_unmatched_'+tag+'_paired.cat',overwrite=True)
os.system('cp %s %s' % (compare_dir+'old_matched_'+tag+'_paired.cat',oldcatfl))
sys.exit()

tags=['old_'+k for k in oldfls.keys()]+['new_'+k for k in newfls.keys()]
files=oldfls.values()+newfls.values()
fls_dict={}
final_fls_dict={}
cats_dict={}
import time
## first exclude the regions
for tag, catfl in zip(tags,files):
	if tag.endswith('photometry'): continue
	t0=time.time()
	cat_rm_regs , catfl_regs_removed=cattools.clean_from_regions(catfl,catflout='/u/ki/awright/data/fgas_pz_masses/compare_MACS1115+01_io/inputs_regs_removed/'+tag+'_rm_regs.cat',regfl='/u/ki/awright/data/fgas_pz_masses/compare_MACS1115+01_io/regions_old_and_new_combined_cleaned.reg')
	fls_dict[tag]=catfl_regs_removed
	cats_dict[tag]=cat_rm_regs
	t1=time.time()
	print 'tag='+tag+' takes %.1f seconds' % (t1-t0)
	#cattools.ldaccat_to_ds9(cat_rm_regs,'/u/ki/awright/data/fgas_pz_masses/compare_MACS1115+01_io/inputs_regs_removed/'+tag+'_paired_rm_regs.tsv',image='/u/ki/awright/data/MACS1115+01/W-C-RC/SCIENCE/coadd_MACS1115+01_gabodsid1554/coadd.fits',printinfo=False,keys=txt_keys)

## then exclude the stuff outside the .75-3 Mpc annulus
try:
        cluster=os.environ['cluster']
except:
        cluster='MACS1115+01'
	zcluster=0.355

import shearprofile as sp

for tag, catfl in zip(tags,files):
	if tag.endswith('photometry'): continue
	t0=time.time()
	catfl_regs_removed = fls_dict[tag]
	cat_regs_removed = cats_dict[tag]
	r_arc_from_center = cattools.cat_calc_dists( cat_regs_removed , (5000,5000), .20)
	r_mpc = r_arc_from_center  * (1./3600.) * (np.pi / 180. ) * sp.angulardist(zcluster)
	dist_filter=(r_mpc<3.0) * (r_mpc>.75)
	cat_final=cat_regs_removed.filter(dist_filter)
	cat_final.saveas(finaldir_in+tag+'.cat',overwrite=True)
	final_fls_dict[tag]=finaldir_in+tag+'.cat'
	t1=time.time()
	print 'tag='+tag+' takes %.1f seconds to calc dists and filter out %2.2f percent of objects' % (t1-t0,100.0*dist_filter.mean())

	print(tag,r_mpc.mean())
	f=figure()
	title(tag+' dist from center in Mpc')
	hist(r_mpc,bins=arange(0,5,.25))
	f.savefig(finaldir_out+'plt_dist_from_center_in_Mpc.png')

	txt_keys=['ALPHA_J2000','DELTA_J2000','SeqNr']
	txt_keys=['x','y','SeqNr']
	cattools.ldaccat_to_ds9(cat_rm_regs,finaldir_in+tag+'.tsv',image='/u/ki/awright/data/MACS1115+01/W-C-RC/SCIENCE/coadd_MACS1115+01_gabodsid1554/coadd.fits',printinfo=False,keys=txt_keys)

## match just the annulus objects (750kpc and 3Mpc)

#match_pair_stats(oldcatfl=oldfls['photometry'],newcatfl=newfls['photometry'],tag='photometry')
cattools.match_pair_stats(final_fls_dict['old_coadd_photo'],final_fls_dict['new_coadd_photo'],tag='coadd_photo')
cattools.match_pair_stats(final_fls_dict['old_coadd_filtered'],final_fls_dict['new_coadd_filtered'],tag='coadd_filtered')
cattools.match_pair_stats(final_fls_dict['old_cut_lensing'],final_fls_dict['new_cut_lensing'],tag='cut_lensing')


#ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale -title "cut_lensing: match-paired (green) , unmatch-new (blue) , unmatch-old (black)"  /u/ki/awright/data/MACS1115+01/W-C-RC/SCIENCE/coadd_MACS1115+01_gabodsid1554/coadd.fits -catalog import tsv new_matched_cut_lensing_paired.cat -catalog import tsv new_unmatched_cut_lensing_paired.cat -catalog import tsv old_unmatched_cut_lensing_paired.cat  &

oldphoto=ldac.openObjectFile(final_fls_dict['old_coadd_photo'])
newphoto=ldac.openObjectFile(final_fls_dict['new_coadd_photo'])
old=ldac.openObjectFile(final_fls_dict['old_cut_lensing'])
new=ldac.openObjectFile(final_fls_dict['new_cut_lensing'])
	
	
cutkeys_old=['rh','rg', "MAG_APER1-SUBARU-COADD-1-W-C-RC", "MAG_APER1-SUBARU-COADD-1-W-C-IC", "MAG_APER1-SUBARU-COADD-1-W-J-V"]
cutkeys_new=['rh','rg', "MAG_APER1-SUBARU-10_2-1-W-C-RC", "MAG_APER1-SUBARU-10_3-1-W-J-V", "MAG_APER1-SUBARU-10_3-1-W-J-B"]

titles_old=["rh > 2.01774 ", "rg < 4.1826", "22.0 < MAG_APER1-SUBARU-COADD-1-W-C-RC < 24.8 ", "MAG_APER1-SUBARU-COADD-1-W-C-IC <= 25.3", "MAG_APER1-SUBARU-COADD-1-W-J-V <= 26.1"]
titles_new=["rh > 2.01526", "rg < 4.53896", "22.0 < MAG_APER1-SUBARU-10_2-1-W-C-RC < 24.6 ", "MAG_APER1-SUBARU-10_3-1-W-J-V <= 26.3", "MAG_APER1-SUBARU-10_3-1-W-J-B <= 26.5"]
lines_old=[2.01774, 4.1826 , 24.8 , 25.3, 26.1]
lines_new=[2.01526, 4.53896, 24.6, 26.3, 26.5]

f=figure(figsize=(20,10))
i=0
for j,(cutkey,titlei,line) in enumerate(zip(cutkeys_old,titles_old,lines_old)):
	i+=1
	data=old[cutkey]
	dataphoto=oldphoto[cutkey]
	ax=f.add_subplot(2,5,i)
	if j==0: ylabel('OLD CATALOG ROW')
	title(titlei,size=9)
	N,bins,patch=hist(dataphoto[dataphoto>0],bins=30,label='coadd_photo')
	N,bins,patch=hist(data,bins=bins,histtype='step',label='cut_lensing')
	axvline(lines_old[j],color='red',ls=':',label='old cut')
	axvline(lines_new[j],color='blue',ls=':',label='new cut')
	if j==0: legend()
	
for j,(cutkey,titlei,line) in enumerate(zip(cutkeys_new,titles_new,lines_new)):
	i+=1
	data=new[cutkey]
	dataphoto=newphoto[cutkey]
	ax=f.add_subplot(2,5,i)
	if j==0: ylabel('NEW CATALOG ROW')
	title(titlei,size=9)
	N,bins,patch=hist(dataphoto[dataphoto>0],bins=30,label='coadd_photo')
	N,bins,patch=hist(data,bins=bins,histtype='step',label='cut_lensing')
	axvline(lines_old[j],color='red',ls=':',label='old cut')
	axvline(lines_new[j],color='blue',ls=':',label='new cut')
	if j==0: legend()
tight_layout()
f.savefig(finaldir_out+'plt_cut_column_differences.png')

## how does the match do if they're cut at different values (24.6 for new and 24.8 for old) verses at the same value (24.6)
key_old="MAG_APER1-SUBARU-COADD-1-W-C-RC"
key_new="MAG_APER1-SUBARU-10_2-1-W-C-RC"
oldcut=24.8
newcut=24.6
oldcatfl=final_fls_dict['old_coadd_filtered']
newcatfl=final_fls_dict['new_coadd_filtered']
oldcat=cattools.GetCat(oldcatfl,tablename='OBJECTS',cattype='ldac',printinfo=False)
newcat=cattools.GetCat(newcatfl,tablename='OBJECTS',cattype='ldac',printinfo=False)
oldmag=oldcat[key_old]
newmag=newcat[key_new]
magcutold=(oldmag > 22.0)*(oldmag<oldcut)
magcutnew=(newmag > 22.0)*(newmag<newcut)
oldcutcat=oldcat.filter(magcutold)
newcutcat=newcat.filter(magcutnew)
print "\n\n"
print "\nhow does the match do if they're cut at different values (24.6 for new and 24.8 for old)?"
cattools.match_pair_stats(oldcutcat,newcutcat,tag='coadd_filtered_and_cut_different_values')
samecut=min(oldcut,newcut)
samemagcutold=(oldmag > 22.0)*(oldmag<samecut)
samemagcutnew=(newmag > 22.0)*(newmag<samecut)
sameoldcutcat=oldcat.filter(samemagcutold)
samenewcutcat=newcat.filter(samemagcutnew)
print "\nhow does the match do if they're cut at the same value (24.6)?"
cattools.match_pair_stats(sameoldcutcat,samenewcutcat,tag='coadd_filtered_and_cut_same_values')
show()
sys.exit()

## Is there a bias between the W-C-RC magnitudes?
key_old="MAG_APER1-SUBARU-COADD-1-W-C-RC"
key_new="MAG_APER1-SUBARU-10_2-1-W-C-RC"
oldfl=finaldir_out+"old_matched_coadd_filtered_paired.cat"
newfl=finaldir_out+"new_matched_coadd_filtered_paired.cat"
oldfo=pyfits.open(oldfl)
newfo=pyfits.open(newfl)
newcat=ldac.LDACCat(newfo['OBJECTS'])
oldcat=ldac.LDACCat(oldfo['OBJECTS'])

oldmag=oldcat[key_old]
newmag=newcat[key_new]
magcutboth=(oldmag > 22.0) * (newmag > 22.0)
oldmag_clean=oldmag[magcutboth]
newmag_clean=newmag[magcutboth]
args_in_sort=oldmag_clean.argsort()
olddetmag=oldmag_clean[args_in_sort]
newdetmag=newmag_clean[args_in_sort]
def cutnumstring(oldcut=24.8,newcut=24.6):
	old_total=(olddetmag<oldcut).sum()
	new_total=((newdetmag<newcut).sum())
	diffcut_str="""cutting Rmagold<%.1f and Rmagnew<%.1f, gives you old_len=%s new_len=%s percentage old is larger=%2.2f """ % (oldcut, newcut, old_total, new_total , old_total/float(new_total)*100 - 100 )
	return diffcut_str

s0=cutnumstring(oldcut=24.8,newcut=24.6)
s1=cutnumstring(oldcut=24.6,newcut=24.6)
s2=cutnumstring(oldcut=24.8,newcut=24.8)
figstring='\n'.join([s0,s1,s2])

## just plot histograms of 
f=figure()
ax=f.add_subplot(1,1,1)
N,bins,patch=hist(newdetmag,bins=30,label='new R-band mags')
N,bins,patch=hist(olddetmag,bins=bins,histtype='step',label='old R-band mags')
axvline(lines_old[2],color='red',ls=':',label='old cut')
axvline(lines_new[2],color='blue',ls=':',label='new cut')
figtext(.2,.8,figstring,size=9)
legend()
f.savefig(finaldir_out+'plt_hists_oldmag_newmag_Rband.png')

## now plot to see if there is a bias

f=figure()
ax=f.add_subplot(1,1,1)
plot(olddetmag,newdetmag,'k.')
grid()
f=imagetools.AxesSquare(f)
yd,yu=ax.get_ylim()
plot([yd,yu],[yd,yu],'r--')
xlabel('old cat mag: '+key_old)
ylabel('new cat mag: '+key_new)
f.savefig(finaldir_out+'plt_oldmag_vs_newmag_Rband.png')

f=figure(figsize=(14,14))
ax=f.add_subplot(1,1,1)
title('plot R-band mags from old (i.e. ~2012) catalog and new catalog for MACS1115+01\nerrorbars go out 32% in each direction from the median')
oldMnew=olddetmag-newdetmag
#plot(olddetmag,oldMnew,'k.')
grid()
ax.set_ylim(-1.25,1.25)

xd,xu=(22,29)
magbins=arange(xd,xu+.1,.1)
oldbins=digitize(olddetmag,magbins)-1
means,meds,errors= [] , [] , []
for i in arange(len(magbins)):
	meani,medi,errori=imagetools.ArrayInfo(oldMnew[oldbins==i],printout=False,dictout=False)
	means,meds,errors= means+[meani],meds+[medi],errors+[errori]
means,meds,errors=array( means ) , array( meds ), array( errors )

plot([xd,xu],[0,0],'r--')
Lerrs=meds-errors[:,0]
Uerrs=errors[:,1]-meds
errorbar(magbins,meds,yerr=[Lerrs,Uerrs])
#plot(magbins,means,color='purple',ls=':',label='mean')
figtext(.2,.8,'mean and median are almost exactly the same up until magnitude of ~25')
xlabel('old cat mag: '+key_old)
ylabel('old-new cat mags: '+key_old+"-"+key_new)
ax.set_xlim(xd,xu)
axvline(24.8,color='red',ls=':',label='old cut')
axvline(24.6,color='blue',ls=':',label='new cut')
tight_layout()
f.savefig(finaldir_out+'plt_faintmag_differences.png')
show()

#adam-SHNT## no bias between the W-C-RC magnitudes, so just confirm that you can take the coadd_photo matched-objects
#	apply the cuts in rh, rg, Pgscut, snrcut, shear_cut, and imagcut (and probably the other mag cuts and later the RS cut and stuff too)
# 	then make the faint-mag cut for the "new" catalog at the larger value (24.8 instead of 24.6), and confirm that you'll have about the same number of objects.



#compkeys=[ 'x', 'y', 'rg', 'nu', 'rnumax', 'numax', 'rmax', 'flux', 'mag', 'nbad', 'rh', 'e1', 'deltae1', 'e2', 'deltae2', 'A', 'B', 'Theta', 'Psh11', 'Psh22', 'Psh12', 'Psh21', 'Psm11', 'Psm22', 'Psm12', 'Psm21', 'cl', 'q11', 'q22', 'q12', 'Xsh11', 'Xsh22', 'Xsh12', 'Xsm11', 'Xsm22', 'Xsm12', 'eh0', 'eh1', 'em0', 'em1', 'snratio', 'Flag', 'IMAFLAGS_ISO', 'NIMAFLAGS_ISO', 'CLASS_STAR', 'theta_al', 'eps_abs', 'IMAFLAGS_lensimage', 'AVE_WEIGHT0', 'AVE_WEIGHT1', 'REL_AVE_WEIGHT0', 'REL_AVE_WEIGHT1', 'RELMEAN_AVE_WEIGHT0', 'RELMEAN_AVE_WEIGHT1', 'snratio_scaled0', 'snratio_scaled1', 'e1anisocorr', 'e2anisocorr', 'e1corrpol', 'e2corrpol', 'rgbin', 'rg3bin', 'rg9bin', 'SeqNr', 'PshstPsmst', 'Pg11', 'Pg22', 'Pg12', 'Pg21', 'Pgs', 'Pgi11', 'Pgi22', 'Pgi12', 'Pgi21', 'gs1', 'gs2', 'g1', 'g2', 'gs', 'g', 'ISOAREA_DETECT']
#f=figure(figsize=(17,17))
#for j,k in enumerate(compkeys):
#	both=append(oldphoto[k],newphoto[k])
#	minmin,maxmax=both.min(),both.max()
#	bins=arange(minmin,maxmax,40)
#	ax=f.add_subplot(9,9,j+1)
#	title(k)
#	try:
#		hist(oldphoto[k],bins=bins,histtype='step',label='old coadd_photo')
#	except IndexError:
#		continue
#	hist(newphoto[k],bins=bins,histtype='step',label='new coadd_photo')
#	hist(old[k],bins=bins,histtype='step',label='old cut_lensing')
#	hist(new[k],bins=bins,histtype='step',label='new cut_lensing')
#	if j==0: legend()
#
#show()
