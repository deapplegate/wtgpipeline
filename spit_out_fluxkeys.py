#!/usr/bin/env python

import sys
import photocalibrate_cat as pcc, ldac
import convert_aper, utilities


catfile = sys.argv[1]


cat = ldac.openObjectFile(catfile)

cat = convert_aper.convertAperColumns(cat)

flux_keys, fluxerr_keys, magonlykeys, other_keys = utilities.sortFluxKeys(cat.keys())

for fluxkey in flux_keys:

    filter = pcc.extractFilter(fluxkey)
        
    if pcc._is2Darray(cat[fluxkey]) or pcc._isNotValidFilter(filter):
        continue

    print fluxkey


for magkey in magonlykeys:

    magtype = pcc.extractMagType(magkey)
    filter = pcc.extractMagFilter(magkey)

    if pcc._isNotValidFilter(filter):
        continue
    
    print magkey
        
