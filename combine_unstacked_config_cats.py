#!/usr/bin/env python
##########################
#Piece together catalogs from a single filter, but multiple configuration
##########################

import sys, pyfits, ldac, os, shutil, re


########################

def _transferOtherHDUs(catfile):

    hdulist = pyfits.open(catfile)
    otherhdus = []
    for hdu in hdulist:
        try:
            if hdu.header['EXTNAME'] != 'OBJECTS':
                otherhdus.append(hdu)
        except KeyError:
            pass

    return otherhdus

#########################

flux_search = re.compile('^FLUX_')
fluxerr_search = re.compile('^FLUXERR_')
mag_search = re.compile('^MAG_')
magerr_search = re.compile('^MAGERR_')
rejectKeys = "FLUX_RADIUS".split()
def _sortFluxKeys(keylist):

    fluxkeys = []
    fluxerrkeys = []
    magonlykeys = []
    otherkeys = []
    for key in keylist:
        if flux_search.match(key) and key not in rejectKeys:
            fluxkeys.append(key)
        elif fluxerr_search.match(key):
            fluxerrkeys.append(key)
        elif magerr_search.match(key):
            continue
        elif mag_search.match(key):
            magtype = _extractMagType(key)
            fluxkey = 'FLUX_%s' % magtype
            if fluxkey not in keylist:
                magonlykeys.append(key)
        else:
            otherkeys.append(key)

    return fluxkeys, fluxerrkeys, magonlykeys, otherkeys

#########################################

def _extractColumn(cat, key):

    for col in cat.hdu.columns.data:
        if col.name == key:
            return col

    return None

#########################################

_fluxsplit = re.compile('^FLUX_(.+)')

def _extractFluxType(fluxkey):

    match = _fluxsplit.match(fluxkey)
    if match is None:
        raise FluxKeyException('Cannot parse fluxkey: %s' % fluxkey)

    suffix = match.group(1)
    return suffix

######################################

_magsplit = re.compile('^MAG_(.+)')

def _extractMagType(magkey):

    match = _magsplit.match(magkey)
    if match is None:
        raise FluxKeyException('Cannot parse magkey: %s' % magkey)

    suffix = match.group(1)
    return suffix

#########################################


outfile = sys.argv[1]
instrument = sys.argv[2]
coaddcatfile = sys.argv[3]
inputcatfiles = sys.argv[4:]

coaddcat = ldac.openObjectFile(coaddcatfile)

fluxkeys, fluxerrkeys, magonlykeys, otherkeys = _sortFluxKeys(coaddcat.keys())

cols = [_extractColumn(coaddcat, key) for key in otherkeys]
cols = []

for key in otherkeys:
    
    format = filter(lambda x: x.name == key, coaddcat.hdu.columns)[0].format
    cols.append(pyfits.Column(name = '%s-%s' % (key, instrument), format = format, array = coaddcat[key]))


for flux_key in fluxkeys:
    
    fluxtype = _extractFluxType(flux_key)

    fluxerr_key = 'FLUXERR_%s' % fluxtype
    mag_key = 'MAG_%s' % fluxtype
    magerr_key = 'MAGERR_%s' % fluxtype

    format = filter(lambda x: x.name == flux_key, coaddcat.hdu.columns)[0].format

    cols.append(pyfits.Column(name = '%s-%s-COADD-1' % (flux_key, instrument), format = format, array = coaddcat[flux_key]))
    cols.append(pyfits.Column(name = '%s-%s-COADD-1' % (fluxerr_key, instrument), format = format, array = coaddcat[fluxerr_key]))
    cols.append(pyfits.Column(name = '%s-%s-COADD-1' % (mag_key, instrument), format = format, array = coaddcat[mag_key]))
    cols.append(pyfits.Column(name = '%s-%s-COADD-1' % (magerr_key, instrument), format = format, array = coaddcat[magerr_key]))

for mag_key in magonlykeys:



    magtype = _extractMagType(mag_key)

    magerr_key = 'MAGERR_%s' % magtype

    format = filter(lambda x: x.name == mag_key, coaddcat.hdu.columns)[0].format

    cols.append(pyfits.Column(name = '%s-%s-COADD-1' % (mag_key, instrument), format = format, array = coaddcat[mag_key]))
    cols.append(pyfits.Column(name = '%s-%s-COADD-1' % (magerr_key, instrument), format = format, array = coaddcat[magerr_key]))


cats = [ ldac.openObjectFile(catfile) for catfile in inputcatfiles ]    

for cat in cats:

    fluxkeys, fluxerrkeys, magonlykeys, otherkeys = _sortFluxKeys(cat.keys())

    for flux_key in fluxkeys:

        fluxtype = _extractFluxType(flux_key)
        
        fluxerr_key = 'FLUXERR_%s' % fluxtype
        mag_key = 'MAG_%s' % fluxtype
        magerr_key = 'MAGERR_%s' % fluxtype

        cols.append(_extractColumn(cat, flux_key))
        cols.append(_extractColumn(cat, fluxerr_key))
        cols.append(_extractColumn(cat, mag_key))
        cols.append(_extractColumn(cat, magerr_key))


objects = pyfits.new_table(pyfits.ColDefs(cols))
objects.header.update('EXTNAME', 'OBJECTS')

hdus = [pyfits.PrimaryHDU(), objects]
hdus.extend(_transferOtherHDUs(inputcatfiles[0]))

hdulist = pyfits.HDUList(hdus)
hdulist.writeto(outfile, clobber=True)


    
