#! /usr/bin/env python
#adam-example# ipython -i adam_make_comparable_CRmask.py /gpfs/slac/kipac/fs1/u/awright/SUBARU//MACS1226+21/W-S-Z+_2011-01-06/SCIENCE/SUPA0128343_3OCF.fits /u/ki/awright/my_data/thesis_stuff/old_cosmics/CRNCRmask_SUPA0128343_3.fits /u/ki/awright/my_data/thesis_stuff/old_cosmics/oldCRmask_SUPA0128343_3.fits
import sys,os,inspect                                                                                                                                                             
sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
from import_tools import *
curfile=os.path.abspath(inspect.getfile(inspect.currentframe()))
FileString=os.path.basename(curfile)
## args cleaned in ~/bonnpipeline:
import adam_quicktools_ArgCleaner
argv=adam_quicktools_ArgCleaner.ArgCleaner(sys.argv)
image_fl = argv[0]
CRNmask_fl = argv[1]
oldmask_fl = argv[2]

conn8=array([[1,1,1],[1,1,1],[1,1,1]])
conn4=array([[0,1,0],[1,1,1],[0,1,0]])
connS=array([[0,1,1,0],[1,1,1,1],[1,1,1,1],[0,1,1,0]],dtype=bool)
import astropy
from astropy.io import ascii
from copy import deepcopy as cp
from numpy import histogram
#import new image tools
#import pymorph
import skimage                                                                                                                                      
#from skimage import measure
#import mahotas

image=imagetools.GetImage(image_fl)
#        back_im=scipy.stats.scoreatpercentile(image,48)
CRNmaskfo=astropy.io.fits.open(CRNmask_fl)
CRNmask=asarray(CRNmaskfo[0].data,dtype=bool)
CRNheader=CRNmaskfo[0].header
CRNmaskfo.close()
oldmaskfo=astropy.io.fits.open(oldmask_fl)
oldmask=asarray(oldmaskfo[0].data,dtype=bool)
oldheader=oldmaskfo[0].header
oldmaskfo.close()
old_unmask=logical_not(oldmask)
CRN_unmask=logical_not(CRNmask)
CRN_masked_image=image.copy()
CRN_masked_image[CRNmask]=-2000
old_masked_image=image.copy()
old_masked_image[oldmask]=-2000

## save masked images
files2check=[image_fl]
flname=os.path.basename(image_fl).split('.')[0]
BASE=os.path.basename(image_fl).split('OCF')[0]
OUTDIR="/u/ki/awright/my_data/thesis_stuff/compare_CRN_to_old_cosmics/"
OUTIMAGECRN=OUTDIR+'CRN_mask_'+os.path.basename(image_fl)
OUTIMAGEOLD=OUTDIR+'OLD_mask_'+os.path.basename(image_fl)
hdu=astropy.io.fits.PrimaryHDU(old_masked_image)
hdu.header=oldheader
hdu.writeto(OUTIMAGEOLD,overwrite=True)
files2check.append(OUTIMAGEOLD)
hdu=astropy.io.fits.PrimaryHDU(CRN_masked_image)
hdu.header=CRNheader
hdu.writeto(OUTIMAGECRN,overwrite=True)
files2check.append(OUTIMAGECRN)
print "\n"+"\nds9 -zscale -tile mode column "+" ".join(files2check)+" -zscale -lock frame image -lock crosshair image -geometry 2000x2000 &"
#        header=CRfl[0].header
#        OBJECT=header['MYOBJ']
#        FILTER=header['FILTER']
#        CCDnum=header['IMAGEID']
#        #if CCDnum==7: PLOT_ON_OFF=1
#
#        #iter0: take the original files2check and prepare them for blending
#        files2check=[]
#        flname=os.path.basename(fl).split('.')[0]
#        BASE=os.path.basename(fl).split('OCF')[0]
#        #get cosmics images
#        OFB='%s_%s_%s' % (OBJECT,FILTER,BASE,)
#        CR_segfl='/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_CRN-cosmics_%s_%s.%s.fits' % (OBJECT,FILTER,BASE,)
#        CR_filtfl='/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/FILTERED_CRN-cosmics_%s_%s.%s.fits' % (OBJECT,FILTER,BASE,)
#        CRfitsfl=astropy.io.fits.open(CR_filtfl)
#        rms=CRfitsfl[0].header['MYRMS']
#        rms_bins=arange(10,100,5)
#        #adam-tmp# rms_bins=arange(10,90,5)
#        bthresh1_bin=digitize([rms],rms_bins)[0] #no "-1" here because I want the top-edge of the bin, not the bottom edge
#        #adam-tmp# if bthresh1_bin==0 or bthresh1_bin>15:
#        if bthresh1_bin==0 or bthresh1_bin>17:
#                print "adam-Error: in running BB on fl=",fl,"\n\nrun this command to check it out: ipython -i -- ~/thiswork/eyes/CRNitschke/blocked_blender.2.2.py ",fl,"\n\n"; raise Exception('this rms just is not right')
#        bthresh1=rms_bins[bthresh1_bin]
#        dt=CRfitsfl[0].header['CRN_DT']*rms#; ft=CRfitsfl[0].header['CRN_FT']*rms
#        dt_times_pt01=int(dt*.01+1) #this is like a ceiling function
