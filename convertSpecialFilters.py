#!/usr/bin/env python
##############
# Rename appropriate columns for special filter catalogs in the unstacked process
###############

import pyfits, ldac, sys, utilities

###############

__cvs_id__ = "$Id: convertSpecialFilters.py,v 1.2 2009-08-10 23:42:40 dapple Exp $"

###############

catfile = sys.argv[1]
outcat = sys.argv[2]



cat = ldac.openObjectFile(catfile)

fluxkeys, fluxerrkeys, otherkeys = utilities.sortFluxKeys(cat.keys())

cols = [cat.extractColumn(key) for key in otherkeys]


for fluxkey in fluxkeys:

    fluxtype = utilities.extractFluxType(fluxkey)

    fluxerr_key = 'FLUXERR_%s' % (fluxtype)
    mag_key = 'MAG_%s' % (fluxtype)
    magerr_key = 'MAGERR_%s' % (fluxtype)

    id ='SPECIAL-0-1'

    if len(cat[fluxkey].shape) == 1:
        cols.append(pyfits.Column(name='%s-%s' % (fluxkey, id), 
                                  format='E', 
                                  array=cat[fluxkey]))
        cols.append(pyfits.Column(name='%s-%s' % (fluxerr_key, id),
                                  format='E', 
                                  array=cat[fluxerr_key]))
        cols.append(pyfits.Column(name='%s-%s' % (mag_key, id), 
                                  format='E', 
                                  array=cat[mag_key]))
        cols.append(pyfits.Column(name='%s-%s' % (magerr_key, id),
                                  format='E', 
                                  array=cat[magerr_key]))

    else:
        nelements = cat[fluxkey].shape[1]
        cols.append(pyfits.Column(name='%s-%s' % (fluxkey, id), 
                                  format='%dE' % nelements, 
                                  array=cat[fluxkey]))
        cols.append(pyfits.Column(name='%s-%s' % (fluxerr_key, id), 
                                  format='%dE' % nelements, 
                                  array=cat[fluxerr_key]))
        cols.append(pyfits.Column(name='%s-%s' % (mag_key, id), 
                                  format='%dE' % nelements, 
                                  array=cat[mag_key]))
        cols.append(pyfits.Column(name='%s-%s' % (magerr_key, id), 
                                  format='%dE' % nelements, 
                                  array=cat[magerr_key]))

objects =     ldac.LDACCat(pyfits.new_table(pyfits.ColDefs(cols), 
                                            header=cat.hdu.header))
objects.hdu.header.update('EXTNAME', 'OBJECTS')


hdus = [pyfits.PrimaryHDU(), objects.hdu]

hdulist = pyfits.open(catfile)
otherhdus = []
for hdu in hdulist:
    try:
        if hdu.header['EXTNAME'] != 'OBJECTS':
            otherhdus.append(hdu)
    except KeyError:
        pass

hdus.extend(otherhdus)

hdulist = pyfits.HDUList(hdus)


hdulist.writeto(outcat, clobber=True)


    

            
