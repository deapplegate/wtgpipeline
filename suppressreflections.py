#!/usr/bin/env python
#######################

'''
suppressreflections.py regiondir image1 image2 image3...

Given the locations of reflection rings around stars, this module removes and masks reflections and rings.

Each image needs a weight and flag file.

Star reflections are marked by ds9 circle regions. Stars are seperated by a non-circle region in the file.
'''

##########################

import unittest, sys, re, os, glob, tempfile, subprocess, regionfile as rf
import wcsregionfile as wrf
import astropy, astropy.io.fits as pyfits
import leastsq
import numpy as np
from optparse import OptionParser

#########################

__cvs_id__ = "$Id: suppressreflections.py,v 1.20 2010-05-12 19:35:29 dapple Exp $"

#################################################
### MAIN
#################################################

def main(argv = sys.argv):

    parser = OptionParser()

    parser.add_option('-m', '--mask', dest='mask', default=False, action='store_true')

    options, args = parser.parse_args(argv)

    regiondir = args[1]
    images = args[2:]

    print options.mask

    if options.mask:

        print 'masking!'

        for imagefile in images:
            print 'Processing %s' % imagefile
            
            weightfile, flagfile, regionbase = findAssociatedFiles(imagefile)
            regionfile = os.path.join(regiondir, regionbase)
            
            outimage, outweight, outflag = findOutfiles(imagefile, 'R')
            
            processMask(imagefile, weightfile, flagfile, regionfile,
                         outimage, outweight, outflag)

    else:
        for imagefile in images:

            print 'Processing %s' % imagefile

            weightfile, flagfile, regionbase = findAssociatedFiles(imagefile)
            regionfile = os.path.join(regiondir, regionbase)
            
            outimage, outweight, outflag = findOutfiles(imagefile, 'R')
            
            processImage(imagefile, weightfile, flagfile, regionfile,
                         outimage, outweight, outflag)

##################################################
### SITE SPECIFIC ASSUMPTIONS
##################################################

__sextractor_config_file__ = "photconf/suppressreflections.config.sex"

###########################

def findAssociatedFiles(filename):

    dirname, basefilename = os.path.split(filename)

    base, ext = os.path.splitext(basefilename)

    weightdir = '%s/../WEIGHTS' % dirname

    weightfile = os.path.normpath(os.path.join(weightdir, '%s.weight.fits' % base))
    flagfile = os.path.normpath(os.path.join(weightdir, '%s.flag.fits' % base))

    match = re.match('(.+?_\d+)\w*', base)
    if match is None:
        raise ValueError('Cannot recognize filename: %s' % base)
    root = match.group(1)
    regionfile = '%s.reg' % root


    return weightfile, flagfile, regionfile

################################

def findOutfiles(imagefile, extension):

    dirname, basefilename = os.path.split(imagefile)

    base, ext = os.path.splitext(basefilename)

    newbase = '%sR' % base

    outimage = '%s/%s.fits' % (dirname, newbase)

    weightdir = '%s/../WEIGHTS' % dirname

    outweight = os.path.normpath(os.path.join(weightdir, '%s.weight.fits' % newbase))
    outflag = os.path.normpath(os.path.join(weightdir, '%s.flag.fits' % newbase))


    return outimage, outweight, outflag



##################################################
# USER FUNCTIONS
##################################################

def createLinks(imagefile, weightfile, flagfile,
                outimage, outweight, outflag):

    if os.path.exists(outimage):
        os.remove(outimage)
    os.symlink(imagefile, outimage)

    if os.path.exists(outweight):
        os.remove(outweight)
    os.symlink(weightfile, outweight)
        
    if os.path.exists(outflag):
        os.remove(outflag)
    os.symlink(flagfile, outflag)
    return
    

def processImage(imagefile, weightfile, flagfile, regionfile, 
                 outimage, outweight, outflag):
    '''
    @brief Given input and output filenames, processes star subtraction and masking

    @param imagefile filename of input image
    @param weightfile filename of input weight image
    @param flagfile filename of input flag image
    @param regionfile filename of input region file detailing star reflection circles
    @param outimage filename for star subtracted image
    @param outweight filename for masked weight file
    @param outflag filename for masked flag file

    @returns none
    '''
    
    if not os.path.exists(regionfile):
        print 'Regionfile does not exist'
        createLinks(imagefile, weightfile, flagfile, outimage, outweight, outflag)
        return


    image, imageheader = loadImage(imagefile)

    stars = readRegionFile(open(regionfile).readlines(), image.shape)

    if len(stars) == 0:
        print 'No Stars in region file'
        createLinks(imagefile, weightfile, flagfile, outimage, outweight, outflag)
        return

    weights, weightheader = loadImage(weightfile)
    flags, flagheader = loadImage(flagfile)
    objectMask = createObjectMask(imagefile, weightfile, flagfile)

    mask = flags.copy()
    mask[objectMask > 0] = 1


    newimage = subtractStars(image, mask, stars, weight = weights, buffer = 20)

    newweight, newflag = maskStars(weights, flags, stars)

    saveImage(outimage, newimage, imageheader)
    saveImage(outweight, newweight)
    saveImage(outflag, newflag)
    
    
##########################

def processMask(imagefile, weightfile, flagfile, regionfile, 
                 outimage, outweight, outflag):
    '''
    @brief Given input and output filenames, processes star masking only

    @param imagefile filename of input image
    @param weightfile filename of input weight image
    @param flagfile filename of input flag image
    @param regionfile filename of input region file detailing star reflection circles
    @param outimage filename for star subtracted image
    @param outweight filename for masked weight file
    @param outflag filename for masked flag file

    @returns none
    '''
    
    weights, weightheader = loadImage(weightfile)
    flags, flagheader = loadImage(flagfile)

    mask = flags

    stars = readRegionFile(open(regionfile).readlines(), weights.shape)

    if len(stars) == 0:
        if os.path.exists(outweight):
            os.remove(outweight)
        os.symlink(weightfile, outweight)
        
        if os.path.exists(outflag):
            os.remove(outflag)
        os.symlink(flagfile, outflag)
        return


    newweight, newflag = maskStars(weights, flags, stars)

    saveImage(outweight, newweight)
    saveImage(outflag, newflag)
    
    
##########################

def createObjectMask(imagefile, weightfile, flagfile, workdir=None):
    '''
    @brief Runs source extractor to generate a mask for objects

    @param imagefile filename of input image
    @param weightfile filename of input weight image
    @param flagfile filename of input flag image
    @param workdir place to write temporary files

    @returns an image of 0,1's where 1 is a pixel occupied by an object in the original image
    '''

    objects = None

    try:

        deleteWorkdir = False
        if workdir is None:
            workdir = tempfile.mkdtemp()
            deleteWorkdir = True


        basename, ext = os.path.splitext(os.path.basename(imagefile))
        objectsfile = os.path.join(workdir, '%s_objs.fits' % basename)

        cmd = 'sex -c %(config)s %(imagefile)s -WEIGHT_IMAGE %(weightfile)s -FLAG_IMAGE %(flagfile)s -CHECKIMAGE_NAME %(objectsfile)s' % \
            {'config' : __sextractor_config_file__,
             'imagefile' : imagefile,
             'weightfile' : weightfile,
             'flagfile' : flagfile,
             'objectsfile' : objectsfile}

        subprocess.check_call([cmd], shell=True)

        objects = pyfits.open(objectsfile)[0].data
        objects[objects > 0] = 1
    


    finally:
        if deleteWorkdir and os.path.exists(workdir):
            toDelete = glob.glob('%s/*' % workdir)
            for file in toDelete:
                os.remove(file)
            os.rmdir(workdir)

        else:
            if os.path.exists(objectsfile):
                os.remove(objectsfile)

    return objects


##########################

commentline = re.compile('^#')

def readRegionFile(txtlines, imageSize):
    '''
    @brief Parses a list of strings into grouped stars

    @param txtlines a list of strings
    @param imageSize pyfits shape of associated image (NAXIS2,NAXIS1)

    @returns a list of stars, where each star is a list of Ring objects defining a star's reflections

    '''

    if type(txtlines) != type([]):
        txtlines = txtlines.splitlines()

    rings = [ Ring.fromCircle(x) for x in \
                  filter(lambda x: isinstance(x, rf.Circle), rf.parseRegionFile(txtlines))]

    stars = groupRings(rings)

    filteredStars = []
    for star in stars:
        bigRing = star[-1]
        if not (bigRing.x + bigRing.r < 0 or \
                    bigRing.x - bigRing.r > imageSize[1] or \
                    bigRing.y + bigRing.r < 0 or \
                    bigRing.y - bigRing.r > imageSize[0]):
            filteredStars.append(star)
            
        
    
    return filteredStars


############################

def constructReflectionModel(image, mask, rings, weight = None, buffer=50, background_radii=100):
    '''
    @brief Constructs reflection model for a star
    
    @param image input image to measure reflections from
    @param mask image where 1 is a bad pixel or an object
    @param rings a list of Ring objects characterizing one star
    @param weight a weight file for an image
    @param buffer radial distance around each ring to ignore when fitting the model

    @returns model an image of the star reflection model and background in the input image
    '''
    
    X,Y = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))

    if weight is None:
        weight = np.ones_like(image)

    mask = np.copy(mask)
    mask[weight < 1e-6 ] = 1

    dRs = [np.sqrt((X-r.x)**2 + (Y-r.y)**2) for r in rings]

    ######

    select = np.logical_and(mask == 0, np.logical_and(dRs[-1] > rings[-1].r+buffer,
                                                      dRs[-1] < rings[-1].r + background_radii))

    dr = dRs[-1][select]
    pix = image[select]
    curWeight = weight[select]
    aveBackground = np.sum(curWeight * pix) / np.sum(curWeight)

    #######

    levels = []
    for i in xrange(0, len(rings)-1):

        select = np.logical_and(mask == 0,np.logical_and(dRs[i] > rings[i].r + buffer,
                                                         dRs[i+1] < rings[i+1].r - buffer))

        dr = dRs[i][select]
        if dr.size == 0:
            levels.append((0,0))
            continue
        pix = image[select] - aveBackground
        curWeight = weight[select]
        params, isCon = leastsq.linear_leastsq(dr, pix, 1./np.sqrt(curWeight))
        levels.append(params)


    model = np.zeros_like(image)
    for i in xrange(1,len(rings)):
        insideRing = np.logical_and(dRs[i-1] > rings[i-1].r, dRs[i] < rings[i].r)
        model[insideRing] = dRs[i-1][insideRing]*levels[i-1][0] + levels[i-1][1]

    return model

#############################

def maskStars(weight, flag, stars, buffer=50):
    '''
    @brief masks out ring features in a weight and flag image

    @param weight weight image to mask (numpy 2d array)
    @param flag flag image to mask (numpy 2d array)
    @param stars list of stars, where each star is a list of Ring objects
    @param buffer radial range around each ring to mask

    @returns newweight, newflag  masked weight and flag images
    '''

    

    weight = weight.copy()
    flag = flag.copy()


    for rings in stars:

        X,Y = np.meshgrid(np.arange(weight.shape[1]), np.arange(weight.shape[0]))

        dRs = [np.sqrt((X-ring.x)**2 + (Y-ring.y)**2) for ring in rings]

        inRing1 = dRs[0] < (rings[0].r + buffer)
        weight[inRing1] = 0
        flag[inRing1] = 1



        for dR, ring in zip(dRs[1:], rings[1:]):
            
            inRing = np.logical_and(dR > (ring.r - buffer), dR < (ring.r + buffer))

            #weight[inRing] = 0
            flag[inRing] = 1


    return weight, flag

#############################

def subtractStars(image, flag, stars, weight = None, buffer=50):
    '''
    @brief removes star reflections and background from image by iterating over stars

    @params image image to model and remove star reflections from (numpy 2d array)
    @params flag image of 0,1's where a 1 is a bad pixel or object
    @params stars list of stars, where each star is a list of Ring objects marking reflections
    @params buffer size around each ring to ignore in modeling

    @returns image image with star reflections (and background) removed
    '''

    if weight is None:
        weight = np.ones_like(image)


    for i in xrange(len(stars)):
     
        otherstars = stars[0:i] + stars[i+1:]

        newweight, newflag = maskStars(weight, flag, otherstars, buffer)

        
        model = constructReflectionModel(image, newflag, stars[i], weight = newweight, buffer=buffer)
        image = image - model


    return image

########################################################
    


########################################################
### UTILITY CLASSES
########################################################

class Ring(rf.Circle):

    def __init__(self, x, y, r, **keywords):
        rf.Circle.__init__(self, (x,y),r,**keywords)

    def __getattr__(self, name):
        if name == 'x':
            return self.center[0]
        if name == 'y':
            return self.center[1]
        if name == 'r':
            return self.radius
        if name == 'tag':
            if 'tag' in self.attributes:
                return self.attributes['tag']
            else:
                return None
        return rf.Circle.__getattribute__(self, name)


    syntax = re.compile('circle\((.+?),(.+?),(.+?)\)')

    
    
    @classmethod
    def fromString(cls, txt):

        match = Ring.syntax.match(txt)



        if match is None:
            raise SyntaxError('Cannot translate into Ring: %s' % txt)

        return Ring(float(match.group(1)),
                    float(match.group(2)),
                    float(match.group(3)))

    @classmethod
    def fromCircle(cls, acircle):
        return cls(acircle.center[0], acircle.center[1], acircle.radius, **acircle.attributes)

    def __eq__(self, other):
        return self.x == other.x and \
            self.y == other.y and \
            self.r == other.r

    def __repr__(self):
        return '<Ring center=(%f,%f) radius=%f>' % (self.x, self.y, self.r)

    def contains(self, aring):

        dist = np.sqrt((self.x - aring.x)**2 + (self.y - aring.y)**2)

        return dist <= self.r - aring.r


##########################################################
### UTILITY FUNCTIONS
##########################################################


def loadImage(filename):

    image = pyfits.open(filename)[0]

    return image.data, image.header

##########################

def saveImage(filename, image, header = None):

    pyfits.PrimaryHDU(image, header=header).writeto(filename, overwrite=True)


############################

class RingConfusionException(Exception): pass

def groupRings(regions):

    sortedRings = sorted(regions, lambda x,y: cmp(x.r, y.r))

    stars = []

    for ring in sortedRings:

        matches = []
        tagmatches = []
        for star in stars:

            if ring.contains(star[-1]):

                if ring.tag is None:
                    matches.append(star)
                    continue

                tagConflict = False
                for starRing in star:

                    if starRing.tag is None:
                        continue
                    elif starRing.tag != ring.tag:
                        tagConflict = True
                        break
                    else:
                        tagmatches.append(star)
                        break

                if not tagConflict:
                    matches.append(star)
                    

        nmatches = len(matches)
        ntagmatches = len(tagmatches)

        if nmatches == 0:
            stars.append([ring])
        elif nmatches == 1:
            matches[0].append(ring)
        elif ntagmatches == 1:
            tagmatches[0].append(ring)
        else:
            raise RingConfusionException(ring)
        
            
    sortedStars = sorted(stars, lambda x,y: cmp(len(x), len(y)), reverse=True)



    return sortedStars

    


############################################################
### TESTING
############################################################

class TestGroupRings(unittest.TestCase):

    def testOneStar(self):

        rings = [Ring(919.4,3182.4,182.93164),
                 Ring(928.46667,3173.3333,69.593566),
                 Ring(910.33333,3182.4,351.79447)]

        stars = [[Ring(928.46667,3173.3333,69.593566),
                  Ring(919.4,3182.4,182.93164),
                  Ring(910.33333,3182.4,351.79447)]]

        self.assertEquals(stars, groupRings(rings))

    def testTwoStars(self):

        rings = [Ring(919.4,3182.4,182.93164),
                   Ring(910.33333,3182.4,351.79447),
                   Ring(846.86667,2176,148.45513),
                   Ring(837.8,2221.3333,305.67992),
                   Ring(828.73333,2212.2667,245.79471),
                   Ring(828.73333,2212.2667,528.04565),
                   Ring(928.46667,3173.3333,69.593566),]

        stars = [[Ring(846.86667,2176,148.45513),
                  Ring(828.73333,2212.2667,245.79471),
                  Ring(837.8,2221.3333,305.67992),
                  Ring(828.73333,2212.2667,528.04565)],
                 [Ring(928.46667,3173.3333,69.593566),
                  Ring(919.4,3182.4,182.93164),
                  Ring(910.33333,3182.4,351.79447)]]

        self.assertEquals(stars, groupRings(rings))

    def testOverlappingMinorStar(self):

        rings = [Ring(883.13333,2846.9333,80.859022),
                 Ring(901.26667,2837.8667,300.63893),
                 Ring(1390.8667,2846.9333,107.91074),
                 Ring(1399.9333,2810.6667,303.31271),
                 Ring(874.06667,2874.1333,666.68692)]

        stars = [[Ring(883.13333,2846.9333,80.859022),
                  Ring(901.26667,2837.8667,300.63893),
                  Ring(874.06667,2874.1333,666.68692)],
                 [Ring(1390.8667,2846.9333,107.91074),
                  Ring(1399.9333,2810.6667,303.31271)]]

        self.assertEquals(stars, groupRings(rings))

    def testSimpleAntiGroup(self):

        rings = [Ring(6658.8327,6419.3168,114.2888, tag='{Group 3}'),
                 Ring(5960.9529,6413.4276,1337.695, tag='{Group 2}')]

        stars = [[Ring(6658.8327,6419.3168,114.2888, tag='{Group 3}')],
                 [Ring(5960.9529,6413.4276,1337.695, tag='{Group 2}')]]

        self.assertEquals(stars, groupRings(rings))

    def testSimpleProGroup(self):

        rings = [Ring(6658.8327,6419.3168,114.2888),
                 Ring(6002.1779,6407.5383,174.68296, tag='{Group 2}'),
                 Ring(5960.9529,6413.4276,1337.695, tag='{Group 2}')]

        stars = [[Ring(6002.1779,6407.5383,174.68296, tag='{Group 2}'),
                  Ring(5960.9529,6413.4276,1337.695, tag='{Group 2}')],
                 [Ring(6658.8327,6419.3168,114.2888)]]

        self.assertEquals(stars, groupRings(rings))

    def testTagConflict(self):

        rings = [Ring(6658.8327,6419.3168,114.2888),
                 Ring(6002.1779,6407.5383,174.68296),
                 Ring(5960.9529,6413.4276,1337.695)]

        self.assertRaises(RingConfusionException, groupRings, rings)

        
    def testTagConflict_Tags(self):

        rings = [Ring(6658.8327,6419.3168,114.2888, tag='{Group 2}'),
                 Ring(6002.1779,6407.5383,174.68296, tag='{Group 2}'),
                 Ring(5960.9529,6413.4276,1337.695, tag='{Group 2}')]

        self.assertRaises(RingConfusionException, groupRings, rings)

    def testNonOverlappingTagConflict(self):

        regionfile = '''circle(239.85417,1271.2711,373.2043) # color=red width=2 tag={Group 3}
circle(213.98543,1246.2475,734.59645) # color=red width=2 tag={Group 3}
circle(192.45328,1225.4188,1051.7073) # color=red width=2 tag={Group 3}
circle(167.79821,1201.5693,1403.0933) # color=red width=2 tag={Group 3}
circle(-1584.7093,757.48331,373.2043) # color=red width=2 tag={Group 3}
circle(-1575.643,742.29722,734.59645) # color=red width=2 tag={Group 3}'''
        rings = [ Ring.fromCircle(rf.Circle.fromStr(x)) for x in regionfile.splitlines() ]

        stars = [rings[0:4], rings[4:]]

        self.assertEquals(stars, groupRings(rings))

        

        
    def testTripleStars_AntiGroup(self):

        
        rings = [Ring(5557.5371,6360.424,376.48289, tag='{Group 1}'),
                 Ring(5978.6207,6389.8704,388.99078),
                 Ring(6658.8327,6419.3168,114.2888, tag='{Group 3}'),
                 Ring(6620.5524,6398.7044,369.99343),
                 Ring(5525.1461,6333.9223,760.27046),
                 Ring(6002.1779,6407.5383,174.68296, tag='{Group 2}'),
                 Ring(5560.4817,6392.8151,138.11697),
                 Ring(5560.4817,6277.9741,1067.2162, tag='{Group 1}'),
                 Ring(5536.9246,6283.8634,1396.797, tag='{Group 1}'),
                 Ring(5960.9529,6413.4276,1337.695, tag='{Group 2}')]

        stars = [[Ring(5560.4817,6392.8151,138.11697),
                 Ring(5557.5371,6360.424,376.48289),
                 Ring(5525.1461,6333.9223,760.27046),
                 Ring(5560.4817,6277.9741,1067.2162),
                 Ring(5536.9246,6283.8634,1396.797)],
                 [Ring(6002.1779,6407.5383,174.68296),
                 Ring(5978.6207,6389.8704,388.99078),
                 Ring(5960.9529,6413.4276,1337.695)],
                 [Ring(6658.8327,6419.3168,114.2888),
                  Ring(6620.5524,6398.7044,369.99343)]]



        self.assertEquals(stars, groupRings(rings))


    def testTripleStars_AssociateNoTag(self):

        rings = [Ring(6658.8327,6419.3168,114.2888, tag='{Group 3}'),
                 Ring(6620.5524,6398.7044,369.99343),
                 Ring(6002.1779,6407.5383,174.68296, tag='{Group 2}'),
                 Ring(5560.4817,6392.8151,138.11697)]

        stars = [[Ring(6658.8327,6419.3168,114.2888, tag='{Group 3}'),
                  Ring(6620.5524,6398.7044,369.99343)],
                 [Ring(5560.4817,6392.8151,138.11697)],
                 [Ring(6002.1779,6407.5383,174.68296, tag='{Group 2}')]]

        grouped = groupRings(rings)

        self.assertEquals(stars, grouped)
                 
        
        

    def testContains(self):

        ringA = Ring(221.26667,1768,148.45513)
        ringB = Ring(710.86667,1786.1333,205.53195)
        ringC = Ring(1109.8,1731.7333,69.593566)
        ringD = Ring(1091.6667,1731.7333,351.79447)
        ringE = Ring(1481,1713.6,205.68956)

        self.failIf(ringA.contains(ringB))
        self.failIf(ringC.contains(ringA))
        self.failIf(ringB.contains(ringC))
        self.failIf(ringC.contains(ringB))
        self.failIf(ringC.contains(ringE))
        self.failUnless(ringD.contains(ringC))
        self.failIf(ringC.contains(ringD))

    def testTag(self):

        ringA = Ring(221.26667,1768,148.45513, tag='{Group 1}')

        self.assertEquals(ringA.tag, '{Group 1}')

    def testNoTag(self):
        
        ringA = Ring(221.26667,1768,148.45513)

        self.assertEquals(ringA.tag, None)
        


######################


class TestModel(unittest.TestCase):

    def testReturnType(self):

        imagesize = (512,128)
        model = constructReflectionModel(np.ones(imagesize), 
                                         np.zeros(imagesize), 
                                         [Ring(0,0,20), Ring(0,0,120)],
                                         buffer=1)

        self.assertEquals(model.shape, imagesize)
        

    ######################

    def testRecoverGradient(self):

        input = 2*np.ones((512, 128))

        x_star = np.array([120, 100])

        X,Y = np.meshgrid(np.arange(input.shape[1]), np.arange(input.shape[0]))
        dR = np.sqrt((X - x_star[0])**2 + (Y - x_star[1])**2)
        
        input[dR < 30] = 50
        select = np.logical_and(dR >= 30, dR < 100)
        input[select] = 15 + dR[select]*-.1

        rings = [Ring(x_star[0], x_star[1], 30), Ring(x_star[0], x_star[1], 100)]

        model = constructReflectionModel(input, np.zeros_like(input), rings, buffer=1)

        validTest = np.logical_and(dR > 30, np.logical_or(dR <99, dR > 101))
        saveImage('input.fits', input)
        saveImage('model.fits', model)
        self.assertTrue((np.abs(model[validTest] - input[validTest] + 2) < 1e-2).all())

    #########################

    def testMask(self):

        input = 2*np.ones((512, 128))

        mask = np.zeros_like(input)

        input[400:415, 100:120] = 1e15
        mask[400:415, 100:120] = 1

        x_star = np.array([120, 100])

        X,Y = np.meshgrid(np.arange(input.shape[1]), np.arange(input.shape[0]))
        dR = np.sqrt((X - x_star[0])**2 + (Y - x_star[1])**2)
        
        input[dR < 30] = 50
        select = np.logical_and(dR >= 30, dR < 100)
        input[select] = 15 + dR[select]*-.1

        rings = [Ring(x_star[0], x_star[1], 30), Ring(x_star[0], x_star[1], 100)]
        
        model = constructReflectionModel(input, mask, rings, buffer=1)

        validTest = np.logical_and(np.logical_and(dR > 30, 
                                                  np.logical_or(dR <99, 
                                                                dR > 101)),
                                   mask > 1)
                                   
        self.assertTrue((np.abs(model[validTest] - input[validTest]) < 1e-2).all())

    ###################

    def testWeightFile(self):

        input = 2*np.ones((512, 128))

        mask = np.zeros_like(input)
        weight = np.ones_like(input)

        input[400:415, 100:120] = 10000
        weight[400:415, 100:120] = .0003



        x_star = np.array([120, 100])

        X,Y = np.meshgrid(np.arange(input.shape[1]), np.arange(input.shape[0]))
        dR = np.sqrt((X - x_star[0])**2 + (Y - x_star[1])**2)
        
        input[dR < 30] = 50
        select = np.logical_and(dR >= 30, dR < 100)
        input[select] = 15 + dR[select]*-.1

        rings = [Ring(x_star[0], x_star[1], 30), Ring(x_star[0], x_star[1], 100)]
        
        model = constructReflectionModel(input, mask, rings, weight = weight, buffer=1)

        expected = np.copy(input)
        expected[weight != 1] = 2

        validTest = np.logical_and(np.logical_and(dR > 30, 
                                                  np.logical_or(dR <99, 
                                                                dR > 101)),
                                   mask == 0)

        
        self.assertTrue((np.abs(model[validTest] - expected[validTest] + 2) < .1).all())

        

    ####################

class TestStarMasking(unittest.TestCase):

    def testBasic(self):

        weight = np.ones((512, 128))
        flag = np.zeros_like(weight)
        x_star = np.array([120, 100])
        rings = [Ring(x_star[0], x_star[1], 30), Ring(x_star[0], x_star[1], 100)]

        X,Y = np.meshgrid(np.arange(weight.shape[1]), np.arange(weight.shape[0]))
        dR = np.sqrt((X - x_star[0])**2 + (Y - x_star[1])**2)

        insideR1 = dR < rings[0].r
        ring2 = np.logical_and(dR > rings[1].r - 2, dR < rings[1].r + 2)

        newweight, newflag = maskStars(weight, flag, [rings], buffer=2)


        #self.assertTrue((newweight[ring2] == 0).all())
        self.assertTrue((newweight[insideR1] == 0).all())
        self.assertTrue((newflag[ring2] == 1).all())
        self.assertTrue((newflag[insideR1] == 1).all())

    ###############

    def testNoOverwrite(self):

        weight = np.ones((512, 128))
        flag = np.zeros_like(weight)
        x_star = np.array([120, 100])
        rings = [Ring(x_star[0], x_star[1], 30), Ring(x_star[0], x_star[1], 100)]

        X,Y = np.meshgrid(np.arange(weight.shape[1]), np.arange(weight.shape[0]))
        dR = np.sqrt((X - x_star[0])**2 + (Y - x_star[1])**2)

        insideR1 = dR < rings[0].r
        ring2 = np.logical_and(dR > rings[1].r - 2, dR < rings[1].r + 2)

        newweight, newflag = maskStars(weight, flag, [rings], buffer=2)

        self.assertTrue((weight == 1).all())
        self.assertTrue((flag == 0).all())

    ###################

    def testMultipleStars(self):

        weight = np.ones((512, 128))
        flag = np.zeros_like(weight)

        expectedweight = np.ones_like(weight)
        expectedflag = np.zeros_like(weight)

        x_star1 = np.array([120, 100])

        X,Y = np.meshgrid(np.arange(weight.shape[1]), np.arange(weight.shape[0]))
        dR = np.sqrt((X - x_star1[0])**2 + (Y - x_star1[1])**2)
        
        flag[dR < 5] = 1
        expectedweight[dR < 35] = 0
        expectedflag[dR < 35] = 1

        select = np.logical_and(dR >= 30, dR < 100)
        inRing = np.logical_and(dR > 95, dR < 105)
        #expectedweight[inRing] = 0
        expectedflag[inRing] = 1

        stars = [[Ring(x_star1[0], x_star1[1], 30), Ring(x_star1[0], x_star1[1], 100)]]

        x_star2 = np.array([70, 140])
        dR = np.sqrt((X - x_star2[0])**2 + (Y - x_star2[1])**2)
        
        flag[dR < 5] = 1
        expectedweight[dR < 20] = 0
        expectedflag[dR < 20] = 1

        select = np.logical_and(dR >= 15, dR < 30)
        inRing = np.logical_and(dR > 25, dR < 35)
        #expectedweight[inRing] = 0
        expectedflag[inRing] = 1

        stars.append([Ring(x_star2[0], x_star2[1], 15), Ring(x_star2[0], x_star2[1], 30)])


        newweight, newflag = maskStars(weight, flag, stars, buffer=5)

        self.assertTrue((expectedweight == newweight).all())
        self.assertTrue((expectedflag == newflag).all())
        
    
#######################

class TestSubtractStars(unittest.TestCase):

    def testBasic(self):

        image = np.zeros((4080,2000))
        flag = np.zeros_like(image)

        stars = [[Ring(169.62191,2275.477,381.84674),
                  Ring(260.92933,2318.7279,709.7176),
                  Ring(337.81979,2386.0071,969.41448),
                  Ring(222.4841,2361.9788,1424.1761)]]

        newimage = subtractStars(image, flag, stars, buffer=1)

        self.assertEquals(newimage.shape, image.shape)

        ##################

    def testRemoveSimpleReflectionsAndMask(self):

        image = 15*np.ones((512, 128)) 
        flag = np.zeros_like(image)

        x_star = np.array([120, 100])

        X,Y = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
        dR = np.sqrt((X - x_star[0])**2 + (Y - x_star[1])**2)
        
        image[dR < 30] = 50
        select = np.logical_and(dR >= 30, dR < 100)
        image[select] = 15 + dR[select]*-.1

        stars = [[Ring(x_star[0], x_star[1], 30), Ring(x_star[0], x_star[1], 100)]]

        newimage = subtractStars(image, flag, stars, buffer=5)


        validTest = np.logical_and(dR > 35, np.logical_or(dR <95, dR > 105))
        validMask = np.logical_or(dR < 29, np.logical_and(dR >97, dR < 103))

        saveImage('test.fits', newimage)
        
        self.assertTrue((np.abs(newimage[validTest] - 15) < 1e-2).all())


    #######################

    def testRemoveMultipleReflections(self):

        image = 10*np.ones((512, 128)) 
        flag = np.zeros_like(image)

        expectedflag = np.zeros_like(image)

        x_star1 = np.array([120, 100])

        X,Y = np.meshgrid(np.arange(image.shape[1]), np.arange(image.shape[0]))
        dR = np.sqrt((X - x_star1[0])**2 + (Y - x_star1[1])**2)
        
        image[dR < 30] = 50
        flag[dR < 5] = 1
        expectedflag[dR < 35] = 1

        select = np.logical_and(dR >= 30, dR < 100)
        image[select] = 15 + dR[select]*-.1
        inRing = np.logical_and(dR > 95, dR < 105)
        expectedflag[inRing] = 1

        stars = [[Ring(x_star1[0], x_star1[1], 30), Ring(x_star1[0], x_star1[1], 100)]]

        x_star2 = np.array([70, 140])
        dR = np.sqrt((X - x_star2[0])**2 + (Y - x_star2[1])**2)
        
        image[dR < 15] = 25
        flag[dR < 5] = 1
        expectedflag[dR < 20] = 1

        select = np.logical_and(dR >= 15, dR < 30)
        image[select] = image[select] + 2 + dR[select]*-.05
        inRing = np.logical_and(dR > 25, dR < 35)
        expectedflag[inRing] = 1

        stars.append([Ring(x_star2[0], x_star2[1], 15), Ring(x_star2[0], x_star2[1], 30)])


        newimage = subtractStars(image, flag, stars, buffer=5)

        self.assertTrue((np.abs(newimage[expectedflag == 0] - 10) < 1).all())

        

        

#################################

class TestInterpretRegions(unittest.TestCase):

    def testAssociateStars(self):

        regiontxt='''
# Region file format: DS9 version 4.0
# Filename: /u/ki/dapple/subaru/MACS1149+22/W-J-V/SCIENCE/coadd_MACS1149+22_all/coadd.fits
global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source
physical
circle(5478.0318,6684.3345,373.77281) # color=red width=2 tag={Group 1}
circle(5480.9764,6654.8881,736.84446) # color=red width=2 tag={Group 1}
circle(5480.9764,6628.3863,1055.499) # color=red width=2 tag={Group 1}
circle(4637.0442,5908.6345,202.03205) # color=red width=2 tag={Group 2}
circle(4652.2286,5891.1618,373.77281) # color=red width=2 tag={Group 2}
circle(4645.133,5861.7154,736.84446) # color=red width=2 tag={Group 2}
circle(5466.6878,6575.3828,1418.2524) # color=red width=2 tag={Group 1}
circle(8724.6446,6374.247,202.03205) # color=red width=2 tag={Group 4}
circle(8655.7426,6332.9289,373.77281) # color=red width=2 tag={Group 4}
circle(8631.0768,6300.9724,736.84446) # color=red width=2 tag={Group 4}
circle(2234.9358,1767.0683,179.85811) # color=red width=2 tag={Group 6}
circle(2275.2206,1834.9369,373.77281) # color=red width=2 tag={Group 6}
circle(2345.9362,1888.3218,736.84446) # color=red width=2 tag={Group 6}
circle(7611.5659,1169.7763,373.77281) # color=red width=2 tag={Group 5}
circle(7561.7997,1243.2415,736.84446) # color=red width=2 tag={Group 5}
circle(7544.2294,1322.1614,1055.499) # color=red width=2 tag={Group 5}
circle(4205.3173,9036.1446,139.52686) # color=red width=2 tag={Group 3}
circle(4225.5218,8976.0012,373.77281) # color=red width=2 tag={Group 3}
circle(7464.6798,1402.19,1418.2524) # color=red width=2 tag={Group 5}
'''

        stars = [[Ring(5478.0318,6684.3345,373.77281),
                  Ring(5480.9764,6654.8881,736.84446),
                  Ring(5480.9764,6628.3863,1055.499), 
                  Ring(5466.6878,6575.3828,1418.2524)],
                 [Ring(4637.0442,5908.6345,202.03205),
                  Ring(4652.2286,5891.1618,373.77281),
                  Ring(4645.133,5861.7154,736.84446)], 
                 [Ring(8724.6446,6374.247,202.03205),  
                  Ring(8655.7426,6332.9289,373.77281), 
                  Ring(8631.0768,6300.9724,736.84446)], 
                 [Ring(2234.9358,1767.0683,179.85811), 
                  Ring(2275.2206,1834.9369,373.77281), 
                  Ring(2345.9362,1888.3218,736.84446)], 
                 [Ring(7611.5659,1169.7763,373.77281), 
                  Ring(7561.7997,1243.2415,736.84446), 
                  Ring(7544.2294,1322.1614,1055.499),  
                  Ring(7464.6798,1402.19,1418.2524)],
                 [Ring(4205.3173,9036.1446,139.52686), 
                  Ring(4225.5218,8976.0012,373.77281)]]
        
        parsedStars = readRegionFile(regiontxt,(10000,10000))

        self.assertEquals(len(stars), len(parsedStars))


    #################

    def testFilterOffChipStars(self):

        regiontxt='''
# Region file format: DS9 version 4.0
# Filename: /u/ki/dapple/subaru/MACS1149+22/W-J-V/SCIENCE/coadd_MACS1149+22_all/coadd.fits
global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source
physical
circle(5478.0318,6684.3345,373.77281) # color=red width=2 tag={Group 1}
circle(5480.9764,6654.8881,736.84446) # color=red width=2 tag={Group 1}
circle(5480.9764,6628.3863,1055.499) # color=red width=2 tag={Group 1}
circle(5466.6878,6575.3828,1418.2524) # color=red width=2 tag={Group 1}
circle(4652.228,5891.1618,373.77281) # color=red width=2 tag={Group 2}
circle(4645.133,5861.7154,736.84446) # color=red width=2 tag={Group 2}
circle(-5000,2000,2.03205) # color=red width=2 tag={Group 4}
circle(-5000,2000,373.77281) # color=red width=2 tag={Group 4}
circle(-5000,2000,736.84446) # color=red width=2 tag={Group 4}
'''

        parsedStars = readRegionFile(regiontxt, imageSize=(10000,10000))


        self.assertEquals(len(parsedStars), 2)

        self.assertEquals(parsedStars[0][0].x,5478.0318 )
        self.assertEquals(parsedStars[1][0].x,4652.228 )

        

#####################################

class TestLoadImages(unittest.TestCase):

    def testFindAssociated(self):

        filename = 'SCIENCE/SUPA0011008_3OCFS.fits'

        weightfile, flagfile, regionfile = findAssociatedFiles(filename)

        self.assertEquals(weightfile, 'WEIGHTS/SUPA0011008_3OCFS.weight.fits')
        self.assertEquals(flagfile, 'WEIGHTS/SUPA0011008_3OCFS.flag.fits')
        self.assertEquals(regionfile,'SUPA0011008_3.reg')


    ##########

    def testFindOutFiles(self):

        imagefile = 'SCIENCE/SUPA0011008_3OCFS.fits'
        ext = 'R'

        outimage, outweight, outflag = findOutfiles(imagefile, ext)

        self.assertEquals(outimage, 'SCIENCE/SUPA0011008_3OCFSR.fits')
        self.assertEquals(outweight, 'WEIGHTS/SUPA0011008_3OCFSR.weight.fits')
        self.assertEquals(outflag, 'WEIGHTS/SUPA0011008_3OCFSR.flag.fits')
                          

#################

class TestObjectSubtraction(unittest.TestCase):

    def setUp(self):
        self.shape = (200,100)
        image = np.ones(self.shape)
        weight = np.ones_like(image)
        flag = np.zeros_like(image)

        image[100:105,50:62] = 25

        self.object = image == 25
        
        def writeImage(image, name):
            if not os.path.exists(name):
                pyfits.PrimaryHDU(image).writeto(name)

        self.workdir = 'suppressreflections_tmp'
        if not os.path.exists(self.workdir):
            os.mkdir(self.workdir)

        self.imagename = os.path.join(self.workdir, 'suppressreflections_image.fits')
        self.weightname = os.path.join(self.workdir, 'suppressreflections_weight.fits')
        self.flagname = os.path.join(self.workdir, 'suppressreflections_flag.fits')
        writeImage(image, self.imagename )
        writeImage(weight, self.weightname)
        writeImage(flag, self.flagname)
        


    ##########

    def tearDown(self):

        if os.path.exists(self.workdir):

            toDelete = glob.glob('%s/*' % self.workdir)

            for file in toDelete:
                os.remove(file)

            os.rmdir(self.workdir)
        


    ############

    def testCreateObjectMask(self):

        
        noobjs_flag = createObjectMask(self.imagename, 
                                       self.weightname, 
                                       self.flagname, 
                                       workdir = self.workdir)

        workfiles = glob.glob('%s/*' % self.workdir)
        self.assertEquals(len(workfiles), 3)

        self.assertEquals(noobjs_flag.shape, self.shape)
        
        self.assertTrue((noobjs_flag[np.logical_not(self.object)] == 0).all())
        self.assertTrue((noobjs_flag[self.object] == 1).all())

#######################


def test():

    testcases = [TestModel, TestInterpretRegions, TestSubtractStars, TestStarMasking, TestLoadImages, TestObjectSubtraction, TestGroupRings] 

    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)


#############################################
### COMMAND LINE
##############################################

if __name__ == '__main__':

    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        test()
    else:
        main()
