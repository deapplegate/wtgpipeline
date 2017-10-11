#!/usr/bin/env python
######################

from __future__ import with_statement
import unittest, sys, math, re, os, optparse
import numpy, astropy, astropy.io.fits as pyfits
from scipy import interpolate
import ldac, utilities

######################

__cvs_id__ = "$Id: measure_unstacked_photometry.py,v 1.15 2010-06-07 18:00:24 dapple Exp $"


##############################################################
# USAGE
##############################################################

usage = '''
measure_unstacked_photometry.py -o outfile [ -i instrum ] [ -m mastercat ] [-f] cat1 cat2 ...

Takes individual ldac catalogs and statistically combine flux measurements.
All other columns are copied from the mastercat.
Will recalculate flux errors based on proper Background Aperture RMS, 
 and will optionally rescale fluxs between images.

'''

###############################################################
# DEFAULTS & GLOBALS
###############################################################

__fluxscale_default__ = True
__bad_mag__ = -99
__bad_flux__ = -99
__resampling_sigma_scaling__ = 1.5


################################################################
# USER CALLABLE FUNCTIONS
################################################################

def loadImage(catfile):
    '''loadImage
       @param catfile string filename for ldac cat produced for an image
       @returns Image object needed for measureUnstackedPhotometry'''

    cat = ldac.openObjectFile(catfile)
    gain = readGain(catfile)
    apers = readApers(catfile)
    catbase, ext = os.path.splitext(catfile)

    photinfo = ldac.openObjectFile(catfile, 'PHOTINFO')
    rms = photinfo['BACKGROUND_RMS']

    return Image(cat, rms, apers, gain)

################################################################

def _isVector(flux):

    return len(flux.shape) > 2

####

def _noFlagsMatch(flags, flagno):
    return not (flags == flagno).any()

####


def measureUnstackedPhotometry(images, 
                               fluxkey = 'FLUX_APER',
                               fluxscale = False):
    '''measureUnstackedPhotometry
       @param images A list of Image objects for each input catalog
       @param fluxkey Key in each image catalog with flux measurement
       @param fluxscale Rescale fluxes between images before combining
       @returns chip id : (flux, fluxerr) dictionary for each chip type'''

    fluxtype = utilities.extractFluxType(fluxkey)
    fluxerr_key = 'FLUXERR_%s' % fluxtype

    fluxs = _stackFluxs([ image.cat[fluxkey] for image in images ])
    origErrs = _stackFluxs([ image.cat[fluxerr_key] for image in images ])
    errs = _stackFluxs([ image.getFluxErr(fluxkey) for image in images ])


    flag = _stackFluxs([image.cat['Flag'] for image in images])
    MaxVal = _stackFluxs([image.cat['MaxVal'] for image in images])
    BackGr = _stackFluxs([image.cat['BackGr'] for image in images])
    peakvals = MaxVal + BackGr

    imaflags = _stackFluxs([image.cat['IMAFLAGS_ISO'] for image in images])

    combinedFluxs = {}
    for chipId in [1,2,4,8]:

        if _noFlagsMatch(imaflags, chipId):
            continue

        mask = cuts(fluxs, origErrs, peakvals, numpy.ones_like(fluxs))

        mask = _setMask(mask, imaflags != chipId)



        if fluxscale:

            mags, magerrs = calcMags(fluxs, errs)
            
            fluxscalingMask = createFluxScalingMask(fluxs, flag, mask)
            fluxscalings = measureFluxScaling(mags, magerrs, fluxscalingMask)

            fluxs = fluxscalings*fluxs
            for i in xrange(len(images)):
                if _isVector(fluxs):
                    errs[:,:,i] = images[i].getFluxErr(fluxkey, fluxscalings[:,i])
                else:
                    errs[:,i] = images[i].getFluxErr(fluxkey, fluxscalings[i])

    
        flux, err = statCombineFluxs(fluxs, errs, mask)
        combinedFluxs[chipId] = (flux, err)

    return combinedFluxs

######################################################################

def combineCats(images, instrum=None, mastercat=None, fluxscale = False):
    '''combineCats Given input image objects, returns a catalog with statistically combined fluxs and magnitudes
       @param images List of Image objects describing each input ldac catalog
       @param instrum Instrument name to be included in each output flux column
       @param mastercat Catalog containing other relevant data to be propagated to the output catalog
       @param fluxscale Perform fluxscaling between images
       @returns ldac.LDACCat A catalog where all flux measurements have been statistically combined
       '''
    
    if len(images) == 0:
        return
    
    if len(images) == 1:
        return images[0].cat
    
    referencecat = images[0].cat

    fluxkeys, fluxerrkeys, magonlykeys, otherkeys = utilities.sortFluxKeys(referencecat.keys())
    
    if mastercat is None:
        mastercat = referencecat
    else:
        ignoreFluxkeys, ignoreFluxerrkeys, magonlykeys, otherkeys = utilities.sortFluxKeys(mastercat.keys())

    cols = []
    for key in otherkeys:
        cols.append(mastercat.extractColumn(key))
    
    for fluxkey in fluxkeys:
        
        fluxType = utilities.extractFluxType(fluxkey)
        
        fluxs = measureUnstackedPhotometry(images, fluxkey = fluxkey, 
                                           fluxscale = fluxscale)

        for chipid, (flux, err) in fluxs.iteritems():

            if instrum is None:
                id = '%d' % chipid
            else:
                id = '%s-%d' % (instrum, chipid)

            fluxerr_key = 'FLUXERR_%s' % fluxType

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


#################################################################
# MAIN
#################################################################

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

    parser = optparse.OptionParser(usage = usage)
    parser.add_option('-o', '--outfile',
                      help = 'output catalog name',
                      dest = 'outfile')
    parser.add_option('-i', '--instrum',
                      help = 'Instrument tag',
                      dest = 'instrum')
    parser.add_option('-m', '--mastercat',
                      help = 'Master catalog to pull non Flux columns from',
                      dest = 'mastercat')
    parser.add_option('-f', '--nofluxscale',
                      help = 'Turn off fluxscaling between images',
                      dest = 'fluxscale',
                      action = 'store_false',
                      default = __fluxscale_default__)

    options, catfiles = parser.parse_args()

    if options.outfile is None:
        parser.error('Must specify outfile')
    

    mastercat = None
    if options.mastercat:
        mastercat = ldac.openObjectFile(options.mastercat)

    images = [ loadImage(catfile) for catfile in catfiles ]


    combinedcat = combineCats(images,
                              instrum = options.instrum,
                              mastercat = mastercat,
                              fluxscale = options.fluxscale)

    hdus = [pyfits.PrimaryHDU(), combinedcat.hdu]
    if mastercat:
        hdus.extend(_transferOtherHDUs(options.mastercat))
    else:
        hdus.extend(_transferOtherHDUs(catfiles[0]))
    hdulist = pyfits.HDUList(hdus)
    hdulist.writeto(options.outfile, overwrite=True)



############################################################
# INTERNAL CLASSES
############################################################

class UnknownFluxTypeException(Exception): pass

class Image(object):

    def __init__(self, cat, rms, apers, gain):
        self.cat = cat
        self.rms = rms
        self.apers = apers
        self.gain = gain

        if 'ISOAREA_DETECT' in cat:
            self.area = self.cat['ISOAREA_DETECT']
        else:
            self.area = self.cat['NPIX']

    def getFluxErr(self, fluxkey = 'FLUX_APER', fluxscale = 1.):

        if fluxkey == 'FLUX_APER':
            area = numpy.pi*(self.apers/2.)**2
        elif fluxkey == 'FLUX_ISO':
            area = self.area
        else:
            raise UnknownFluxTypeException(fluxkey)
        return numpy.sqrt(area*(__resampling_sigma_scaling__*self.rms)**2 + fluxscale*numpy.abs(self.cat[fluxkey])/self.gain)


#######################
# UTILITY FUNCTIONS
#######################

def cuts(photflux, errs, peakvals, mask=None):

    if mask is None:
        mask = numpy.ones_like(photflux)
    else:
        mask = numpy.copy(mask)

    mask = _setMask(mask, peakvals > 20000)
    mask[numpy.isnan(photflux)] = 0
    mask[errs == 0.] = 0
                                                   
    return mask


################################


def adjustFlux(fluxs, fluxerrs, gain, backgroundRMS, fluxscales):

    newFlux = fluxs*fluxscales
    newfluxerrs = numpy.sqrt(backgroundRMS + newFlux/gain)/newFlux

    return newFlux, newfluxerrs


#######################


def createFluxScalingMask(photflux, flags, mask = None):

    if mask is None:
        mask = numpy.ones_like(photflux)
    else:
        mask = numpy.copy(mask)

    mask = _setMask(mask, numpy.logical_or(flags == 1, flags == 3))
    mask[photflux < 0] = 0

    return mask

#######################

def _measureFluxScaling_scalar(mags, magerrs, mask):

    mask = numpy.copy(mask)
    mask[numpy.logical_not(numpy.isfinite(mags))] = 0
    mask[mags == __bad_mag__ ] = 0
    mask[mags == 99 ] = 0
    mask[mags == -99 ] = 0

    nObs = numpy.sum(mask, axis=-1)
    nImages = mags.shape[-1]
    nGals = mags.shape[0]

    aveMags = numpy.zeros(nGals)
    stderr = numpy.zeros(nGals)
    for i in xrange(nGals):
       vals = mags[i][mask[i] == 1]
       if len(vals) > 2:
           aveMags[i] = numpy.average(vals)
           stderr[i] = numpy.std(vals)

    aveMagsMatrix = numpy.column_stack(nImages*[aveMags])
    deltaMag = mags - aveMagsMatrix

    allOffsets = numpy.zeros(nImages)
    for i in xrange(nImages):
        goodMags = deltaMag[:,i][numpy.logical_and(nObs > 2, mask[:,i] == 1)]
        weights = 1./stderr[numpy.logical_and(nObs > 2, mask[:,i] == 1)]**2
        if len(goodMags) == 0:
            return numpy.ones(nImages)
        if numpy.logical_or(weights == 0, numpy.isinf(weights)).all():
            weights = numpy.ones_like(weights)
        allOffsets[i] = -numpy.average(goodMags, weights=weights)
        
    return 10**(-.4*allOffsets)

########################################

def measureFluxScaling(mags, magerrs, mask):

    if len(mags.shape) == 2:
        return _measureFluxScaling_scalar(mags, magerrs, mask)

    nApers = mags.shape[1]
    nImages = mags.shape[2]

    scalings = numpy.zeros((nApers, nImages))
    for aper in xrange(nApers):
        scalings[aper,:] = _measureFluxScaling_scalar(mags[:,aper,:],
                                                      magerrs[:,aper,:],
                                                      mask[:,aper,:])

    return scalings
        


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

#########################################

def statCombineFluxs(fluxs, errs, mask, sigmaReject = 5):

    ########

    def identifyOutliers(fluxs, errs, meanFlux, meanErr, nsigma):

        refflux = _stackFluxs(nImages*[meanFlux])
        refsig = _stackFluxs(nImages*[meanErr])
        refsig = numpy.sqrt(refsig**2 + errs**2)
    
        pull = (fluxs - refflux)/refsig
        outliers = numpy.zeros_like(fluxs)
        outliers[abs(pull) > 5] = 1

        return outliers

    ##########
        

    outliers = numpy.zeros_like(mask)

    nImages = fluxs.shape[-1]

    for i in xrange(2):

        local_mask = numpy.ones_like(mask)
        local_mask[numpy.logical_or(mask == 0, outliers == 1)] = 0

        flux, err =  _weightedAverage(fluxs, errs, local_mask)
        skew, std_emp = calcSkewandStd(fluxs, local_mask)

        outliers = identifyOutliers(fluxs, errs, flux, err, sigmaReject)
        nOutliers = outliers.sum(axis=-1)

        allRejected = (nOutliers == nImages)

        if allRejected.any():

            rejectedFluxs = fluxs[allRejected]
            rejectedErrs = errs[allRejected]
            rejectedMeanErr = err[allRejected]
            rejectedMask = mask[allRejected]
            medianVals = _median(rejectedFluxs, rejectedMask)

            rejectedOutliers = identifyOutliers(rejectedFluxs, rejectedErrs, medianVals, rejectedMeanErr, sigmaReject)
            
            outliers[allRejected] = rejectedOutliers

    return skew, err / std_emp




####################################

def _weightedAverage(fluxs, errs, mask):

    nImages = fluxs.shape[-1]
    nGals = fluxs.shape[0]

    local_errs = numpy.copy(errs)
    local_errs[mask == 0] = 1
    weights = mask * (1./local_errs**2)
    
    weightsum = weights.sum(axis=-1)
        
    flux = (weights*fluxs).sum(axis=-1, dtype=numpy.float64)/weightsum
    err = numpy.sqrt(1./weightsum)

    err[numpy.isnan(flux)] = __bad_flux__
    flux[numpy.isnan(flux)] = __bad_flux__


    return flux, err
    

###################

def calcSkewandStd(fluxs, mask):

    nobs = mask.sum(axis=-1)

    unweightedMean = (fluxs*mask).sum(axis=-1) / nobs

    unweightedMeanGrid = numpy.zeros_like(fluxs)
    if len(fluxs.shape) == 2:
        unweightedMeanGrid = (unweightedMeanGrid.T + unweightedMean).T

        unweightedStd = numpy.zeros(fluxs.shape[0])
        skew = numpy.zeros(fluxs.shape[0])
        for i in range(fluxs.shape[0]):
            unweightedStd[i] = numpy.sqrt(numpy.sum((fluxs[i] - unweightedMeanGrid[i])[mask[i] > 0]**2)/nobs[i])
            skew[i] = (numpy.sqrt(nobs[i]*(nobs[i] - 1))/(nobs[i] - 2))*(1./nobs[i])*numpy.sum((fluxs[i] - unweightedMeanGrid[i])[mask[i] > 0]**3)/(unweightedStd[i]**3)

    else:
        for i in range(fluxs.shape[2]):
            unweightedMeanGrid[:,:,i] = unweightedMean

        unweightedStd = numpy.zeros(fluxs.shape[:2])
        skew = numpy.zeros(fluxs.shape[:2])
        for i in range(fluxs.shape[0]):
            unweightedStd[i,:] = numpy.sqrt(numpy.sum((fluxs[i] - unweightedMeanGrid[i])[mask[i] > 0]**2)/nobs[i])
            skew[i,:] = (numpy.sqrt(nobs[i]*(nobs[i] - 1))/(nobs[i] - 2))*(1./nobs[i])*numpy.sum((fluxs[i] - unweightedMeanGrid[i])[mask[i] > 0]**3)/(unweightedStd[i]**3)




    std = unweightedStd / numpy.sqrt(nobs)

    std[nobs == 0] = -1
    skew[nobs < 3] = numpy.nan

    return skew, std


####################################

def _median(fluxs, mask):

    ##############

    def scalarMedian(fluxs, mask):
        nGals = len(fluxs)
        flux = numpy.zeros(nGals)
        for i in xrange(nGals):
            flux[i] = numpy.median(fluxs[i][mask[i] == 1])    
        return flux
        
    ###############


    fluxIsVector = fluxs.ndim == 3
    if fluxIsVector:

        nGals = fluxs.shape[0]        
        nApers = fluxs.shape[1]
        
        flux = numpy.zeros((nGals, nApers))
        
        for aper in xrange(nApers):

            flux[:,aper] = scalarMedian(fluxs[:,aper,:], mask[:,aper,:])

        return flux

    else:
        
        return scalarMedian(fluxs, mask)
                        
    

####################################

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


def calcMags(fluxs, errs):

    mags = -2.5*numpy.log10(fluxs)
    magerrs = 1.0857 * errs / fluxs

    magerrs[ numpy.logical_not(numpy.isfinite(mags)) ] = 0
    mags[ numpy.logical_not(numpy.isfinite(mags)) ] = __bad_mag__

    magerrs[mags > 99] = 99
    magerrs[magerrs > 99] = 99
    mags[mags > 99 ] = 99
    

    return mags, magerrs



######################################

_commentFilter = re.compile('^#')
def readBackgroundRMS(file):

    
    with open(file) as rmsFile:
        for line in rmsFile.readlines():
            if _commentFilter.match(line):
                continue
            try:
                rms = float(line)
                return rms
            except:
                continue

    return rms

###################################

def readGain(cat):

    fields = ldac.openObjectFile(cat, 'FIELDS')
    return fields['GAIN']

###################################

_aperFilter = re.compile('^SEXAPED')
def readApers(cat):

    fields = ldac.openObjectFile(cat, 'FIELDS')
    apers = []
    for key in sorted(fields.keys()):
        if _aperFilter.match(key):
            aper_diameter = fields[key][0]
            if aper_diameter > 0:
                apers.append(aper_diameter)

    return numpy.array(apers)



#################################################
# TESTING
#################################################

class TestComponents(unittest.TestCase):

    def testReadApers(self):

        catFile = 'test_measureUnstackedPhot_readapers.cat'
        
        def cleanUp():
            if os.path.exists(catFile):
                os.remove(catFile)
        try:
            
            if not os.path.exists(catFile):
                cols = [pyfits.Column(name = 'SEXAPED1',
                                     format = 'E',
                                     array = numpy.array([10])),
                        pyfits.Column(name = 'SEXAPED2',
                                      format = 'E',
                                      array = numpy.array([15])),
                        pyfits.Column(name = 'SEXAPED3',
                                     format = 'E',
                                     array = numpy.array([0])),
                        pyfits.Column(name = 'SEXAPED4',
                                     format = 'E',
                                     array = numpy.array([0]))]
                hdu = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
                hdu.header['EXTNAME']= 'FIELDS'
                hdu.writeto(catFile, overwrite = True)
                                     
            
            apers = readApers(catFile)
            
            self.assertTrue((apers == numpy.array([10,15])).all())

        finally:
            cleanUp()



    ###########################    #

    def testReadBackgroundRMS(self):

        rmsFile = 'test_measureUnstackedPhot_readBkgRMS.txt'
        
        def cleanUp():
            if os.path.exists(rmsFile):
                os.remove(rmsFile)
        try:
            
            if not os.path.exists(rmsFile):
                with open(rmsFile, 'w') as output:
                    output.write('#Aperture\tSigma\n')
                    output.write('.15\n')
            
            RMS = readBackgroundRMS(rmsFile)
            self.assertEquals(RMS, .15 )

        finally:
            cleanUp()

    ###################

    def testReadGain(self):

        catFile = 'test_measureUnstackedPhot_readgain.cat'
        
        def cleanUp():
            if os.path.exists(catFile):
                os.remove(catFile)
        try:
            
            if not os.path.exists(catFile):
                cols = [pyfits.Column(name = 'GAIN',
                                     format = 'D',
                                     array = numpy.array([900]))]
                hdu = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
                hdu.header['EXTNAME']= 'FIELDS'
                hdu.writeto(catFile, overwrite = True)
                                     
            
            gain = readGain(catFile)
            
            self.assertEqual(gain, 900)

        finally:
            cleanUp()

    ##################


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

    def testCalcMags(self):

        fluxs = 5*numpy.ones(30)
        fluxerrs = .1*numpy.ones(30)
        
        fluxs[0] = 1e-45
        fluxs[1] = 1e-20
        fluxs[25:] = -1
        fluxs[-1] = 0
        
        mags, magerrs, = calcMags(fluxs, fluxerrs)

        self.assertTrue( (mags[0] == 99) )
        self.assertTrue( (mags[2:25] == -2.5*numpy.log10(5) ).all() )
        self.assertTrue( (mags[25:] == __bad_mag__).all() )
        self.assertTrue( max(mags) <= 99 )

        self.assertTrue( (magerrs[0] == 99) )
        self.assertTrue( (magerrs[2:25] == (1.0857*.1/5)).all() )
        self.assertTrue( (magerrs[25:] == 0).all() )
        self.assertTrue( max(magerrs) <= 99 )


#################

class TestImage(unittest.TestCase):

    def setUp(self):
        
        self.catFile = 'test_measureUnstackedPhot_loadimage.cat0'

        if not os.path.exists(self.catFile):
            cols = [pyfits.Column(name = 'GAIN',
                                  format = 'D',
                                  array = numpy.array([900])),
                    pyfits.Column(name = 'SEXAPED1',
                                  format = 'E',
                                  array = numpy.array([10])),
                    pyfits.Column(name = 'SEXAPED2',
                                  format = 'E',
                                  array = numpy.array([15])),
                    pyfits.Column(name = 'SEXAPED3',
                                  format = 'E',
                                  array = numpy.array([0]))]
            fields = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
            fields.header['EXTNAME']= 'FIELDS'
            cols = [pyfits.Column(name = 'Xpos',
                                  format = 'E',
                                  array = numpy.random.uniform(0,10000,200)),
                    pyfits.Column(name='FLUX_APER',
                                  format = '2E',
                                  array = numpy.ones((200,2))),
                    pyfits.Column(name='FLUX_ISO',
                                  format = 'E',
                                  array = numpy.ones(200)),
                    pyfits.Column(name='ISOAREA_DETECT',
                                  format='E',
                                  array = 10*numpy.ones(200))]
            objects = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
            objects.header['EXTNAME']= 'OBJECTS'

            cols = [pyfits.Column(name='BACKGROUND_RMS', format='E', array = [0.15])]
            photinfo = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
            photinfo.header['EXTNAME']= 'PHOTINFO'
            
            hdulist = pyfits.HDUList([pyfits.PrimaryHDU(), objects, fields, photinfo])
            hdulist.writeto(self.catFile, overwrite = True)


            
    def tearDown(self):
        if os.path.exists(self.catFile):
            os.remove(self.catFile)

            
        

    def testLoadImage(self):
                                        
            
        image = loadImage(self.catFile)
        
        self.assertTrue(isinstance(image, Image))
        self.assertTrue(isinstance(image.cat, ldac.LDACCat))
        self.assertEqual(image.gain, 900)
        self.assertEqual(image.rms, .15)
        self.assertTrue((image.apers == numpy.array([10,15])).all())


    ###############

    def testImageFluxErr_Aper(self):

        image = loadImage(self.catFile)

        errors = image.getFluxErr()

        self.assertEquals(errors.shape, (200,2))

        aper1Area = numpy.pi*(5**2)
        aper2Area = numpy.pi*(7.5**2)
        self.assertTrue((numpy.abs(errors[:,0] - numpy.sqrt(aper1Area*(.15*__resampling_sigma_scaling__)**2 + 1./900)) < 1e-4).all())
        self.assertTrue((numpy.abs(errors[:,1] - numpy.sqrt(aper2Area*(.15*__resampling_sigma_scaling__)**2 + 1./900)) < 1e-4).all())


    ###############

    def testImageFluxErr_Iso(self):
        
        image = loadImage(self.catFile)
        image.cat['ISOAREA_DETECT'][100:] = 100

        errors = image.getFluxErr(fluxkey='FLUX_ISO')

        self.assertEquals(errors.shape, (200,))
        self.assertTrue((numpy.abs(errors[:100] - numpy.sqrt(10*(.15*__resampling_sigma_scaling__)**2 + 1./900)) < 1e-4).all())
        self.assertTrue((numpy.abs(errors[100:] - numpy.sqrt(100*(.15*__resampling_sigma_scaling__)**2 + 1./900)) < 1e-4).all())

    ################
            




##################

class TestUnstackedPhotometry(unittest.TestCase):

    def setUp(self):
        self.nImages = 5
        self.nObjs = 200

        self.images = []
        for i in xrange(self.nImages):
            fluxs = numpy.ones(self.nObjs)
            fluxerrs = numpy.ones_like(fluxs)
            flags = numpy.zeros_like(fluxs)
            imaflags = numpy.ones_like(fluxs)
            BackGr = numpy.zeros_like(fluxs)
            MaxVal = 0.1*numpy.ones_like(fluxs)
            NPIX = numpy.zeros(self.nObjs)
            
            cols = []
            cols.append(pyfits.Column(name='FLUX_APER', format = 'E', array = fluxs))
            cols.append(pyfits.Column(name='FLUXERR_APER', format = 'E', array = fluxs))
            cols.append(pyfits.Column(name='Flag', format = 'J', array = flags))
            cols.append(pyfits.Column(name='IMAFLAGS_ISO', format = 'J', array = imaflags))
            cols.append(pyfits.Column(name='BackGr', format = 'E', array = BackGr))
            cols.append(pyfits.Column(name='MaxVal', format = 'E', array = MaxVal))
            cols.append(pyfits.Column(name='NPIX', format='E', array = NPIX))
            cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(cols))
            self.images.append(Image(cat = cat, apers = numpy.ones(1), rms = 0., gain = 1.))
        

    ############


    def testSimple(self):
        
        combinedFluxs = measureUnstackedPhotometry(self.images)
        chipid, (flux, fluxerr) = combinedFluxs.popitem()

        self.assertEqual(chipid, 1)
        self.assertEqual(len(flux), self.nObjs)
        self.assertEqual(len(fluxerr), self.nObjs)
        self.assertTrue( (numpy.abs(flux - 1) < 1e-8).all() )
        self.assertTrue( (numpy.abs(fluxerr - 1./math.sqrt(self.nImages)) < 1e-8).all() )

    ###########

    def testFluxs(self):

        expectedFluxs = 10**(-.4*numpy.random.uniform(-9,-2, self.nObjs))

        for image in self.images:
            catflux = image.cat['FLUX_APER']
            image.cat['FLUX_APER'][:] = expectedFluxs + 0.05*numpy.random.standard_normal(self.nObjs)
            
        combinedFluxs = measureUnstackedPhotometry(self.images)
        chipid, (flux, fluxerr) = combinedFluxs.popitem()

        self.assertTrue( (numpy.abs(flux - expectedFluxs) < 1e-1).all() )

    ############

    def testCuts(self):

        self.images[-1].cat['MaxVal'][:] = 1e7*numpy.ones(self.nObjs)
        self.images[-1].cat['FLUX_APER'][:] = 1e7*numpy.ones(self.nObjs)

        combinedFluxs = measureUnstackedPhotometry(self.images)
        chipid, (flux, fluxerr) = combinedFluxs.popitem()

        self.assertTrue( (numpy.abs(flux - 1) < 1e-8).all() )
        self.assertTrue( (numpy.abs(fluxerr - 1./math.sqrt(self.nImages - 1)) < 1e-8).all() )

    ############

    def testExcludeErr0(self):

        self.images[-1].cat['FLUXERR_APER'][:] = numpy.zeros(self.nObjs)
        self.images[-1].cat['FLUX_APER'][:] = 2*numpy.ones(self.nObjs)

        combinedFluxs = measureUnstackedPhotometry(self.images)
        chipid, (flux, fluxerr) = combinedFluxs.popitem()

        self.assertTrue( (numpy.abs(flux - 1) < 1e-8).all() )
        self.assertTrue( (numpy.abs(fluxerr - 1./math.sqrt(self.nImages - 1)) < 1e-8).all() )
        

    ############
        
    def testChipIds(self):

        self.images[-1].cat['IMAFLAGS_ISO'][:] = 16*numpy.ones(self.nObjs)

        self.images[-2].cat['FLUX_APER'][:] = 2*numpy.ones(self.nObjs)
        self.images[-2].cat['IMAFLAGS_ISO'][:] = 2*numpy.ones(self.nObjs)
        
        combinedFluxs = measureUnstackedPhotometry(self.images)
         
        self.assertEqual(len(combinedFluxs.keys()), 2)
        self.assertTrue( 1 in combinedFluxs.keys() )
        self.assertTrue( 2 in combinedFluxs.keys() )

        for i in [1,2]:
            flux, fluxerr = combinedFluxs[i]
            self.assertTrue( (numpy.abs(flux - i) < 1e-8).all() )

    ##############

    def testOutliers(self):

        self.images[-1].cat['FLUX_APER'][:] = 50*numpy.ones(self.nObjs)
        
        combinedFluxs = measureUnstackedPhotometry(self.images)
        chipid, (flux, fluxerr) = combinedFluxs.popitem()

        self.assertTrue( (numpy.abs(flux - 1) < 1e-8).all() )
        self.assertTrue( (numpy.abs(fluxerr - 1./math.sqrt(self.nImages-1)) < 1e-8).all() )

    ##############

    def testFluxerr_Area(self):

        for image in self.images:
            image.rms = 1./__resampling_sigma_scaling__
            image.apers = numpy.sqrt(4/numpy.pi)

        combinedFluxs = measureUnstackedPhotometry(self.images)
        chipid, (flux, fluxerr) = combinedFluxs.popitem()

        self.assertTrue( (numpy.abs(flux - 1) < 1e-8).all() )
        self.assertTrue( (numpy.abs(fluxerr - numpy.sqrt(2./self.nImages)) < 1e-5).all() )

    ###############

    def testFluxScale(self):

        inputFluxscales = numpy.ones(self.nImages)
        inputFluxscales[:self.nImages/2] = .5
        inputFluxscales[self.nImages/2:] = 1.5

        for image, fluxscale in zip(self.images, inputFluxscales):
            
            image.cat['FLUX_APER'][:] = image.cat['FLUX_APER']*fluxscale

        combinedFluxs = measureUnstackedPhotometry(self.images, 
                                                   fluxscale = True)
        chipid, (flux, fluxerr) = combinedFluxs.popitem()

        flux = flux - flux[0]

        self.assertTrue( (numpy.abs( flux ) < 1e-8).all() )
    
    ################

    def testFluxKey(self):

        self.images = []
        for i in xrange(self.nImages):
            fluxs = numpy.ones(self.nObjs)
            fluxerrs = numpy.ones_like(fluxs)
            flags = numpy.zeros_like(fluxs)
            imaflags = numpy.ones_like(fluxs)
            BackGr = numpy.zeros_like(fluxs)
            MaxVal = 0.1*numpy.ones_like(fluxs)
            NPIX = numpy.zeros_like(fluxs)
            
            cols = []
            cols.append(pyfits.Column(name='FLUX_APER', format = 'E', array = fluxs))
            cols.append(pyfits.Column(name='FLUXERR_APER', format = 'E', array = fluxs))
            cols.append(pyfits.Column(name='FLUX_ISO', format = 'E', array = fluxs))
            cols.append(pyfits.Column(name='FLUXERR_ISO', format = 'E', array = fluxs))
            cols.append(pyfits.Column(name='Flag', format = 'J', array = flags))
            cols.append(pyfits.Column(name='IMAFLAGS_ISO', format = 'J', array = imaflags))
            cols.append(pyfits.Column(name='BackGr', format = 'E', array = BackGr))
            cols.append(pyfits.Column(name='MaxVal', format = 'E', array = MaxVal))
            cols.append(pyfits.Column(name='NPIX', format = 'E', array = NPIX))
            cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(cols))
            self.images.append(Image(cat = cat, rms = 0., apers = numpy.ones(1), gain = 1.))


        combinedFluxs = measureUnstackedPhotometry(self.images, fluxkey = 'FLUX_APER')
        chipid, (flux, fluxerr) = combinedFluxs.popitem()

        self.assertEqual(chipid, 1)
        self.assertEqual(len(flux), self.nObjs)
        self.assertEqual(len(fluxerr), self.nObjs)
        self.assertTrue( (numpy.abs(flux - 1) < 1e-8).all() )
        self.assertTrue( (numpy.abs(fluxerr - 1./math.sqrt(self.nImages)) < 1e-8).all() )


    ####################


        
        

###########################

    
class TestUnstackedPhotometry_vector(unittest.TestCase):

    def setUp(self):
        self.nImages = 5
        self.nApers = 4
        self.nObjs = 200

        self.images = []
        for i in xrange(self.nImages):
            fluxs = numpy.ones((self.nObjs, self.nApers))
            fluxerrs = numpy.ones_like(fluxs)

            flags = numpy.zeros(self.nObjs)
            imaflags = numpy.ones_like(flags)
            BackGr = numpy.zeros_like(flags)
            MaxVal = 0.1*numpy.ones_like(flags)
            NPIX = numpy.zeros(self.nObjs)
            
            cols = []
            cols.append(pyfits.Column(name='FLUX_APER', 
                                      format = '%dE' % self.nApers, 
                                      array = fluxs))
            cols.append(pyfits.Column(name='FLUXERR_APER', 
                                      format = '%dE' % self.nApers, 
                                      array = fluxs))
            cols.append(pyfits.Column(name='Flag', format = 'J', array = flags))
            cols.append(pyfits.Column(name='IMAFLAGS_ISO', format = 'J', array = imaflags))
            cols.append(pyfits.Column(name='BackGr', format = 'E', array = BackGr))
            cols.append(pyfits.Column(name='MaxVal', format = 'E', array = MaxVal))
            cols.append(pyfits.Column(name='NPIX', format = 'E', array = NPIX))
            cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(cols))
            self.images.append(Image(cat = cat, rms = 0, apers= numpy.ones(self.nApers), gain = 1.))
        

    ############


    def testSimple(self):
        
        combinedFluxs = measureUnstackedPhotometry(self.images)
        chipid, (flux, fluxerr) = combinedFluxs.popitem()

        self.assertEqual(chipid, 1)
        self.assertEqual(flux.shape, (self.nObjs, self.nApers))
        self.assertEqual(fluxerr.shape, (self.nObjs, self.nApers))
        self.assertTrue( (numpy.abs(flux - 1) < 1e-8).all() )
        self.assertTrue( (numpy.abs(fluxerr - 1./math.sqrt(self.nImages)) < 1e-8).all() )

    ###########

    def testFluxs(self):

        expectedFluxs = 10**(-.4*numpy.random.uniform(-9,-2, (self.nObjs, self.nApers)))

        for image in self.images:
            catflux = image.cat['FLUX_APER']
            image.cat['FLUX_APER'][:,:] = expectedFluxs + 0.05*numpy.random.standard_normal((self.nObjs, self.nApers))
            
        combinedFluxs = measureUnstackedPhotometry(self.images)
        chipid, (flux, fluxerr) = combinedFluxs.popitem()

        self.assertTrue( (numpy.abs(flux - expectedFluxs) < 1e-1).all() )

    ############

    def testCuts(self):

        self.images[-1].cat['MaxVal'][:] = 1e7*numpy.ones(self.nObjs)
        self.images[-1].cat['FLUX_APER'][:] = 1e7*numpy.ones((self.nObjs, self.nApers))

        combinedFluxs = measureUnstackedPhotometry(self.images)
        chipid, (flux, fluxerr) = combinedFluxs.popitem()

        self.assertTrue( (numpy.abs(flux - 1) < 1e-8).all() )
        self.assertTrue( (numpy.abs(fluxerr - 1./math.sqrt(self.nImages - 1)) < 1e-8).all() )

    ############
        
    def testChipIds(self):

        self.images[-1].cat['IMAFLAGS_ISO'][:] = 16*numpy.ones(self.nObjs)

        self.images[-2].cat['FLUX_APER'][:,:] = 2*numpy.ones((self.nObjs, self.nApers))
        self.images[-2].cat['IMAFLAGS_ISO'][:] = 2*numpy.ones(self.nObjs)
        
        combinedFluxs = measureUnstackedPhotometry(self.images)
        
        self.assertEqual(len(combinedFluxs.keys()), 2)
        self.assertTrue( 1 in combinedFluxs.keys() )
        self.assertTrue( 2 in combinedFluxs.keys() )

        for i in [1,2]:
            flux, fluxerr = combinedFluxs[i]
            self.assertTrue( (numpy.abs(flux - i) < 1e-8).all() )


    ##############

    def testOutliers(self):

        self.images[-1].cat['FLUX_APER'][:,:] = 40*numpy.ones((self.nObjs, self.nApers))
        
        combinedFluxs = measureUnstackedPhotometry(self.images)
        chipid, (flux, fluxerr) = combinedFluxs.popitem()

        self.assertTrue( (numpy.abs(flux - 1) < 1e-8).all() )
        self.assertTrue( (numpy.abs(fluxerr - 1./math.sqrt(self.nImages-1)) < 1e-8).all() )

    ##############

    def testFluxerr_Area(self):

        for image in self.images:
            image.rms = 1./__resampling_sigma_scaling__
            image.apers = numpy.ones(self.nApers)*numpy.sqrt(4/numpy.pi)

        combinedFluxs = measureUnstackedPhotometry(self.images)
        chipid, (flux, fluxerr) = combinedFluxs.popitem()

        self.assertTrue( (numpy.abs(flux - 1) < 1e-8).all() )
        self.assertTrue( (numpy.abs(fluxerr - numpy.sqrt(2./self.nImages)) < 1e-5).all() )

    ###############

    def testFluxScale(self):

        inputFluxscales = numpy.ones(self.nImages)
        inputFluxscales[:self.nImages/2] = .5
        inputFluxscales[self.nImages/2:] = 1.5

        for image, fluxscale in zip(self.images, inputFluxscales):
            
            image.cat['FLUX_APER'][:,:] = image.cat['FLUX_APER']*fluxscale

        combinedFluxs = measureUnstackedPhotometry(self.images, 
                                                   fluxscale = True)
        chipid, (flux, fluxerr) = combinedFluxs.popitem()


        flux = flux - flux[0]

        self.assertTrue( (numpy.abs( flux ) < 1e-8).all() )

    
        
########################

def fluxErr(flux, areanoise, gain):

    return numpy.sqrt(flux/gain + areanoise)

############

class TestFluxScale(unittest.TestCase):

    def setUp(self):

        self.nObjs = 10000
        self.nImages = 6
        self.areanoise = 1.5
        self.gain=900

        self.object_TargetFluxs = 10**(-.4*numpy.random.uniform(-9,-3,self.nObjs))
        self.object_FluxErrs = fluxErr(self.object_TargetFluxs, self.areanoise,
                                       self.gain)

        self.Observed_Fluxs = numpy.zeros((self.nObjs, self.nImages))
        for i in xrange(self.nObjs):
            self.Observed_Fluxs[i,:] = numpy.random.poisson(lam=self.object_TargetFluxs[i], size=self.nImages)


        self.Observed_FluxErrs = fluxErr(self.Observed_Fluxs, 
                                         self.areanoise, self.gain)

        self.mag_err = 1.0857*self.Observed_FluxErrs / self.Observed_Fluxs
        
        self.mag_aper = -2.5*numpy.log10(self.Observed_Fluxs) + 27        

        self.mask = numpy.ones_like(self.Observed_Fluxs)


    ##################
        

    def testMeasureFluxScaling_nooffset(self):

        scalings = measureFluxScaling(self.mag_aper, 
                                      self.mag_err, 
                                      self.mask)

        self.assertEquals(len(scalings), self.nImages)
        self.assertTrue( (abs(scalings - 1) < .01).all() )

    #################

    def testMeasureFluxScaling_offset(self):

        inputScalings = numpy.ones(self.nImages)
        inputScalings[:3] = .5
        inputScalings[3:] = 1.5
        magScaling = -2.5*numpy.log10(inputScalings)
        magScaling = magScaling - numpy.mean(magScaling)
        inputScalings = 10**(-.4*magScaling)

        measuredFlux = inputScalings*self.Observed_Fluxs
        mag_aper = -2.5*numpy.log10(measuredFlux) + 27
        mag_err = 1.0857*fluxErr(measuredFlux, self.areanoise, self.gain) / measuredFlux


        
        scalings = measureFluxScaling(mag_aper, mag_err, self.mask)

        self.assertEquals(len(scalings), self.nImages)

        scaledFluxs = measuredFlux * scalings
        for i in xrange(self.nImages):
            index = self.nImages - i - 1
            scaledFluxs[:,index] = scaledFluxs[:,index] - scaledFluxs[:,0]


    ###################

    def testMeasureFluxScaling_offset_simple(self):

        inputScalings = numpy.ones(self.nImages)
        inputScalings[:3] = .5
        inputScalings[3:] = 1.5

        measuredMags = numpy.ones((self.nObjs, self.nImages))
        measuredErr = .1*numpy.ones_like(measuredMags)
        for i in xrange(self.nImages):
            measuredMags[:,i] = - 2.5*numpy.log10(inputScalings[i])

        
        scalings = measureFluxScaling(measuredMags, measuredErr, self.mask)


        measuredFluxs = 10**(-.4*measuredMags)
        measuredFluxs = measuredFluxs * scalings

        offset = measuredFluxs[0,0]

        measuredFluxs = measuredFluxs - offset


        self.assertTrue( (numpy.abs(measuredFluxs) < .1).all() )

    ###################

    def testHandleBadMags(self):

        expectedMags = numpy.zeros(self.nObjs)
        expectedMagerrs = .1*numpy.ones(self.nObjs)

        inputScalings = numpy.ones(self.nImages)

        measuredMags = numpy.ones((self.nObjs, self.nImages))
        measuredErr = .1*numpy.ones_like(measuredMags)
        for i in xrange(self.nImages):
            measuredMags[:,i] = expectedMags - 2.5*numpy.log10(inputScalings[i])

        measuredMags[-10:,3] = __bad_mag__

        
        scalings = measureFluxScaling(measuredMags, measuredErr, self.mask)

        measuredFluxs = 10**(-.4*measuredMags)
        scaledFluxs = measuredFluxs*scalings
        scaledFluxs = scaledFluxs - scaledFluxs[0,0]

        self.assertTrue( (numpy.abs(scaledFluxs[measuredMags != __bad_mag__] ) < 0.1).all() )

    ########################

    def testSingleObservations(self):

        measuredMags = numpy.ones((self.nObjs, self.nImages))
        measuredErr = .1*numpy.ones_like(measuredMags)
        mask = numpy.zeros_like(measuredMags)
        for i in xrange(self.nObjs):
            mask[i, i % self.nImages ] = 1

        scalings = measureFluxScaling(measuredMags, measuredErr, mask)

        self.assertTrue( (numpy.abs(scalings - 1) < 1e-2).all() )

    ######################


        
        
    
###############

class TestFluxScale_vector(unittest.TestCase):

    def setUp(self):

        self.nObjs = 10000
        self.nImages = 6
        self.nApers = 4
        self.mask = numpy.ones((self.nObjs, self.nApers, self.nImages))

    ##################
        


    def testMeasureFluxScaling_offset_simple(self):

        expectedMags = numpy.zeros((self.nObjs, self.nApers))
        expectedMagerrs = .1*numpy.ones((self.nObjs, self.nApers))

        inputScalings = numpy.ones(self.nImages)
        inputScalings[:3] = .5
        inputScalings[3:] = 1.5

        measuredMags = numpy.ones((self.nObjs, self.nApers, self.nImages))
        measuredErr = .1*numpy.ones_like(measuredMags)
        for i in xrange(self.nImages):
            measuredMags[:,:,i] = expectedMags - 2.5*numpy.log10(inputScalings[i])

        
        scalings = measureFluxScaling(measuredMags, measuredErr, self.mask)


        measuredFluxs = 10**(-.4*measuredMags)
        measuredFluxs = measuredFluxs * scalings
        for i in xrange(self.nImages):
            index  = self.nImages - i - 1
            measuredFluxs[:,:,index] = measuredFluxs[:,:,index] - measuredFluxs[:,:,0]


        self.assertTrue( (numpy.abs(measuredFluxs) < .1).all() )

    
###############

class TestCombineFluxs(unittest.TestCase):

#    def testStackFluxs_scalar(self):
#
#        fluxs = [ i*numpy.ones(10) for i in xrange(6) ]
#        expected = numpy.column_stack(fluxs)
#        stackedFlux = _stackFluxs(fluxs)
#        self.assertEquals(stackedFlux.shape, expected.shape)
#        for i in xrange(6):
#            self.assertTrue((stackedFlux[i] == expected).all())
#        
#
#    #################
#
#    def testStackFluxs_vector(self):
#
#        fluxs=[i*numpy.ones((10,3)) for i in xrange(6)]
#        stackedFlux = _stackFluxs(fluxs)
#        self.assertEquals(stackedFlux.shape, (10,3,6))
#        for i in xrange(6):
#            self.assertTrue((stackedFlux[:,:,i] == i*numpy.ones((10,3))).all())
#
#    #################

    def testWeightedAverage(self):

        fluxs = numpy.ones((30,6))
        for i in xrange(30):
            fluxs[i,:] = i
        errs = numpy.ones_like(fluxs)
        mask = numpy.ones((30,6))

        flux, err = _weightedAverage(fluxs,errs,mask)
        self.assertEquals(flux.shape, (30,))
        self.assertEquals(err.shape, (30,))
        self.assertTrue((flux == numpy.array(xrange(30))).all())
        self.assertTrue((abs(err -numpy.ones(30)/numpy.sqrt(6)) < 1e-8).all())

    #####################

    def testWeightedAverage_mask(self):

        fluxs = numpy.ones((30,6))
        for i in xrange(30):
            fluxs[i,:] = i
        fluxs[:,2] = 1e5
        errs = numpy.ones_like(fluxs)
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

    def testWeightedAverage_allbad(self):

        fluxs = numpy.ones((30,6))
        errs = .1*numpy.ones((30,6))
        mask = numpy.zeros_like(fluxs)

        flux, err = _weightedAverage(fluxs, errs, mask)

        self.assertTrue( (flux == __bad_flux__).all() )
        self.assertTrue( (err == __bad_flux__).all() )

    ###########################

    def testStatCombineFluxs(self):

        fluxs = numpy.ones((10,5))
        errs = .1*numpy.ones_like(fluxs)
        mask = numpy.ones_like(fluxs)

        fluxs[:,-1] = 1.1
        
        flux, err = statCombineFluxs(fluxs, errs, mask)

        expectedFlux = 1.02
        expectedErr = .1/numpy.sqrt(5)

        self.assertTrue((expectedFlux == flux).all())
        self.assertTrue((expectedErr == err).all())
        
    ##########################

    def testStatCombineFluxs_5sigmaReject(self):

        fluxs = numpy.ones((10,5))
        errs = .1*numpy.ones_like(fluxs)
        mask = numpy.ones_like(fluxs)

        fluxs[:,-1] = 2
        
        flux, err = statCombineFluxs(fluxs, errs, mask)

        expectedFlux = 1
        expectedErr = .1/numpy.sqrt(4)

        self.assertTrue((expectedFlux == flux).all())
        self.assertTrue((expectedErr == err).all())

    ###########################

    def testBadFlux(self):

        self.assertTrue(__bad_flux__ < 0)

    ############################

    def testStatCombineFluxs_NullingOutliers(self):
 
        fluxs = numpy.ones((3,5))
        fluxs[:,2] = 1e5
        errs = 0.1*numpy.ones_like(fluxs)
        mask = numpy.ones_like(fluxs)

        flux, err = statCombineFluxs(fluxs,errs,mask)

        self.assertTrue((flux == 1).all())
        self.assertTrue((err == (0.1/numpy.sqrt(4))).all())

    ###############################

    def testStatCombineFluxs_NullingAndLegitOutliers(self):

        fluxs = numpy.ones((3,6))
        fluxs[:,2] = 1.1
        fluxs[:,3] = 2
        fluxs[1:,-1] = 1e5
        errs = 0.1*numpy.ones_like(fluxs)
        mask = numpy.ones_like(fluxs)

        flux, err = statCombineFluxs(fluxs,errs,mask)

        expectedFlux = 1.025*numpy.ones(3)
        expectedFlux[0] = 1.02
        
        expectedErr = (0.1/numpy.sqrt(4)) * numpy.ones(3)
        expectedErr[0] = 0.1/ numpy.sqrt(5)

        self.assertTrue((numpy.abs(flux - expectedFlux) < 1e-5).all())
        self.assertTrue((numpy.abs(err - expectedErr) < 1e-5).all())


    ###############################

    def testStatCombineFluxs_NullingAndLegitOutliers_Vector(self):

        fluxs = numpy.ones((3,5,6))
        fluxs[:,:,2] = 1.1
        fluxs[:,:,3] = 2
        fluxs[1:,:,-1] = 1e5
        errs = 0.1*numpy.ones_like(fluxs)
        mask = numpy.ones_like(fluxs)

        flux, err = statCombineFluxs(fluxs,errs,mask)

        self.assertEquals(flux.shape, (3,5))
        self.assertEquals(err.shape, (3,5))

        expectedFlux = 1.025*numpy.ones((3,5))
        expectedFlux[0,:] = 1.02
        
        expectedErr = (0.1/numpy.sqrt(4)) * numpy.ones((3,5))
        expectedErr[0,:] = 0.1/ numpy.sqrt(5)
        

        self.assertTrue((numpy.abs(flux - expectedFlux) < 1e-5).all())
        self.assertTrue((numpy.abs(err - expectedErr) < 1e-5).all())
        
        
        
    ###############################

    def testMedian_Simple(self):

        fluxs = numpy.ones((3,5))
        fluxs[:,2] = 1e5
        errs = 0.1*numpy.ones_like(fluxs)
        mask = numpy.ones_like(fluxs)

        flux = _median(fluxs, mask)

        self.assertTrue((flux == 1).all())

    #################################

    def testMedian_Mask(self):

        fluxs = numpy.vstack(10*[numpy.arange(6)])
        fluxs[:,2] = 1e5
        errs = 0.1*numpy.ones_like(fluxs)
        mask = numpy.ones_like(fluxs)
        mask[5:,3] = 0

        flux = _median(fluxs, mask)
        
        expected = 3.5*numpy.ones(10)
        expected[5:] = 4

        self.assertTrue((flux == expected).all())


    #################################

    def testMedian_vectorFlux(self):

        fluxImages = []
        for i in xrange(6):
            fluxImages.append(i*numpy.ones((10,3)))
        fluxs = _stackFluxs(fluxImages)

        fluxs[:,:,2] = 1e5
        mask = numpy.ones_like(fluxs)
        
        flux = _median(fluxs, mask)

        expected = 3.5*numpy.ones((10,3))

        self.assertTrue((flux == expected).all())
        


##############################

class TestCombineCatalogs(unittest.TestCase):

    ################

    def testCombineCats(self):
        
        normkeys = 'FLUX_APER FLUXERR_APER MAG_APER MAGERR_APER BLANK1 BLANK2'.split()
        mastercols = [pyfits.Column(name = k, 
                                    format = 'E', 
                                    array = numpy.ones(30)) \
                          for k in normkeys]
        mastercols[0] = pyfits.Column(name = 'FLUX_APER', 
                                    format = 'E', 
                                    array = numpy.random.standard_normal(30))
        zerokeys = 'Flag MaxVal BackGr NPIX'.split()
        for key in zerokeys:
            mastercols.append(pyfits.Column(name = key, 
                                            format = 'E', 
                                            array = numpy.zeros(30)))
        onekeys = 'IMAFLAGS_ISO'.split()
        for key in onekeys:
            mastercols.append(pyfits.Column(name = key,
                                            format = 'J',
                                            array = numpy.ones(30)))


        
        cats = [ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(mastercols)))]

        for i in xrange(5):
            cols = [pyfits.Column(name = k, 
                                  format = 'E', 
                                  array = numpy.random.standard_normal(30)) \
                        for k in normkeys]
        
            for key in zerokeys:
                cols.append(pyfits.Column(name = key, 
                                          format = 'E', 
                                          array = numpy.zeros(30)))
            for key in onekeys:
                cols.append(pyfits.Column(name = key,
                                          format = 'E',
                                          array = numpy.ones(30)))


            cats.append(ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))))

        images = [ Image(cat, rms = 0, apers = numpy.ones(1), gain = 1) for cat in cats ]

        keys = normkeys[2:] + zerokeys + onekeys

        combinedcat = combineCats(images)

        self.assertEqual(type(combinedcat), type(cats[0]))
        for key in keys:
            self.assertTrue(key in combinedcat.keys())
        self.assertTrue((combinedcat['BLANK1'] == 1).all())
        self.assertTrue((combinedcat['BLANK2'] == 1).all())

        self.assertTrue((combinedcat['FLUX_APER-1'] != 1).all())
        self.assertTrue((combinedcat['FLUXERR_APER-1'] != 1).all())

        mags, magerrs = calcMags(combinedcat['FLUX_APER-1'], 
                              combinedcat['FLUXERR_APER-1'])


        self.assertTrue( (numpy.abs(combinedcat['MAG_APER-1'] - mags) < 1e-5).all() )
        self.assertTrue( (numpy.abs(combinedcat['MAGERR_APER-1'] - magerrs) < 1e-5).all())


    #######################################


    def testCombineCats_doubleprecision(self):

        doublekeys = 'ALPHA_J2000 DELTA_J2000'.split()
        normkeys = 'FLUX_APER FLUXERR_APER'.split()
        zerokeys = 'Flag MaxVal BackGr NPIX'.split()
        onekeys = 'IMAFLAGS_ISO'.split()

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
            for key in onekeys:
                cols.append(pyfits.Column(name = key,
                                          format = 'D',
                                          array = numpy.ones(30)))


            cats.append(ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))))


        keys = normkeys + zerokeys + doublekeys + onekeys

        images = [ Image(cat, rms=0, apers=numpy.ones(1), gain=1) for cat in cats ]
        
        combinedcat = combineCats(images)

        self.assertEquals(cats[0]['ALPHA_J2000'].dtype, combinedcat['ALPHA_J2000'].dtype)
        self.assertEquals(cats[0]['DELTA_J2000'].dtype, combinedcat['DELTA_J2000'].dtype)
        self.assertTrue((abs(cats[0]['ALPHA_J2000'] - combinedcat['ALPHA_J2000']) < 1e-16).all())
        self.assertTrue((abs(cats[0]['DELTA_J2000'] - combinedcat['DELTA_J2000']) < 1e-16).all())


    ##############################

    def testCombineCats_vector(self):

        normkeys = 'FLUX_APER FLUXERR_APER'.split()
        zerokeys = 'Flag MaxVal BackGr NPIX'.split()
        onekeys = 'IMAFLAGS_ISO'.split()

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

            for key in onekeys:
                cols.append(pyfits.Column(name = key,
                                          format = 'J',
                                          array = numpy.ones(30)))


            cats.append(ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))))


        keys = zerokeys + onekeys

        images = [ Image(cat, rms=0, apers=numpy.ones(1), gain= 1) for cat in cats ]
        
        combinedcat = combineCats(images)

        self.assertEqual(type(combinedcat), type(cats[0]))
        for key in keys:
            self.assertTrue(key in combinedcat.keys())
        self.assertEqual(combinedcat['FLUX_APER-1'].shape, (30,5))
        self.assertEqual(combinedcat['FLUXERR_APER-1'].shape, (30,5))
        self.assertEqual(combinedcat['MAG_APER-1'].shape, (30,5))
        self.assertEqual(combinedcat['MAGERR_APER-1'].shape, (30,5))

    ###################################

    def testCombineCats_multichip(self):
        
        zerokeys = 'Flag MaxVal BackGr NPIX'.split()

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


            flags[25:] = 4

            flux = numpy.ones(30)
            flux[flags==2] = 2
            flux[flags==4] = 4




            
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

        images = [ Image(cat, rms=0, apers=numpy.ones(1), gain= 1) for cat in cats ]
        
        combinedcat = combineCats(images)

        self.assertEqual(type(combinedcat), type(cats[0]))
        for key in keys:
            self.assertTrue(key in combinedcat.keys())
        self.assertEqual(combinedcat['FLUX_APER-1'].shape, (30,))
        self.assertEqual(combinedcat['FLUXERR_APER-1'].shape, (30,))
        self.assertTrue((combinedcat['FLUX_APER-1'][:25] == 1).all())
        self.assertTrue((combinedcat['FLUX_APER-1'][25:] == __bad_flux__).all())

        self.assertEqual(combinedcat['MAG_APER-1'].shape, (30,))
        self.assertEqual(combinedcat['MAGERR_APER-1'].shape, (30,))
        self.assertTrue((combinedcat['MAG_APER-1'][:25] == 0).all())
        self.assertTrue((combinedcat['MAG_APER-1'][25:] == __bad_mag__).all())

        self.assertEqual(combinedcat['FLUX_APER-2'].shape, (30,))
        self.assertEqual(combinedcat['FLUXERR_APER-2'].shape, (30,))
        self.assertTrue((combinedcat['FLUX_APER-2'][:25] == 2).all())
        self.assertTrue((combinedcat['FLUX_APER-2'][25:] == __bad_flux__).all())

        self.assertEqual(combinedcat['MAG_APER-2'].shape, (30,))
        self.assertEqual(combinedcat['MAGERR_APER-2'].shape, (30,))
        self.assertTrue((combinedcat['MAG_APER-2'][:25] == -2.5*numpy.log10(2)).all())
        self.assertTrue((combinedcat['MAG_APER-2'][25:] == __bad_mag__).all())

        self.assertEqual(combinedcat['FLUX_APER-4'].shape, (30,))
        self.assertEqual(combinedcat['FLUXERR_APER-4'].shape, (30,))
        self.assertTrue((combinedcat['FLUX_APER-4'][25:] == 4).all())
        self.assertTrue((combinedcat['FLUX_APER-4'][:25] == __bad_flux__).all())

        self.assertEqual(combinedcat['MAG_APER-4'].shape, (30,))
        self.assertEqual(combinedcat['MAGERR_APER-4'].shape, (30,))
        self.assertTrue((combinedcat['MAG_APER-4'][25:] == -2.5*numpy.log10(4)).all())
        self.assertTrue((combinedcat['MAG_APER-4'][:25] == __bad_mag__).all())



    ######################

    def testCombineCats_instrum(self):

        normkeys = 'FLUX_APER FLUXERR_APER'.split()
        zerokeys = 'Flag MaxVal BackGr NPIX'.split()

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

        images = [ Image(cat, rms=0, apers=numpy.ones(1),  gain=1) for cat in cats ]
        
        combinedcat = combineCats(images, instrum='SUBARU-10_1')

        self.assertEqual(type(combinedcat), type(cats[0]))
        for key in keys:
            self.assertTrue(key in combinedcat.keys())
        self.assertEqual(combinedcat['FLUX_APER-SUBARU-10_1-1'].shape, (30,5))
        self.assertEqual(combinedcat['FLUXERR_APER-SUBARU-10_1-1'].shape, (30,5))
        self.assertEqual(combinedcat['MAG_APER-SUBARU-10_1-1'].shape, (30,5))
        self.assertEqual(combinedcat['MAGERR_APER-SUBARU-10_1-1'].shape, (30,5))

    ##############

    def testCombineCats_mastercat(self):

        normkeys = 'FLUX_APER FLUXERR_APER'.split()
        zerokeys = 'Flag BLANK1 MaxVal BackGr NPIX'.split()


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
        mastercols.append(pyfits.Column(name = 'BLANK1',
                                        format = 'E',
                                        array = numpy.ones(30)))
        mastercat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(mastercols)))


        keys = 'MAG_APER BLANK1'.split()

        images = [ Image(cat, rms=0, apers=numpy.ones(5), gain =  1) for cat in cats ]
        
        combinedcat = combineCats(images,
                                  mastercat = mastercat)
        
        self.assertEqual(type(combinedcat), type(cats[0]))
        for key in keys:
            self.assertTrue(key in combinedcat.keys())
        self.assertTrue((combinedcat['MAG_APER'] == 1).all())
        self.assertTrue((combinedcat['BLANK1'] == 1).all())                  
        self.assertEqual(combinedcat['FLUX_APER-1'].shape, (30,5))
        self.assertEqual(combinedcat['FLUXERR_APER-1'].shape, (30,5))
        self.assertEqual(combinedcat['MAG_APER-1'].shape, (30,5))
        self.assertEqual(combinedcat['MAGERR_APER-1'].shape, (30,5))


        ####################

    def testFluxScale(self):

        normkeys = []
        zerokeys = 'Flag MaxVal BackGr NPIX'.split()
        onekeys = 'FLUX_APER FLUXERR_APER IMAFLAGS_ISO'.split()

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

            for key in onekeys:
                cols.append(pyfits.Column(name = key,
                                          format = 'J',
                                          array = numpy.ones(30)))


            cats.append(ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))))

        cats[0]['FLUX_APER'][:] = .5*numpy.ones(30)
        cats[-1]['FLUX_APER'][:] = 1.5*numpy.ones(30)

        keys = zerokeys + onekeys

        images = [ Image(cat, rms=0, apers=numpy.ones(1), gain=1) for cat in cats ]
        
        combinedcat = combineCats(images, fluxscale = True)

        zeropoint = numpy.mean(combinedcat['FLUX_APER-1'])
        scaledFlux = combinedcat['FLUX_APER-1'] / zeropoint
        self.assertTrue( (scaledFlux == 1).all() )
        
        #verify outlier rejection not triggered
        error1rejected = 1./numpy.sqrt(4)
        error2rejected = 1./numpy.sqrt(3)

        self.assertTrue ( (combinedcat['FLUXERR_APER-1'] != error1rejected).any() )
        self.assertTrue ( (combinedcat['FLUXERR_APER-1'] != error2rejected).any() )


        

        


##################################################

def test():

    testcases = [TestComponents, TestFluxScale, TestUnstackedPhotometry, TestCombineFluxs, TestUnstackedPhotometry_vector, TestCombineCatalogs, TestImage]
    

    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)



#####################################################
# COMMAND LINE EXECUTABLE
#####################################################


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        test()
    else:
        main()
