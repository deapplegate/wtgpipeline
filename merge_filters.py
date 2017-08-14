#!/usr/bin/env python
#######################
# Combine catalogs from different filters into one
#######################

import sys, astropy, astropy.io.fits as pyfits, ldac

########################

__cvs_id__ = "$Id: merge_filters.py,v 1.6 2011/02/03 19:42:28 dapple Exp $"

########################

usage = "merge_filters.py outcat mastercat cat1 suffix1 cat2 suffix2 ..."

########################

def mergeFilters(mastercatfile, filters):
    #filters is a list of (cat, filter) names
    

    #have one set of variable names without suffix so ldac will understand

    print filters[0][0]

    mastercat_hdulist = pyfits.open(mastercatfile)
    mastercat = ldac.openObjectFile(mastercatfile)

    cols = [ col for col in mastercat.hdu.columns ]

    cats = []

    for file,suffix in filters:
                
        cat = ldac.openObjectFile(file) 
        cats.append(cat)
        for col in cat.hdu.columns:
            col.name = '%s-%s' % (col.name, suffix)
            cols.append(col)

    cols = pyfits.ColDefs(cols)
    
    header = mastercat.hdu.header

    objectsHDU = pyfits.BinTableHDU.from_columns(cols, header=header)
    objectsHDU.header.update('EXTNAME', 'OBJECTS')


    hdus = [pyfits.PrimaryHDU(), objectsHDU]
    for hdu in mastercat_hdulist:
        try:
            if hdu.header['EXTNAME'] != 'OBJECTS':
                hdus.append(hdu)
        except KeyError:
            pass

    hdulist = pyfits.HDUList(hdus)
    return hdulist


###############################


if __name__ == '__main__':

    if len(sys.argv) < 4:
        print usage
        sys.exit(1)

    outcat = sys.argv[1]

    mastercat = sys.argv[2]

    args = sys.argv[3:]
    filters = []
    for i in xrange(len(args)/2):
        filters.append((args[2*i],args[2*i+1]))

    if len(filters) < 1:
        print usage
        sys.exit(1)
    
    hdulist = mergeFilters(mastercat, filters)

    hdulist.writeto(outcat, clobber=True)
