#!/usr/bin/env python
#######################

import os, sys, unittest, re, optparse as op, glob
import astropy.io.fits as pyfits
import wcsregionfile as wrf, wcsconvertregions as wcr

#######################

__cvs_id__ = "$Id: transferMasks.py,v 1.2 2010-04-03 00:37:26 dapple Exp $"

#######################

def flatten(l):
  out = []
  for item in l:
    if isinstance(item, (list, tuple)):
      out.extend(flatten(item))
    else:
      out.append(item)
  return out

#######################

def sortImages(files):

    chips = {}

    for file in files:

        chip = file.chip

        if chip not in chips:
            chips[chip] = {}
        
        rotation = file.header['ROTATION']

        if rotation not in chips[chip]:
            chips[chip][rotation] = []

        chips[chip][rotation].append(file)

    return chips

######################

def transferRegions(sourceRegions, destinationImages):

    outputRegions = []

    for image in destinationImages:

        outputRegions.append([ x.convertTo(image.wcs) for x in sourceRegions ])

    return outputRegions

######################

def processImages(sourcefiles, destinationfiles, inputRegionDir, outputRegionDir):

    print 'a'

    sourceImages = [ loadImage(filename, inputRegionDir) for filename in sourcefiles ]


    print 'b'

    destinationImages = [ loadImage(filename, outputRegionDir) for filename in destinationfiles ]

    print 'c'

    sortedSources = sortImages(sourceImages)

    sortedDestinations = sortImages(destinationImages)


    for chip, rotations in sortedSources.iteritems():

        print chip

        for rotation, sources in rotations.iteritems():

            print rotation

            source = sources[0]

            if chip in sortedDestinations and rotation in sortedDestinations[chip]:
              destinations = sortedDestinations[chip][rotation]

              for destination in destinations:
                wcr.processConversion(source.regions, destination.name, destination.scampfile, destination.regionfile)



########################

def main(argv = sys.argv):

    parser = op.OptionParser()

    parser.add_option('-i', '--input-regiondir', dest='inputRegionDir')
    parser.add_option('-d', '--destination-regiondir', dest='destinationRegionDir')
    parser.add_option('-s', '--source', dest='sourcefiles')

    options, args = parser.parse_args(argv)

    sourcefiles = flatten([glob.glob(x) for x in options.sourcefiles.split()])

    if len(sourcefiles) == 0:
        print "Cannot find source files!"
        sys.exit(1)

    destinationfiles = args[1:]

    processImages(sourcefiles, destinationfiles, options.inputRegionDir, options.destinationRegionDir)

    
########################

extension_regex = re.compile('_\d\d?(\w+)\.')

def loadImage(filename, regionDir):

    match = extension_regex.search(filename)
    ext = match.group(1)

    scampfile, regionfile = wcr.findLocalFiles(filename, ext, regionDir)

    header = pyfits.getheader(filename)

    wcs = wcr.constructImageWCS(filename, scampfile)

    return Image(filename, header, wcs, regionfile, scampfile)


#######################

class Image(object):

    def __init__(self, name, header = None, wcs = None, regionfile = None, scampfile = None):
        self.name = name
        self.header = header
        self.wcs = wcs
        self.regionfile = regionfile
        self.regions = None
        self.originalRegions = False
        self.scampfile = scampfile

        if self.regionfile is not None and os.path.exists(self.regionfile):
            self.regions = filter(lambda x: x is not None, wrf.parseRegionFile(open(self.regionfile).readlines(), self.wcs))
            self.originalRegions = True
        
        self.chip = self._findChip()

    ##########

    chip_regex = re.compile('_(\d\d?)')

    def _findChip(self):

        match = Image.chip_regex.search(self.name)
        
        return int(match.group(1))

    ###########

    def saveRegions(self):
        
        if self.regions is None:
            return
        
        assert(not self.originalRegions)
        wrf.writeRegionFile(self.regionfile, self.regions)
        

    

########################

class TestTransferMasks(unittest.TestCase):

    def testSortImages(self):

        files = [ Image('SUPA001_1OCFS.fits', header={'ROTATION' : 0}),
                  Image('SUPA002_1OCFS.fits', header={'ROTATION' : 0}),
                  Image('SUPA003_1OCFS.fits', header={'ROTATION' : 1}),
                  Image('SUPA004_2OCFS.fits', header={'ROTATION' : 0}) ]
                  
        sorted = sortImages(files)

        self.assertTrue(1 in sorted)
        self.assertTrue(0 in sorted[1])
        self.assertEquals(len(sorted[1][0]), 2)

        chip1_rot0 = [ x.name for x in sorted[1][0] ]
        self.assertTrue(files[0].name in chip1_rot0)
        self.assertTrue(files[1].name in chip1_rot0)

        self.assertEquals(len(sorted[1][1]), 1)
        self.assertEquals(sorted[1][1][0].name, files[2].name)

        
        self.assertTrue(2 in sorted)
        self.assertEquals(files[3].name, sorted[2][0][0].name)

    ###############

    def testGetChip(self):

        animage = Image('SUPA001_1OCFS.fits')

        self.assertEquals(animage.chip, 1)

    ################


        
        
    

#######################

def test():

    testcases = [TestTransferMasks]
    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)

########################

if __name__ == '__main__':

    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        test()
    else:
        main()

