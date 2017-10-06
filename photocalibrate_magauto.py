#!/usr/bin/env python
##############################
# Apply a photometric calibration to a catalog
##############################

from __future__ import with_statement
import unittest, sys, re, os, optparse
import astropy.io.fits as pyfits, numpy, measure_unstacked_photometry
import ldac, utilities, photometry_db

photometry_db.initConnection()

##############################

__cvs_id__ = "$Id: photocalibrate_magauto.py,v 1.1 2009-08-28 23:43:51 dapple Exp $"

##############################
# USAGE
#############################

usage='photocalibrate_cat.py <-d> -i in.cat -c cluster -o out.cat'

##############################
# GLOBALS & DEFAULTS
##############################

__get_zeropoint_default__ = photometry_db.getZeropoint
__get_extinction_default__ = utilities.getExtinction
__get_dust_default__ = utilities.getDust

##############################
# EXCEPTIONS
##############################

class UnrecognizedFilterException(Exception): pass

##############################
# USER CALLABLE FUNCTIONS
##############################

def _isNotValidFilter(filter):
    if filter is None:
        return True
    try:
        utilities.parseFilter(filter)
        return False
    except utilities.UnrecognizedFilterException:
        return True

###

def photoCalibrateCat(cat, cluster, 
                      getZeropoint = __get_zeropoint_default__,
                      getExtinction = __get_extinction_default__,
                      getDust = __get_dust_default__):

    flux_keys, fluxerr_keys, other_keys = utilities.sortFluxKeys(cat.keys())

    filters = []
    cols = []
    for key in cat.keys():
        match = re.match('MAG_AUTO-(.+)', key)
        if match is not None:
            filters.append(match.group(1))            
        else:
            if not re.match('^MAGERR_AUTO', key):
                cols.append(cat.extractColumn(key))
            






    ebv = None
    if 'ebv' in cat:
        ebv = cat['ebv']
    elif getDust:
        ebv = getDust(cat['ALPHA_J2000'], cat['DELTA_J2000'])
        cols.append(pyfits.Column(name='ebv', format='E', array=ebv))

    for filter in filters:

        magerr_key = 'MAGERR_AUTO-%s' % filter

        obs_type = None
        for flux_key in flux_keys:
            match = re.match('FLUX_APER-(.+)-%s' % filter, flux_key)
            if match is not None:
                obs_type = match.group(1)
                break

        if obs_type is None:
            continue

        fitID = '%s-%s_A1' % (obs_type,filter)
        zp = getZeropoint(cluster, fitID)

        mag = cat['MAG_AUTO-%s' % filter] + zp

        magerr = cat['MAGERR_AUTO-%s' % filter] + zp

        if ebv is not None:
            extinction = getExtinction('%s-%s' % (obs_type,filter))

            dustCorrection = -extinction*ebv

            mag = mag + dustCorrection
            magerr = magerr + dustCorrection


        cols.append(pyfits.Column(name = 'MAG_AUTO-%s' % filter,
                                  format = 'E',
                                  array = mag))
        cols.append(pyfits.Column(name = magerr_key,
                                  format = 'E',
                                  array = magerr))

    calibratedCat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols)))

    if cat.hdu.header.has_key('EXTNAME'):
        calibratedCat.hdu.header['EXTNAME']= cat.hdu.header['EXTNAME']

    return calibratedCat
        
        

##############################
# MAIN
##############################


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


def main(argv = sys.argv):

    parser = optparse.OptionParser(usage = usage)

    parser.add_option('-i', '--in',
                      help='Input catalog name',
                      dest='incatfile')
    parser.add_option('-c', '--cluster',
                      help='Name of cluster',
                      dest='cluster')
    parser.add_option('-o', '--out',
                      help='name of output catalog',
                      dest='outcatfile')
    parser.add_option('-d', '--nodust',
                      help='Turn off dust correction',
                      dest='doDust',
                      action='store_false',
                      default=True)
    

    options, args = parser.parse_args(argv)

    if options.incatfile is None:
        parser.error('Input catalog required!')
    
    if options.cluster is None:
        parser.error('Cluster Name is required!')

    if options.outcatfile is None:
        parser.error('Output catalog is required!')

    if len(args) != 1:
        parser.error('One catalog needed!')

    cat = ldac.openObjectFile(options.incatfile)

    if options.doDust:
        calibratedCat = photoCalibrateCat(cat, options.cluster)
    else:
        calibratedCat = photoCalibrateCat(cat, options.cluster, getDust = None)

    hdus = [pyfits.PrimaryHDU(), calibratedCat.hdu]
    hdus.extend(_transferOtherHDUs(options.incatfile))
    hdulist = pyfits.HDUList(hdus)
    hdulist.writeto(options.outcatfile, overwrite=True)


    



##############################
# COMMANDLINE EXECUTABLE
##############################

if __name__ == '__main__':
    
    main()
