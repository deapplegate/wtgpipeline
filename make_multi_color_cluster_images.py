#! /usr/bin/env python
import astropy
import astropy.io.fits
import os

# 
fgas_clusters =['Zw2089','RXJ2129','MACS1115+01']
for cl in fgas_clusters:
	dir='/u/ki/awright/my_data/SUBARU/'+cl+'/coadds_together_'+cl+'/'
	for filter in ['W-J-B','W-C-RC','W-S-Z+']:
		fl1=dir+'coadd_'+cl+'_all.'+filter+'.fits'
		fl2=dir+'coadd_'+cl+'_3s.'+filter+'_2015-12-15_CALIB.fits'
		if not os.path.isfile(fl2):
			print 'not a file: ',fl2
			continue
		flpretty=dir+'coadd_'+cl+'_pretty.'+filter+'.fits'
		flw=dir+'weights/'+os.path.basename(fl1).replace('fits','weight.fits')
		im1=astropy.io.fits.open(fl1)[0].data
		missing = im1==0
		im1w=astropy.io.fits.open(flw)[0].data
		imw=im1w #/im1w.sum()
		im2=astropy.io.fits.open(fl2)[0].data
		from numpy import *
		conn8=array([[1,1,1],[1,1,1],[1,1,1]])                                                                                                                                              
		conn4=array([[0,1,0],[1,1,1],[0,1,0]])
		pretty=where(imw>10**-3,im1,im2)

		## fill in sat stars
		from scipy import ndimage
		#(pretty==0)
		if filter=='W-S-Z+':
			bigs=(pretty>1.3)
		elif filter=='W-J-B':
			bigs=(pretty>4.0)
		else:
			 bigs=(pretty>7.0)
		BBCRseg,BBCR_Nlabels=ndimage.label(bigs,conn8)
		BBCRslices=ndimage.find_objects(BBCRseg) ; BBCRlabels=arange(BBCR_Nlabels)+1
		bigs_b4=bigs.copy()

		for l,sl in zip(BBCRlabels,BBCRslices):
		    spots=BBCRseg[sl]==l
		    spotsfilled=ndimage.binary_fill_holes(spots)
		    fillings=spotsfilled * logical_not(spots)
		    
		    missing_some=missing[sl][fillings].any()
		    # if it didn't actually fill something in, then remove this thing
		    if not ( spotsfilled.sum() > spots.sum() ) or not missing_some:
		        bigs[sl][spots]=0
		bigsfilled=ndimage.binary_fill_holes(bigs)

		## save image
		
		bigsfilledexpand=ndimage.binary_dilation(bigsfilled)

		BBCRseg,BBCR_Nlabels=ndimage.label(bigsfilledexpand,conn8)
		BBCRslices=ndimage.find_objects(BBCRseg) ; BBCRlabels=arange(BBCR_Nlabels)+1
		pretty_b4=pretty.copy()
		for l,sl in zip(BBCRlabels,BBCRslices):
		    spots=BBCRseg[sl]==l
		    pretty[sl][spots]=pretty_b4[sl][spots].max()

		## save image
		os.system('cp '+fl1+' '+flpretty)
		fopretty=astropy.io.fits.open(flpretty,'update')
		fopretty[0].data=pretty
		fopretty.flush()

		if 0:
			from matplotlib.pylab import *
			f=figure()
			title('bigs')
			imshow(bigs,interpolation='nearest')
			f=figure()
			title('bigsfilled')
			imshow(bigsfilled,interpolation='nearest')
			f=figure()
			title('bigsfilledexpand')
			imshow(bigsfilledexpand,interpolation='nearest')
			show()

		print 'ds9e '+' '.join([fl1,fl2,flpretty]) + ' &'
