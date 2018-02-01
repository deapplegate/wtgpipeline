#! /usr/bin/env python
from astroquery.vizier import Vizier
import astropy.units as u 
import astropy.coordinates as coord
import requests
from astropy.io.votable import parse_single_table
import astropy.io.fits as pyfits
def panstarrs_query(ra_deg, dec_deg, rad_deg, mindet=1, 
                    maxsources=50001,
                    server=('https://archive.stsci.edu/'+
                            'panstarrs/search.php')): 
    """
    Query Pan-STARRS DR1 @ MAST
    parameters: ra_deg, dec_deg, rad_deg: RA, Dec, field 
                                          radius in degrees
                mindet: minimum number of detection (optional)
                maxsources: maximum number of sources
                server: servername
    returns: astropy.table object
    """
    r = requests.get(server, 
    params= {'RA': ra_deg, 'DEC': dec_deg, 
             'SR': rad_deg, 'max_records': maxsources, 
             'outputformat': 'VOTable', 
             'ndetections': ('>%d' % mindet)}) 
 
    # write query data into local file 
    outf = open('panstarrs.xml', 'w') 
    outf.write(r.text) 
    outf.close() 
 
    # parse local file into astropy.table object 
    data = parse_single_table('panstarrs.xml')
    return data.to_table(use_names_over_ids=True)

def joincats(cat1, cat2, cat1id='objID', cat2id = 'objID'):

    cat1order = {}
    for i, x in enumerate(cat1[cat1id]):
        cat1order[x] = i 
        
    cat2add_to_cat1 = []
    for x in cat2[cat2id]:
        if x in cat1order:
            cat2add_to_cat1.append(False)
        else:
            cat2add_to_cat1.append(True)

    cat2keep = numpy.array(cat2add_to_cat1)
    cat2new = cat2.filter(cat2keep)                                                                                                                                                                   
    return cat1.append(cat2new)

MACS0429_ra=67.40041667 ; MACS0429_dec=-2.88555556
#A2204_ra=248.19666667; A2204_dec=5.57555556
#bigA2204_2=panstarrs_query(ra+,dec+.2,.4)

from math import *
import numpy
import itertools
import sys
sys.path.append('/u/ki/awright/bonnpipeline/')
import ldac
search_radius=.425

grid_steps=numpy.array([-2,-1,0,1,2])
moves=[]
for x,y in itertools.permutations(grid_steps,2):
    if abs(x)+abs(y)<6: moves.append((x,y))
allmoves=moves+[(-1,-1),(0,0),(1,1)]
#startMACS0429=panstarrs_query(MACS0429_ra,MACS0429_dec,.425,maxsources=50001)
#startMACS0429.write('MACS0429_startcat_%s.txt' % (ii),format="ascii.fixed_width")
probs=['objName', 'raStack', 'decStack', 'raStackErr', 'decStackErr', 'nStackDetections',"Ang Sep (')"]
#'gQfPerfect', 'gMeanKronMag', 'gMeanKronMagErr', 'rQfPerfect', 'rMeanKronMag', 'rMeanKronMagErr', 'iQfPerfect', 'iMeanKronMag', 'iMeanKronMagErr', 'zQfPerfect', 'zMeanKronMag', 'zMeanKronMagErr', 'yQfPerfect', 'yMeanKronMag', 'yMeanKronMagErr']
goodkeys=['objID', 'raMean', 'decMean', 'raMeanErr', 'decMeanErr', 'nDetections', 'objInfoFlag', 'qualityFlag', 'epochMean', 'ng', 'nr', 'ni', 'nz', 'gQfPerfect', 'gMeanPSFMag', 'gMeanPSFMagErr', 'gMeanKronMag', 'gMeanKronMagErr', 'gMeanApMag', 'gMeanApMagErr', 'gFlags', 'rQfPerfect', 'rMeanPSFMag', 'rMeanPSFMagErr', 'rMeanKronMag', 'rMeanKronMagErr', 'rMeanApMag', 'rMeanApMagErr', 'rFlags', 'iQfPerfect', 'iMeanPSFMag', 'iMeanPSFMagErr', 'iMeanKronMag', 'iMeanKronMagErr', 'iMeanApMag', 'iMeanApMagErr', 'iFlags', 'zQfPerfect', 'zMeanPSFMag', 'zMeanPSFMagErr', 'zMeanKronMag', 'zMeanKronMagErr', 'zMeanApMag', 'zMeanApMagErr', 'zFlags']
goodkeys_types=[int,float,float,float,float,int,int,int,float,int,int,int,int,float,float,float,float,float,float,float,int,float,float,float,float,float,float,float,int,float,float,float,float,float,float,float,int,float,float,float,float,float,float,float,int]
goodtypes={}
for key,v in zip(goodkeys,goodkeys_types):
    if key=='objID': continue
    goodtypes[key]={'python':v}
    if v==float: goodtypes[key]['ldac']='D'
    if v==int: goodtypes[key]['ldac']='K'


## do the tiling
ii=0
for dx,dy in allmoves:
	ii+=1
	ra,dec=MACS0429_ra+dx*.6, MACS0429_dec+dy*.6
	bigMACS0429=panstarrs_query(ra,dec,search_radius,mindet=4,maxsources=50001)
	print len(bigMACS0429), " ii=",ii
	if len(bigMACS0429)>48000: print "adam-look Error: len too long, ii=",ii
	filter_i=bigMACS0429['ni'].data.data>0

	## now filter the stars out
	#filterit*=bigMACS0429["gQfPerfect"].data.data>=.85
	#filterit*=bigMACS0429["rQfPerfect"].data.data>=.85
	#filterit*=bigMACS0429["iQfPerfect"].data.data>=.85
	#filterit*=bigMACS0429["zQfPerfect"].data.data>=.85
	#diff_psf_kron=bigMACS0429["iMeanPSFMag"].data.data-bigMACS0429["iMeanKronMag"].data.data< 0.05
	#filterit*=diff_psf_kron

	## save in ldac format
	cols=[pyfits.Column(name='objID', format='18A' ,array = bigMACS0429['objID'].data.data[filter_i])]
	for key in goodkeys:
		if key=='objID': continue
		cols.append(pyfits.Column(name=key,format=goodtypes[key]['ldac'], array = numpy.array(bigMACS0429[key].data,dtype=goodtypes[key]['python'])[filter_i])) #bigMACS0429

	hduSTDTAB = pyfits.BinTableHDU.from_columns(cols)
	hdu = pyfits.PrimaryHDU()
	hdulist = pyfits.HDUList([hdu,hduSTDTAB])
	hdulist[1].header['EXTNAME']='OBJECTS'
	hdulist.writeto('/nfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/panstarrs_cats/new_startcat_%s_%s.ldac' % (dx,dy),clobber=True)
	#bigMACS0429.write('/nfs/slac/kipac/fs1/u/awright/MACS0429_panstarrs_cats/MACS0429_startcat_%s_%s.txt' % (dx,dy),format="ascii.tab")
	if ii==1:
		mastercat=ldac.LDACCat(hduSTDTAB)
	else:
		mastercat=joincats(mastercat,ldac.LDACCat(hduSTDTAB))
	print ii,': dx,dy=',dx,dy,': len(bigMACS0429)=',len(bigMACS0429),': len(mastercat)=',len(mastercat)

mastercat.saveas('/nfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/panstarrs_cats/new_startcat_combined.ldac')
print "len(mastercat)=",len(mastercat)
