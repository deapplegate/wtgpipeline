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

args=glob('/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_compare/BB_ERASED_*_3.fits')
#CR_segfl='/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_BB_CRN-cosmics_MACS0429-02_W-J-B.SUPA0154630_9.fits'
#/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_CRN-cosmics_MACS0429-02_W-J-B.SUPA0154630_1.fits
#CR_newsegfl=CR_segfl.replace('SEGMENTATION_CRN-cosmics','SEGMENTATION_BB_CRN-cosmics')
compdir='/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_compare/'
alldir='/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/'
time=[]
rms=[]
seeing=[]
Nstars_rm=[]
Nmasks0=[]
NmasksN=[]
Npix0=[]
NpixN=[]
for arg in args:
    try:
	CR_segfl=alldir+'SEGMENTATION_CRN-cosmics_'+arg.split('_BBCR_')[-1]
	#adam-tmp# put BB or BBSS in here depending on the final output
	CR_newsegfl=alldir+'SEGMENTATION_BBSS_CRN-cosmics_'+arg.split('_BBCR_')[-1]
	#fo=astropy.io.fits.open(arg)
	#fo=astropy.io.fits.open(arg)
	fo=astropy.io.fits.open(arg)
	header=fo[0].header
	if header['CONFIG']=='10_3':
		pass
	else:
		print header['CONFIG'],arg
		continue
	im=fo[0].data
	if im.max()>0:
		image=asarray(im,dtype=bool)
		StarRMseg,Nlabels=scipy.ndimage.label(image,conn8)
	else:
		Nlabels=0
	print Nlabels,header['MYSEEING'],header['EXPTIME'],header['MYRMS']
	fo=astropy.io.fits.open(CR_newsegfl)
	segfinal=fo[0].data
	CRmasksN=segfinal.max()
	CRpixN=(segfinal>0).sum()
	fo=astropy.io.fits.open(CR_segfl)
	seginit=fo[0].data
	seginit.max()
	CRmasks0=seginit.max()
	CRpix0=(seginit>0).sum()

	Nmasks0.append(CRmasks0)
	NmasksN.append(CRmasksN)
	Npix0.append(CRpix0)
	NpixN.append(CRpixN)
	seeing.append(header['MYSEEING'])
	time.append(header['EXPTIME'])
	rms.append(header['MYRMS'])
	Nstars_rm.append(Nlabels)
    except IOError as e:
	print e
	continue

ANstars_rm=array(Nstars_rm)
Aseeing=array(seeing)
Arms=array(rms)
ANmasks0=array(Nmasks0)
ANpix0=array(Npix0)
ANmasksN=array(NmasksN)
ANpixN=array(NpixN)
Atime=array(time)
ANmasksNrate=array(NmasksN)/Atime

def seeing_binned(Aprop):
	less_pt6=Aprop[Aseeing<=0.6]
	pt6_to_pt7=Aprop[(Aseeing>0.6) * (Aseeing<0.7)]
	great_pt7=Aprop[Aseeing>=0.7]
	print '<=0.6:',less_pt6.mean()
	print '0.6<seeing<0.7:',pt6_to_pt7.mean()
	print '>=0.7:',great_pt7.mean()

print '\n# masks, 0 and N:'
seeing_binned(ANmasks0)
seeing_binned(ANmasksN)


print '\n# pixels, 0 and N:'
seeing_binned(ANpix0)
seeing_binned(ANpixN)

print '\nmask rate:'
seeing_binned(ANmasksNrate)

ANpixNrate=array(NpixN)/Atime
ANpix0rate=array(Npix0)/Atime

print '\nmask-pixels rate at 0:'
seeing_binned(ANpix0rate)

print '\nmask-pixels rate at N:'
seeing_binned(ANpixNrate)
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

