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

from my_cluster_params import ra_cluster,dec_cluster
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

#clusters =['MACS0429-02','MACS1226+21','RXJ2129','MACS1115+01',"MACS0416-24",'MACS0159-08', 'Zw2089', 'Zw2701', 'A2204']
cluster='A2204'

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
filters['pos_err']=(numpy.sqrt(mastercat['decMeanErr']**2+mastercat['raMeanErr']**2)<2*PIXSCALE)

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
keys=['ni','iQfPerfect','iMagDiff']
filter_stars=filters['pos_err'].copy()
for k in keys:
	filter_stars*=filters[k]
	print k, filters[k].mean()
	print " cut %s passed = %4.3f" % (k,filters[k].mean())
print " all of the above cuts combined = %4.3f" % (filter_stars.mean())

if not os.path.isdir('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/PHOTOMETRY/' % (cluster)):
	os.mkdir('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/PHOTOMETRY/' % (cluster))
# main cut
if os.path.isfile('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/PHOTOMETRY/astrefcat-stars_only.cat' % (cluster)):
	os.system('mv /nfs/slac/kipac/fs1/u/awright/SUBARU/%s/PHOTOMETRY/astrefcat-stars_only.cat /nfs/slac/kipac/fs1/u/awright/SUBARU/%s/PHOTOMETRY/astrefcat-stars_only.cat.old' % (cluster,cluster))
mastercat_stars=mastercat.filter(filter_stars)
# now filter the stars out
mastercat_stars.saveas('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/PHOTOMETRY/astrefcat-stars_only.cat' % (cluster),overwrite=True)

## now open in a different format
incat="astrefcat-stars_only"
mastercat=pyfits.open('/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/PHOTOMETRY/%s.cat' % (cluster,incat))
master=mastercat[1].data


sdss_keys=['flags','clean', 'ra', 'dec', 'raErr', 'decErr', 'psfMag_u', 'psfMag_g', 'psfMag_r', 'psfMag_i', 'psfMag_z', 'psfMagErr_u', 'psfMagErr_g', 'psfMagErr_r', 'psfMagErr_i', 'psfMagErr_z']
from astropy.table import Table
flags=master.columns['iFlags'].array.copy()
clean=master.columns['iFlags'].array.copy()
uMag=master.columns['iMeanPSFMag'].array.copy()
uMagErr=master.columns['iMeanPSFMag'].array.copy()
for i in range(len(clean)):
    uMag[i]=-999.0
    uMagErr[i]=99.0
    flags[i]=0
    clean[i]=1
outcols=[flags,clean]
names=['flags','clean']
dtypes=[flags.dtype,clean.dtype]
names+=['ra', 'dec', 'raErr', 'decErr']
dtypes+=[float,float,float,float]
outcols+=[master.columns['raMean'].array,master.columns['decMean'].array,master.columns['raMeanErr'].array*1/3600.0,master.columns['decMeanErr'].array*1/3600.0]
names.append('psfMag_u')
dtypes.append(float)
outcols.append(uMag)
magkeys=['gMeanPSFMag', 'rMeanPSFMag', 'iMeanPSFMag', 'zMeanPSFMag']
for k in magkeys:
	k0=k[0]
	dtypes.append(float)
	names.append('psfMag_'+k0)
	outcols.append(master.columns[k].array)

names.append('psfMagErr_u')
dtypes.append(float)
outcols.append(uMagErr)
magerrkeys=['gMeanPSFMagErr', 'rMeanPSFMagErr', 'iMeanPSFMagErr', 'zMeanPSFMagErr']
for k in magerrkeys:
	k0=k[0]
	dtypes.append(float)
	names.append('psfMagErr_'+k0)
	outcols.append(master.columns[k].array)

#outcols=[master.columns[k].array for k in savekeys]
#t = Table(data=outcols,names=savekeys,dtype=[str,float,float,float,float,float,float,float,float,float,float])
t = Table(data=outcols,names=names,dtype=dtypes)
fullincat='/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/PHOTOMETRY/%s' % (cluster,incat)
t.write("%s.tsv" % (fullincat) , format='ascii.tab',overwrite=True)
os.system("column -t %s.tsv > %s.txt" % (fullincat,fullincat))
os.system("rm %s.tsv" % (fullincat,))
illum_cat='/nfs/slac/kipac/fs1/u/awright/SUBARU/%s/PHOTOMETRY/%s' % (cluster,'panstarrs_stars_illumcorr.csv')
t.write(illum_cat,format='ascii.csv',overwrite=True)
