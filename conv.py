import astropy.io.fits as pyfits, os

filters = []
vals = []
for filter in ['SUBARU-10_2-1-W-S-I+','SUBARU-10_2-1-W-J-B','SUBARU-10_2-1-W-S-Z+','SUBARU-10_2-1-W-S-G+','SUBARU-10_2-1-W-S-R+','SUBARU-10_2-1-W-J-V']:
	filters.append(filter)	
	vals.append(0)


cols = []
cols.append(pyfits.Column(name='filter', format='60A',array=filters))
cols.append(pyfits.Column(name='zeropoints', format='E',array=vals))


tab = pyfits.open('/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_APER/COSMOS_PHOTOZ.stars.calibrated.cat')
hdu_mags = tab['OBJECTS']

hduFILTERS = pyfits.BinTableHDU.from_columns(cols) 

hdu = pyfits.PrimaryHDU()
hdulist = pyfits.HDUList([hdu,hdu_mags,hduFILTERS])
hdulist[1].header['EXTNAME']='OBJECTS'
hdulist[2].header['EXTNAME']='ZPS'
print file

outfile = '/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_APER/COSMOS_PHOTOZ.stars.test.cat'
os.system('rm ' + outfile)
import re
hdulist.writeto(outfile)
print outfile , '$#######$'
#print 'done'
