#! /usr/bin/env python
import glob,os
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
fl='/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/new_startcat_combined.ldac' % (cluster)
fo=pyfits.open(fl)
mastercat=ldac.LDACCat(fo[1])
print "len(mastercat)=",len(mastercat)

filters={}
PIXSCALE=0.2632
filters['ng']=mastercat['ng']>0
filters['nr']=mastercat['nr']>0
filters['ni']=mastercat['ni']>0
filters['nz']=mastercat['nz']>0
filters['gQfPerfect']=mastercat['gQfPerfect']>=.85
filters['rQfPerfect']=mastercat['rQfPerfect']>=.85
filters['iQfPerfect']=mastercat['iQfPerfect']>=.85
filters['zQfPerfect']=mastercat['zQfPerfect']>=.85
filters['iMagDiff']=mastercat["iMeanPSFMag"]-mastercat["iMeanKronMag"]< 0.05
filters['pos_err']=(numpy.sqrt(mastercat['decMeanErr']**2+mastercat['raMeanErr']**2)<PIXSCALE)

# main cut
filter_poserr_3filt=filters['pos_err']*filters['nr']*filters['ni']*filters['nz']
filter_poserr_4filt=filters['pos_err']*filters['nr']*filters['ni']*filters['nz']*filters['ng']
filter_3filt=filters['nr']*filters['ni']*filters['nz']

##
# star: num dets>0 for griz
# star: QfPerfect>0 for griz
# star: iMeanPSFMag-iMeanKronMag< 0.05
# qual: sqrt(decMeanErr**2+raMeanErr**2)<.04
##
keys=['ng','nr','ni','nz','gQfPerfect','rQfPerfect','iQfPerfect','zQfPerfect','iMagDiff','pos_err']
filter_stars=filters['pos_err'].copy()
for k in keys:
	filter_stars*=filters[k]
	print k, filters[k].mean()
	print " cut %s passed = %4.3f" % (k,filters[k].mean())
print " all of the above cuts combined = %4.3f" % (filter_stars.mean())

# main cut
mastercat_use=mastercat.filter(filter_poserr_3filt)
mastercatng=mastercat.filter(filter_poserr_4filt)
mastercat3filt=mastercat.filter(filter_3filt)
mastercat_stars=mastercat.filter(filter_stars)
sys.exit()
mastercat_use.saveas('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/astrefcat.cat' % (cluster),overwrite=True)
#
mastercat3filt.saveas('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/astrefcat-3filt_only.cat' % (cluster),overwrite=True)
# main cut + cut ng
mastercatng.saveas('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/astrefcat-also_ng.cat' % (cluster),overwrite=True)
# now filter the stars out
mastercat_stars.saveas('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/astrefcat-stars_only.cat' % (cluster),overwrite=True)

print ' len(mastercat),len(mastercat_use),len(mastercatng),len(mastercat_stars)=',len(mastercat),len(mastercat_use),len(mastercatng),len(mastercat_stars)

fnames=[ "/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/astrefcat-3filt_only.cat" % (cluster), "/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/astrefcat.cat" % (cluster), "/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/astrefcat-ng_cat.cat" % (cluster), "/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/astrefcat-stars_only.cat" % (cluster)]
cats=[mastercat,mastercat_use,mastercatng,mastercat_stars]
savekeys=["objID","raMean","decMean","raMeanErr","decMeanErr","iMeanPSFMag","iMeanPSFMagErr","iMeanKronMag","iMeanKronMagErr","iMeanApMag","iMeanApMagErr"]
#for fname,cat in zip(fnames,cats):
#	#cols_cp=[] #masterhdu.columns
#	#masterhdu=cat.hdu
#	#for col in masterhdu.columns:
#	#    if col.name in savekeys:
#	#	cols_cp.append(col)
#	#hduSTDTAB = pyfits.BinTableHDU.from_columns(cols_cp)
#	#hdu = pyfits.PrimaryHDU()
#	#hdulist = pyfits.HDUList([hdu,hduSTDTAB])
#	#hdulist[1].header['EXTNAME']='LDAC_OBJECTS'
#	#hdulist.writeto(fname,clobber=True)

from astropy.table import Table
for incat in ["astrefcat-3filt_only","astrefcat","astrefcat-stars_only","astrefcat-also_ng"]:

	mastercat=pyfits.open('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/%s.cat' % (cluster,incat))
	master=mastercat[1].data
	master["raMeanErr"]*=1/3600.0
	master["decMeanErr"]*=1/3600.0
	outcols=[master.columns[k].array for k in savekeys]
	incat='/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/panstarrs_cats/%s' % (cluster,incat)
	t = Table(data=outcols,names=savekeys,dtype=[str,float,float,float,float,float,float,float,float,float,float])
	t.write("%s.tsv" % (incat) , format='ascii.tab',overwrite=True)
	os.system("column -t %s.tsv > %s.txt" % (incat,incat))
	os.system("rm %s.tsv" % (incat,))
	print "asctoldac -i %s.txt -o %s.cat -t LDAC_OBJECTS -c ~/wtgpipeline/asctoldac_panstarrs.config" % (incat,incat)

#plotkeys=['iMeanPSFMag', 'iMeanKronMag', 'iMeanApMag', 'iMeanPSFMagErr', 'iMeanKronMagErr', 'iMeanApMagErr', 'raMeanErr', 'decMeanErr']
#f=figure()
#for i,k in enumerate(plotkeys):
#    f.add_subplot(3,3,i+1)
#    title(k)
#    hist(mastercat[k],bins=20)

if not os.path.isdir('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/PHOTOMETRY/' % (cluster)):
	os.mkdir('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/PHOTOMETRY/' % (cluster))

