#! /usr/bin/env python
#adam-does# this file runs BartStar.getstars and then saves this so that these detections can be blocked from masking by blocked_blender.py
#adam-use# this should be used with the CRNitschke pipeline
import sys ; sys.path.append('/u/ki/awright/InstallingSoftware/pythons')
from import_tools import *
#import sextract
import BartStar
namespace=globals()
import astropy
savedir='/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_stars/'
SEXDIR='/u/ki/awright/InstallingSoftware/pythons/sextractimtools/'
def getstar_segments(star_infl,seeing=None,radmagrange=None,mode='liberal',unsat_cut=None,**kwargs): #,mode="liberal",unsat_cut=None,ELLIPTICITY=.25)
	'''run getstar() and get a segmentation image of just the stars'''
	CRfl=astropy.io.fits.open(star_infl)
	header=CRfl[0].header
	OBJECT=header['MYOBJ']
	FILTER=header['FILTER']
	if unsat_cut==None: #this means include saturated stars!
		return_names=['star_table','good_box','sat_star_box','star_fitsfl']
		star_table,good_box,sat_star_box,star_fitsfl=BartStar.getstar(star_infl,seeing=seeing,radmagrange=radmagrange,mode=mode,unsat_cut=unsat_cut,return_names=return_names,**kwargs)
		all_stars_box=good_box+sat_star_box #star or saturated star
	else:
		return_names=['star_table','good_box','star_fitsfl']
		star_table,good_box,star_fitsfl=BartStar.getstar(star_infl,seeing=seeing,radmagrange=radmagrange,mode=mode,unsat_cut=unsat_cut,return_names=return_names,**kwargs)
		all_stars_box=good_box
        flname=os.path.basename(star_infl).split('.')[0]
        if 'OCF' in star_infl:
                BASE=os.path.basename(star_infl).split('OCF')[0]
        else:
                BASE=flname
	star_only_table=star_table[all_stars_box]
	starlabellist=star_table['NUMBER'].data
	starll = starlabellist[all_stars_box]
	segments_all=imagetools.GetImage(star_fitsfl)
	segments_stars=zeros(segments_all.shape,dtype=segments_all.dtype)
	for count,label in enumerate(starll): #re-number the stars
		segments_stars[segments_all==label]=count+1
		star_only_table['NUMBER'][count]=count+1
	#now save the catalog file, align the columns, and add the header to the top of the file
	star_only_catfl=savedir+"CATALOG_CRN-stars_%s_%s.%s.cat" % (OBJECT,FILTER,BASE,)
	star_only_table.write(star_only_catfl,format='ascii.no_header')
	os.system("column -t "+star_only_catfl+" > "+star_only_catfl+".tmp")
	os.system('cat '+SEXDIR+'stars.sex.header '+star_only_catfl+".tmp > "+star_only_catfl)
	os.system('rm '+star_only_catfl+".tmp")
        #ssnew=scipy.ndimage.grey_dilation(segments_stars,footprint=conn8)
	star_only_segfl=savedir+"SEGMENTATION_CRN-stars_%s_%s.%s.fits" % (OBJECT,FILTER,BASE,)
        hdu=astropy.io.fits.PrimaryHDU(segments_stars)
        hdu.writeto(star_only_segfl ,overwrite=True)
        print "wrote the CATALOG %s and the SEGMENTATION image %s of the stars (%s stars in total) picked from the image %s" % (star_only_catfl,star_only_segfl,count,star_infl)
	os.system("rm "+star_fitsfl)
	os.system("rm "+star_fitsfl.replace('.fits','.cat'))
	namespace.update(locals())

if __name__ == "__main__":
	if len(sys.argv)<2:
		sys.exit()
	if not os.path.isfile(sys.argv[1]):
		print "sys.argv[1]=",sys.argv[1]
		raise Exception(sys.argv[1]+" is not a file!")
	else:
		img_name=sys.argv[1]
	print "Using stars2block.py to get stars for: "+img_name
	CRfl=astropy.io.fits.open(img_name)
	header=CRfl[0].header
	if 'MYSEEING' in header.keys():seeing=header['MYSEEING'];print "using MYSEEING=%.2f" % (seeing)
	else:seeing=None
	getstar_segments(img_name,seeing=seeing,mode="liberal",unsat_cut=None,ELLIPTICITY=.25)
