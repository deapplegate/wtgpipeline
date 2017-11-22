#! /usr/bin/env python
import numpy, sys, pickle, astropy.io.fits as pyfits
import ldac
sys.path.append("/u/ki/awright/wtgpipeline/")
cat=ldac.openObjectFile("/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat")
catold = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos.cat')
#pdzcat=pyfits.open("/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/pdz_v2.0_010312.fits")
#pdz2015=ldac.LDACCat(pdzcat[1])
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

#pdz_array=pdz_match[:,10:]
#pdz.columns.names[10] 'Z0_00'
#pdz.columns.names[0] 'ID'
sys.exit()
# zphot  'Z_FINAL'
# zpdf   'Z_MED_PDZ'
# zchi   'ZMIN_CHI2'
# zphot2 'SECOND_PEAK'
Z_FINAL,Z_MED_PDZ,ZMIN_CHI2,SECOND_PEAK=[],[],[],[]
zkeys=['Z_FINAL','Z_MED_PDZ','ZMIN_CHI2','SECOND_PEAK']
match={'Z_FINAL':[],'Z_MED_PDZ':[],'ZMIN_CHI2':[],'SECOND_PEAK':[]}

pdz_ids=pdz.data['ID']
cat_ids=cat['ID']

for id in cat_ids:
	id_array=pdz_ids==id
	for zkey in zkeys:
		match[zkey].append(pdz.data[zkey][id_array])

for k in cat.keys():
    if 'z' in k and 'qso' not in k and 'err' not in k and 'M' not in k:
        print k
        exec k+"=cat['"+k+"']"

# zchi zpdf zphot zphot2
cdfs={}
for row in pdz.data:
	cdfs[row[0]]=numpy.cumsum(row[10:])

fl=open('compare_matched_pdzs.pkl','wb')
for id in pdz_match2['ID']:
    for k in ['ra','dec']:
        try: 
		string='%s %s %s %.5f %s %.5f %s %.5f' % (id,k,'catold',catold[k][catold['id'].searchsorted(id)],'pdznew',pdz_match2[k.upper()][pdz_match2['ID'].searchsorted(id)],'pdz2015',pdz_match[k.upper()][pdz_match['ID2008'].searchsorted(id)])
        except:
		string='%s %s %s %.5f %s %.5f %s %s' % (id,k,'catold',catold[k][catold['id'].searchsorted(id)],'pdznew',pdz_match2[k.upper()][pdz_match2['ID'].searchsorted(id)],'pdz2015','NONE')
	fl.write(string+'\n')
fl.close()
