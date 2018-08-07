#! /usr/bin/env python
import sys
import astropy.io.fits as pyfits
from glob import glob

fls=glob('/gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-*[A-Z+]/SCIENCE/SUPA0*.fits')
fls=fls[2068:]
for fl in fls:
    fo=pyfits.open(fl,mode='update')
    fo.verify('fix')
    print "fo[0].header['OBJECT']=", fo[0].header['OBJECT']," : fl=",fl
    fo[0].header['OBJECT']='Zw2089'
    fo[0].header['OBJNAME']='Zw2089'
    fo[0].header['MYOBJ']='Zw2089'
    if 'HIERARCH' in fo[0].header:
        ss=fo[0].header['HIERARCH']
        print 'ss=',ss
        if ss.startswith('ETSEEING'):
		fo[0].header.remove('HIERARCH',remove_all=True)
		value=float(ss.rsplit('= ')[-1])
		print 'value=',value
		fo[0].header['GETSEE']=value
    fo.verify('fix')
    try:
    	fo.close()
    except:
	print 'fo[0].header[BYTEORDR]=',fo[0].header['BYTEORDR']
	fo[0].header.remove('BYTEORDR',remove_all=True)
	fo.close()

fls=glob('/gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-*[A-Z+]/SCIENCE/SUPA0*.fits')
for fl in fls:
    fo=pyfits.open(fl,mode='update')
    fo.verify('fix')
    print "fo[0].header['OBJECT']=", fo[0].header['OBJECT']," : fl=",fl
    fo[0].header['MYOBJ']='MACS0429-02'
    if 'HIERARCH' in fo[0].header:
        ss=fo[0].header['HIERARCH']
        if ss.startswith('ETSEEING'):
		fo[0].header.remove('HIERARCH',remove_all=True)
		value=float(ss.rsplit('= ')[-1])
		fo[0].header['GETSEE']=value
    fo.verify('fix')
    try:
    	fo.close()
    except:
	print 'fo[0].header[BYTEORDR]=',fo[0].header['BYTEORDR']
	fo[0].header.remove('BYTEORDR',remove_all=True)
	fo.close()

sys.exit()

fls=glob('/gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-*[A-Z+]/SCIENCE/SUPA0*.fits')

for fl in fls:
    fo=pyfits.open(fl,mode='update')
    fo.verify('fix')
    print "fo[0].header['OBJECT']=", fo[0].header['OBJECT']," : fl=",fl
    fo[0].header['OBJECT']='RXJ2129'
    fo[0].header['OBJNAME']='RXJ2129'
    fo[0].header['MYOBJ']='RXJ2129'
    if 'HIERARCH' in fo[0].header:
        ss=fo[0].header['HIERARCH']
        if ss.startswith('ETSEEING'):
		fo[0].header.remove('HIERARCH')
		value=float(ss.rsplit('= ')[-1])
		fo[0].header['GETSEE']=value
    fo.verify('fix')
    try:
    	fo.close()
    except:
	print 'fo[0].header[BYTEORDR]=',fo[0].header['BYTEORDR']
	fo[0].header.remove('BYTEORDR',remove_all=True)
	fo.close()
