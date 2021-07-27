#! /usr/bin/env python
import sys,os
sys.path.append('/u/ki/awright/InstallingSoftware/pythons/')
from adam_quicktools_ArgCleaner import ArgCleaner
args=ArgCleaner(sys.argv)
print "args=", args

#/u/ki/awright/data/eyes/coadds-pretty_for_10_3_cr.2/
import pickle
fl=open('/u/ki/awright/thiswork/eyes/Prettys_info.2.1.pkl','rb')
Pinfo=pickle.load(fl) #CRbads[filter][CRnum]['CCDnum','weight_file','file','dark_file','CRtag'] only 'file' and 'CRtag' are useful here
fl.close()

import astropy.io.fits as pyfits

from adam_quicktools_header_key_add import add_key_val
CRfl='/u/ki/awright/thiswork/eyes/CRbads_info.2.1.pkl'
CRfo=open(CRfl)
CRinfo=pickle.load(CRfo)
CRfo.close()

for k in CRinfo.keys():
    CRfl=CRinfo[k]['dark_file']
    CRtime=pyfits.open(CRfl)[0].header['EXPTIME']
    infls=glob('/nfs/slac/kipac/fs1/u/awright/eyes/eye-10_3_cr.2.1/W-C-RC/both/edge_out/inputs/eye_CRnum%s_Pnum*.fits' % (k,))
    print k, len(infls)

    for fl in infls:
        add_key_val(fl,['EXPTIME'],[CRtime])
