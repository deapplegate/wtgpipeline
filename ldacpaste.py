#!/usr/bin/env python
#######################

# Imitate the LDACPASTE program, but hopefully be less of a pain about the FIELDS table

########################

import ldac, astropy, astropy.io.fits as pyfits, sys

########################

outcat = sys.argv[1]

inputcats = sys.argv[2:]


finalcat = ldac.openObjectFile(inputcats[0])

for catfile in inputcats[2:]:

    cat = ldac.openObjectFile(catfile)

    finalcat = finalcat.append(cat)


hdulist = pyfits.open(inputcats[0])

newhdulist = [pyfits.PrimaryHDU(), finalcat.hdu]

for table in hdulist:
    
    if 'EXTNAME' in table.header and table.header['EXTNAME'] != 'OBJECTS' and table.header['EXTNAME'] != 'FIELDS':

        newhdulist.append(table)

    elif 'EXTNAME' in table.header and table.header['EXTNAME'] == 'FIELDS':


        fields = ldac.LDACCat(table)

        fields['OBJECT_COUNT'][:] = len(finalcat)

        newhdulist.append(fields.hdu)

newhdulist = pyfits.HDUList(newhdulist)

newhdulist.writeto(outcat, overwrite=True)


    
