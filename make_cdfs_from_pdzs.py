#! /usr/bin/env python
import numpy, sys, pickle, astropy.io.fits as pyfits
sys.path.append("/u/ki/awright/wtgpipeline/")
import ldac
catold = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos.cat')
pdz2015fo=pyfits.open("/u/ki/awright/COSMOS_2017/COSMOS_2015/pdz_cosmos2015_ID2008_added.fits")
pdz2015=ldac.LDACCat(pdz2015fo[1])

colnames=[('Z%.2f' % (z)).replace('.','_') for z in numpy.arange(0,6.01,.01)]
pdz_match=pdz2015.matchById(catold,"id","ID2008")
pdz_array=numpy.column_stack([pdz_match[k] for k in colnames])
pdzs=pdz_array.astype(numpy.float32)
pz_cdfs=pdzs.cumsum(axis=1)
normit=pz_cdfs[:,-1]
pz_cdfs_norm=(pz_cdfs.T/normit).T

fl=open('/u/ki/awright/COSMOS_2017/COSMOS_2015/id2pz_cdf_2015_matched_catold.pkl','wb')
id2pz_cdf={}
for id , cdf in zip(pdz_match['ID2008'],pz_cdfs_norm):
    id2pz_cdf[id]=cdf

pickle.dump(id2pz_cdf,fl)
fl.close()
