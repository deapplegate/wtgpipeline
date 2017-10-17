#!/usr/bin/env python
######################
# Given catalogs from the coadded image, each individual exposure, 
#   and relative zeropoints, merge into one photometric catalog
######################

import re, unittest, numpy, astropy, astropy.io.fits as pyfits, ldac, sys, math
from optparse import OptionParser

######################

usage = '''
merge_unstacked_photometry.py -o outfile -s saturation [ -i instrum ] [ -m mastercat ] cat1 cat2 ...

Takes individual ldac catalogs and statistically combine flux measurements.
All other columns are copied from the mastercat

'''

######################

__cvs_id__ = "$Id: merge_unstacked_photometry.py,v 1.14 2009-08-03 18:43:51 dapple Exp $"

__max_ccd_id__ = 8

######################
# Exception Classes
######################

class FluxKeyException(Exception): pass

#######################
# Utility Functions
#######################

flux_search = re.compile('^FLUX_')
fluxerr_search = re.compile('^FLUXERR_')
rejectKeys = "FLUX_RADIUS".split()
def _sortFluxKeys(keylist):

    fluxkeys = []
    fluxerrkeys = []
    otherkeys = []
    for key in keylist:
        if flux_search.match(key) and key not in rejectKeys:
            fluxkeys.append(key)
        elif fluxerr_search.match(key):
            fluxerrkeys.append(key)
        else:
            otherkeys.append(key)

    return fluxkeys, fluxerrkeys, otherkeys

########################################

def _stackFluxs(fluxs):
    
    nfluxs = len(fluxs)
    fluxshape = fluxs[0].shape
    naxis = len(fluxshape)
    resultshape = []
    for i in xrange(naxis):
        resultshape.append(fluxshape[i])
    resultshape.append(nfluxs)
    
    result = numpy.zeros(tuple(resultshape))
    selector = [slice(fluxshape[i]) for i in xrange(naxis)]
    selector.append(0)
    for i in xrange(nfluxs):
        selector[-1] = i
        result[selector] = fluxs[i]

    return result
    

########################################

def _setMask(mask, condition):

    if len(mask.shape) == 2:
        mask[condition] = 0
    else:
        for i in xrange(mask.shape[1]):
            submask = mask[:,i,:]
            submask[condition] = 0
            mask[:,i,:] = submask

    return mask

########################################

def _weightedAverage(fluxs, errs, mask):

    weights = mask * (1./errs**2)
    weightsum = weights.sum(axis=-1, dtype=numpy.float64)
    flux = (weights*fluxs).sum(axis=-1, dtype=numpy.float64)/weightsum
    err = numpy.sqrt(1./weightsum)

    err[numpy.isnan(flux)] = 0
    flux[numpy.isnan(flux)] = -99


    return flux, err

########################################

def _medianHelper(fluxs,mask):
    goodfluxs = fluxs[mask>0]
    if len(goodfluxs) == 0:
        return -99, 0
    if len(goodfluxs) == 1:
        return goodfluxs[0], float('inf')
    sorted = numpy.sort(goodfluxs)
    midpoint = len(sorted)/2.
    if len(sorted) % 2 == 0:
        flux = sorted[midpoint]
        maxpoint = min(midpoint+2, len(sorted)-1)
        minpoint = max(midpoint-2, 0)
        err = (sorted[maxpoint] - sorted[minpoint])/2.
    else:
        midpoint = int(midpoint)
        flux = (sorted[midpoint] + sorted[midpoint + 1])/2.
        maxpoint = min(midpoint+1, len(sorted)-1)
        minpoint = max(midpoint-1, 0)
        err = (sorted[maxpoint] - sorted[minpoint])/2.

    return flux,err

####
        
def _median(fluxs, errs, mask):


    if len(fluxs.shape) == 2:
        nelements = fluxs.shape[0]
        flux = numpy.zeros(nelements)
        err = numpy.zeros_like(flux)
        for i in xrange(nelements):
            flux[i],err[i] = _medianHelper(fluxs[i,:], mask[i,:])
    else:
        nelements = fluxs.shape[0]
        nmeasures = fluxs.shape[1]
        flux = numpy.zeros((nelements, nmeasures))
        err = numpy.zeros_like(flux)
        for i in xrange(nelements):
            for j in xrange(nmeasures):
                flux[i,j],err[i,j] = _medianHelper(fluxs[i,j,:],mask[i,j,:])

    return flux,err

########################################

def _noFlagsMatch(flags, flagno):
    return not (flags == flagno).any()

####

def _combineFluxs(fluxs, errs, flags, 
                  maxvals, backgrounds, 
                  saturations, combine=_median):
    
    stackedFlux = _stackFluxs(fluxs)
    stackedErrs = _stackFluxs(errs)

    maxvals = numpy.column_stack(maxvals)
    backgrounds = numpy.column_stack(backgrounds)
    peakvals = maxvals + backgrounds
    saturations = numpy.array(saturations)

    
    combinedFluxs = {}
    flags = numpy.column_stack(flags)
    for chipid in [1,2,4,8]:

        if _noFlagsMatch(flags, chipid):
            continue

        mask = numpy.ones_like(stackedFlux)
        mask = _setMask(mask, flags != chipid )
        mask = _setMask(mask, peakvals > saturations)


        flux, err = combine(stackedFlux,
                            stackedErrs,
                            mask)    

        combinedFluxs[chipid] = (flux, err)


    return combinedFluxs

########################################

def _extractColumn(cat, key):

    for col in cat.hdu.columns:
        if col.name == key:
            return col

    return None

#########################################

_fluxsplit = re.compile('^FLUX_(.+)')

def _construct_fluxerr_key(fluxkey):

    match = _fluxsplit.match(fluxkey)
    if match is None:
        raise FluxKeyException('Cannot parse fluxkey: %s' % fluxkey)

    suffix = match.group(1)
    return 'FLUXERR_%s' % suffix
    

#########################################
# User Callable Functions
#########################################

def combineCats(catlist, saturation, instrum=None, mastercat=None):
    #returns ldac cat
    
    if len(catlist) == 0:
        return
    
    if len(catlist) == 1:
        return cats[0]
    
    referencecat = catlist[0]

    fluxkeys, fluxerrkeys, otherkeys = _sortFluxKeys(referencecat.keys())
    
    if mastercat is None:
        mastercat = referencecat
    else:
        ignoreFluxkeys, ignoreFluxerrkeys, otherkeys = _sortFluxKeys(mastercat.keys())

    print fluxkeys
    print fluxerrkeys
    print otherkeys

    cols = []
    for key in otherkeys:
        cols.append(_extractColumn(mastercat, key))
    
    for fluxkey in fluxkeys:
        
        fluxerr_key = _construct_fluxerr_key(fluxkey)
        
        inputfluxs = []
        inputerrs = []
        inputflags = []
        inputmaxvals = []
        inputbackgr = []
        saturations = []
        for cat in catlist:
            inputfluxs.append(cat[fluxkey])
            inputerrs.append(cat[fluxerr_key])
            inputflags.append(cat['IMAFLAGS_ISO'])
            inputmaxvals.append(cat['MaxVal'])
            inputbackgr.append(cat['BackGr'])
            saturations.append(saturation)
        fluxs = _combineFluxs(inputfluxs,
                              inputerrs,
                              inputflags,
                              inputmaxvals,
                              inputbackgr,
                              saturations)

        for chipid, (flux, err) in fluxs.iteritems():

            if instrum is None:
                id = '%d' % chipid
            else:
                id = '%s-%d' % (instrum, chipid)

            if len(flux.shape) == 1:
                cols.append(pyfits.Column(name='%s-%s' % (fluxkey, id), 
                                          format='E', 
                                          array=flux))
                cols.append(pyfits.Column(name='%s-%s' % (fluxerr_key, id),
                                          format='E', 
                                          array=err))
            else:
                nelements = flux.shape[1]
                cols.append(pyfits.Column(name='%s-%s' % (fluxkey, id), 
                                          format='%dE' % nelements, 
                                          array=flux))
                cols.append(pyfits.Column(name='%s-%s' % (fluxerr_key, id), 
                                          format='%dE' % nelements, 
                                          array=err))

    return ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols), 
                                         header=mastercat.hdu.header))


    
############################
############################
############################
# Testing Functions
############################

class TestCombineFluxs(unittest.TestCase):

    def setUp(self):
        self.testfluxs = [ numpy.random.standard_normal(30) for i in xrange(6) ]
        self.testerrs = [ numpy.ones(30) for i in xrange(6) ]
        self.testflags = [ numpy.ones(30) for i in xrange(6) ]
        self.testmaxvals = [ numpy.zeros(30) for i in xrange(6) ]
        self.testbackgr = [ numpy.zeros(30) for i in xrange(6) ]
        self.saturation = 6*[5]

    ##############

    def testCombineFluxs(self):


        combinedfluxs = _combineFluxs(self.testfluxs, 
                                                  self.testerrs, 
                                                  self.testflags,
                                                  self.testmaxvals,
                                                  self.testbackgr,
                                                  self.saturation)
        self.failIf(combinedfluxs is None)
        self.assertEqual(len(combinedfluxs.keys()), 1)

        chipid, (combinedflux, combinederr) = combinedfluxs.popitem()

        self.assertEqual(chipid, 1)

        self.assertEqual(len(combinedflux), 30)
        self.assertEqual(combinedflux.shape, (30,))

        self.failIf(combinederr is None)
        self.assertEqual(len(combinederr), 30)
        self.assertEqual(combinederr.shape, (30,))

    #################

    def testCombineFluxs_flag(self):

        self.testfluxs = [numpy.ones(30) for i in xrange(6)]
        self.testfluxs[-1] = 1e5*numpy.ones(30)
        self.testflags[-1] = 16*numpy.ones(30)

        combinedfluxs = _combineFluxs(self.testfluxs, 
                                      self.testerrs, 
                                      self.testflags,
                                      self.testmaxvals,
                                      self.testbackgr,
                                      self.saturation)

        chipid, (combinedflux, combinederr) = combinedfluxs.popitem()

        self.assertTrue((combinedflux == 1).all())

    #################

    def testCombineFluxs_ccdflagignore(self):

        self.testfluxs = [numpy.ones(30) for i in xrange(6)]
        self.testflags = [numpy.ones(30) for i in xrange(6)]

        combinedfluxs = _combineFluxs(self.testfluxs, 
                                      self.testerrs, 
                                      self.testflags,
                                      self.testmaxvals,
                                      self.testbackgr,
                                      self.saturation)

        chipid, (combinedflux, combinederr) = combinedfluxs.popitem()

        self.assertTrue((combinedflux == 1).all())


    #################

    def testCombineFluxs_flag_vector(self):

        self.testfluxs = [numpy.ones((30,5)) for i in xrange(6)]
        self.testfluxs[-1] = 1e5*numpy.ones((30,5))
        self.testerrs = [numpy.ones((30,5)) for i in xrange(6)]
        self.testflags[-1] = 32*numpy.ones(30)

        combinedfluxs = _combineFluxs(self.testfluxs, 
                                      self.testerrs, 
                                      self.testflags,
                                      self.testmaxvals,
                                      self.testbackgr,
                                      self.saturation)

        chipid, (combinedflux, combinederr) = combinedfluxs.popitem()

        self.assertTrue((combinedflux == 1).all())

    #################

    def testCombineFluxs_multichip(self):

        self.testfluxs = [numpy.ones((30,5)) for i in xrange(6)]
        self.testfluxs[-1] = 2*numpy.ones((30,5))
        self.testerrs = [numpy.ones((30,5)) for i in xrange(6)]
        self.testflags = [numpy.ones(30) for i in xrange(6)]
        self.testflags[-1] = 2*numpy.ones(30)

        combinedfluxs = _combineFluxs(self.testfluxs, 
                                      self.testerrs, 
                                      self.testflags,
                                      self.testmaxvals,
                                      self.testbackgr,
                                      self.saturation)

        self.assertTrue(1 in combinedfluxs.keys())
        self.assertTrue((combinedfluxs[1][0] == 1).all())
        self.assertEquals(len(combinedfluxs[1][0]), 30)
        self.assertEquals(len(combinedfluxs[1][1]), 30)

        self.assertTrue(2 in combinedfluxs.keys())
        self.assertTrue((combinedfluxs[2][0] == 2).all())
        self.assertEquals(len(combinedfluxs[2][0]), 30)
        self.assertEquals(len(combinedfluxs[2][1]), 30)



    ##############

    def testCombineFluxs_saturation(self):

        self.testfluxs= [numpy.ones(30) for i in xrange(6) ]
        self.testfluxs[-1] = 1e5*numpy.ones(30)
        self.testmaxvals[-1] = 1e4*numpy.ones(30)

        combinedfluxs = _combineFluxs(self.testfluxs, 
                                      self.testerrs, 
                                      self.testflags,
                                      self.testmaxvals,
                                      self.testbackgr,
                                      self.saturation)

        chipid, (combinedflux, combinederr) = combinedfluxs.popitem()


        self.assertTrue((combinedflux == 1).all())

    ###################

    def testCombineFluxs_fluxvector(self):

        self.testfluxs=[i*numpy.ones((30,5)) for i in xrange(6) ]
        self.testerrs=[numpy.ones((30,5)) for i in xrange(6) ]
        
        combinedfluxs = _combineFluxs(self.testfluxs, 
                                                  self.testerrs, 
                                                  self.testflags,
                                                  self.testmaxvals,
                                                  self.testbackgr,
                                                  self.saturation)

        chipid, (combinedflux, combinederr) = combinedfluxs.popitem()

        self.assertEquals(combinedflux.shape, (30,5))

    ####################

    def testCombineFluxs_finite(self):

        self.testfluxs=[math.pi*1e60*numpy.ones(30) for i in xrange(6) ]
        self.testerrs=[numpy.sqrt(f) for f in self.testfluxs]
        
        combinedfluxs = _combineFluxs(self.testfluxs, 
                                                  self.testerrs, 
                                                  self.testflags,
                                                  self.testmaxvals,
                                                  self.testbackgr,
                                                  self.saturation)

        chipid, (combinedflux, combinederr) = combinedfluxs.popitem()

        self.assertTrue(numpy.isfinite(combinedflux).all())
        self.assertTrue(numpy.isfinite(combinederr).all())

    #####################

    def testCombineFluxs_allbad(self):

        self.testflags = [ 32*numpy.ones(30) for i in xrange(6) ]
        combinedfluxs = _combineFluxs(self.testfluxs, 
                                                  self.testerrs, 
                                                  self.testflags,
                                                  self.testmaxvals,
                                                  self.testbackgr,
                                                  self.saturation)

        self.assertEquals(combinedfluxs.keys(), [])

        


    #################

    def testStackFluxs_scalar(self):

        fluxs = [ i*numpy.ones(10) for i in xrange(6) ]
        expected = numpy.column_stack(fluxs)
        stackedFlux = _stackFluxs(fluxs)
        self.assertEquals(stackedFlux.shape, expected.shape)
        for i in xrange(6):
            self.assertTrue((stackedFlux[i] == expected).all())
        

    #################

    def testStackFluxs_vector(self):

        fluxs=[i*numpy.ones((10,3)) for i in xrange(6)]
        stackedFlux = _stackFluxs(fluxs)
        self.assertEquals(stackedFlux.shape, (10,3,6))
        for i in xrange(6):
            self.assertTrue((stackedFlux[:,:,i] == i*numpy.ones((10,3))).all())

    #################

    def testSetMask_scalar(self):

        mask = numpy.ones((10,6))
        flag = numpy.array(10*[[0,0,0,0,0,1]])
        newmask = _setMask(mask, flag > 0)
        self.assertTrue((newmask == (1 - flag)).all())

    #################

    def testSetMask_vector(self):

        mask = numpy.ones((10,5,6))
        flag = numpy.array(10*[[0,0,0,0,0,1]])
        expected = 1 - flag
        newmask = _setMask(mask, flag > 0)
        self.assertEquals(newmask.shape, (10,5,6))
        for i in xrange(5):
            self.assertTrue((newmask[:,i,:] == expected).all())

    #################


    #####################

    def testWeightedAverage(self):

        testfluxs = [ numpy.ones(30) for i in xrange(6)]
        fluxs = _stackFluxs(testfluxs)
        for i in xrange(30):
            fluxs[i,:] = i
        errs = _stackFluxs(self.testerrs)
        mask = numpy.ones((30,6))

        flux, err = _weightedAverage(fluxs,errs,mask)
        self.assertEquals(flux.shape, (30,))
        self.assertEquals(err.shape, (30,))
        self.assertTrue((flux == numpy.array(xrange(30))).all())
        self.assertTrue((abs(err -numpy.ones(30)/numpy.sqrt(6)) < 1e-8).all())

    #####################

    def testWeightedAverage_mask(self):

        testfluxs = [ numpy.ones(30) for i in xrange(6)]
        fluxs = _stackFluxs(testfluxs)
        for i in xrange(30):
            fluxs[i,:] = i
        fluxs[:,2] = 1e5
        errs = _stackFluxs(self.testerrs)
        mask = numpy.ones((30,6))
        mask[:,2] = 0.

        flux, err = _weightedAverage(fluxs,errs,mask)
        self.assertEquals(flux.shape, (30,))
        self.assertEquals(err.shape, (30,))
        self.assertTrue((flux == numpy.array(xrange(30))).all())
        self.assertTrue((abs(err -numpy.ones(30)/numpy.sqrt(5)) < 1e-8).all())

    ########################

    def testWeightedAverage_vector(self):

        testfluxs = [ numpy.ones((30,5)) for i in xrange(6)]
        fluxs = _stackFluxs(testfluxs)
        for i in xrange(30):
            fluxs[i,:,:] = i
        errs = _stackFluxs(testfluxs)
        mask = numpy.ones((30,5,6))
        mask[:,:,2] = 0.

        flux, err = _weightedAverage(fluxs,errs,mask)
        self.assertEquals(flux.shape, (30,5))
        self.assertEquals(err.shape, (30,5))

        expectedFluxs = numpy.ones((30,5))
        for i in xrange(30):
            expectedFluxs[i,:] = i
        self.assertTrue((flux == expectedFluxs).all())

        self.assertTrue((abs(err - numpy.ones((30,5))/numpy.sqrt(5)) < 1e-8).all())

    ###########################

    def testWeightedAverage_nearzeroweights(self):

        testfluxs = [ numpy.ones(30) for i in xrange(6)]
        fluxs = _stackFluxs(testfluxs)
        for i in xrange(30):
            fluxs[i,:] = i
        testerrs = [ math.pi*1e30*numpy.ones(30) for i in xrange(6) ]
        errs = _stackFluxs(testerrs)
        mask = numpy.ones((30,6))

        flux, err = _weightedAverage(fluxs,errs,mask)

        self.assertEquals(flux.shape, (30,))
        self.assertEquals(err.shape, (30,))
        self.assertTrue((abs(flux - numpy.array(xrange(30))) < 1e-8 ).all())
        self.assertTrue((abs(err - math.pi*1e30*numpy.ones(30)/numpy.sqrt(6)) < 1e-8).all())
        


    ##########################

    def testMedian(self):

        testfluxs = [ numpy.ones(30) for i in xrange(6)]
        fluxs = _stackFluxs(testfluxs)
        for i in xrange(30):
            fluxs[i,:] = i
        errs = _stackFluxs(self.testerrs)
        mask = numpy.ones((30,6))

        flux, err = _median(fluxs,errs,mask)
        self.assertEquals(flux.shape, (30,))
        self.assertEquals(err.shape, (30,))
        self.assertTrue((flux == numpy.array(xrange(30))).all())
        self.assertTrue((abs(err) < 1e-8).all())

    #####################

    def testMedian_mask(self):

        testfluxs = [ numpy.ones(30) for i in xrange(6)]
        fluxs = _stackFluxs(testfluxs)
        for i in xrange(30):
            fluxs[i,:] = i
        fluxs[:,2] = 1e5
        errs = _stackFluxs(self.testerrs)
        mask = numpy.ones((30,6))
        mask[:,2] = 0.

        flux, err = _median(fluxs,errs,mask)
        self.assertEquals(flux.shape, (30,))
        self.assertEquals(err.shape, (30,))
        self.assertTrue((flux == numpy.array(xrange(30))).all())
        self.assertTrue((abs(err) < 1e-8).all())

    ########################

    def testMedian_vector(self):

        testfluxs = [ numpy.ones((30,5)) for i in xrange(6)]
        fluxs = _stackFluxs(testfluxs)
        for i in xrange(30):
            fluxs[i,:,:] = i
        fluxs[:,:,2] = 1e5
        errs = _stackFluxs(testfluxs)
        mask = numpy.ones((30,5,6))
        mask[:,:,2] = 0.

        flux, err = _median(fluxs,errs,mask)
        self.assertEquals(flux.shape, (30,5))
        self.assertEquals(err.shape, (30,5))

        expectedFluxs = numpy.ones((30,5))
        for i in xrange(30):
            expectedFluxs[i,:] = i
        self.assertTrue((flux == expectedFluxs).all())

        self.assertTrue((abs(err) < 1e-8).all())

    ##########################

    def testMedian_outofbounds(self):

        testfluxs = [ 1e5*numpy.ones(30) for i in xrange(6)]
        fluxs = _stackFluxs(testfluxs)
        fluxs[:,2] = numpy.array(xrange(30))
        fluxs[:,3] = numpy.array(xrange(30))
        errs = _stackFluxs(self.testerrs)
        mask = numpy.zeros((30,6))
        mask[:,2] = 1.
        mask[:,3] = 1.

        flux, err = _median(fluxs,errs,mask)
        self.assertEquals(flux.shape, (30,))
        self.assertEquals(err.shape, (30,))
        self.assertTrue((flux == numpy.array(xrange(30))).all())
        self.assertTrue((abs(err) < 1e-8).all())

    ##############################

    def testMedian_vector_outofbounds(self):

        testfluxs = [ 1e5*numpy.ones((30,5)) for i in xrange(6)]
        fluxs = _stackFluxs(testfluxs)
        fluxs[:,:,2] = 1
        fluxs[:,:,3] = 1
        errs = _stackFluxs(testfluxs)
        mask = numpy.zeros((30,5,6))
        mask[:,:,2] = 1.
        mask[:,:,3] = 1.

        flux, err = _median(fluxs,errs,mask)
        self.assertEquals(flux.shape, (30,5))
        self.assertEquals(err.shape, (30,5))

        expectedFluxs = numpy.ones((30,5))
        self.assertTrue((flux == expectedFluxs).all())

        self.assertTrue((abs(err) < 1e-8).all())


        

#############################


class TestComponents(unittest.TestCase):

    ################

    def testSortFluxKeys(self):

        keys = 'FLUX_APER1 FLUXERR_APER1 MAG_APER1 MAGERR_APER1 FLUX_AUTO2 FLUXERR_AUTO2'.split()
        fluxkeys, fluxerrkeys, otherkeys = _sortFluxKeys(keys)
        self.assertEquals(fluxkeys, 'FLUX_APER1 FLUX_AUTO2'.split())
        self.assertEquals(fluxerrkeys, 'FLUXERR_APER1 FLUXERR_AUTO2'.split())
        self.assertEquals(otherkeys, 'MAG_APER1 MAGERR_APER1'.split())

    ################

    def testSortFluxKeys_badones(self):

        keys = "FLUX_APER FLUX_APER1 MAG_APER FLUX_KRON FLUX_AUTO FLUX_RADIUS".split()
        fluxkeys, fluxerrkeys, otherkeys = _sortFluxKeys(keys)
        self.assertEquals(fluxkeys, "FLUX_APER FLUX_APER1 FLUX_KRON FLUX_AUTO".split())
        self.assertEquals(otherkeys, "MAG_APER FLUX_RADIUS".split())

    ################

    def testExtractColumn(self):

        keys = 'FLUX_APER1 FLUXERR_APER1 BLANK1 BLANK2 MAG_APER1 MAGERR_APER1'.split()
        cols = [pyfits.Column(name = k, 
                                    format = 'E', 
                                    array = numpy.ones(30)) \
                          for k in keys]
        cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols)))

        extractedCol = _extractColumn(cat, 'BLANK1')
        self.assertTrue((extractedCol.array == cols[2].array).all())
        self.assertEqual(extractedCol.name, cols[2].name)
        self.assertEqual(extractedCol.format, cols[2].format)
        

    #################

    def testConstructFluxErrKey(self):

        errkey = _construct_fluxerr_key('FLUX_APER1')
        self.assertEquals(errkey, 'FLUXERR_APER1')

    def testConstructFluxErrKey_Badkey(self):

        self.assertRaises(FluxKeyException, 
        _construct_fluxerr_key, 'FAKE1_FAKE')

    #################

    def testCombineCats(self):
        
        normkeys = 'FLUX_APER1 FLUXERR_APER1 MAG_APER1 MAGERR_APER1 BLANK1 BLANK2'.split()
        mastercols = [pyfits.Column(name = k, 
                                    format = 'E', 
                                    array = numpy.ones(30)) \
                          for k in normkeys]
        mastercols[0] = pyfits.Column(name = 'FLUX_APER1', 
                                    format = 'E', 
                                    array = numpy.random.standard_normal(30))
        zerokeys = 'MaxVal BackGr'.split()
        for key in zerokeys:
            mastercols.append(pyfits.Column(name = key, 
                                            format = 'E', 
                                            array = numpy.zeros(30)))
        mastercols.append(pyfits.Column(name = 'IMAFLAGS_ISO',
                                        format = 'J',
                                        array = numpy.ones(30)))


        
        cats = [ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(mastercols)))]

        for i in xrange(5):
            cols = [pyfits.Column(name = k, 
                                  format = 'E', 
                                  array = numpy.random.standard_normal(30)) \
                        for k in normkeys]
            cols[0] = pyfits.Column(name = 'FLUX_APER1', 
                                    format = 'E', 
                                    array = numpy.random.standard_normal(30))
        
            for key in zerokeys:
                cols.append(pyfits.Column(name = key, 
                                          format = 'E', 
                                          array = numpy.zeros(30)))
            cols.append(pyfits.Column(name = 'IMAFLAGS_ISO',
                                      format = 'E',
                                      array = numpy.ones(30)))


            cats.append(ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))))

        keys = normkeys[2:] + zerokeys
        keys.append('IMAFLAGS_ISO')
        
        combinedcat = combineCats(cats, saturation=5)

        self.assertEqual(type(combinedcat), type(cats[0]))
        for key in keys:
            self.assertTrue(key in combinedcat.keys())
        self.assertTrue((combinedcat['BLANK1'] == 1).all())
        self.assertTrue((combinedcat['BLANK2'] == 1).all())
        self.assertTrue((combinedcat['MAG_APER1'] == 1).all())
        self.assertTrue((combinedcat['MAGERR_APER1'] == 1).all())
        self.assertTrue((combinedcat['FLUX_APER1-1'] != 1).all())
        self.assertTrue((combinedcat['FLUXERR_APER1-1'] != 1).all())

    #######################################


    def testCombineCats_doubleprecision(self):

        doublekeys = 'ALPHA_J2000 DELTA_J2000'.split()
        normkeys = 'FLUX_APER FLUXERR_APER'.split()
        zerokeys = 'MaxVal BackGr'.split()

        cats = []
        for i in xrange(6):
            cols = [pyfits.Column(name = k, 
                                  format = 'E', 
                                  array = numpy.random.standard_normal(30))\
                        for k in normkeys]
            for key in zerokeys:
                cols.append(pyfits.Column(name = key, 
                                          format = 'E', 
                                          array = numpy.zeros(30)))

            for key in doublekeys:
                cols.append(pyfits.Column(name = key,
                                          format = 'D',
                                          array = numpy.random.standard_normal(30)))
            cols.append(pyfits.Column(name = 'IMAFLAGS_ISO',
                                      format = 'D',
                                      array = numpy.ones(30)))


            cats.append(ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))))


        keys = normkeys + zerokeys + doublekeys
        keys.append('IMAFLAGS_ISO')

        
        combinedcat = combineCats(cats, saturation=5)

        self.assertEquals(cats[0]['ALPHA_J2000'].dtype, combinedcat['ALPHA_J2000'].dtype)
        self.assertEquals(cats[0]['DELTA_J2000'].dtype, combinedcat['DELTA_J2000'].dtype)
        self.assertTrue((abs(cats[0]['ALPHA_J2000'] - combinedcat['ALPHA_J2000']) < 1e-16).all())
        self.assertTrue((abs(cats[0]['DELTA_J2000'] - combinedcat['DELTA_J2000']) < 1e-16).all())


    ##############################

    def testCombineCats_vector(self):

        normkeys = 'FLUX_APER FLUXERR_APER'.split()
        zerokeys = 'MaxVal BackGr'.split()

        cats = []
        for i in xrange(6):
            cols = [pyfits.Column(name = k, 
                                  format = '5E', 
                                  array = numpy.random.standard_normal((30,5)))\
                        for k in normkeys]
            for key in zerokeys:
                cols.append(pyfits.Column(name = key, 
                                          format = 'E', 
                                          array = numpy.zeros(30)))

            cols.append(pyfits.Column(name = 'IMAFLAGS_ISO',
                                      format = 'J',
                                      array = numpy.ones(30)))


            cats.append(ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))))


        keys = zerokeys

        
        combinedcat = combineCats(cats, saturation=5)

        self.assertEqual(type(combinedcat), type(cats[0]))
        for key in keys:
            self.assertTrue(key in combinedcat.keys())
        self.assertEqual(combinedcat['FLUX_APER-1'].shape, (30,5))
        self.assertEqual(combinedcat['FLUXERR_APER-1'].shape, (30,5))

    ###################################

    def testCombineCats_multichip(self):
        
        zerokeys = 'MaxVal BackGr'.split()

        cats = []
        for i in xrange(6):

            cols = [ pyfits.Column(name = key, 
                                   format = 'E', 
                                   array = numpy.zeros(30)) \
                         for key in zerokeys ]

            if i == 1:
                flags = numpy.ones(30)
            elif i == 2:
                flags = 2*numpy.ones(30)
            else:
                flags = numpy.random.random_integers(1,2,30)


            flags[25:] = 3

            flux = numpy.ones(30)
            flux[flags==2] = 2
            flux[flags==3] = 3




            
            fluxerr = numpy.random.standard_normal(30)
            
            cols.append(pyfits.Column(name = 'FLUX_APER',
                                      format = 'E',
                                      array = flux))
            cols.append(pyfits.Column(name = 'FLUXERR_APER',
                                      format = 'E',
                                      array = fluxerr))
            cols.append(pyfits.Column(name = 'IMAFLAGS_ISO',
                                      format = 'J',
                                      array = flags))
                                      




            cats.append(ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))))


        keys = zerokeys

        
        combinedcat = combineCats(cats, saturation=5)

        self.assertEqual(type(combinedcat), type(cats[0]))
        for key in keys:
            self.assertTrue(key in combinedcat.keys())
        self.assertEqual(combinedcat['FLUX_APER-1'].shape, (30,))
        self.assertEqual(combinedcat['FLUXERR_APER-1'].shape, (30,))
        self.assertTrue((combinedcat['FLUX_APER-1'][:25] == 1).all())
        self.assertTrue((combinedcat['FLUX_APER-1'][25:] == -99).all())

        self.assertEqual(combinedcat['FLUX_APER-2'].shape, (30,))
        self.assertEqual(combinedcat['FLUXERR_APER-2'].shape, (30,))
        self.assertTrue((combinedcat['FLUX_APER-2'][:25] == 2).all())
        self.assertTrue((combinedcat['FLUX_APER-2'][25:] == -99).all())

        self.assertEqual(combinedcat['FLUX_APER-3'].shape, (30,))
        self.assertEqual(combinedcat['FLUXERR_APER-3'].shape, (30,))
        self.assertTrue((combinedcat['FLUX_APER-3'][25:] == 3).all())
        self.assertTrue((combinedcat['FLUX_APER-3'][:25] == -99).all())

    ######################

    def testCombineCats_instrum(self):

        normkeys = 'FLUX_APER FLUXERR_APER'.split()
        zerokeys = 'MaxVal BackGr'.split()

        cats = []
        for i in xrange(6):
            cols = [pyfits.Column(name = k, 
                                  format = '5E', 
                                  array = numpy.random.standard_normal((30,5)))\
                        for k in normkeys]
            for key in zerokeys:
                cols.append(pyfits.Column(name = key, 
                                          format = 'E', 
                                          array = numpy.zeros(30)))

            cols.append(pyfits.Column(name = 'IMAFLAGS_ISO',
                                      format = 'J',
                                      array = numpy.ones(30)))


            cats.append(ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))))


        keys = zerokeys

        
        combinedcat = combineCats(cats, saturation=5, instrum='SUBARU-10_1')

        self.assertEqual(type(combinedcat), type(cats[0]))
        for key in keys:
            self.assertTrue(key in combinedcat.keys())
        self.assertEqual(combinedcat['FLUX_APER-SUBARU-10_1-1'].shape, (30,5))
        self.assertEqual(combinedcat['FLUXERR_APER-SUBARU-10_1-1'].shape, (30,5))

    ##############

    def testCombineCats_mastercat(self):

        normkeys = 'FLUX_APER FLUXERR_APER'.split()
        zerokeys = 'MaxVal BackGr'.split()

        cats = []
        for i in xrange(6):
            cols = [pyfits.Column(name = k, 
                                  format = '5E', 
                                  array = numpy.random.standard_normal((30,5)))\
                        for k in normkeys]
            for key in zerokeys:
                cols.append(pyfits.Column(name = key, 
                                          format = 'E', 
                                          array = numpy.zeros(30)))

            cols.append(pyfits.Column(name = 'IMAFLAGS_ISO',
                                      format = 'J',
                                      array = numpy.ones(30)))


            cats.append(ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))))

        
        mastercols = []
        mastercols.append(pyfits.Column(name = 'FLUX_APER',
                                        format = 'E',
                                        array = 1e5*numpy.ones(30)))
        mastercols.append(pyfits.Column(name = 'MAG_APER',
                                        format = 'E',
                                        array = numpy.ones(30)))
        mastercat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(mastercols)))


        keys = ['MAG_APER']

        
        combinedcat = combineCats(cats, 
                                  saturation=5, 
                                  mastercat = mastercat)

        self.assertEqual(type(combinedcat), type(cats[0]))
        for key in keys:
            self.assertTrue(key in combinedcat.keys())
        self.assertTrue((combinedcat['MAG_APER'] == 1).all())
        self.assertEqual(combinedcat['FLUX_APER-1'].shape, (30,5))
        self.assertEqual(combinedcat['FLUXERR_APER-1'].shape, (30,5))

        
            

#################################
#################################
#################################
# Main Driver Functions
#################################
        

def test():

    testcases = [TestCombineFluxs, TestComponents]
    
    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)

#####################

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


def main(args = sys.argv):

    parser = OptionParser(usage = usage)
    parser.add_option('-o', '--outfile',
                      help = 'output catalog name',
                      dest = 'outfile')
    parser.add_option('-s', '--saturation',
                      help = 'Saturation Pixel Level',
                      dest = 'saturation')
    parser.add_option('-i', '--instrum',
                      help = 'Instrument tag',
                      dest = 'instrum')
    parser.add_option('-m', '--mastercat',
                      help = 'Master catalog to pull non Flux columns from',
                      dest = 'mastercat')

    options, catfiles = parser.parse_args()

    if options.outfile is None or \
            options.saturation is None:
        parser.error('Must specify outfile and saturation level')
    

    catlist = [ ldac.openObjectFile(catfile) for catfile in catfiles ]
    mastercat = None
    if options.mastercat:
        mastercat = ldac.openObjectFile(options.mastercat)

    combinedcat = combineCats(catlist, options.saturation, 
                              instrum = options.instrum,
                              mastercat = mastercat)

    hdus = [pyfits.PrimaryHDU(), combinedcat.hdu]
    if mastercat:
        hdus.extend(_transferOtherHDUs(options.mastercat))
    else:
        hdus.extend(_transferOtherHDUs(catfiles[0]))
    hdulist = pyfits.HDUList(hdus)
    hdulist.writeto(options.outfile, overwrite=True)

    

    


####################

if __name__ == '__main__':
    
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        test()
    else:
        main()
