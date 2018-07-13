#! /usr/bin/env python
#adam-does# matches the redshifts from our pipeline/bpz to external reference redshifts

#ADVICE: when starting fresh with a new cluster. first search for #adam-Warning# in this code and change stuff whereever there is a #adam-Warning#
#adam-Warning#
# convert_to_mags("/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.APER1.1.CWWSB_capak.list.all" , "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.alter.cat" , "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.APER1.1.CWWSB_capak.list.all.EVERY.cat")
run_name,mag_cat=("/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.APER1.1.CWWSB_capak.list.all" , "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.calibrated_PureStarCalib.alter.cat")
import astropy.io.fits as pyfits
from matplotlib.pylab import *
import numpy
import ldac

import sys,os
purepath=sys.path
addpath=[os.environ['BPZPATH']]+purepath
sys.path=addpath
from useful import ejecuta,get_header,put_header,get_str,put_str,get_data,get_2Darray,put_2Darray,params_file,params_commandline,view_keys,match_resol,overlap,match_objects,match_min,match_min2
from coeio import loaddata, loadfile, params_cl, str2num, loaddict, findmatch1, pause  #, prange, plotconfig
sys.path=purepath+['/u/ki/awright/InstallingSoftware/pythons/']
import imagetools

#adam-Warning# names to put on plots
cluster=os.environ['cluster']
ztrue=0.355
bpzmode="PureStarCalib-lenscut-and-RScut"
nametag="-%s-%s" % (cluster,bpzmode)


#adam-SHNT# use lens_cat to cut down to those objects that passed_lensing the lensing cuts only!
lens_fl="/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554/cut_lensing.cat"
#mag_fl = "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.calibrated_PureStarCalib.alter.cat"
lens_fo = pyfits.open(lens_fl)[4]
SeqNr_lens=lens_fo.data.field('SeqNr')
passed_lensing=SeqNr_lens-1

rs_fl="/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554/MACS1115+01_redsequence.cat"
#mag_fl = "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.calibrated_PureStarCalib.alter.cat"
rs_fo = pyfits.open(rs_fl)[4]
SeqNr_rs=rs_fo.data.field('SeqNr')
passed_rs=SeqNr_rs-1

## get bpz info for data that passed_lensing lensing cuts!
cat = run_name + '.bpz'
zs_all=get_2Darray(cat)
zs_rs=get_2Darray(cat)[passed_rs]
zs_lens=get_2Darray(cat)[passed_lensing]
print '1.) sum(passed_lensing)=',passed_lensing.sum()
print '1.) sum(passed_rs)=',passed_rs.sum()


mag = pyfits.open(mag_cat)[1]
NFILT_all=mag.data.field('NFILT')
NFILT_lens=mag.data.field('NFILT')[passed_lensing]
NFILT_rs=mag.data.field('NFILT')[passed_rs]
print_num_lens= "# passed lensing cuts: %s" % (len(NFILT_lens))
print_num_rs =  "# passed   RS    cuts: %s" % (len(NFILT_rs))
print_per_lens= "%" +" passed lensing cuts: %.2f" % (len(NFILT_lens)*100.0/float(len(mag.data.field('NFILT'))))
print_per_rs =  "%" + " passed   RS    cuts: %.2f" % (len(NFILT_rs)*100.0/float(len(mag.data.field('NFILT'))))
lens_info=print_per_lens+'\n'+print_num_lens
rs_info=print_per_rs+'\n'+print_num_rs
#print lens_info
#print rs_info
## plotting bpz output
zrange=arange(.01,4.01,.01)
zbins=zrange-.005

#adam-new# now get the pdzs!
import pdzfile_utils
pdzmanager = pdzfile_utils.PDZManager.parsePDZ('/nfs/slac/g/ki/ki18/anja/SUBARU//MACS1115+01/PHOTOMETRY_W-C-RC_aper//MACS1115+01.APER1.1.CWWSB_capak.list.all.probs')
pdzrange,pdz_lens=pdzmanager.associatePDZ(SeqNr_lens)
pdzrange,pdz_rs=pdzmanager.associatePDZ(SeqNr_rs)
pdz_stack=pdz_lens.sum(axis=0)
pdz_stack_rs=pdz_rs.sum(axis=0)
pdzbins=np.array(pdzrange-pdzrange[0]/2)
# (pdzbins==zbins).all() is True
pdz_peak=pdzbins[pdz_stack.argmax()]
pdz_peak_rs=pdzbins[pdz_stack_rs.argmax()]
#adam-SHNT# I'm not so sure about the binning, if it's supposed to start at 0.00 or 0.01
pdz_peak_str='pdz peak: %.3f True Z: %.3f (difference: %.3f)' % (pdz_peak,ztrue, pdz_peak-ztrue)
pdz_peak_str_rs='pdz peak: %.3f True Z: %.3f (difference: %.3f)' % (pdz_peak_rs,ztrue, pdz_peak_rs-ztrue)
#adam-SHNT# make the p(z) quality cut from here:                                                                                                                                                                                                                        
# /nfs/slac/kipac/fs1/u/rherbonn/photoz/WtG/scripts/cut_bpzcat.py


import sys,os,inspect ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
from import_tools import *
curfile=os.path.abspath(inspect.getfile(inspect.currentframe()))
FileString=os.path.basename(curfile)
#args=imagetools.ArgCleaner(sys.argv,FileString)
import numpy as np
import matplotlib.pyplot as plt
import astropy
from astropy.coordinates import SkyCoord
from astropy import units as u

#CLUSTER_SUBARU_ID,SUB_RA,SUB_DEC,z_found,z_err
print """\n\nsome AGN I removed: MACS115_19151 and MACS1115_25724"""
specz_file="/u/ki/awright/wtgpipeline/MACS1115_specz_galaxies.csv"
#bpz_file= "/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.calibrated_PureStarCalib.cat"
bpz_file='/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.APER1.1.CWWSB_capak.list.all.EVERY.cat'
speczcat=astropy.io.ascii.read(specz_file)
bpzfo=astropy.io.fits.open(bpz_file)
bpzcat=bpzfo[-1]
bpztables=[ bpzfo[i].name for i in range(len(bpzfo))]
print 'of bpztables=',bpztables,'chose ',bpztables[-1]

#adam-example# bpzcat=astropy.io.fits.open("/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.calibrated.bpztab.cat")
# os.system("ldacdesc -i /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/PHOTOMETRY_W-C-RC_aper/MACS1115+01.calibrated.bpztab.cat")
# primary OBJECTS PHOTINFO FIELDS BPZTAB
rakey='DATA_ALPHA_J2000-SUBARU-W-C-RC'
deckey='DATA_DELTA_J2000-SUBARU-W-C-RC'
bpz_ra=bpzcat.data.field(rakey)
bpz_dec=bpzcat.data.field(deckey)
lens_ra=bpz_ra[passed_lensing]
lens_dec=bpz_dec[passed_lensing]
rs_ra=bpz_ra[passed_rs]
rs_dec=bpz_dec[passed_rs]

#fk5 is J2000 by default!
bpz_coords=SkyCoord(bpz_ra*u.degree,bpz_dec*u.degree,frame="fk5")
rs_coords=SkyCoord(rs_ra*u.degree,rs_dec*u.degree,frame="fk5")
lens_coords=SkyCoord(lens_ra*u.degree,lens_dec*u.degree,frame="fk5")

## now get specz info
speczcoords=SkyCoord(speczcat["SUB_RA"].data*u.degree,speczcat["SUB_DEC"].data*u.degree,frame="fk5")

idx_lens, d2d_lens, d3d = speczcoords.match_to_catalog_sky(lens_coords)
idx_rs, d2d_rs, d3d = speczcoords.match_to_catalog_sky(rs_coords)
d2d_rs_arcsec=d2d_rs.deg*3600
d2d_lens_arcsec=d2d_lens.deg*3600
lt1pix_apart_rs=d2d_rs_arcsec<.2
#adam-final# no close lensing matches and only 9 RS matches, same as other way of matching

## match catalogs and choose ones that are 1 pixel apart or less
idx, d2d, d3d = speczcoords.match_to_catalog_sky(bpz_coords)
d2d_arcsec=d2d.deg*3600
lt1pix_apart=d2d_arcsec<.2

## successful matches:
print """some bad matches to purge: """
print speczcat[logical_not(lt1pix_apart)]
print "were this many arcsecs from their match:", d2d_arcsec[logical_not(lt1pix_apart)]

Midx, Md2d , Md2d_arcsec= idx[lt1pix_apart], d2d[lt1pix_apart], d2d_arcsec[lt1pix_apart]
Mspec_cat = speczcat[lt1pix_apart]
Mspec_coords=speczcoords[lt1pix_apart]
Mbpz_cat=bpzcat.data[Midx]

## now save to ascii file
########Z_S_SeqNr=Mbpz_SeqNr[match_goodsingles]
########Z_S_z=zspec_z[match_goodsingles]
########## save catalog of the good matches
########bpz_path=os.path.split(bpz_file)
########outtable=astropy.table.table.Table( data=[ Z_S_SeqNr, Z_S_z ], names=['SeqNr','z'])
########outtable.write(bpz_path[0]+"/match_specz_and_bpz_cats.txt",format="ascii.commented_header")

## plot the spec-z vs photo-z distribution
ID=zs_lens[:,0]
ID_lens=array(ID,dtype=int)
ID_rs=zs_rs[:,0]
ID_rs=array(ID_rs,dtype=int)
id_rs=set(ID_rs)
id_lens=set(ID_lens)
ID_bpz=bpzcat.data.field('DATA_SeqNr')
id_bpz=set(ID_bpz)
ID_Mbpz=array(Mbpz_cat['DATA_SeqNr'],dtype=int)
id_Mbpz=set(ID_Mbpz)
ID_Mbpz_in_rs=array(list(id_Mbpz.intersection(id_rs)),dtype=int)
id_Mbpz.intersection(id_lens)

Mbpz_in_rs=array([id in id_rs for id in ID_Mbpz],dtype=bool)
print '1.) len(Mbpz_in_rs)=',len(Mbpz_in_rs) , ' len(ID_Mbpz)=',len(ID_Mbpz)
print '1.) sum(Mbpz_in_rs)=',sum(Mbpz_in_rs)
#all False: Mbpz_in_lens=[id in id_lens for id in ID_Mbpz]

## now plot stuff
lens_keys=[col.name for col in lens_fo.columns]
rs_keys=[col.name for col in rs_fo.columns]
bpz_keys=[ Mbpz_cat.columns[i].name for i in range(len(Mbpz_cat.columns))]
#print 'keys to work with:'+' '.join(bpz_keys)
Z_B = Mbpz_cat['DATA_BPZ_Z_B']
spec_z=Mspec_cat["z_found"].data
print '1.) len(Mbpz_cat)=',len(Mbpz_cat) , ' len(Mspec_coords)=',len(Mspec_coords) , ' len(Mspec_cat)=',len(Mspec_cat)
print '1.) len(Z_B)=',len(Z_B) , ' len(spec_z)=',len(spec_z)

zlims=[0,1.1]
f=figure(figsize=(9,9))
plot(zlims,zlims,'k-')
plot(spec_z,Z_B,'kx',label='non-RS object')
plot(spec_z[Mbpz_in_rs],Z_B[Mbpz_in_rs],'ro',label='RS object')
xlim(zlims)
ylim(zlims)
grid()
xlabel('spec-z')
ylabel('BPZ_Z_B')
title('BPZ Z_BEST vs. Spec-Z for all objects (RS catalog also shown, lensing catalog had no matches)')
legend()
f.savefig('plt_compare_MACS1115_specz_and_bpz')

zlims=[0.3,.44]
f=figure(figsize=(9,9))
plot(zlims,zlims,'k-')
plot(spec_z,Z_B,'kx',label='non-RS object')
plot(spec_z[Mbpz_in_rs],Z_B[Mbpz_in_rs],'ro',label='RS object')
xlim(zlims)
ylim(zlims)
grid()
xlabel('spec-z')
ylabel('BPZ_Z_B')
title('BPZ Z_BEST vs. Spec-Z for all objects (RS catalog also shown, lensing catalog had no matches)')
legend()
f.savefig('plt_compare_MACS1115_specz_and_bpz-RS_zoom')


## which cuts do they fail?
cuts_fl="/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554/cc_cuts3.dat"
cuts_fo=open(cuts_fl)
cuts_lines=[line.strip() for line in cuts_fo.readlines()]
magcuts=[]
for l in cuts_lines:
    if l.startswith("HYBRID"):
	magcuts.append(l)
    if l.startswith("MAG_APER1"):
	ll=l.replace("MAG_APER1","DATA_MAG_APER1")
	ll_cuts=ll.split(' AND ')
	for ll_cut in ll_cuts:
	    if ll_cut not in magcuts:
		magcuts.append(ll_cut)

magcut_info={}
for cut in magcuts:
    ckey,crel,cnum = cut.split(' ')
    print "Mbpz_cat['"+ckey+"']"+crel+cnum
    exec "cutout=Mbpz_cat['"+ckey+"']"+crel+cnum
    magcut_info[cut]=cutout

for k,val in magcut_info.items():
    print "#% passed "+k+":",val.mean()*100

#% passed DATA_MAG_APER1-SUBARU-10_2-1-W-C-RC > 22.0: 0.0
#% passed DATA_MAG_APER1-SUBARU-10_3-1-W-J-V > 0.0: 100.0
#% passed DATA_MAG_APER1-SUBARU-10_2-1-W-C-RC <= 26.3: 100.0
#% passed DATA_MAG_APER1-SUBARU-10_2-1-W-C-RC < 24.6: 100.0
#% passed DATA_MAG_APER1-SUBARU-10_2-1-W-C-RC > 0.0: 90.9090909090909
#% passed DATA_MAG_APER1-SUBARU-10_3-1-W-J-B > 0.0: 100.0
#% passed DATA_MAG_APER1-SUBARU-10_3-1-W-J-B <= 26.5: 100.0
#% passed DATA_MAG_APER1-SUBARU-10_3-1-W-J-V <= 26.3: 100.0


## remove objects that failed with pdz cut
import pickle
fo=open('SeqNr_fail_pdz_cut.pkl','rb')
SeqNr_fail_pdz_cut=array(pickle.load(fo))
fo.close()

Midx_new=list(Midx.copy())
idx_fail_pdz_cut=SeqNr_fail_pdz_cut-1
for id in idx_fail_pdz_cut:
    if id in Midx:
        print id
        Midx_new.remove(id)

newer=array([id in Midx_new for id in idx])
Mspec_cat = speczcat[lt1pix_apart*newer]
Mspec_coords=speczcoords[lt1pix_apart*newer]
Mbpz_cat=bpzcat.data[Midx_new]

##
SeqNr_all=zs_all[:,0]
sall=set(SeqNr_all)
slens=set(SeqNr_lens)
srs=set(SeqNr_rs)
sfail=set(SeqNr_fail_pdz_cut)
srs_pass=srs.difference(sfail)
slens_pass=slens.difference(sfail)
sall_pass=sall.difference(sfail)
print '2.) len(srs_pass)=',len(srs_pass) , ' len(srs)=',len(srs)
print '2.) len(slens_pass)=',len(slens_pass) , ' len(slens)=',len(slens)
print '2.) len(Mbpz_cat)=',len(Mbpz_cat) , ' len(Mspec_coords)=',len(Mspec_coords) , ' len(Mspec_cat)=',len(Mspec_cat)


SeqNr_rs=array(list(srs_pass),dtype=int)
SeqNr_lens=array(list(slens_pass),dtype=int)
SeqNr_all=array(list(sall_pass),dtype=int)
passed_lensing=SeqNr_lens-1
passed_pdz=SeqNr_all-1
passed_rs=SeqNr_rs-1

## get bpz info for data that passed_lensing lensing cuts!
cat = run_name + '.bpz'
zs_all=get_2Darray(cat)[passed_pdz]
zs_rs=get_2Darray(cat)[passed_rs]
zs_lens=get_2Darray(cat)[passed_lensing]
print '2.) sum(passed_lensing)=',passed_lensing.sum()
print '2.) sum(passed_rs)=',passed_rs.sum()

## plot the spec-z vs photo-z distribution
ID=zs_lens[:,0]
ID_lens=array(ID,dtype=int)
ID_rs=zs_rs[:,0]
ID_rs=array(ID_rs,dtype=int)
id_rs=set(ID_rs)
id_lens=set(ID_lens)
ID_bpz=bpzcat.data.field('DATA_SeqNr')
id_bpz=set(ID_bpz)
ID_Mbpz=array(Mbpz_cat['DATA_SeqNr'],dtype=int)
id_Mbpz=set(ID_Mbpz)
ID_Mbpz_in_rs=array(list(id_Mbpz.intersection(id_rs)),dtype=int)
id_Mbpz.intersection(id_lens)

Mbpz_in_rs=array([id in id_rs for id in ID_Mbpz],dtype=bool)
print '2.) len(Mbpz_in_rs)=',len(Mbpz_in_rs) , ' len(ID_Mbpz)=',len(ID_Mbpz)
print '2.) sum(Mbpz_in_rs)=',sum(Mbpz_in_rs)
#all False: Mbpz_in_lens=[id in id_lens for id in ID_Mbpz]

## now plot stuff
lens_keys=[col.name for col in lens_fo.columns]
rs_keys=[col.name for col in rs_fo.columns]
bpz_keys=[ Mbpz_cat.columns[i].name for i in range(len(Mbpz_cat.columns))]
#print 'keys to work with:'+' '.join(bpz_keys)
Z_B = Mbpz_cat['DATA_BPZ_Z_B']
spec_z=Mspec_cat["z_found"].data
print '2.) len(Z_B)=',len(Z_B) , ' len(spec_z)=',len(spec_z)

zlims=[0,1.1]
f=figure(figsize=(9,9))
plot(zlims,zlims,'k-')
plot(spec_z,Z_B,'kx',label='non-RS object')
plot(spec_z[Mbpz_in_rs],Z_B[Mbpz_in_rs],'ro',label='RS object')
xlim(zlims)
ylim(zlims)
grid()
xlabel('spec-z')
ylabel('BPZ_Z_B')
title('BPZ Z_BEST vs. Spec-Z for all objects (RS catalog also shown, lensing catalog had no matches)')
legend()
f.savefig('plt_compare_MACS1115_specz_and_bpz-passed_pdz')

zlims=[0.3,.44]
f=figure(figsize=(9,9))
plot(zlims,zlims,'k-')
plot(spec_z,Z_B,'kx',label='non-RS object')
plot(spec_z[Mbpz_in_rs],Z_B[Mbpz_in_rs],'ro',label='RS object')
xlim(zlims)
ylim(zlims)
grid()
xlabel('spec-z')
ylabel('BPZ_Z_B')
title('BPZ Z_BEST vs. Spec-Z for all objects (RS catalog also shown, lensing catalog had no matches)')
legend()
f.savefig('plt_compare_MACS1115_specz_and_bpz-RS_zoom-passed_pdz')
show()



## which cuts do they fail?
cuts_fl="/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/LENSING_W-C-RC_W-C-RC_aper/gabodsid1554/cc_cuts3.dat"
cuts_fo=open(cuts_fl)
cuts_lines=[line.strip() for line in cuts_fo.readlines()]
magcuts=[]
for l in cuts_lines:
    if l.startswith("HYBRID"):
	magcuts.append(l)
    if l.startswith("MAG_APER1"):
	ll=l.replace("MAG_APER1","DATA_MAG_APER1")
	ll_cuts=ll.split(' AND ')
	for ll_cut in ll_cuts:
	    if ll_cut not in magcuts:
		magcuts.append(ll_cut)

magcut_info={}
for cut in magcuts:
    ckey,crel,cnum = cut.split(' ')
    print "Mbpz_cat['"+ckey+"']"+crel+cnum
    exec "cutout=Mbpz_cat['"+ckey+"']"+crel+cnum
    magcut_info[cut]=cutout

for k,val in magcut_info.items():
    print "#% passed "+k+":",val.mean()*100

