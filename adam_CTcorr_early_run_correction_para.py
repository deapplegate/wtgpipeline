#! /usr/bin/env python
#adam-does# this makes crosstalk corrected images (OCFX) from uncorrected images (OCF) and the ctcorr difference images (diff) made by adam_CTcorr_make_images_para.sh
#adam-use# this does the job of adam_CTcorr_run_correction_para.py, but before splitting off by ${cluster}!
#adam-use# use this to correct for the effect of crosstalk further down the pipeline than you would otherwise if you start out using the ctcorr in pre-processing
#adam-example# ./parallel_manager.sh ./adam_CTcorr_run_correction_para.py 'W-C-RC' '2010-02-12' 'MACS1226+21' 'OCF'
#adam-example# ./adam_CTcorr_early_run_correction_para.py 'W-C-RC' '2011-11-04' 'MACS0416-24' 'OCFR'
# so it's either: ./parallel_manager.sh ./adam_CTcorr_early_run_correction_para.py ${filter} ${run} ${ending}
# or it's       : ./adam_CTcorr_early_run_correction_para.py ${filter} ${run} ${ending}
import astropy, astropy.io.fits as pyfits
import sys,os,inspect
sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
from import_tools import *
curfile=os.path.abspath(inspect.getfile(inspect.currentframe()))
FileString=os.path.basename(curfile)
args=imagetools.ArgCleaner(sys.argv,FileString)
try:
	filter,run,ending,chips=args
	chips_list=asarray(chips.split(),dtype=int)
except ValueError:
	filter,run,ending=args
	chips=" 1 2 3 4 5 6 7 8 9 10"
	chips_list=arange(1,11)

print "filter,run,ending,chips=",filter,run,ending,chips

## Now the difference images from ctcorr!
endingX=ending+"X"
for chip in chips_list:
	fls_diff=glob("/u/ki/awright/data/%s_%s/SCIENCE/IM_diff/SUPA*_%i_diff.fits" % (run,filter,chip))
	for fl_diff in fls_diff:
		basename_diff=os.path.basename(fl_diff)[:-10]
		fl_ending="/u/ki/awright/data/%s_%s/SCIENCE/%s%s.fits" % (run,filter,basename_diff,ending)
		if not os.path.isfile(fl_ending):
			raise Exception("PROBLEM with input file to correct:\nfl_ending=%s\nINPUT args are:\n\tfilter=%s\n\trun=%s\n\tending=%s\n\tchips=%s" % (fl_ending,filter,run,ending,chips))
		flX="/u/ki/awright/data/%s_%s/SCIENCE/%s%s.fits" % (run,filter,basename_diff,endingX)
		im_diff=pyfits.open(fl_diff)[0].data
		im_diff=asarray(im_diff,dtype=float32)
		print "%s: min=%.1f mean=%.1f max=%.1f " % (os.path.basename(fl_diff),im_diff.min(),im_diff.mean(),im_diff.max())
		# nanmin(ma.array(logdivXC,mask=logical_not(isfinite(logdivXC))))
		# nanmax(ma.array(logdivXC,mask=logical_not(isfinite(logdivXC))))
		im_ending=pyfits.open(fl_ending)[0].data
		head=pyfits.open(fl_ending)[0].header
		head['CTCORR']=True
		im_ending=asarray(im_ending,dtype=float32)
		imX=im_ending-im_diff
		hdu=pyfits.PrimaryHDU(imX,header=head)
		hdu.writeto(flX,overwrite=True)
