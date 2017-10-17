#! /usr/bin/env python
#adam-does# measures the median value of the radially masked left side ccds and right-side ccds for the DOME and SKY flats to give a measure of which SCIENCE_norm images are flatter.
import astropy.io.fits as pyfits,os,sys
from glob import glob
#sys.path.append('~/InstallingSoftware/pythons/')
import imagetools
import numpy as n
import matplotlib.pylab as p

for pprun in ["2010-03-12_W-J-B","2010-11-04_W-J-B","2009-09-19_W-J-V","2010-03-12_W-C-RC"]:
	SKY_L_med=[]
	SKY_R_med=[]
	DOME_L_med=[]
	DOME_R_med=[]
	original="/nfs/slac/g/ki/ki18/anja/SUBARU/%s/SCIENCE/ORIGINALS/SUPA*.fits" % (pprun,)
	fls=glob(original)
	fls=[os.path.basename(fl).split(".")[0] for fl in fls]

	## set up masks
	Lmask={}
	Rmask={}
	for chip in [1,2,6,7]:
		maskfl="/nfs/slac/g/ki/ki18/anja/SUBARU/RADIAL_MASKS/SUBARU_10_3/RadialMask_10_3_%s.fits" % (chip)
		maskdata=n.asarray(pyfits.open(maskfl)[0].data,dtype=bool)
		Lmask[chip]=maskdata.flatten()
	for chip in [4,5,9,10]:
		maskfl="/nfs/slac/g/ki/ki18/anja/SUBARU/RADIAL_MASKS/SUBARU_10_3/RadialMask_10_3_%s.fits" % (chip)
		maskdata=n.asarray(pyfits.open(maskfl)[0].data,dtype=bool)
		Rmask[chip]=maskdata.flatten()

	##Lmed first
	for fl in fls:
		print "now on: ",fl

		LDOME=n.array((0,))
		LSKY=n.array((0,))
		for chip in [1,2,6,7]:
			maskdata=Lmask[chip]
			DOMEfl="/nfs/slac/g/ki/ki18/anja/SUBARU/%s/SCIENCE_norm_DOMEFLAT/%s_%sOCFN.fits" % (pprun,fl,chip)
			SKYfl="/nfs/slac/g/ki/ki18/anja/SUBARU/%s/SCIENCE_norm_SKYFLAT/%s_%sOCFN.fits" % (pprun,fl,chip)
			DOMEdata=pyfits.open(DOMEfl)[0].data
			SKYdata=pyfits.open(SKYfl)[0].data
			LDOME=n.append(LDOME,DOMEdata.flatten()[maskdata])
			LSKY=n.append(LSKY,SKYdata.flatten()[maskdata])
		LDOMEmed=n.median(LDOME)
		DOME_L_med.append(LDOMEmed)
		LSKYmed=n.median(LSKY)
		SKY_L_med.append(LSKYmed)

		##Rmed second
		RDOME=n.array((0,))
		RSKY=n.array((0,))
		for chip in [4,5,9,10]:
			maskdata=Rmask[chip]
			DOMEfl="/nfs/slac/g/ki/ki18/anja/SUBARU/%s/SCIENCE_norm_DOMEFLAT/%s_%sOCFN.fits" % (pprun,fl,chip)
			SKYfl="/nfs/slac/g/ki/ki18/anja/SUBARU/%s/SCIENCE_norm_SKYFLAT/%s_%sOCFN.fits" % (pprun,fl,chip)
			DOMEdata=pyfits.open(DOMEfl)[0].data
			SKYdata=pyfits.open(SKYfl)[0].data
			RDOME=n.append(RDOME,DOMEdata.flatten()[maskdata])
			RSKY=n.append(RSKY,SKYdata.flatten()[maskdata])
		RDOMEmed=n.median(RDOME)
		DOME_R_med.append(RDOMEmed)
		RSKYmed=n.median(RSKY)
		SKY_R_med.append(RSKYmed)
	## get skews
	SKY_L_med=n.asarray(SKY_L_med)
	SKY_R_med=n.asarray(SKY_R_med)
	DOME_L_med=n.asarray(DOME_L_med)
	DOME_R_med=n.asarray(DOME_R_med)
	DOME_skew = DOME_L_med - DOME_R_med
	SKY_skew = SKY_L_med - SKY_R_med
	for i,fl in enumerate(fls):
		if abs(DOME_skew[i])>abs(SKY_skew[i]):
			FLATTEST="SKYFLAT"
		else:
			FLATTEST="DOMEFLAT"
		print pprun, fl , FLATTEST, DOME_skew[i], SKY_skew[i]

######## from matplotlib.pylab import *
########imagetools.PlotImage(maskdata,plotlim=(0,1))
#########imagetools.PlotImage(maskdata,plotlim=(0,1))
########maskdata.dtype
########maskdata.dtype='bool'
########maskdata
########imagetools.PlotImage(maskdata,plotlim=(0,1))
########imshow(maskdata,vmin=0,vmax=1,interpolation='nearest',origin='lower left')
########maskdata
########print maskdata
########print maskdata
########print maskdata[0]
########maskdata[0]
########for i in range(4000):
########	    print maskdata[i].sum()
########show()
