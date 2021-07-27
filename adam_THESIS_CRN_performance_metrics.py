#! /usr/bin/env python
#adam-predecessor# this derives from adam_THESIS_CRN_number_of_masks.py
from matplotlib.pylab import *
import astropy
from glob import glob
import scipy.ndimage
import os
import pymorph
import skimage
from skimage import measure
from skimage import morphology
import mahotas
import sys ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
from import_tools import *
conn8=array([[1,1,1],[1,1,1],[1,1,1]])
conn4=array([[0,1,0],[1,1,1],[0,1,0]])
connS=array([[0,1,1,0],[1,1,1,1],[1,1,1,1],[0,1,1,0]],dtype=bool)

from adam_quicktools_ArgCleaner import ArgCleaner
args=ArgCleaner(sys.argv)
print "args=", args

#/u/ki/awright/data/eyes/coadds-pretty_for_10_3_cr.2/
import pickle
fl=open('/u/ki/awright/thiswork/eyes/Prettys_info.2.1.pkl','rb')
Pinfo=pickle.load(fl) #CRbads[filter][CRnum]['CCDnum','weight_file','file','dark_file','CRtag'] only 'file' and 'CRtag' are useful here
fl.close()

import astropy.io.fits as pyfits

from adam_quicktools_header_key_add import add_key_val
CRfl='/u/ki/awright/thiswork/eyes/CRbads_info.2.1.pkl'
CRfo=open(CRfl)
CRinfo=pickle.load(CRfo)
CRfo.close()


#args=glob('/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_compare/BB_ERASED_*_3.fits')
#/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_CRN-cosmics_MACS0429-02_W-J-B.SUPA0154630_1.fits
tinput_dir='/nfs/slac/kipac/fs1/u/awright/eyes/eye-10_3_cr.2.1/W-C-RC/both/edge_out/inputs/'
toutput_dir='/nfs/slac/kipac/fs1/u/awright/eyes/eye-10_3_cr.2.1/W-C-RC/both/edge_out/outputs/'
OUTDIR="/u/ki/awright/my_data/thesis_stuff/CRN_final_purecomp/"
tinputfls=glob('/nfs/slac/kipac/fs1/u/awright/eyes/eye-10_3_cr.2.1/W-C-RC/both/edge_out/inputs/eye_CRnum[0-9]_Pnum*.fits')
tinputfls+=glob('/nfs/slac/kipac/fs1/u/awright/eyes/eye-10_3_cr.2.1/W-C-RC/both/edge_out/inputs/eye_CRnum1[0-9]_Pnum*.fits')
tinputfls+=glob('/nfs/slac/kipac/fs1/u/awright/eyes/eye-10_3_cr.2.1/W-C-RC/both/edge_out/inputs/eye_CRnum20_Pnum*.fits')
#tinputfls=glob(OUTDIR+'CRNmask_eye_CRnum0_Pnum*.fits')

compdir='/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_compare/'
alldir='/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/'
time=[]
rms=[]
seeing=[]
CRN_Ntracks=[]
pure_mask_level=[]
pure_mask_overmask_frac=[]
comp_mask_level=[]
comp_pix_level=[]
for fl in tinputfls:
    try:
        flname=os.path.basename(fl).split('.')[0]
        if 'OCF' in fl:
                BASE=os.path.basename(fl).split('OCF')[0]
        else:
                BASE=flname
	#CR_segfl=alldir+'SEGMENTATION_CRN-cosmics_'+fl.split('_BBCR_')[-1]
	CR_segfl=OUTDIR+'CRNmask_'+BASE+".fits"
	CRNfo=astropy.io.fits.open(CR_segfl)
	CRNheader=CRNfo[0].header
	CRN_seg=CRNfo[0].data
	CRN_Nlabels=CRN_seg.max()
	CRN_labels=arange(CRN_Nlabels)+1
	CRN_mask=CRNfo[0].data>0
	CRN_slices=scipy.ndimage.find_objects(CRN_seg)

	CR_expsegfl=OUTDIR+'CRNmask_expanded_'+BASE+".fits"
	CRNexpfo=astropy.io.fits.open(CR_expsegfl)
	CRN_exp_mask=asarray(CRNexpfo[0].data,dtype=bool)
	#print (CRN_exp_mask[truth]>0.0).mean()

	tofl=toutput_dir+BASE+".fits"
	tofo=astropy.io.fits.open(tofl)
	toheader=tofo[0].header
	toim=tofo[0].data
	truth=tofo[0].data>0

	#adam-tmp# put BB or BBSS in here depending on the final output
	#CR_newsegfl=alldir+'SEGMENTATION_BBSS_CRN-cosmics_'+fl.split('_BBCR_')[-1]
	#fo=astropy.io.fits.open(fl)
	#fo=astropy.io.fits.open(fl)
	tifo=astropy.io.fits.open(fl)
	tiheader=tifo[0].header
	tiim=tifo[0].data
	true_seg,true_Nlabels=scipy.ndimage.label(truth,conn8)
	true_labels=arange(true_Nlabels)+1
	true_slices=scipy.ndimage.find_objects(true_seg)

	CRN_exp_seg,CRN_exp_Nlabels=scipy.ndimage.label(CRN_exp_mask,conn8)
	CRN_exp_labels=arange(CRN_exp_Nlabels)+1
	CRN_exp_slices=scipy.ndimage.find_objects(CRN_exp_seg)
	hits=[]
	frac_necessarys=[]
	for l in CRN_labels:
		sl=CRN_slices[l-1]
		spots=CRN_seg[sl]==l
		true_spots=truth[sl]
		true_at_CRNl=true_spots[spots]
		hit=true_at_CRNl.any()
		frac_necessary=true_at_CRNl.mean()
		#lseg_num=spots.sum()

		hits.append(hit)
		frac_necessarys.append(frac_necessary)
	CRNl_frac_true=array(frac_necessarys)
	CRNl_hit=array(hits)
	pure_mask=CRNl_hit.mean()
	# true hit CRN?
	thits=[]
	tfrac_necessarys=[]
	for l in true_labels:
		sl=true_slices[l-1]
		spots=true_seg[sl]==l
		CRN_spots=CRN_exp_mask[sl]
		CRN_at_truel=CRN_spots[spots]
		thit=CRN_at_truel.any()
		tfrac_necessary=CRN_at_truel.mean()
		#lseg_num=spots.sum()

		thits.append(thit)
		tfrac_necessarys.append(tfrac_necessary)
	truel_frac_CRN=array(tfrac_necessarys)
	truel_hit=array(thits)
	comp_mask=truel_hit.mean()
	#fo=astropy.io.fits.open(CR_newsegfl)
	#CRN_seg=fo[0].data
	CRmasksN=CRN_seg.max()
	CRpixN=(CRN_seg>0).sum()

	comp_pix=(CRN_exp_mask[truth]>0.0).mean()
	pure_pix=(truth[CRN_mask]>0.0).mean()

	print comp_pix , pure_mask, pure_pix , CRN_exp_Nlabels,true_Nlabels,tiheader['MYSEEING'],tiheader['EXPTIME'],tiheader['MYRMS']
	#fo=astropy.io.fits.open(CR_segfl)
	#seginit=fo[0].data
	#seginit.max()
	#CRmasks0=seginit.max()
	#CRpix0=(seginit>0).sum()
	pure_mask_level.append(pure_mask)
	pure_mask_overmask_frac.append(1-CRNl_frac_true.mean())
	comp_mask_level.append(comp_mask)
	comp_pix_level.append(comp_pix)
	seeing.append(tiheader['MYSEEING'])
	time.append(tiheader['EXPTIME'])
	rms.append(tiheader['MYRMS'])
	CRN_Ntracks.append(CRN_Nlabels)
    except IOError as e:
	print e
	continue

ACRN_Ntracks=array(CRN_Ntracks)
Aseeing=array(seeing)
Arms=array(rms)
Apure_mask_level=array(pure_mask_level)
Acomp_mask_level=array(comp_mask_level)
Apure_mask_overmask_frac=array(pure_mask_overmask_frac)
Acomp_pix_level=array(comp_pix_level)
Atime=array(time)
ANmasksNrate=array(ACRN_Ntracks)/Atime

def seeing_binned(Aprop):
	less_pt6=Aprop[Aseeing<=0.6]
	pt6_to_pt7=Aprop[(Aseeing>0.6) * (Aseeing<0.7)]
	great_pt7=Aprop[Aseeing>=0.7]
	print '<=0.6:',less_pt6.mean()
	print '0.6<seeing<0.7:',pt6_to_pt7.mean()
	print '>=0.7:',great_pt7.mean()
	return round(less_pt6.mean(),2),round(pt6_to_pt7.mean(),2),round(great_pt7.mean(),2)

print '\n# purity at mask level:'
pure=seeing_binned(Apure_mask_level)

print '\n# overmasking by this amount on average:'
om=seeing_binned(Apure_mask_overmask_frac)


print '\n# completeness at mask level :'
compm=seeing_binned(Acomp_mask_level)
print '\n# completeness at pixel level :'
compp=seeing_binned(Acomp_pix_level)

print '\nCRN masks per exptime:'
Nmask=seeing_binned(ANmasksNrate)

seeings=['seeing<=0.6','0.6<seeing<0.7','seeing>=0.7']

import astropy.table as tbl
Seeings=['Seeing$\leq 0\\arcsecf6$','$0\\arcsecf6<$Seeing$<0\\arcsecf7$','Seeing$\geq0\\arcsecf7$']
tab=tbl.Table(data=[Seeings , pure, compp , compm ],names=['Seeing Range','Purity per mask','Completeness per pixel','Completeness per mask'])
#tab=tbl.Table(data=[Seeings , pure, compp , compm , om ],names=['Seeing Range','Purity at mask level','Completeness at pixel level','Completeness at mask level', 'Frac. Mask Outside'])
tab.write('CRN_table.tex',format='latex',overwrite=True)
## for BB masks:
# masks, 0 and N:
#<=0.6: 1041.33333333
#0.6<seeing<0.7: 1074.14516129
#>=0.7: 779.873786408
#<=0.6: 593.855072464
#0.6<seeing<0.7: 561.225806452
#>=0.7: 353.32038835
## pixels, 0 and N:
#<=0.6: 11096.8985507
#0.6<seeing<0.7: 13478.0
#>=0.7: 9933.27184466
#<=0.6: 22824.4202899
#0.6<seeing<0.7: 26138.3870968
#>=0.7: 18999.7378641
#mask rate:
#<=0.6: 3.49563607085
#0.6<seeing<0.7: 2.98745519713
#>=0.7: 1.69027777778

## for BB masks:
#mask-pixels rate at 0:
#<=0.6: 65.8068639291
#0.6<seeing<0.7: 71.0849171147
#>=0.7: 47.9930690399

#mask-pixels rate at N:
#<=0.6: 134.256549919
#0.6<seeing<0.7: 136.891610663
#>=0.7: 90.5776240561

## for BBSS masks:
#mask-pixels rate at 0:
#<=0.6: 65.8068639291
#0.6<seeing<0.7: 71.0849171147
#>=0.7: 47.9930690399

#mask-pixels rate at N:
#<=0.6: 102.991151369
#0.6<seeing<0.7: 114.216966846
#>=0.7: 86.5826941748

