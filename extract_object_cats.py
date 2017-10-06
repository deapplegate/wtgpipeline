#!/usr/bin/env python
######################
'''
 Creates photometry catalog and associated output for a given exposure and detection image.
 Will convolve images if requested.
 ISO areas of objects are measured from the detection image, or from a premeasured catalog.
 
 Also implements python calls to sextractor and ldacconv
'''
######################


import sys, unittest, os, subprocess, glob, shutil, optparse, difflib
import numpy, astropy, astropy.io.fits as pyfits
import ldac, bashreader

#######################

__cvs_id__ = "$Id: extract_object_cats.py,v 1.10 2010-11-12 20:33:56 dapple Exp $"


#######################
# GLOBAL CONSTANTS
#######################

PROGS = bashreader.parseFile('progs.ini')
PHOTCONF = './photconf'
DATACONF = PROGS['dataconf']
DETECT_OBJS_CONFIG = './photconf/detect.objs.conf.sex'
SMOOTH_IMAGE_CONFIG = './photconf/smooth.image.conf.sex'
DEFAULT_CONV = '%s/default.conv' % DATACONF

os.environ['DATACONF'] = DATACONF



#######################
# USER FUNCTIONS
#######################


def sextractor(image, detect = None, config = None, 
               callMethod = subprocess.check_call,
               **keywords):
    '''
    Calls the program sextractor from python.
    @param image (str - filename) image to measure photometry from
    @param detect (str - filename) detection image to use
    @param config (str - filename) configuration file to use
    @param callMethod (function) for debugging purposes -- function that makes the system call

    All keywords are appended to the command line in source extractor format. Values that are lists are 
       converted to comma seperated lists in the system call.
    '''

    configFlag = ''
    if config:
        configFlag = '-c %s' % config

    imageFlag = image
    if detect:
        imageFlag = '%s,%s' % (detect,image)
    
    command = '%s %s %s' % (PROGS['p_sex'], configFlag, imageFlag)


    isiterable = lambda obj: hasattr(obj,'__iter__')

    params = sorted(keywords.keys())
    for param in params:
        val = keywords[param]
        if isiterable(val):
            val=','.join(map(str, val))
        elif isinstance(val, type(True)):
            if val:
                val = 'Y'
            else:
                val = 'N'
        else:
            val = str(val)
        command = command + ' -%s %s' % (param.upper(), val)

    callMethod(command.split())

    return command

######################

def ldacconv(catalog, output, filter = '1', callMethod = subprocess.check_call):
    '''
    Calls ldacconv to convert a catalog to LDAC format
    @param catalog (str - filename) name of catalog to convert
    @param output (str - filename) name of output file
    @param file (str) Name of filter to pass to ldacconv (optional)
    @param callMethod (function) for debugging -- function to make system call
    '''

    command = 'ldacconv -b 1 -c 1 -f %s -i %s -o %s' % (filter, catalog, output)
    
    callMethod(command.split())

#######################

def createConvolutionKernel(orig_seeing, new_seeing, pixscale, output, callMethod = subprocess.check_call):
    '''
    Calls create_gausssmoothing_kernel.py to create a smoothing kernel
    @param orig_seeing (float - arcseconds) the current seeing of the image
    @param new_seeing (float - arcseconds) the desired seeing of the image
    @param pixscale (float - arcseconds / pixel) pixel size in the image
    @param output (str - filename) name for filter
    @param callmethod (function) for debugging -- function to make system call

    seeing values and pixscale in arcseconds
    '''

    if new_seeing <= orig_seeing:
        
        shutil.copy(DEFAULT_CONV, output)

    else:
    
        command = 'python create_gausssmoothing_kernel.py %.3f %.3f %.3f %s' % \
            (orig_seeing, new_seeing, pixscale, output)

        callMethod(command.split())

##########################

def computePixScale(header):
    if header.__contains__('CDELT1'): #adam: new version of pyfits makes you switch from has_key to __contains__
        cdelt1 = header['CDELT1']
        cdelt2 = header['CDELT2']
    else:
        cdelt1 = header['CD1_1']
        cdelt2 = header['CD2_2']


    pixscale = (abs(float(cdelt1)) + abs(float(cdelt2))) / (2.0) * 3600.0
    
    return pixscale



##########################

def updatePhotInfo(catfile, table = 'PHOTINFO', **keywords):

    if len(keywords) == 0:
        return


    cols = []
    
    photinfo = ldac.openObjectFile(catfile, table)
    new_keys = {}
    if photinfo:

        for key, value in keywords.iteritems():

            if key in photinfo.keys():
                photinfo[key][:] = value
            else:
                new_keys[key] = value

        cols.extend(photinfo.hdu.columns)

    else:
        
        new_keys = keywords


    for key, value in new_keys.iteritems():
        cols.append(pyfits.Column(name = key, format = findPyfitsType(value), array = [value]))

    photinfo = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
    photinfo.header['EXTNAME']= table

    hdulist = pyfits.open(catfile)
    newhdulist = [pyfits.PrimaryHDU(), photinfo]
    for hdu in hdulist:
        try:
            if hdu.header['EXTNAME'] != table:
                newhdulist.append(hdu)
        except KeyError:
            pass

    pyfits.HDUList(newhdulist).writeto(catfile, overwrite='True')
            

#######################

_dumpFile = lambda file: ''.join(open(file).readlines())

def extractObjectCats(detectImage, detectWeight, 
                      photImage, photWeight, photFlag, 
                      output, fwhm = None, new_fwhm = None,
                      measureArea = True,
                      callMethod = subprocess.check_call):

    '''
    Creates a photometry catalog of objects in an image.
    Will use detectImage to determine aperatures on photImage, and will properly measure aperture sizes in output catalog. Smoothing, if requested, will also be done before catalog creation.

    @param detectImage (str - filename) detection image to define apertures
    @param detectWeight (str - filename) detection weight image
    @param photImage (str - filename) image to measure photometry from
    @param photWeight (str - filename) weight image for photometry
    @param photFlag (str - filename) flag image for photometry
    @param output (str - filename) name of output catalog
    @param fwhm (float - arcseconds) current seeing in photImage
    @param new_fwhm (float - arcseconds) desired seeing in photImage before photometry measurements
    @param measureArea (bool/str - filename) either True/False to measure area from the detection image, or a catalog to draw aperature sizes from -- should be measured from detectImage
    @param callMethod (function) for debugging -- function to make system call
    '''


    photbase = os.path.splitext(output)[0]
    noobjsImage = '%s.noobjs.fits' % photbase

    photinfo = {}

    header = pyfits.getheader(photImage)

    ######

    doConvolveImage = lambda fwhm, new_fwhm: fwhm is not None and new_fwhm is not None

    if doConvolveImage(fwhm, new_fwhm):
        outputdir = os.path.dirname(output)
        if outputdir == '':
            outputdir = '.'
        outputbase = os.path.splitext(os.path.basename(output))[0]
        filter = '%s/%s.conv' % (outputdir, outputbase)

        pixscale = computePixScale(header)

        createConvolutionKernel(fwhm, new_fwhm, pixscale, filter, callMethod = callMethod)

        filteredImage = '%s.filtered.fits' % photbase
        
        #smoothing call
        sextractor(image = photImage, config = SMOOTH_IMAGE_CONFIG,
                   weight_image = photWeight,
                   flag_image = photFlag,
                   filter_name = filter,
                   checkimage_name = [noobjsImage, filteredImage],
                   callMethod = callMethod)

        #object extraction call
        extract_call = sextractor(detect = detectImage, image = filteredImage, config = DETECT_OBJS_CONFIG,
                                  catalog_name = '%s0' % output,
                                  gain = header['GAIN'],
                                  weight_image = [detectWeight, photWeight],
                                  flag_image = photFlag,
                                  checkimage_type = 'NONE',
                                  callMethod = callMethod)

        photinfo.update({'ORIGINAL_FWHM' : fwhm,
                         'TARGET_FWHM' : new_fwhm,
                         'SMOOTH_FILTER' : filter,
                         'EXTRACTION_CALL' : extract_call,
                         'EXTRACTION_CONFIG' : _dumpFile(DETECT_OBJS_CONFIG)})
        

    
    else:
        
        #object extraction call
        extract_call = sextractor(detect = detectImage, image = photImage, config = DETECT_OBJS_CONFIG,
                                  catalog_name = '%s0' % output,
                                  gain = header['GAIN'],
                                  weight_image = [detectWeight, photWeight],
                                  flag_image = photFlag,
                                  checkimage_name = '%s.noobjs.fits' % photbase,
                                  callMethod = callMethod)

        photinfo.update({'EXTRACTION_CALL' : extract_call,
                         'EXTRACTION_CONFIG' : _dumpFile(DETECT_OBJS_CONFIG)})

    ########

    calcDetectionArea = lambda detectImage, photImage, measureArea: detectImage != photImage and isinstance(measureArea, bool) and measureArea

    if calcDetectionArea(detectImage, photImage, measureArea):
        #measure aperture size from detect image
        detectcat = '%s.detect.cat' % photbase


        extractObjectCats(detectImage = detectImage, detectWeight = detectWeight,
                          photImage = detectImage, photWeight = detectWeight, photFlag = photFlag,
                          output = detectcat,
                          callMethod = callMethod)

        cat = ldac.openObjectFile(detectcat)
        
        area = cat['ISOAREA_DETECT']

        photinfo['DETECT_AREA'] = detectImage

        os.remove(detectcat)


    elif isinstance(measureArea, str):
        #read aperture size from input catalog

        cat = ldac.openObjectFile(measureArea)

        area = cat['ISOAREA_DETECT']

        photinfo['DETECT_AREA'] = measureArea

    else:
        #no need to measure aperture sizes

        cat = ldac.openObjectFile('%s0' % output, 'LDAC_OBJECTS')

        area = cat['ISOAREA_IMAGE']

        photinfo['DETECT_AREA'] = photImage

    #######

    ldacconv('%s0' % output, output, callMethod = callMethod)

    rms = measureRMS('%s.noobjs.fits' % photbase)

    photinfo['BACKGROUND_RMS'] = rms

    photinfo['background_rms_source'] = photImage

    #######

    updatePhotInfo(output, **photinfo)

    hdulist = pyfits.open(output)

    header = hdulist['OBJECTS'].header

    cols = [pyfits.Column(name = 'ISOAREA_DETECT', format = 'E', array = area)]
    cols.extend(hdulist['OBJECTS'].columns)
    data = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols), header = header)

    hdulist['OBJECTS'] = data

    hdulist.writeto(output, overwrite=True)

    os.remove('%s0' % output)
    os.remove('%s.noobjs.fits' % photbase)


########################################
    

def main(argv = sys.argv, toCall = extractObjectCats):

    usage = 'extract_object_cats.py --di FILE --dw FILE --pi FILE --pw FILE --pf FILE -o FILE'

    parser = optparse.OptionParser(usage = usage)
    parser.add_option('--di', '--detect-image', dest='detectImage',
                      help = 'Image to define detection apertures',
                      metavar='FILE')
    parser.add_option('--dw', '--detect-weight', dest='detectWeight',
                      help = 'Weight image for detection image',
                      metavar = 'FILE')

    parser.add_option('--pi', '--phot-image', dest='photImage',
                      help = 'Image to measure photometry from',
                      metavar = 'FILE')
    parser.add_option('--pw', '--phot-weight', dest='photWeight',
                      help = 'Weight image for photometry image',
                      metavar = 'FILE')
    parser.add_option('--pf', '--phot-flag', dest='photFlag',
                      help = 'Flag image for photometry image',
                      metavar = 'FILE')
    
    parser.add_option('-o', '--output', dest='output',
                      help = 'name of output catalog',
                      metavar = 'FILE')

    parser.add_option('--fwhm', dest='fwhm',
                      help = 'Current fwhm of the image',
                      metavar = 'ARCSEC',
                      type = 'float',
                      default = None)
    parser.add_option('--new-fwhm', dest='new_fwhm',
                      help = 'Target fwhm to convolve to', 
                      metavar = 'ARCSEC',
                      type = 'float',
                      default = None)
    parser.add_option('--noarea', dest='measureArea',
                      help = 'Measure area from the photometry image',
                      default = True,
                      action = 'store_false')
    parser.add_option('--areacat', dest='areacat',
                      help = 'Catalog from which to read detection area : Overrides --noarea',
                      metavar = 'FILE',
                      default = None)


    options, args = parser.parse_args(argv)

    if options.detectImage is None or \
            options.detectWeight is None or \
            options.photImage is None or \
            options.photWeight is None or \
            options.photFlag is None or \
            options.output is None:

        parser.error('Need to specify all input images and output file')
    

    if options.areacat is not None:
        options.measureArea = options.areacat


    toCall(detectImage = options.detectImage,
           detectWeight = options.detectWeight,
           photImage = options.photImage,
           photWeight = options.photWeight,
           photFlag = options.photFlag,
           output = options.output,
           fwhm = options.fwhm,
           new_fwhm = options.new_fwhm,
           measureArea = options.measureArea)

########################

def measureRMS(noobjsFile):

    data = pyfits.getdata(noobjsFile)
    
    return float(numpy.std(data[data != 0], dtype=numpy.float128))

#######################

def findPyfitsType(value):

    if type(value) == type(5.6):
        format = 'E'
    elif type(value) == type(5):
        format = 'J'
    elif type(value) == type(numpy.ones(1)):
        format = 'E'
    else:
        value = str(value)
        if len(value) <= 512:
            format = '512A'
        else:
            format = '%dA' % len(value)

    return format


        


##############################################
# TESTING
##############################################

class FakeCall(object):

    def __init__(self):
        self.command = None

    def __call__(self, command):
        self.command = command

#####

class TestSextractor(unittest.TestCase):

    def setUp(self):

        progs = bashreader.parseFile('progs.ini') 

        self.sex_command = progs['p_sex']
    
    ######

    def testBasic(self):
        
        receiver = FakeCall()
        
        image = 'fake.fits'

        sextractor(image, callMethod=receiver)
        
        expected = '%s %s' % (self.sex_command, image)
        
        self.assertEquals(expected.split(), receiver.command)

    #######

    def testConfigFile(self):

        receiver = FakeCall()
        image = 'fake.fits'
        config = 'myconfig.sex'

        sextractor(image, config=config, callMethod=receiver)

        expected = '%s -c %s %s' % (self.sex_command, config, image)

        self.assertEquals(expected.split(), receiver.command)

    ########

    def testOptions(self):

        receiver = FakeCall()
        image = 'fake.fits'
        config = 'myconfig.sex'

        sextractor(image, config=config, catalog_name='mycat.cat', 
                   weight_type = 'MAP_WEIGHT', gain=3.5, callMethod=receiver)

        
        expected = '%s -c %s %s -CATALOG_NAME mycat.cat -GAIN %s -WEIGHT_TYPE MAP_WEIGHT ' % (self.sex_command, config, image, str(3.5))

        self.assertEquals(expected.split(), receiver.command)

    ######

    def testDualImageMode(self):

        receiver = FakeCall()
        detect = 'detect.fits'
        phot = 'phot.fits'
        
        sextractor(phot, detect=detect, callMethod=receiver)

        expected = '%s %s,%s' % (self.sex_command, detect, phot)
        
        self.assertEquals(expected.split(), receiver.command)

    ######

    def testListedOptions(self):

        receiver = FakeCall()
        image = 'fake.fits'

        sextractor(image, GAIN = 3.5, 
                   weights=['detect.weight.fits', 'phot.weight.fits'], 
                   callMethod=receiver)

        
        expected = '%s %s -GAIN %s -WEIGHTS detect.weight.fits,phot.weight.fits' % (self.sex_command, image, str(3.5))

        self.assertEquals(expected.split(), receiver.command)

    #######

    def testBoolOptions(self):

        receiver = FakeCall()
        
        image = 'fake.fits'

        sextractor(image, filter = True, callMethod = receiver)
        expected = '%s %s -FILTER Y' % (self.sex_command, image)
        self.assertEquals(expected.split(), receiver.command)

        sextractor(image, filter = False, callMethod = receiver)
        expected = '%s %s -FILTER N' % (self.sex_command, image)
        self.assertEquals(expected.split(), receiver.command)

    #########

    def testReturnCommandString(self):

        receiver = FakeCall()
        detect = 'detect.fits'
        phot = 'phot.fits'
        
        command = sextractor(phot, detect=detect, callMethod=receiver)

        self.assertEquals(command.split(), receiver.command)
        


        
#############################

class TestLDACConv(unittest.TestCase):

    def testConverts(self):

        receiver = FakeCall()

        ldacconv('mycat.cat0', 'mycat.cat', callMethod = receiver)

        expected = 'ldacconv -b 1 -c 1 -f 1 -i mycat.cat0 -o mycat.cat'
        
        self.assertEquals(expected.split(), receiver.command)

    def testConvertsFilter(self):

        receiver = FakeCall()

        ldacconv('mycat.cat0', 'mycat.cat', filter = 'r', callMethod = receiver)

        expected = 'ldacconv -b 1 -c 1 -f r -i mycat.cat0 -o mycat.cat'
        
        self.assertEquals(expected.split(), receiver.command)
        

    
    

##############################

class Interceptor(object):
    def __init__(self):
        self.commands = []
    def __call__(self, command):
        self.commands.append(command)
        subprocess.check_call(command)

def isObjectExtractionCall(command, image = None):

    if command[0] != PROGS['p_sex']:
        return False

    foundExtract = False
    for i, entry in zip(numpy.arange(len(command)), command):
        if entry == '-c':
            if command[i+1] == DETECT_OBJS_CONFIG:
                foundExtract = True

    if not foundExtract:
        return False

    if image is not None:
        image1, image2 = command[3].split(',')

        return (image2 == image)

    else:
        return True
    


class TestExtract(unittest.TestCase):

    def setUp(self):

        self.size = (500,500)
        self.detectObjLength = 4
        self.photObjLength = 10
        self.gain = 100.
        self.pixscale = 1.1

        middle = numpy.array(self.size)/2.

        self.detectImageFile = 'eoc_test_detect.fits'
        if not os.path.exists(self.detectImageFile):
            image = 0.02*numpy.random.standard_normal(self.size)
            deltaObj = self.detectObjLength / 2.
            image[middle[0]-deltaObj:middle[0]+deltaObj, 
                  middle[1]-deltaObj:middle[1]+deltaObj] = 30
            hdu = pyfits.PrimaryHDU(image)
            hdu.header['gain']= 150.
            hdu.header['PIXSCALE']= self.pixscale
            hdu.header['CD1_1']= self.pixscale / 3600 
            hdu.header['CD2_2']= self.pixscale / 3600 
            hdu.writeto(self.detectImageFile)
        
        self.detectWeightFile = 'eoc_test_detect.weight.fits'
        if not os.path.exists(self.detectWeightFile):
            image = numpy.ones(self.size)
            hdu = pyfits.PrimaryHDU(image)
            hdu.writeto(self.detectWeightFile)

        self.photImageFile = 'eoc_test_phot.fits'
        if not os.path.exists(self.photImageFile):
            image = 0.5*numpy.random.standard_normal(self.size)
            deltaObj = self.photObjLength / 2.
            image[middle[0]-deltaObj:middle[0]+deltaObj, 
                  middle[1]-deltaObj:middle[1]+deltaObj] = 2            
            hdu = pyfits.PrimaryHDU(image)
            hdu.header['gain']= self.gain
            hdu.header['PIXSCALE']= self.pixscale
            hdu.header['CD1_1']= self.pixscale / 3600 
            hdu.header['CD2_2']= self.pixscale / 3600 
            hdu.writeto(self.photImageFile)

        self.photWeightFile = 'eoc_test_phot.weight.fits'
        if not os.path.exists(self.photWeightFile):
            image = numpy.ones(self.size)
            hdu = pyfits.PrimaryHDU(image)
            hdu.writeto(self.photWeightFile)
        
        self.photFlagFile = 'eoc_test_phot.flag.fits'
        if not os.path.exists(self.photFlagFile):
            image = numpy.zeros(self.size, dtype=numpy.int32)
            hdu = pyfits.PrimaryHDU(image)
            hdu.writeto(self.photFlagFile)

 
        self.areaCat = 'eoc_test_area.cat'
        self.fixedArea = 22.222
        if not os.path.exists(self.areaCat):

            areacat = 'eoc_test_tmparea.cat'

            try:

                sextractor(detect = self.detectImageFile, image = self.detectImageFile, config = DETECT_OBJS_CONFIG,
                           catalog_name = areacat,
                           weight_image = [self.detectWeightFile, self.detectWeightFile],
                           flag_image = self.photFlagFile,
                           checkimage_type = 'NONE')

                cat = ldac.openObjectFile(areacat, 'LDAC_OBJECTS')
                self.nObjs = len(cat)

            finally:
                if os.path.exists(areacat):
                    os.remove(areacat)


            area = self.fixedArea*numpy.ones(self.nObjs)
            hdu = pyfits.BinTableHDU.from_columns(pyfits.ColDefs([pyfits.Column(name = 'ISOAREA_DETECT',
                                                                 format = 'E',
                                                                 array = area)]))
            hdu.header['EXTNAME']= 'OBJECTS'
            hdu.writeto(self.areaCat, overwrite = True)
 


        self.outputCat = 'eoc_test_phot.cat'
        self.filter = './eoc_test_phot.conv'

        self.toDelete = [self.detectImageFile, self.detectWeightFile, self.outputCat,
                         self.photImageFile, self.photWeightFile, 
                         self.photFlagFile,  self.filter, self.areaCat]

    ##########

    def tearDown(self):

        for item in self.toDelete:
            if os.path.exists(item):
                os.remove(item)

    ##########

    def testCatExistsInLDAC(self):

        interceptor = Interceptor()

        extractObjectCats(detectImage = self.detectImageFile,
                          detectWeight = self.detectWeightFile,
                          photImage = self.photImageFile,
                          photWeight = self.photWeightFile,
                          photFlag = self.photFlagFile,
                          output = self.outputCat, callMethod = interceptor)

        self.assertTrue(os.path.exists(self.outputCat))
        
        cat = ldac.openObjectFile(self.outputCat)
        self.assertTrue(cat)

    ###########

    def testUseConfig(self):

        interceptor = Interceptor()

        extractObjectCats(detectImage = self.detectImageFile,
                          detectWeight = self.detectWeightFile,
                          photImage = self.photImageFile,
                          photWeight = self.photWeightFile,
                          photFlag = self.photFlagFile,
                          output = self.outputCat, callMethod = interceptor)

        foundConfig = False
        goodArgs = '-WEIGHT_IMAGE -FLAG_IMAGE -GAIN -CATALOG_NAME -c -CHECKIMAGE_NAME'.split()
        for command in interceptor.commands:
            if command[0] == PROGS['p_sex']:
                for i, entry in zip(numpy.arange(len(command)), command):
                    if entry == '-c':
                        foundConfig = command[i+1] == DETECT_OBJS_CONFIG
                    if entry == '-FLAG_IMAGE':
                        self.assertEquals(command[i+1], self.photFlagFile)
                    if foundConfig:
                        if entry[0] == '-':
                            self.assertTrue(entry in goodArgs, entry)
        self.assertTrue(foundConfig)

    ########

    def testStoreSEConfigInPhotInfo(self):


        interceptor = Interceptor()

        extractObjectCats(detectImage = self.detectImageFile,
                          detectWeight = self.detectWeightFile,
                          photImage = self.photImageFile,
                          photWeight = self.photWeightFile,
                          photFlag = self.photFlagFile,
                          output = self.outputCat, callMethod = interceptor)

        photinfo = ldac.openObjectFile(self.outputCat, 'PHOTINFO')

        filterFunc = lambda  x: isObjectExtractionCall(x)
        command = filter(filterFunc, interceptor.commands)[0]

        self.assertEquals(command, photinfo['EXTRACTION_CALL'][0].split())

        configFile = open(DETECT_OBJS_CONFIG).readlines()

        extract_config = photinfo['EXTRACTION_CONFIG'][0].splitlines(True)
        if extract_config[-1][-1] != '\n':
            extract_config[-1] = '%s\n' % extract_config[-1]


        self.assertEquals(configFile, extract_config)
        

        

    ########

    def testGain(self):

        interceptor = Interceptor()

        extractObjectCats(detectImage = self.detectImageFile,
                          detectWeight = self.detectWeightFile,
                          photImage = self.photImageFile,
                          photWeight = self.photWeightFile,
                          photFlag = self.photFlagFile,
                          output = self.outputCat, callMethod = interceptor)

        filterFunc = lambda x: isObjectExtractionCall(x, self.photImageFile)
        command = filter(filterFunc, interceptor.commands)

        self.assertEquals(len(command), 1)

        command = command[0]

        for i, entry in zip(numpy.arange(len(command)), command):
            if entry == '-GAIN':
                self.assertTrue(numpy.abs(float(command[i+1]) - self.gain) < .1)

    ########

    def testConvolve(self):

        interceptor = Interceptor()

        extractObjectCats(detectImage = self.detectImageFile,
                          detectWeight = self.detectWeightFile,
                          photImage = self.photImageFile,
                          photWeight = self.photWeightFile,
                          photFlag = self.photFlagFile,
                          output = self.outputCat, callMethod = interceptor,
                          fwhm = .5, new_fwhm = 1)

        self.assertTrue(os.path.exists(self.filter))

        filterFunc = lambda  x: isObjectExtractionCall(x)
        command = filter(filterFunc, interceptor.commands)[0]

        
        for i, entry in zip(numpy.arange(len(command)), command):
            if entry == '-FILTER_NAME':
                self.assertEquals(command[i+1], self.filter)

        expected = ('python create_gausssmoothing_kernel.py %(seeing_orig).3f %(seeing_new).3f %(PIXSCALE).3f ' % {'seeing_orig' : 0.5, 'seeing_new' : 1.0, 'PIXSCALE' : self.pixscale}).split()

        foundOne = False
        for command in interceptor.commands:
            allMatch = True
            for e1, e2 in zip(expected, command):
                if e1 != e2:
                    allMatch = False
                    break
            if allMatch:
                foundOne = True

        self.assertTrue(foundOne)
        

    ######

    def testDefaultConv(self):

        interceptor = Interceptor()

        extractObjectCats(detectImage = self.detectImageFile,
                          detectWeight = self.detectWeightFile,
                          photImage = self.photImageFile,
                          photWeight = self.photWeightFile,
                          photFlag = self.photFlagFile,
                          output = self.outputCat, callMethod = interceptor,
                          fwhm = 1., new_fwhm = 0.5)

        self.assertTrue(os.path.exists(self.filter))

        filterFunc = lambda  x: isObjectExtractionCall(x)
        command = filter(filterFunc, interceptor.commands)[0]

        
        for i, entry in zip(numpy.arange(len(command)), command):
            if entry == '-FILTER_NAME':
                self.assertEquals(command[i+1], DEFAULT_CONV)


        default_conv = open(DEFAULT_CONV).readlines()

        output_conv = open(self.filter).readlines()

        self.assertEquals(default_conv, output_conv)

    #########

    def testStoreOriginalRMS(self):

        interceptor = Interceptor()

        inputImage = .75*numpy.random.standard_normal(self.size)
        header = pyfits.getheader(self.photImageFile)
        hdu = pyfits.PrimaryHDU(inputImage, header)
        hdu.writeto(self.photImageFile, overwrite=True)
        

        extractObjectCats(detectImage = self.detectImageFile,
                          detectWeight = self.detectWeightFile,
                          photImage = self.photImageFile,
                          photWeight = self.photWeightFile,
                          photFlag = self.photFlagFile,
                          output = self.outputCat, callMethod = interceptor)

        
    
        photinfo = ldac.openObjectFile(self.outputCat, 'PHOTINFO')

        measuredRMS = photinfo['BACKGROUND_RMS']
        self.assertTrue(numpy.abs(measuredRMS - .75) < .1)

        rmsSource  = photinfo['background_rms_source'][0]
        self.assertEquals(rmsSource, self.photImageFile)


    ########

    def testCatMeasuredFromSmoothedImage(self):

        interceptor = Interceptor()

        extractObjectCats(detectImage = self.detectImageFile,
                          detectWeight = self.detectWeightFile,
                          photImage = self.photImageFile,
                          photWeight = self.photWeightFile,
                          photFlag = self.photFlagFile,
                          output = self.outputCat, 
                          fwhm = 0.5, new_fwhm = 0.9,
                          callMethod = interceptor)


        output_base = os.path.splitext(self.outputCat)[0]
        smoothedImage = '%s.filtered.fits' % output_base
        
        self.assertTrue(os.path.exists(smoothedImage))

        filterFunc = lambda  x: isObjectExtractionCall(x, smoothedImage)
        extractCommand = filter(filterFunc, interceptor.commands)

        self.assertEquals(len(extractCommand), 1)

        images = extractCommand[0][3].split(',')
    
        self.assertEquals(images[0], self.detectImageFile)
        self.assertEquals(images[1], smoothedImage)

        foundOne = False
        for command in interceptor.commands:

            if command[0] != PROGS['p_sex']:
                continue

            if command == extractCommand[0]:
                continue

            
            goodArgs = '-CHECKIMAGE_NAME -c -FILTER_NAME -WEIGHT_IMAGE -FLAG_IMAGE'.split()
            foundFilterName = False
            failed = False
            for i, entry in zip(numpy.arange(len(command)), command):
                
                if i == 3:
                    if entry != self.photImageFile:
                        failed = True
                        break
                
                if entry == '-FILTER_NAME':
                    if command[i+1] != self.filter:
                        failed = True
                        break
                    foundFilterName = True

                if entry == '-c':
                    if command[i+1] != SMOOTH_IMAGE_CONFIG:
                        failed = True
                        break

                if entry[0] == '-':
                    if entry not in goodArgs:
                        failed = True
                        break
                
                
            if failed:
                continue

            if foundFilterName:
                foundOne = True
                break
                
        

        self.assertTrue(foundOne)
        self.assertTrue(os.path.exists(smoothedImage))


    ###############

    def testSmoothedImagePhotInfo(self):
 
        extractObjectCats(detectImage = self.detectImageFile,
                          detectWeight = self.detectWeightFile,
                          photImage = self.photImageFile,
                          photWeight = self.photWeightFile,
                          photFlag = self.photFlagFile,
                          output = self.outputCat, 
                          fwhm = 0.5, new_fwhm = 0.9)


        photinfo = ldac.openObjectFile(self.outputCat, 'PHOTINFO')

        self.assertEquals(photinfo['ORIGINAL_FWHM'], 0.5)
        self.assertEquals(photinfo['TARGET_FWHM'], 0.9)
        self.assertEquals(photinfo['SMOOTH_FILTER'], self.filter)


    ##################

    
    def testArea(self):

        extractObjectCats(detectImage = self.detectImageFile,
                          detectWeight = self.detectWeightFile,
                          photImage = self.photImageFile,
                          photWeight = self.photWeightFile,
                          photFlag = self.photFlagFile,
                          output = self.outputCat, 
                          fwhm = 0.5, new_fwhm = 0.9)

        cat = ldac.openObjectFile(self.outputCat)

        extractObjectCats(detectImage = self.detectImageFile,
                          detectWeight = self.detectWeightFile,
                          photImage = self.detectImageFile,
                          photWeight = self.detectWeightFile,
                          photFlag = self.photFlagFile,
                          output = '%s.output.cat' % self.outputCat)

        detect_cat = ldac.openObjectFile('%s.output.cat' % self.outputCat)

        self.assertTrue((cat['ISOAREA_DETECT'] == detect_cat['NPIX']).all())
        

    ################

    def testNoCalcArea(self):

        interceptor = Interceptor()

        extractObjectCats(detectImage = self.detectImageFile,
                          detectWeight = self.detectWeightFile,
                          photImage = self.detectImageFile,
                          photWeight = self.detectWeightFile,
                          photFlag = self.photFlagFile,
                          output = self.outputCat, 
                          callMethod = interceptor)

        commandCount = 0
        for command in interceptor.commands:

            if command[0] == PROGS['p_sex']:
                commandCount += 1

        self.assertEquals(commandCount, 1)

        cat = ldac.openObjectFile(self.outputCat)

        self.assertTrue((cat['NPIX'] == cat['ISOAREA_DETECT']).all())


    #################

    def testAreaPhotInfo(self):

        extractObjectCats(detectImage = self.detectImageFile,
                          detectWeight = self.detectWeightFile,
                          photImage = self.detectImageFile,
                          photWeight = self.detectWeightFile,
                          photFlag = self.photFlagFile,
                          output = self.outputCat)

        photinfo = ldac.openObjectFile(self.outputCat, 'PHOTINFO')

        self.assertEquals(photinfo['DETECT_AREA'][0], self.detectImageFile)
        

    ##################

    def testAreaGiven(self):

        interceptor = Interceptor()

        extractObjectCats(detectImage = self.detectImageFile,
                          detectWeight = self.detectWeightFile,
                          photImage = self.photImageFile,
                          photWeight = self.photWeightFile,
                          photFlag = self.photFlagFile,
                          output = self.outputCat,
                          measureArea = self.areaCat,
                          callMethod = interceptor)

        
        cat = ldac.openObjectFile(self.outputCat)

        photinfo = ldac.openObjectFile(self.outputCat, 'PHOTINFO')


        self.assertTrue((cat['ISOAREA_DETECT'] == self.fixedArea).all())

        self.assertEquals(photinfo['DETECT_AREA'], self.areaCat)

        
        
        filterFunc = lambda  x: isObjectExtractionCall(x, self.detectImageFile)
        extractCommand = filter(filterFunc, interceptor.commands)

        self.assertEquals(len(extractCommand), 0)

        
    #####################

    def testForceNoAreaCalc(self):

        try:

            extractObjectCats(detectImage = self.detectImageFile,
                              detectWeight = self.detectWeightFile,
                              photImage = self.photImageFile,
                              photWeight = self.photWeightFile,
                              photFlag = self.photFlagFile,
                              output = self.outputCat, 
                              measureArea = False)

            cat = ldac.openObjectFile(self.outputCat)

            sextractor(detect = self.detectImageFile, image = self.photImageFile, config = DETECT_OBJS_CONFIG,
                       catalog_name = '%s.area.cat' % self.outputCat,
                       weight_image = [self.detectWeightFile, self.photWeightFile],
                       flag_image = self.photFlagFile,
                       checkimage_type = 'NONE')


            area_cat = ldac.openObjectFile('%s.area.cat' % self.outputCat, 'LDAC_OBJECTS')
            self.assertTrue(area_cat)


            sextractor(detect = self.detectImageFile, image = self.detectImageFile, config = DETECT_OBJS_CONFIG,
                       catalog_name = '%s.detect.cat' % self.outputCat,
                       weight_image = [self.detectWeightFile, self.detectWeightFile],
                       flag_image = self.photFlagFile,
                       checkimage_type = 'NONE')


            detect_cat = ldac.openObjectFile('%s.detect.cat' % self.outputCat, 'LDAC_OBJECTS')
            self.assertTrue(detect_cat)

            self.assertTrue((cat['ISOAREA_DETECT'] == area_cat['ISOAREA_IMAGE']).all())
            self.assertTrue((cat['ISOAREA_DETECT'] != detect_cat['ISOAREA_IMAGE']).any())

        finally:

            files = [ '%s.area.cat' % self.outputCat , '%s.detect.cat' % self.outputCat ]
            for file in files:
                if os.path.exists(file):
                    os.remove(file)
        

    ######################





        
########################

class TestConvolve(unittest.TestCase):

    def setUp(self):

        self.old_seeing = 0.5
        self.new_seeing = 1.1
        self.pixscale = 0.2
        self.output = 'eoc_test_convolve.conv'


    #######

    def tearDown(self):

        if os.path.exists(self.output):
            os.remove(self.output)

    ########

    def testBasic(self):

        interceptor = Interceptor()

        createConvolutionKernel(orig_seeing = self.old_seeing, 
                                new_seeing = self.new_seeing, 
                                pixscale = self.pixscale, 
                                output = self.output,
                                callMethod = interceptor)

        expected = ('python create_gausssmoothing_kernel.py %.3f %.3f %.3f %s' % \
                        (self.old_seeing, self.new_seeing, self.pixscale, self.output)).split()

        self.assertEquals(interceptor.commands[0], expected)
    
        self.assertTrue(os.path.exists(self.output))

    def testNoConvolve(self):

        interceptor = Interceptor()

        createConvolutionKernel(orig_seeing = self.old_seeing, 
                                new_seeing = 0.4, 
                                pixscale = self.pixscale, 
                                output = self.output,
                                callMethod = interceptor)


        self.assertEquals(len(interceptor.commands), 0)
    
        self.assertTrue(os.path.exists(self.output))

        default_conv = open(DEFAULT_CONV).readlines()

        output_conv = open(self.output).readlines()

        self.assertEquals(default_conv, output_conv)

#######################

class TestMeasureRMS(unittest.TestCase):

    def setUp(self):

        self.image = 'eoc_test_measurerms.fits' 

        if not os.path.exists(self.image):
            image = .75*numpy.random.standard_normal((100,100))
            image[47:53,47:53] = 0
            hdu = pyfits.PrimaryHDU(image)
            hdu.writeto(self.image)

    #####

    def tearDown(self):

        if os.path.exists(self.image):
            os.remove(self.image)

    #####

    def testBasic(self):

        rms = measureRMS(self.image)

        self.assertTrue(numpy.abs(rms - .75) < .05)

        self.assertEquals(type(rms), type(5.5))


########################

class FakeFunction(object):

    def __init__(self):

        self.args = []
        self.keywords = {}

    def __call__(self, *args, **keywords):
        
        self.args = args
        self.keywords = keywords

        
class TestMain(unittest.TestCase):


    def testBasic(self):

        foo = FakeFunction()

        call = './extract_object_cats.py --di detect.fits --dw detect.weight.fits --pi phot.fits --pw phot.weight.fits --pf phot.flag.fits -o mycat.cat'.split()

        main(argv = call, toCall = foo)


        self.assertEquals(len(foo.args), 0)

        self.assertEquals(foo.keywords['detectImage'], 'detect.fits')
        self.assertEquals(foo.keywords['detectWeight'], 'detect.weight.fits')
        self.assertEquals(foo.keywords['photImage'], 'phot.fits')
        self.assertEquals(foo.keywords['photWeight'], 'phot.weight.fits')
        self.assertEquals(foo.keywords['photFlag'], 'phot.flag.fits')
        self.assertEquals(foo.keywords['output'], 'mycat.cat')
        self.assertEquals(foo.keywords['fwhm'], None)
        self.assertEquals(foo.keywords['new_fwhm'], None)
        self.assertEquals(foo.keywords['measureArea'], True)
        self.assertTrue('callMethod' not in foo.keywords)

        #########


    def testConvolve(self):
        
        foo = FakeFunction()

        call = './extract_object_cats.py --di detect.fits --dw detect.weight.fits --pi phot.fits --pw phot.weight.fits --pf phot.flag.fits -o mycat.cat --fwhm 0.5 --new-fwhm 0.9'.split()

        main(argv = call, toCall = foo)


        self.assertEquals(len(foo.args), 0)

        self.assertEquals(foo.keywords['fwhm'], 0.5)
        self.assertEquals(foo.keywords['new_fwhm'], 0.9)

        ############

    def testArea(self):

        
        foo = FakeFunction()

        call = './extract_object_cats.py --di detect.fits --dw detect.weight.fits --pi phot.fits --pw phot.weight.fits --pf phot.flag.fits -o mycat.cat --fwhm 0.5 --new-fwhm 0.9 --area test.cat'.split()

        main(argv = call, toCall = foo)

        self.assertEquals(foo.keywords['measureArea'], 'test.cat')

    ##################

    def testForceNoArea(self):

        foo = FakeFunction()

        call = './extract_object_cats.py --di detect.fits --dw detect.weight.fits --pi phot.fits --pw phot.weight.fits --pf phot.flag.fits -o mycat.cat --fwhm 0.5 --new-fwhm 0.9 --noarea'.split()

        main(argv = call, toCall = foo)

        self.assertEquals(foo.keywords['measureArea'], False)
        


    def testHelp(self):

        foo = FakeFunction()

        call = './extract_object_cats.py'.split()

        self.assertRaises(SystemExit, main, argv = call, toCall = foo)

        self.assertEquals(len(foo.args), 0)
        self.assertEquals(len(foo.keywords), 0)

        
class TestUpdatePhotInfo(unittest.TestCase):

    def setUp(self):

        self.cat = 'eoc_test_updatePhotInfo.cat'
        if not os.path.exists(self.cat):
            seqnr = numpy.arange(15)
            xpos = numpy.arange(15)
            ypos = numpy.arange(15)
            flux = numpy.random.standard_normal(15)
            fluxerr = numpy.random.standard_normal(15)
            
            cols = [ pyfits.Column(name = 'SeqNr',
                                   format = 'K',
                                   array = seqnr),
                     pyfits.Column(name = 'Xpos',
                                   format = 'E',
                                   array = xpos),
                     pyfits.Column(name = 'Ypos',
                                   format = 'E',
                                   array = ypos),
                     pyfits.Column(name = 'FLUX_ISO',
                                   format = 'E',
                                   array = flux),
                     pyfits.Column(name = 'FLUXERR_ISO',
                                   format = 'E',
                                   array = fluxerr)]

            self.objects = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
            self.objects.header['EXTNAME']= 'OBJECTS'

            self.fields = pyfits.BinTableHDU.from_columns(pyfits.ColDefs([pyfits.Column(name='Fake', format = 'E', array = numpy.ones(2))]))
            self.fields.header['EXTNAME']= 'FIELDS'

            hdulist = pyfits.HDUList([pyfits.PrimaryHDU(), self.objects, self.fields])
            hdulist.writeto(self.cat)

    #####

    def tearDown(self):

        if os.path.exists(self.cat):
            os.remove(self.cat)

    ####

    def testUpdateInfoBasic(self):

        updatePhotInfo(self.cat, rms = .15)

        self.assertTrue(os.path.exists(self.cat))
        
        photinfo = ldac.openObjectFile(self.cat, 'PHOTINFO')

        self.assertEquals(photinfo['rms'], .15)

    #########

    def testNothing(self):

        photinfo = {}
        
        updatePhotInfo(self.cat, **photinfo)


    ##########

        

    def testUpdateInfoPreserveOther(self):

        updatePhotInfo(self.cat, rms = .15)

        self.assertTrue(os.path.exists(self.cat))
        
        hdulist = pyfits.open(self.cat)

        self.assertEquals(len(hdulist), 4)

        for hdu in hdulist:
            
            try:

                self.assertTrue(hdu.header['EXTNAME'] in 'OBJECTS FIELDS PHOTINFO'.split())

                if hdu.header['EXTNAME'] == 'OBJECTS':
                    comparison = self.objects
                elif hdu.header['EXTNAME'] == 'FIELDS':
                    comparison = self.fields
                else:
                    continue
                    
                self.assertTrue((hdu.data == comparison.data).all())
                
                self.assertEquals(hdu.columns.names, comparison.columns.names)
                self.assertEquals(hdu.columns.formats, comparison.columns.formats)

            except KeyError:

                pass


    #########

    def testAddInfo(self):

        cols = [pyfits.Column('rms', format='E', array = [.25]),
                    pyfits.Column('other', format='20A', array = ['stuff'])]
        photinfo = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
        photinfo.header['EXTNAME']= 'PHOTINFO'

        hdus = [pyfits.PrimaryHDU(), self.objects, self.fields, photinfo]
        pyfits.HDUList(hdus).writeto(self.cat, overwrite=True)

        updatePhotInfo(self.cat, rms = .15, source='calculated')

        newphotinfo = ldac.openObjectFile(self.cat, 'PHOTINFO')

        self.assertTrue(newphotinfo)

        self.assertEquals(newphotinfo['rms'], .15)
        self.assertEquals(newphotinfo['other'], 'stuff')
        self.assertEquals(newphotinfo['source'], 'calculated')

        
                    

    #########


    def testFindPyfitsType(self):

        self.assertEquals(findPyfitsType(5), 'J')
        self.assertEquals(findPyfitsType(5.5), 'E')
        self.assertEquals(findPyfitsType('raw'), '512A')

        longString = ' '.join(150*['aaaaaaaaaaaaaaaa'])
        self.assertEquals(findPyfitsType(longString), '%dA' % len(longString))

                                                               
    ##########

    def testStoreLongString(self):
        
        toStore = ' '.join(150*['aaaaaaaaaaaaa'])

        updatePhotInfo(self.cat, SEcommand=  toStore)

        photinfo = ldac.openObjectFile(self.cat, 'PHOTINFO')
        
        self.assertEquals(toStore, photinfo['SEcommand'])
        
        
        
        
        
        
        
                
        
        
            
########################

def test():

    testcases = [TestExtract, TestSextractor, TestLDACConv, TestConvolve, TestMeasureRMS, TestMain, TestUpdatePhotInfo]

    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)


##########################################################
# COMMAND LINE OPS
##########################################################

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        test()

    else:

        main()
