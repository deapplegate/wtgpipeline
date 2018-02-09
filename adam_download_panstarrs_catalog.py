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

ra_cluster={}
dec_cluster={}
ra_cluster['MACS0429-02']=67.40041667 ; dec_cluster['MACS0429-02']=-2.88555556
ra_cluster['RXJ2129']=322.41625000 ; dec_cluster['RXJ2129']=0.08888889
#A2204_ra=248.19666667; A2204_dec=5.57555556
#bigA2204_2=panstarrs_query(ra+,dec+.2,.4)

from math import *
import numpy
import itertools
import sys
import ldac
import os
search_radius=.425

grid_steps=numpy.array([-2,-1,0,1,2])
moves=[]
for x,y in itertools.permutations(grid_steps,2):
    if abs(x)+abs(y)<4: moves.append((x,y))
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

cluster='RXJ2129'
if not os.path.isdir('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/' % (cluster)):
	os.mkdir('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/' % (cluster))

## do the tiling
ii=0
for dx,dy in allmoves:
	ii+=1
	ra,dec=ra_cluster[cluster]+dx*.6, dec_cluster[cluster]+dy*.6
	big_tile_cat=panstarrs_query(ra,dec,search_radius,mindet=4,maxsources=50001)
	print len(big_tile_cat), " ii=",ii
	if len(big_tile_cat)>48000: print "adam-look Error: len too long, ii=",ii
	filter_i=big_tile_cat['ni'].data.data>0

	## now filter the stars out
	#filterit*=big_tile_cat["gQfPerfect"].data.data>=.85
	#filterit*=big_tile_cat["rQfPerfect"].data.data>=.85
	#filterit*=big_tile_cat["iQfPerfect"].data.data>=.85
	#filterit*=big_tile_cat["zQfPerfect"].data.data>=.85
	#diff_psf_kron=big_tile_cat["iMeanPSFMag"].data.data-big_tile_cat["iMeanKronMag"].data.data< 0.05
	#filterit*=diff_psf_kron

	## save in ldac format
	cols=[pyfits.Column(name='objID', format='18A' ,array = big_tile_cat['objID'].data.data[filter_i])]
	for key in goodkeys:
		if key=='objID': continue
		cols.append(pyfits.Column(name=key,format=goodtypes[key]['ldac'], array = numpy.array(big_tile_cat[key].data,dtype=goodtypes[key]['python'])[filter_i])) #big_tile_cat

	hduSTDTAB = pyfits.BinTableHDU.from_columns(cols)
	hdu = pyfits.PrimaryHDU()
	hdulist = pyfits.HDUList([hdu,hduSTDTAB])
	hdulist[1].header['EXTNAME']='OBJECTS'
	hdulist.writeto('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/new_startcat_%s_%s.ldac' % (cluster,dx,dy),overwrite=True)
	if ii==1:
		mastercat=ldac.LDACCat(hduSTDTAB)
	else:
		mastercat=joincats(mastercat,ldac.LDACCat(hduSTDTAB))
	print ii,': dx,dy=',dx,dy,': len(big_tile_cat)=',len(big_tile_cat),': len(mastercat)=',len(mastercat)

mastercat.saveas('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/new_startcat_combined.ldac' % (cluster),overwrite=True)
print "len(mastercat)=",len(mastercat)
