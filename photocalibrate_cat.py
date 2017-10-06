#!/usr/bin/env python
##############################
# Apply a photometric calibration to a catalog
##############################

from __future__ import with_statement
import unittest, sys, re, os, optparse, copy, math
import astropy.io.fits as pyfits, numpy, measure_unstacked_photometry
import ldac, utilities, photometry_db, convert_aper


##############################

__cvs_id__ = "$Id: photocalibrate_cat.py,v 1.28 2010-11-12 20:33:56 dapple Exp $"

##############################
# USAGE
#############################

usage='photocalibrate_cat.py <-d> -i in.cat -c cluster -o out.cat '

##############################
# GLOBALS & DEFAULTS
##############################


##################################################
### Photometry Global Database
##################################################

class Phot_db(object):
    '''Provide lazy, proxy access to the photometry database of choice'''
    def __init__(self, db, *args, **keywords):
        self.db = db
        self.instance = None
        self.args = args
        self.keywords = keywords
    def __getattr__(self, name):
        if self.instance is None:
            self.instance = self.db(*self.args, **self.keywords)

        return getattr(self.instance, name)

__default_photometry_db__ = Phot_db(photometry_db.Photometry_db)


##################################################


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

def _is2Darray(array):
    return len(array.shape) > 1

def _getSourceExtractorZP(cat):

    return ldac.openObjectFile(cat.sourcefile, 'FIELDS')['SEXMGZPT'][0]

###

def photoCalibrateCat(cat, cluster, type='standard',  specification = {},
                      getExtinction = __get_extinction_default__,
                      getDust = __get_dust_default__,
                      photometry_db = __default_photometry_db__):

    flux_keys, fluxerr_keys, magonlykeys, other_keys = utilities.sortFluxKeys(cat.keys())

    cols = []
    for key in other_keys:
        if not (re.match('^MAG_', key) or re.match('^MAGERR_', key)):
            cols.append(cat.extractColumn(key))

    ebv = None
    if 'ebv' in cat:
        ebv = cat['ebv']
    else:
        if getDust:
            ebv = getDust(cat['ALPHA_J2000'], cat['DELTA_J2000'])
            cols.append(pyfits.Column(name='ebv', format='E', array=ebv))

    zp_list = []
    zperr_list = []
    filters = []
    for fluxkey in flux_keys:

        filter = extractFilter(fluxkey)

        if _is2Darray(cat[fluxkey]) or _isNotValidFilter(filter):
            continue

        print 'Processing %s' % fluxkey
        
        fluxtype = extractFluxType(fluxkey)
        fluxerr_key = 'FLUXERR_%s-%s' % (fluxtype, filter)
        mag_key = 'MAG_%s-%s' % (fluxtype, filter)
        magerr_key = 'MAGERR_%s-%s' % (fluxtype, filter)


        flux = cat[fluxkey]
        err = cat[fluxerr_key]

        flux, err, zp, zperr = applyZeropoint(cluster, filter, flux, 
                                              fluxtype, err, type, 
                                              cat, photometry_db = photometry_db, 
                                              specification = specification)

        print 'Found zp = %3.2f +/- %1.4f' % (zp, zperr)

        filters.append(mag_key)

        zp_list.append(zp)
        zperr_list.append(zperr)

        if ebv is not None and getDust is not None:
            flux, err = applyDust(filter, flux, err, ebv, getExtinction)

        mag, magerr = measure_unstacked_photometry.calcMags(flux, err)

        cols.append(pyfits.Column(name = fluxkey,
                                  format = 'E',
                                  array = flux))
        cols.append(pyfits.Column(name = fluxerr_key,
                                  format = 'E',
                                  array = err))
        cols.append(pyfits.Column(name = mag_key,
                                  format = 'E',
                                  array = mag))
        cols.append(pyfits.Column(name = magerr_key,
                                  format = 'E',
                                  array = magerr))


    for magkey in magonlykeys:



        magtype = extractMagType(magkey)
        filter = extractMagFilter(magkey)

        if _isNotValidFilter(filter):
            continue

        print 'Processing %s' % magkey

        magerr_key = 'MAGERR_%s-%s' % (magtype, filter)
        
        calibration = photometry_db.getZeropoint(cluster, filter = filter, **specification)
        
        if calibration is None:
            zp = 0
            zperr = 0
        else:
            zp = calibration.zp - _getSourceExtractorZP(cat)
            try:
                zperr = calibration.zperr
            except AttributeError:
                zperr = 0.

        print 'Found zp = %3.2f +/- %1.4f' % (zp, zperr)
            
        dustCorrection = 0.
        if getExtinction:
            extinction = getExtinction(filter)

            dustCorrection = -extinction*ebv


        newmag = cat[magkey] + zp + dustCorrection


        cols.append(pyfits.Column(name = magkey, format = 'E', array = newmag))





    calibratedCat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols)))

 
    if cat.hdu.header.has_key('EXTNAME'):
        calibratedCat.hdu.header['EXTNAME']= cat.hdu.header['EXTNAME']

    ''' now make table with zeropoints used to calibrate catalog '''
    zp_cols = [pyfits.Column(name = 'filter',
                             format= '60A',
                             array=filters),
               pyfits.Column(name = 'zeropoints',
                             format= 'E',
                             array=numpy.array(zp_list)),
               pyfits.Column(name = 'errors',
                             format = 'E',
                             array = numpy.array(zperr_list))]
   

    zpCat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(zp_cols)))
    zpCat.hdu.header['EXTNAME']= 'ZPS'


    return calibratedCat, zpCat


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

    ###
    
    def parse_spec(option, opt, value, parser):

        key, val = value.split('=')
        
        if not hasattr(parser.values, 'specification'):
            setattr(parser.values, 'specification', {})
            
        parser.values.specification[key] = val

       
    ###


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
    parser.add_option('-t', '--type',
                      help='Type of zeropoint -- standard, slr, lephare',
                      dest='type',
                      default='standard')
    parser.add_option('--spec', dest='specification',
                      action='callback',
                      type= 'string', 
                      help='key=val set determines the uniqueness of this calibration',
                      default = {},
                      callback = parse_spec)


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
    converted = convert_aper.convertAperColumns(cat)

    
    if options.doDust:                                                                 
        calibratedCat, zpCat = photoCalibrateCat(converted, options.cluster, options.type, specification = options.specification)
    else:
        calibratedCat, zpCat = photoCalibrateCat(converted, options.cluster, options.type, getDust = None, specification = options.specification)

    hdus = [pyfits.PrimaryHDU(), calibratedCat.hdu, zpCat.hdu]
    hdus.extend(_transferOtherHDUs(options.incatfile))
    hdulist = pyfits.HDUList(hdus)
    hdulist.writeto(options.outcatfile, overwrite=True)


    

##############################
# UTILITY FUNCTIONS
##############################

def applyZeropoint(cluster, filter, flux, fluxtype, err, type='standard', cat=None, 
                   photometry_db = photometry_db, specification = {}):

                   

    if photometry_db is None:
        return flux, err, 0, 0


    calibration = photometry_db.getZeropoint(cluster, filter = filter, **specification)

    if calibration is None:
        zp = 0

    else:
        zp = calibration.zp

    
    if hasattr(calibration, 'zperr'):
        zperr = calibration.zperr
    else:
        zperr = 0.



    if type == 'slr' and hasattr(calibration, 'fitFilter'):

        referenceFlux = cat['FLUX_%s-%s' % (fluxtype, calibration.fitFilter)]
        referenceErr = cat['FLUXERR_%s-%s' % (fluxtype, calibration.fitFilter)]


        snratio = flux / err
        reference_snratio = referenceFlux/ referenceErr

        bad_flux_cut = numpy.logical_and(flux != measure_unstacked_photometry.__bad_flux__,
                                         referenceFlux != measure_unstacked_photometry.__bad_flux__)

        zero_flux_cut = numpy.logical_and(flux != 0, referenceFlux != 0)

        snratio_cut = numpy.logical_and(numpy.logical_and(numpy.isfinite(snratio), snratio > 5),
                                        numpy.logical_and(numpy.isfinite(reference_snratio), reference_snratio > 5))



        mask = numpy.logical_and(numpy.logical_and(bad_flux_cut,
                                                   zero_flux_cut),
                                 snratio_cut)

        mag_ref = -2.5*numpy.log10(referenceFlux)
        mag = -2.5*numpy.log10(flux)
        difference = mag_ref - mag

        difference = difference[mask]

        relativeZP = numpy.median(difference)

        zp = zp + relativeZP   #make the magnitudes the same



    calibratedflux, calibratederr = applyOffset(flux, err, zp)
    
    calibratedflux[flux == measure_unstacked_photometry.__bad_flux__] = measure_unstacked_photometry.__bad_flux__
    calibratederr[flux == measure_unstacked_photometry.__bad_flux__] = measure_unstacked_photometry.__bad_flux__


    return calibratedflux, calibratederr, zp, zperr



#####################

def applyDust(filter, flux, fluxerr, ebv, getExtinction = __get_extinction_default__):

    if getExtinction is None:
        return flux, fluxerr

    extinction = getExtinction(filter)

    dustCorrection = -extinction*ebv

    corrflux, corrfluxerr = applyOffset(flux, fluxerr, dustCorrection)
    
    corrflux[flux == measure_unstacked_photometry.__bad_flux__] = measure_unstacked_photometry.__bad_flux__
    corrfluxerr[flux == measure_unstacked_photometry.__bad_flux__] = measure_unstacked_photometry.__bad_flux__

    return corrflux, corrfluxerr
    

#####################

filter_pattern = re.compile('^FLUX_(\w+)-(.+)')
def extractFilter(fluxkey):

    match = filter_pattern.match(fluxkey)
    if match is None:
        return None
    return match.group(2)

###

magfilter_pattern = re.compile('^MAG_(\w+)-(.+)')
def extractMagFilter(magkey):
    

    match = magfilter_pattern.match(magkey)

    if match is None:
        return None
    return match.group(2)

####

def extractFluxType(fluxkey):

    match = filter_pattern.match(fluxkey)
    if match is None:
        return None
    return match.group(1)

####

def extractMagType(magkey):

    match = magfilter_pattern.match(magkey)
    if match is None:
        return None
    return match.group(1)


###################

def applyOffset(flux, fluxerr, offset):


    fluxscale = 10**(-.4*offset)

    reffluxscale = fluxscale
    
    return reffluxscale * flux, reffluxscale * fluxerr

######################






    

##############################
# TESTING
##############################

class fakeCalibration(object):
    def __init__(self, zp):
        self.zp = zp

class fakeCalDB(object):
    def __init__(self, getzp):
        self.getzp = getzp
    def getZeropoint(self, *args, **kw):
        return self.getzp(*args, **kw)

class TestComponents(unittest.TestCase):

    def testExtractFilter(self):

        realFilter = 'SUBARU-10_2-1-W-S-Z+'
        filter = extractFilter('FLUX_ISO-%s' % realFilter)
        self.assertEqual(filter, realFilter)

        filter = extractFilter('FLUX_APER1-%s' % realFilter)
        self.assertEqual(filter, realFilter)

    #############################

    def testApplyOffset(self):

        flux = numpy.ones(30000)
        fluxerr = numpy.ones(30000)
        zeropoints = 27
        
        scaledFluxs = applyOffset(flux, fluxerr, zeropoints)

        mags = -2.5*numpy.log10(scaledFluxs)
        
        errmags = -2.5*numpy.log10(scaledFluxs)
        
        self.assertTrue( (mags == 27).all() )
        self.assertTrue( (errmags == 27).all() )

    #############################

#    def testApplyOffset_per_aper(self):
#
#        fluxs = numpy.ones(30)
#        errs = numpy.ones(30)
#        offsets = -2.5*numpy.log10(numpy.arange(1,6))
#
#        scaledFluxs, scaledErrs = applyOffset(fluxs, errs, offsets)
#
#        expected = numpy.ones((30,5)) * numpy.arange(1,6)
#
#        self.assertTrue( (numpy.abs(scaledFluxs - expected) < 1e-8).all() )
#        self.assertTrue( (numpy.abs(scaledErrs - expected) < 1e-8).all() )
#
    ##############################

    def testApplyOffset_per_obj(self):

        fluxs = numpy.ones(30)
        errs = numpy.ones(30)
        offsets = -2.5*numpy.log10(numpy.arange(1,31))
        refOffsets = numpy.arange(1,31)

        scaledFluxs, scaledErrs = applyOffset(fluxs, errs, offsets)

        self.assertTrue( (numpy.abs(scaledFluxs - refOffsets) < 1e-8).all())
        self.assertTrue( (numpy.abs(scaledErrs - refOffsets) < 1e-8).all())

    ##############################

    def testApplyZeropoints(self):

        #########

        def getZP(cluster, filter, **spec):
            return fakeCalibration(2.)

        ########

        flux = numpy.ones(30)
        err = numpy.ones(30)

        expected = 10**(-.4*2)

        calcflux, calcerr, zp, zperr = applyZeropoint('fake', 'fake', flux, 'APER0', 
                                         err, photometry_db=fakeCalDB(getZP))


        self.assertTrue( (calcflux == expected).all())
        self.assertTrue( (calcerr == expected).all())
        self.assertEqual(zp, 2)
        self.assertEqual(zperr, 0)

    ##########################

    def testApplyZeropoints_nocalib(self):

        def getZP(cluster, filter, **spec):
            return None

        flux = numpy.ones(30)
        err = numpy.ones(30)

        zp_flux, zp_fluxerr, zp, zperr = applyZeropoint('fake', 'fake', flux, 'APER0',
                                             err, photometry_db=fakeCalDB(getZP))

        self.assertTrue( (zp_flux == flux).all() )
        self.assertTrue( (zp_fluxerr == err).all() )
        self.assertEquals(zp, 0)
        self.assertEquals(zperr, 0)

    ##########################

    def testApplyZeropoints_preserveflag(self):

        ########

        def getZP(cluster, filter, **spec):
            return fakeCalibration(2.)

        ########

        flux = numpy.ones(30)
        flux[20:] = measure_unstacked_photometry.__bad_flux__

        err = numpy.ones(30)
        err[20:] = measure_unstacked_photometry.__bad_flux__


        calcflux, calcerr, zp, zperr = applyZeropoint('fake', 'fake', flux, 'APER0', 
                                         err, photometry_db=fakeCalDB(getZP))

        self.assertTrue( (calcflux[20:30] == measure_unstacked_photometry.__bad_flux__).all())
        self.assertTrue( (calcerr[20:30] == measure_unstacked_photometry.__bad_flux__).all())

    
    #############################


####
#def applyZeropoint(cluster, filter, flux, fluxtype, err, type='standard', cat=None, 
#                   photometry_db = photometry_db, specification = {}):
###

    def testApplyZeropoints_testSLR(self):

        objectMag = 24.2

        target_zp1 = 27.4
        target_zp2 = 27.9
        target_zperr = 0.1


        flux1 = 10**(-0.4*(objectMag - target_zp1))*numpy.ones(10)
        flux2 = 10**(-0.4*(objectMag - target_zp2))*numpy.ones(10)

        cols = [pyfits.Column(name = 'FLUX_APER-filter1', format = 'E', array = flux1),
                pyfits.Column(name = 'FLUXERR_APER-filter1', format = 'E', array = 0.001*flux1),
                pyfits.Column(name = 'FLUX_APER-filter2', format = 'E', array = flux2),
                pyfits.Column(name = 'FLUXERR_APER-filter2', format = 'E', array = 0.001*flux2)]
        cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols)))

        ##########

        class fakeSLR(object):
            def __init__(self, zp, zperr, fitFilter):
                self.zp = zp
                self.fitFilter = fitFilter
                self.zperr = zperr
                
        def getZP(cluster, filter, **spec):
            return fakeSLR(target_zp2, target_zperr, 'filter2')

        ##########

        corFlux, corErr, zp, zperr = applyZeropoint('testcluster', 'filter1', flux1, 'APER', 0.001*flux1,
                                             type='slr', cat = cat, photometry_db = fakeCalDB(getZP))

        
        self.assertTrue(numpy.abs(zp - target_zp1) < 1e-3, 'Expected: %3.2f Found: %3.2f' % (target_zp1, zp))

        corMag = -2.5*numpy.log10(corFlux)

        self.assertTrue((numpy.abs(corMag - objectMag) < 1e-3).all(), 'Expected: %3.2f Found: %3.2f' % (objectMag, corMag[0]))

        self.assertTrue((numpy.abs(target_zperr - zperr) < 1e-5))

    #######################


    def testSkipApplyZeropoints(self):

        flux = numpy.ones(30)
        err = numpy.ones(30)

        calcflux, calcerr, zp, zperr = applyZeropoint('fake', 'fake', flux, 'APER0',
                                         err, photometry_db = None)

        self.assertTrue( (calcflux == flux).all())
        self.assertTrue( (calcerr == err).all())

    ##########################

    def testUseSpecifications(self):

        class FakeDB(object):
            def __init__(self):
                self.calls = []
            def getZeropoint(self, cluster, **kw):
                self.calls.append((cluster, kw))
                return None

        #########

        db = FakeDB()
        applyZeropoint(cluster ='testcluster', filter = 'SUBARU-10_2-1-W-J-V', flux = numpy.ones(100), 
                       fluxtype = 'APER', err = 0.1*numpy.ones(100), photometry_db = db, specification = {'myspec' : 'custom',
                                                                                                         'fluxtype' : 'iso'})

        self.assertEquals(len(db.calls), 1)
        cluster, kw = db.calls[0]
        
        self.assertEquals(cluster, 'testcluster')
        self.assertEquals(kw['filter'], 'SUBARU-10_2-1-W-J-V')
        self.assertEquals(kw['fluxtype'], 'iso')
        self.assertEquals(kw['myspec'], 'custom')

            

    ##########################

    def testApplyDust(self):

        ebv = numpy.ones(30)
        ebv[:15] = -3
        ebv[15:] = 3
        

        flux = numpy.ones(30)
        err = numpy.ones(30)

        #####

        def extinction(filter):
            return .2

        ####
        
        dust_flux, dust_err = applyDust('fake', flux, err, 
                                        ebv, getExtinction = extinction)

        expected = 10**(.4*.2*ebv)
        refExpected = expected
            
        self.assertTrue( (numpy.abs(dust_flux - refExpected) < 1e-8).all())
        self.assertTrue( (numpy.abs(dust_err - refExpected) < 1e-8).all())

    #########################

    def testApplyDust_propflag(self):

        
        ebv = numpy.ones(30)
        ebv[:15] = -3
        ebv[15:] = 3
        

        flux = numpy.ones(30)
        flux[20:30] = measure_unstacked_photometry.__bad_flux__
        
        fluxerr = numpy.ones(30)
        fluxerr[20:30] = measure_unstacked_photometry.__bad_flux__

        #####

        def extinction(filter):
            return .2

        ####
        
        dust_flux, dust_err = applyDust('fake', flux, fluxerr, 
                                        ebv, getExtinction = extinction)

        self.assertTrue((dust_flux[20:30] == measure_unstacked_photometry.__bad_flux__).all())
        self.assertTrue((dust_err[20:30] == measure_unstacked_photometry.__bad_flux__).all())
    #########################

    def testSkipApplyDust(self):

        flux, err = applyDust('fake', numpy.ones(30), 
                         numpy.ones(30), 
                         numpy.ones(30), 
                         getExtinction = None)

        self.assertTrue( (flux == 1).all() )
        self.assertTrue( (err == 1).all() )

    ##########################


        

        

        
        

        
        

##############################


class TestPhotoCalibrateCatalog(unittest.TestCase):

    def setUp(self):
        self.nObjs = 200
        self.filters = ['MEGAPRIME-0-1-%s' % f for f in 'u g r i z'.split()]
        cols = []
        cols.append(pyfits.Column(name='ALPHA_J2000',
                                  format='D',
                                  array=numpy.random.standard_normal(self.nObjs)))
        cols.append(pyfits.Column(name='DELTA_J2000',
                                  format='D',
                                  array=numpy.random.standard_normal(self.nObjs)))
        cols.append(pyfits.Column(name='FLUX_RADIUS',
                                  format='E',
                                  array=numpy.random.uniform(0,10,self.nObjs)))
        for filter in self.filters:
            cols.append(pyfits.Column(name='FLUX_ISO-%s' % filter,
                                      format='E',
                                      array=numpy.ones(self.nObjs)))
            cols.append(pyfits.Column(name='FLUXERR_ISO-%s' % filter,
                                      format='E',
                                      array=numpy.ones(self.nObjs)))
            cols.append(pyfits.Column(name='FLUX_APER0-%s' % filter,
                                      format='E',
                                      array=numpy.ones(self.nObjs)))
            cols.append(pyfits.Column(name='FLUXERR_APER0-%s' % filter,
                                      format='E',
                                      array=numpy.ones(self.nObjs)))


        self.goodkeys = [col.name for col in cols]

        cols.append(pyfits.Column(name='FLUX_APER-SUBARU-10_1-1',
                                  format='E',
                                  array=numpy.random.uniform(0,500,self.nObjs)))
        cols.append(pyfits.Column(name='FLUXERR_APER-SUBARU-10_1-1',
                                  format='E',
                                  array=numpy.random.uniform(0,500,self.nObjs)))
        cols.append(pyfits.Column(name='FLUX_APER1-SUBARU-10_1-1-W-J-V',
                                  format='5E',
                                  array=numpy.ones((self.nObjs, 5))))
        cols.append(pyfits.Column(name='FLUXERR_APER1-SUBARU-10_1-1-W-J-V',
                                  format='5E',
                                  array=numpy.ones((self.nObjs,5))))
        cols.append(pyfits.Column(name='FLUX_ISO-SUBARU-10_1-1-W-J-V',
                                  format='E',
                                  array=numpy.ones(self.nObjs)))
        cols.append(pyfits.Column(name='FLUXERR_ISO-SUBARU-10_1-1-W-J-V',
                                  format='E',
                                  array=numpy.ones(self.nObjs)))


        self.cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols)))
        self.cluster = 'fake_cluster'
        self.zps = {}
        self.extinction = {}
        self.targetFlux = 10
        ext = 1
        for filter in self.filters:
            self.extinction[filter] = ext
            ext += 1
            self.zps[filter] = -2.5*numpy.log10(self.targetFlux)

    ######################

            
    def testReturnsCat(self):

        def getZP(cluster, filter, **spec):
            return fakeCalibration(0.)


        cat, zps = photoCalibrateCat(self.cat, cluster=self.cluster, type='standard', getDust = None, photometry_db = fakeCalDB(getZP))

        self.assertTrue(isinstance(cat, ldac.LDACCat))
        for key in self.goodkeys:
            self.assertTrue( key in cat, key )


    ########################

    def testOptionalExtName(self):

        def getZP(cluster, filter, **spec):
            return fakeCalibration(0.)

        self.cat.hdu.header['EXTNAME']= 'PSSC_fakery'

        cat, zps = photoCalibrateCat(self.cat, cluster=self.cluster, type='standard', getDust = None, photometry_db = fakeCalDB(getZP))

        self.assertEqual(cat.hdu.header['EXTNAME'], self.cat.hdu.header['EXTNAME'])        

    #########################

    def testApplyCalibration(self):

        ########

        def getZP(cluster, filter, **spec):
            if not filter in self.zps:
                return None
            return fakeCalibration(self.zps[filter])


        ########


        cat, zps = photoCalibrateCat(self.cat, 
                                cluster=self.cluster, 
                                type='standard',
                                photometry_db = fakeCalDB(getZP),
                                getDust = None)


        expected = numpy.column_stack(self.targetFlux*numpy.ones(self.nObjs))

        for filter in self.filters:
            self.assertTrue( (numpy.abs(cat['FLUX_ISO-%s' % filter] - expected) < 1e-8).all())
            self.assertTrue( (numpy.abs(cat['FLUX_APER0-%s' % filter] - expected) < 1e-8).all())

    ###########################

    def testDustCorrect(self):

        ###

        def extinction(filter):
            if not filter in self.extinction:
                return 0
            return self.extinction[filter]

        ####

        def dust(alpha, delta):

            return .4*numpy.ones_like(alpha)

        ####
        
        cat, zps = photoCalibrateCat(self.cat,
                                cluster = self.cluster,
                                type='standard',
                                photometry_db = None,
                                getExtinction = extinction,
                                getDust = dust)


        self.assertTrue('ebv' in cat)

        for filter in self.filters:
            expected = 10**(.4*self.extinction[filter]*.4) * numpy.ones(self.nObjs)
            self.assertTrue( (numpy.abs(cat['FLUX_ISO-%s' % filter] - expected) < 1e-5).all())

    ##############################

    def testNoDoubleDust(self):

        cols = []
        cols.append(pyfits.Column(name='ALPHA_J2000',
                                  format='D',
                                  array=numpy.random.standard_normal(self.nObjs)))
        cols.append(pyfits.Column(name='DELTA_J2000',
                                  format='D',
                                  array=numpy.random.standard_normal(self.nObjs)))
        cols.append(pyfits.Column(name='FLUX_RADIUS',
                                  format='E',
                                  array=numpy.random.uniform(0,10,self.nObjs)))
        for filter in self.filters:
            cols.append(pyfits.Column(name='FLUX_ISO-%s' % filter,
                                      format='E',
                                      array=numpy.ones(self.nObjs)))
            cols.append(pyfits.Column(name='FLUXERR_ISO-%s' % filter,
                                      format='E',
                                      array=numpy.ones(self.nObjs)))

        self.goodkeys = [col.name for col in cols]

        cols.append(pyfits.Column(name='FLUX_APER-SUBARU-10_1-1',
                                  format='E',
                                  array=numpy.random.uniform(0,500,self.nObjs)))
        cols.append(pyfits.Column(name='FLUXERR_APER-SUBARU-10_1-1',
                                  format='E',
                                  array=numpy.random.uniform(0,500,self.nObjs)))
        cols.append(pyfits.Column(name='FLUX_ISO-SUBARU-10_1-1-W-J-V',
                                  format='E',
                                  array=numpy.ones(self.nObjs)))
        cols.append(pyfits.Column(name='FLUXERR_ISO-SUBARU-10_1-1-W-J-V',
                                  format='E',
                                  array=numpy.ones(self.nObjs)))
        cols.append(pyfits.Column(name='ebv',
                                  format='E',
                                  array=numpy.ones(self.nObjs)))

        cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols)))

        
        ###

        def getZP(cluster, filter, **spec):
            if not filter in self.zps:
                return None
            return fakeCalibration(self.zps[filter])




        def extinction(filter):
            if not filter in self.extinction:
                return 0
            return self.extinction[filter]

        ####

        
        newcat, zps = photoCalibrateCat(cat,
                                        cluster = self.cluster,
                                        type='standard',
                                        photometry_db = fakeCalDB(getZP),
                                        getExtinction = extinction,
                                        getDust = None)


        self.assertTrue('ebv' in newcat)

        expected = numpy.column_stack(self.targetFlux*numpy.ones(self.nObjs))

        for filter in self.filters:
            self.assertTrue( (numpy.abs(newcat['FLUX_ISO-%s' % filter] - expected) < 1e-8).all())


        

        ######################

    def testPropogateFlag(self):

        def getZP(cluster, filter, **spec):
            return fakeCalibration(self.zps[filter])


        cols = []
        cols.append(pyfits.Column(name='ALPHA_J2000',
                                  format='D',
                                  array=numpy.random.standard_normal(self.nObjs)))
        cols.append(pyfits.Column(name='DELTA_J2000',
                                  format='D',
                                  array=numpy.random.standard_normal(self.nObjs)))
        for filter in self.filters:
            flux = numpy.ones(self.nObjs)
            flux[-10:self.nObjs] = measure_unstacked_photometry.__bad_flux__
            cols.append(pyfits.Column(name='FLUX_ISO-%s' % filter,
                                      format='E',
                                      array=flux))
            cols.append(pyfits.Column(name='FLUXERR_ISO-%s' % filter,
                                      format='E',
                                      array=flux))

        cols.append(pyfits.Column(name='FLUX_ISO-SUBARU-10_1-1',
                                  format='E',
                                  array=numpy.random.uniform(0,500,self.nObjs)))
        cols.append(pyfits.Column(name='FLUXERR_ISO-SUBARU-10_1-1',
                                  format='E',
                                  array=numpy.random.uniform(0,500,self.nObjs)))

        cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols)))

        calibrated, zps = photoCalibrateCat(cat,
                                       cluster = self.cluster,
                                       type='standard',
                                       photometry_db = fakeCalDB(getZP),
                                       getExtinction = None,
                                       getDust = None)

        for filter in self.filters:
            self.assertTrue( (calibrated['FLUX_ISO-%s' % filter][-10:self.nObjs] == measure_unstacked_photometry.__bad_flux__).all() )
            self.assertTrue( (calibrated['FLUXERR_ISO-%s' % filter][-10:self.nObjs] == measure_unstacked_photometry.__bad_flux__).all() )


    ##############################


    def testPropagateSpecifications(self):

        class FakeDB(object):
            def __init__(self):
                self.calls = []
            def getZeropoint(self, cluster, **kw):
                self.calls.append((cluster, kw))
                return None

        #########

        db = FakeDB()

#def photoCalibrateCat(cat, cluster, type,  
#                      getExtinction = __get_extinction_default__,
#                      getDust = __get_dust_default__,
#                      photometry_db = __default_photometry_db__):
        

        photoCalibrateCat(self.cat, self.cluster, getExtinction = None, getDust = None, photometry_db = db,
                          specification={'myspec' : 'custom',
                                         'fluxtype' : 'iso'})


        self.assertEquals(len(db.calls), 11)

        for cluster, kw in db.calls:
            self.assertEquals(cluster, self.cluster)
            self.assertTrue('filter' in kw)
            self.assertEquals(kw['fluxtype'], 'iso')

    

    ###################################

    def testZPTableConsistant(self):

        testFilter = 'MEGAPRIME-0-1-r'
        filterZP = 27.1

        flux_name = 'FLUX_APER0-%s' % testFilter
        fluxerr_name = 'FLUXERR_APER0-%s' % testFilter
        mag_name = 'MAG_APER0-%s' % testFilter

        def getZP(cluster, filter, **kw):
            if filter == testFilter:
                return fakeCalibration(filterZP)
            return None
        
        expected_mags = 26.
        raw_mags = expected_mags*numpy.ones(self.nObjs) - filterZP
        fluxs = 10**(-0.4*raw_mags)
        fluxerrs = 0.001*fluxs


        self.cat[flux_name][:] = fluxs
        self.cat[fluxerr_name][:] = fluxerrs

        calibrated, zp_cat = photoCalibrateCat(self.cat, self.cluster, getExtinction = None, 
                                            getDust = None, photometry_db = fakeCalDB(getZP))

        zps = {}
        for filter, zp in zip(zp_cat['filter'], zp_cat['zeropoints']):
            zps[filter] = zp


        self.assertTrue(numpy.abs(zps[testFilter]- filterZP) < 1e-6)
        
        self.assertTrue((numpy.abs(calibrated[mag_name] - expected_mags) < 1e-6).all(), 'Expected: %3.2f, Returned: %3.2f' % (expected_mags, calibrated[mag_name][0]))



##############################

def test():

    testcases = [TestComponents, TestPhotoCalibrateCatalog]
    
    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)



##############################
# COMMANDLINE EXECUTABLE
##############################

if __name__ == '__main__':
    
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        test()
    else:
        main()
