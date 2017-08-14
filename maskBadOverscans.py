#!/usr/bin/env python
################
# @file maskBadOverscans.py
# @author Douglas Applegate
# @date 2/14/07 (Vday - what a lame day)
# 
# @brief Checks the overscan region of an image
#         for electron bleedthrough from an image obj (ie star)
#         near the edge. Creates a mask with the appropriate row eliminated
################

__cvs_id__ = "$Id: maskBadOverscans.py,v 1.4 2008-07-09 01:22:15 dapple Exp $"

########################################################################

usage = \
'''
maskBadOverscans.py  maindir workdir prefix [options]
       ex: maskBadOverscans.py /path/to/date_filter SCIENCE SUPA

  or

maskBadOverscans.py test
'''

########################################################################

import astropy, astropy.io.fits as pyfits, re, unittest, sys, os, numpy, math, glob
import bashreader, leastsq, TestBadOverscansTestData, regionfile
from optparse import OptionParser

########################################################################

import BonnLogger

########################################################################

########################################################################
# UTILITY CLASSES
#################

class NothingToDoException(Exception): pass

class NoInstrumentException(Exception): pass

class BadInstrumentFileException(Exception): pass

########################################################################

class OverscanInfo(dict):
    '''class OverscanInfo
         Extracts relevant info about the size & shape
         of the overscan region from a dictionary-interfaced object.
    '''
    
    def __init__(self, config = None):
        '''@param config a dictionary-interfaced object
              config should have entries 'ovscan[x|y]',
              and 'cut[x|y]
        '''

        self.directionIsX = None
        if config is not None:
            self.readConfig(config)

    ###

    def __str__(self):
        astr = "OverscanInfo:\n"
        if self.isXDirection():
            astr += "\tDirection: X\n"
        else:
            astr += "\tDirection: Y\n"

        for chip, chipData in self.iteritems():
            astr += "\tChip %d: %s\n" % (chip, chipData)

        return astr

    ###
	
    def setXOverscanDir(self):
        self.directionIsX = True

    def setYOverscanDir(self):
        self.directionIsX = False

    def isYDirection(self):
        return not self.directionIsX

    def isXDirection(self):
        return self.directionIsX

    ###

    def isInitialized(self):

        if self.directionIsX == None:
            return False

        for chip in self.itervalues():
            for entry in chip.iteritems():
                if entry is None:
                    return False

        return True

    ###
	
    def addChip(self, chipId):
        if chipId not in self:
            self[chipId] = {'min':None,
                            'max':None,
                            'offset':None}

    ###
	
    def setMin(self, chipId, min):
        self[chipId]['min'] = min
	
    def getMin(self, chipId):
        return self[chipId]['min']
    
    def setMax(self, chipId, max):
        self[chipId]['max'] = max+1
            
    def getMax(self, chipId):
        return self[chipId]['max']

    ###

    def setOffset(self, chipId, offset):
        self[chipId]['offset'] = offset

    def getOffset(self, chipId):
        return self[chipId]['offset']

    ###

    def _parseOverscan(self, config):

        def parseDirection(direction):
            if direction == 'x': 
                self.setXOverscanDir()
            else:
                self.setYOverscanDir()

        ###
                
        def parseMinOrMax(index):
            if index == '1':
                return self.setMin
            else:
                return self.setMax

        ###
    
        parameterNames = config.keys()
        for param in parameterNames:

            match = re.match('ovscan([xy])(\d+)', param)
            if match is None: 
                continue
       
            parseDirection(match.group(1))

            addPixVal = parseMinOrMax(match.group(2))
        
            overscanBoundaries = getattr(config, param).iteritems()
            for chipId, pixIndex in overscanBoundaries:
                self.addChip(chipId)
                addPixVal(chipId, pixIndex - 1)

    ###

    def _parseOffset(self, config):

        if self.isXDirection():
            paramName = 'cuty'
        else:
            paramName = 'cutx'

        offsets = getattr(config, paramName).iteritems()
        for chip, offset in offsets:
            self.setOffset(chip, offset)

    ###

    def readConfig(self, config):
        '''@param config a dictionary-interfaced object
              config should have entries 'ovscan[x|y]',
              and 'cut[x|y]
        '''

        self._parseOverscan(config)
        self._parseOffset(config)
    
        if not self.isInitialized():
            raise BadInstrumentFileException

    
######################################################################
######################################################################

##############################
#USER METHODS
#############

def maskOverscanLines(image, overscanInfo, chipId, 
                      buffer = 1,
                      threshold = 3.,
                      bumpWidth = 2):
    '''
    @brief Given an image, return polygons of areas to exclude due to a bad
             overscan correction

    @param image a 2d numpy array. First index is y dimension
    @param overscanInfo an OverscanInfo object
    @param chipId id key in overscanInfo corresponding to image
    @param buffer number of rows around a detected overscan anomoly region 
             to also exclude
    @param threshold detection threshold of overscan anomolies
    @param bumpWidth required width of anomoly (in pixels) for detection
    
    @returns a set of regionfile.Polygon objects
    '''

    overscan = rejectOutliersByLine(extractOverscan(image,
                                                    overscanInfo, chipId))

    bumps = mergeBumps(findExclusions(overscan, threshold = threshold,
                                      bumpWidth = bumpWidth))

    if overscanInfo.isXDirection():
        polygons = makePolygons(imageWidth = image.shape[1], 
                                imageOffset = overscanInfo.getOffset(chipId), 
                                ranges = bumps,
                                buffer = buffer)
    else:
        polygons = makePolygons(imageWidth = image.shape[0], 
                                imageOffset = overscanInfo.getOffset(chipId),
                                ranges = bumps,
                                buffer = buffer,
                                vertical = True)

    return polygons

    
######################################################################

def processDirectory(maindir, dir, prefix = '', buffer = 4, 
                     threshold = 3., bumpWidth = 2):
    '''
    @brief Given a directory, process all images in directory for masking
    
    @param maindir date_filter directory name
    @param dir subdirectory to examine, eg, SCIENCE
    @param prefix process only files starting with given prefix phrase

    @param buffer number of rows around a detected overscan anomoly region 
             to also exclude
    @param threshold detection threshold of overscan anomolies
    @param bumpWidth required width of anomoly (in pixels) for detection

    @effects Appends region files in the maindir/dir/reg directory with 
               masking info

    NOTE: Assumes Bonn pipeline structures
    
    '''

    dirPath = '%s/%s' % (maindir, dir)

    ###

    def getOverscanInfo():
        if 'INSTRUMENT' not in os.environ:
            raise NoInstrumentException

        instrumentFile = '%s.ini' % os.environ['INSTRUMENT']

        return OverscanInfo(bashreader.parseFile(instrumentFile))

    ###

    def makeRegiondir():
        regiondir = '%s/reg' % dirPath
        if not os.path.exists(regiondir):
            os.mkdir(regiondir)
        return regiondir

    ###

    def getImageFiles():

        if os.path.exists('%s/SPLIT_IMAGES' % dirPath):
            filenames = glob.glob('%s/SPLIT_IMAGES/*.fits' % dirPath)
        else:
            filenames = glob.glob('%s/*.fits' % dirPath)

        if len(filenames) == 0:
            raise NothingToDoException

        return filenames

    ###

    def getImage(filename):
        fitsFile = pyfits.open(fullFilename)
        image = fitsFile[0].data
        fitsFile.close()
        return image

    ###

    overscanInfo = getOverscanInfo()

    regiondir = makeRegiondir()

    filenames = getImageFiles()
        
    for fullFilename in filenames:
        
        filename = os.path.basename(fullFilename)

        print 'Processing %s...' % filename

        match = re.match('(%s\d+_(\d+))\.fits' % prefix, filename)

        if match is None:
            print '! Skipping %s' % filename
            continue

        basename = match.group(1)
        chipId = int(match.group(2))

        image = getImage(filename)
 
        maskedRegions = maskOverscanLines(image, overscanInfo, chipId,
                                          buffer = buffer,
                                          threshold = threshold,
                                          bumpWidth = bumpWidth)

        regionFilename = '%s/%s.reg' % (regiondir, basename)
        
        regionfile.writeRegionFile(regionFilename, maskedRegions)
        
##########################################################################
##########################################################################

##################################
#UTILITY METHODS
################

def extractOverscan(image, overscanInfo, chipId):

    if overscanInfo.isYDirection():
        #because default fits image has y as first axis
        image = image.transpose()


    xmin = overscanInfo.getMin(chipId)
    xmax = overscanInfo.getMax(chipId)

    overscan = image[:,xmin:xmax]
    return overscan

############################################################################

def rejectOutliersByLine(image):
    
    reducedImage = numpy.zeros((image.shape[0], image.shape[1]-2))
    for i in xrange(len(image)):
        a = image[i]
        
        minPix = a.argmin()
        
        a = numpy.hstack([a[0:minPix],a[minPix+1:]])

        maxPix = a.argmax()

        a = numpy.hstack([a[0:maxPix],a[maxPix+1:]])

        reducedImage[i] = a
        
    return reducedImage

###############################################################################

def _convertToIndices(boolArray):
    return numpy.arange(len(boolArray))[boolArray]

###############################################################################

class _piecewiseLinear(object):

    def __init__(self, x1, x2):

        self.x1 = x1
        self.x2 = x2

    ###

    def __call__(self, x, params):
        
        Aa = params[0]
        Ab = params[1]
        Ac = params[2]
        Bc = params[3]

        Bb = (Ac - Ab)*self.x2 + Bc
        Ba = (Ab - Aa)*self.x1 + Bb

        Ya = Aa*x + Ba
        Yb = Ab*x + Bb
        Yc = Ac*x + Bc
        
        return numpy.where(x <= self.x1, Ya, numpy.where(x <= self.x2, Yb, Yc))


##############################################################################

def findExclusions(image, threshold = 3, bumpWidth = 2):

    marginalizedImage = numpy.sum(image, axis=1)

    X = numpy.arange(len(marginalizedImage))

    backgroundModel = _piecewiseLinear(len(marginalizedImage)/3,
                                       2*len(marginalizedImage)/3)

    ######################

    def findBumps(knownBumps):
    
        imageNoBumps = marginalizedImage[numpy.logical_not(knownBumps)]
        xNoBumps = X[numpy.logical_not(knownBumps)]
        
        average = numpy.mean(imageNoBumps)

        bkgroundParams, chisq, covar, isConverged = \
            leastsq.leastsq(backgroundModel, [0,0,0,average],
                            xNoBumps, imageNoBumps, fullOutput = True)

        bkground = backgroundModel(X, bkgroundParams)
        
        stddev = numpy.sqrt(numpy.mean( \
                (bkground[numpy.logical_not(knownBumps)] - imageNoBumps)**2))

        candidates = marginalizedImage > (bkground + threshold*stddev)


        ###########
	
        def filterOverBumpWidth(candidates, operator):
            filtered = candidates
            for i in xrange(1,bumpWidth):
                filtered = operator(candidates, numpy.roll(candidates, i))
                filtered[0:i] = candidates[0:i]
                filtered = operator(filtered, numpy.roll(candidates, -i))
                filtered[-i:] = candidates[-i:]
            return filtered

        ############

        randomsEliminated = filterOverBumpWidth(candidates,
                                                numpy.logical_and)

        bumps = filterOverBumpWidth(randomsEliminated, numpy.logical_or)

       	return bumps

    ###############

    nExcludedRows = 0
    excluded = findBumps(numpy.array(len(marginalizedImage)*[False]))
    while len(excluded[excluded==True]) > nExcludedRows:
        nExcludedRows = len(excluded[excluded==True])
        excluded = findBumps(excluded)


    return _convertToIndices(excluded).tolist()
    

###################################################################### 

###
def _nextElementIsContinuous(alist, curVal):
    return len(alist) > 0 and alist[-1] == (curVal + 1)
###


def mergeBumps(bumps):

    
    sortedBumps = sorted(bumps, reverse=True)

    ranges = []
    while len(sortedBumps) != 0:
        min = sortedBumps.pop()
        max = min
        while _nextElementIsContinuous(sortedBumps, max):
            max = sortedBumps.pop()
        ranges.append((min,max))
    return ranges

######################################################################

def makePolygons(imageWidth, imageOffset, ranges, buffer = 1, vertical = False):

    def makeHorizontalBox(arange):
        return [0, arange[0] - imageOffset - buffer,
             imageWidth, arange[0] - imageOffset - buffer,
             imageWidth, arange[1] - imageOffset + buffer,
             0, arange[1] - imageOffset + buffer]
    
    ###

    def makeVerticalBox(arange):
        return [arange[0] - imageOffset - buffer , 0,
             arange[1] - imageOffset +  buffer, 0,
             arange[1] - imageOffset + buffer, imageWidth,
             arange[0] - imageOffset - buffer, imageWidth]

    ###

    def applyFitsStartsat1Offset(box):
        return [x+1 for x in box]

    ###

    makeBox = makeHorizontalBox
    if vertical:
        makeBox = makeVerticalBox

    regions = []

    for arange in ranges:
        regions.append(regionfile.Polygon(applyFitsStartsat1Offset(   \
                    makeBox(arange)) ) )

    return regions

        

            
########################################################################
########################################################################

#######################
#TESTING CLASSES
#########

class TestOverscanInfo(unittest.TestCase):

    def setUp(self):

        configTxt = '''
OVSCANX1=([6]=1  [7]=1  [3]=1  [4]=1  [9]=1  [8]=2055 [1]=2065 [2]=2055 [5]=2055 [10]=1)
OVSCANX2=([6]=28 [7]=28 [3]=28 [4]=28 [9]=28 [8]=2080 [1]=2080 [2]=2080 [5]=2080 [10]=28)
        
CUTX=([6]=40 [7]=40 [3]=40 [4]=40 [9]=40 [8]=40 [1]=40 [2]=40 [5]=40 [10]=40)
CUTY=([6]=10 [7]=10 [3]=10 [4]=10 [9]=10 [8]=10 [1]=10 [2]=10 [5]=10 [10]=10)

SIZEX=([6]=2000 [7]=2000 [3]=2000 [4]=2000 [9]=2000 [8]=2000 [1]=2000 [2]=2000 [5]=2000 [10]=2000)
SIZEY=([6]=4080 [7]=4080 [3]=4080 [4]=4080 [9]=4080 [8]=4080 [1]=4080 [2]=4080 [5]=4080 [10]=4080)
'''


        self.config = bashreader.parse(configTxt)
                     
                    
    def testGoodInstrumentFile(self):
        
        overscanRegions = OverscanInfo(self.config)
        self.assertEquals(overscanRegions.getMin(1), 2064)
        self.assertEquals(overscanRegions.getMax(1), 2080)
        self.assertEquals(overscanRegions.getMin(2), 2054)
        self.assertEquals(overscanRegions.getMax(2), 2080)
        self.assertEquals(overscanRegions.getMin(3), 0)
        self.assertEquals(overscanRegions.getMax(3), 28)
        self.assertEquals(overscanRegions.getMin(4), 0)
        self.assertEquals(overscanRegions.getMax(4), 28)
        self.assertEquals(overscanRegions.getMin(5), 2054)
        self.assertEquals(overscanRegions.getMax(5), 2080)
        self.assertEquals(overscanRegions.getMin(6), 0)
        self.assertEquals(overscanRegions.getMax(6), 28)
        self.assertEquals(overscanRegions.getMin(7), 0)
        self.assertEquals(overscanRegions.getMax(7), 28)
        self.assertEquals(overscanRegions.getMin(8), 2054)        
        self.assertEquals(overscanRegions.getMax(8), 2080)
        self.assertEquals(overscanRegions.getMin(9), 0)
        self.assertEquals(overscanRegions.getMax(9), 28)
        self.assertEquals(overscanRegions.getMin(10), 0)
        self.assertEquals(overscanRegions.getMax(10), 28)
        self.assertTrue(overscanRegions.isXDirection())
        self.assertFalse(overscanRegions.isYDirection())
        self.assertEquals(overscanRegions.getOffset(1), 10)
        self.assertEquals(overscanRegions.getOffset(2), 10)
        self.assertEquals(overscanRegions.getOffset(3), 10)
        self.assertEquals(overscanRegions.getOffset(4), 10)
        self.assertEquals(overscanRegions.getOffset(5), 10)
        self.assertEquals(overscanRegions.getOffset(6), 10)
        self.assertEquals(overscanRegions.getOffset(7), 10)
        self.assertEquals(overscanRegions.getOffset(8), 10)
        self.assertEquals(overscanRegions.getOffset(9), 10)
        self.assertEquals(overscanRegions.getOffset(10), 10)
        

###################

class TestExtractOverscanRegion(unittest.TestCase):

    def setUp(self):
        overscan = OverscanInfo()
        overscan.setXOverscanDir()
        overscan.addChip(1)
        overscan.setMin(1, 0)
        overscan.setMax(1, 29)
        overscan.setOffset(1, 5)
        self.overscanInfo = overscan
        self.level = 10000
        self.sigma = .5
        self.ysize = 100

        self.image = numpy.hstack([self.level + \
                  self.sigma*numpy.random.standard_normal( \
                               size=(self.ysize, self.overscanInfo.getMax(1))),

                 -self.level + self.sigma*numpy.random.standard_normal( \
                               size=(self.ysize,5))])


    def testExtractOverscan(self):
        
        overscan = extractOverscan(self.image, self.overscanInfo, chipId = 1)
        self.assertEquals(overscan.shape, (100,30))

################################

class TestFitOverscanRegion(unittest.TestCase):

    def setUp(self):

        self.level = 10000
        self.sigma = .5
        self.xsize = 30
        self.ysize = 100

        self.image = self.level + self.sigma*numpy.random.standard_normal( \
                               size=(self.ysize, self.xsize))

    def testRejectOutliers(self):
        self.image[5,3] = 10500
        self.image[7,1] = 11200
        
        overscan = rejectOutliersByLine(self.image)

        self.assertEquals(overscan.shape, (self.ysize, 
                                            self.xsize - 2))
        self.assertTrue((overscan[5] != 10500).any())
        self.assertTrue((overscan[7] != 11200).any())

    def testRejectOutliersAllSame(self):
        image = numpy.array([5*[3.],5*[2.]])
        self.assertTrue(numpy.array_equal(rejectOutliersByLine(image), 
                                          numpy.array([3*[3.],3*[2.]])))

    def testRowConstOffset(self):

        self.image[45,:] += 5*self.sigma
        self.assertEquals(findExclusions(self.image, bumpWidth=1), [45])

    def testFind2Bumps(self):

        self.image[20,:] += 2*self.sigma
        self.image[21,:] += 2*self.sigma
        self.image[22,:] += 2*self.sigma
        self.image[44,:] += 10*self.sigma
        self.image[45,:] += 10*self.sigma
        self.image[46,:] += 10*self.sigma

        self.assertEquals(findExclusions(self.image), [20,21,22,44,45,46])

    def testNoBump(self):

        self.assertEquals(findExclusions(self.image), [])

    def testEqualSensitivity(self):

        bumpsNotDetected = []

        for i in xrange(1, 99):

            image = numpy.ones((100,10))
            image[i-1:i+2,:] *= 5

            if not (findExclusions(image) == range(i-1,i+2)):
                bumpsNotDetected.append(i)

        print "Bumps not detected: %s" % str(bumpsNotDetected)

        self.assertEquals(0, len(bumpsNotDetected))

#########################################################################

class TestCreateRegion(unittest.TestCase):

    def testSingleRegionMerge(self):

        bumps = [45,46,47]
        self.assertEquals(mergeBumps(bumps), [(45,47)])

    def testDoubleRegionMerge(self):

        bumps = [41,42,43,45,46,47]
        self.assertEquals(mergeBumps(bumps), [(41,43), (45,47)])


    #remember: shift by +1 for fits files
    #add 1 pix buffer either side
    def testMakePolygons(self):

        mergedRows = [(41,43)]
        imageWidth = 40
        imageOffset = 5

        self.assertEquals(makePolygons(imageWidth, imageOffset, mergedRows), 
                          [regionfile.Polygon([1,36,41,36,41,40,1,40])])

    def testCreate2Polygons(self):

        mergedRows = [(19,25),(41,43)]
        imageWidth = 40
        imageOffset = 5

        regions = makePolygons(imageWidth, imageOffset, mergedRows)
        self.assertEquals(len(regions), 2)
        self.assertTrue(regionfile.Polygon([1,36,41,36,41,40,1,40]) in regions)
        self.assertTrue(regionfile.Polygon([1,14,41,14,41,22,1,22]) in regions)

    def testYDirection(self):

        mergedRows = [(41,43)]
        imageWidth = 40
        imageOffset = 5

        self.assertEquals(makePolygons(imageWidth, imageOffset, 
                                       mergedRows, vertical=True), 
                          [regionfile.Polygon([36,1,40,1,40,41,36,41])])

    def testAddBuffer(self):
        mergedRows = [(41,43)]
        imageWidth = 40
        imageOffset = 5
        buffer = 3

        self.assertEquals(makePolygons(imageWidth, imageOffset, mergedRows,
                                       buffer = buffer), 
                          [regionfile.Polygon([1,34,41,34,41,42,1,42])])

    

#########################################################################
        
class TestRealBump(unittest.TestCase):

    def setUp(self):

        self.overscan = TestBadOverscansTestData.realbump

        self.image = rejectOutliersByLine(self.overscan)

    def testFindRealBump(self):
        #doesn't have anything outside 58 - 84, but has at least 62-80
        exclude = numpy.array(findExclusions(self.image))
        self.failIf(numpy.logical_or(exclude < 58, exclude > 84).any())
        for i in xrange(62,81):
            self.failIf((exclude != i).all(), 'Missing: %d' % i)

###################################################################

class TestRealDataNoDetect(unittest.TestCase):

    def setUp(self):

        self.image = TestBadOverscansTestData.nodetect


        configTxt = '''
OVSCANX1=([6]=1  [7]=1  [3]=1  [4]=1  [9]=1  [8]=2055 [1]=2065 [2]=2055 [5]=2055 [10]=1)
OVSCANX2=([6]=28 [7]=28 [3]=28 [4]=28 [9]=28 [8]=2080 [1]=2080 [2]=2080 [5]=2080 [10]=28)
        
CUTX=([6]=40 [7]=40 [3]=40 [4]=40 [9]=40 [8]=40 [1]=40 [2]=40 [5]=40 [10]=40)
CUTY=([6]=10 [7]=10 [3]=10 [4]=10 [9]=10 [8]=10 [1]=10 [2]=10 [5]=10 [10]=10)

SIZEX=([6]=2000 [7]=2000 [3]=2000 [4]=2000 [9]=2000 [8]=2000 [1]=2000 [2]=2000 [5]=2000 [10]=2000)
SIZEY=([6]=4080 [7]=4080 [3]=4080 [4]=4080 [9]=4080 [8]=4080 [1]=4080 [2]=4080 [5]=4080 [10]=4080)
'''


        self.overscan = OverscanInfo(bashreader.parse(configTxt))

    ####

    def testNoDetect(self):

        regions = maskOverscanLines(self.image, self.overscan, 7)

        self.assertEquals(len(regions), 0)

        


        
    

###################################################################

class TestProcessChip(unittest.TestCase):

    def testXDirectionChip(self):

        image = numpy.ones((50,30))
        overscan = OverscanInfo()
        overscan.setXOverscanDir()
        overscan.addChip(1)
        overscan.setMin(1, 0)
        overscan.setMax(1, 9)
        overscan.setOffset(1, 5)

        image[10:14,0:10] *= 5
        regions = maskOverscanLines(image, overscan, 1)
        
        self.assertEquals(regions, [regionfile.Polygon([1,5,31,5,31,10,1,10])])

    #######

    def testYDirectionChip(self):

        image = numpy.ones((30,50))
        overscan = OverscanInfo()
        overscan.setYOverscanDir()
        overscan.addChip(1)
        overscan.setMin(1, 20)
        overscan.setMax(1, 29)
        overscan.setOffset(1, 5)

        image[20:,10:14] *= 5
        regions = maskOverscanLines(image, overscan, 1)

        self.assertEquals(regions, [regionfile.Polygon([5,1,10,1,10,31,5,31])])


            


###################################################################
###################################################################


###########################
# METHODS FOR SCRIPT MODE
#############

def test():

    testcases = [TestOverscanInfo, TestFitOverscanRegion,
                 TestExtractOverscanRegion, TestRealBump,
                 TestCreateRegion, TestProcessChip,
                 TestRealDataNoDetect]
    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)

#################################

def main():

    parser = OptionParser(usage)
    parser.add_option('-b', '--buffer-size', dest='buffer',
                      help='Num rows around detected region to exclude',
                      type = int, default = 5)
    parser.add_option('-t', '--threshold', dest='threshold',
                      help='Detection threshold for stars in overscan region',
                      type = float, default = 3)
    parser.add_option('-w', '--bump-width', dest='bumpWidth',
                      help='Required width of a bump for detection (in pix)',
                      type = int, default = 2)

    (options, args) = parser.parse_args()

    if len(args) != 3:
        parser.print_help()
        sys.exit(1)

    maindir = args[0]
    dir     = args[1]
    prefix  = args[2]
    
    processDirectory(maindir, dir, prefix, 
                     buffer = options.buffer,
                     threshold = options.threshold,
                     bumpWidth = options.bumpWidth)

#################################

if __name__ == '__main__':


    if len(sys.argv) < 2 :
        print usage
        sys.exit(1)


        
    
    if sys.argv[1] == 'test':
        test()


    else:
        __bonn_logger_id__ = BonnLogger.addCommand('maskBadOverscans.py', 
                                                       sys.argv[1:])

        main()
        BonnLogger.updateStatus(__bonn_logger_id__, 0)
