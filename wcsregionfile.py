#!/usr/bin/env python
#######################

import sys, unittest, inspect, tempfile, os
import astropy.io.fits as pyfits, pywcs
import numpy as np
import regionfile as rf

#########################

__cvs_id__ = "$Id: wcsregionfile.py,v 1.7 2009-12-15 02:42:58 dapple Exp $"

#########################

def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]

    From: http://kogs-www.informatik.uni-hamburg.de/~meine/python_tricks"""

    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring) and not isinstance(el, rf.Region):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

#########################

class BoundBox(object):
    def __init__(self, xbounds, ybounds):

        self.x = xbounds
        self.y = ybounds

    def __str__(self):
        return str((self.x, self.y))

#########################

class Point(rf.Point):

    def __init__(self, *args):

        if len(args) == 1 and isinstance(args[0], type(np.ones(0))) and args[0].shape == (1,2):
            rf.Point.__init__(self, args[0][0])
        
        else:

            rf.Point.__init__(self, *args)

    #############

    def wcs(self):

        return np.array([self])
            
    ##############
        
    def convert(self, wcs1, wcs2):

        return Point(wcs2.wcs_sky2pix(wcs1.all_pix2sky(self.wcs(), 1), 1))

#########################


class Circle(rf.Circle):

    def __init__(self, wcs, *args, **keywords):

        if len(args) == 1:
            acircle = args[0]
            rf.Circle.__init__(self, acircle.center, acircle.radius, acircle.attributes)
        else:
            rf.Circle.__init__(self, *args,**keywords)

        self.wcs = wcs
        self.center = Point(self.center)

    ###############

    def convertTo(self, newwcs):

        radiuspoint = Point(self.center.wcs() + self.radius*np.array([[1,0]]))

        newcenter = self.center.convert(self.wcs, newwcs)
        newradiuspoint = radiuspoint.convert(self.wcs, newwcs)

        dx = newradiuspoint.wcs() - newcenter.wcs()
        dr = np.sqrt(np.sum(dx**2))
        newradius = float(np.sqrt(np.sum(dr**2)))

        return Circle(newwcs, newcenter, newradius, self.attributes)

    #################

    def __eq__(self, other):

        if self.wcs == other.wcs:
            return rf.Circle.__eq__(self, other)

        otherprime = other.convertTo(self.wcs)

        return (np.abs(otherprime.center.wcs() - self.center.wcs()) < 1).all() and \
            (np.abs(otherprime.radius - self.radius) < 1).all()

    ###################

    def boundingBox(self):

        return BoundBox((self.center[0] - self.radius, self.center[0] + self.radius),
                        (self.center[1] - self.radius, self.center[1] + self.radius))

    ####################

    def inChip(self, buffer=10):

        boundingBox = self.boundingBox()

        naxis1 = self.wcs.naxis1
        naxis2 = self.wcs.naxis2

        return boundingBox.x[1] > -buffer and \
            boundingBox.x[0] < naxis1 + buffer and \
            boundingBox.y[1] > -buffer and \
            boundingBox.y[0] < naxis2 + buffer

    ########################



#######################

class Line(rf.Line):

    def __init__(self, wcs, *args):

        if len(args) == 1:
            aline = args[0]
            p1 = aline.p1
            p2 = aline.p2
        else:
            p1 = args[0]
            p2 = args[1]
        
        rf.Line.__init__(self, p1, p2)
        self.wcs = wcs
        self.p1 = Point(p1)
        self.p2 = Point(p2)

    ###############

    def convertTo(self, newwcs):

        newp1 = self.p1.convert(self.wcs, newwcs)
        newp2 = self.p2.convert(self.wcs, newwcs)

        return Line(newwcs, newp1, newp2)


#########################

def convertToWCS(region, wcs):

    if isinstance(region, rf.Circle):
        return Circle(wcs, region)
    if isinstance(region, rf.Line):
        return Line(wcs, region)
    return None
    

    

#########################

class FileBuffer(object):
    def __init__(self, txt):
        self.txt = txt.splitlines()
    def readlines(self):
        return self.txt[:-1]

#########################

def parseRegionFile(txtlines, wcs):

    regions = rf.parseRegionFile(txtlines)

    return [ convertToWCS(region, wcs) for region in regions ]

#########################

def writeRegionFile(filename, regions, overwrite = True):

    rf.writeRegionFile(filename, regions, overwrite = overwrite)


##########################

wcs1_txt = '''SIMPLE  =                    T / This is a FITS file
BITPIX  =                  -32 /
NAXIS   =                    2 /
NAXIS1  =                10000 / Number of pixels along this axis
NAXIS2  =                10000 / Number of pixels along this axis
EXTEND  =                    T / This file may contain FITS extensions
EQUINOX =            2000.0000 / Mean equinox
RADECSYS= 'FK5     '           / Astrometric system
CTYPE1  = 'RA---TAN'           / WCS projection type for this axis
CUNIT1  = 'deg     '           / Axis unit
CRVAL1  =      2.600700000E+02 / World coordinate on this axis
CRPIX1  =                 5000 / Reference pixel on this axis
CDELT1  =     -5.555555638E-05 / Pixel step along this axis
CTYPE2  = 'DEC--TAN'           / WCS projection type for this axis
CUNIT2  = 'deg     '           / Axis unit
CRVAL2  =      3.560750000E+01 / World coordinate on this axis
CRPIX2  =                 5000 / Reference pixel on this axis
CDELT2  =      5.555555638E-05 / Pixel step along this axis
FGROUPNO=                    1 / SCAMP field group label                       
END
'''

wcs1 = pywcs.WCS(pyfits.Header(txtfile=FileBuffer(wcs1_txt)))


wcs2_txt = '''SIMPLE  =                    T / This is a FITS file
BITPIX  =                  -32 /
NAXIS   =                    2 /
NAXIS1  =                 2000 / Number of pixels along this axis
NAXIS2  =                 4080 / Number of pixels along this axis
EXTEND  =                    T / This file may contain FITS extensions
EQUINOX =            2000.0000 / Mean equinox                                  
RADECSYS= 'FK5     '           / Astrometric system                            
CTYPE1  = 'RA---TAN'           / WCS projection type for this axis             
CTYPE2  = 'DEC--TAN'           / WCS projection type for this axis             
CUNIT1  = 'deg     '           / Axis unit                                     
CUNIT2  = 'deg     '           / Axis unit                                     
CRVAL1  =      2.600863484E+02 / World coordinate on this axis                 
CRVAL2  =      3.561470142E+01 / World coordinate on this axis                 
CRPIX1  =      3.150253241E+03 / Reference pixel on this axis                  
CRPIX2  =     -3.165874081E+01 / Reference pixel on this axis                  
CD1_1   =      1.389101775E-07 / Linear projection matrix                      
CD1_2   =      5.560568528E-05 / Linear projection matrix                      
CD2_1   =      5.572426341E-05 / Linear projection matrix                      
CD2_2   =      2.107580493E-07 / Linear projection matrix                      
PV1_0   =     -5.866337489E-04 / Projection distortion parameter               
PV1_1   =      1.010794632E+00 / Projection distortion parameter               
PV1_2   =     -6.170192876E-03 / Projection distortion parameter               
PV1_4   =     -1.199707133E-02 / Projection distortion parameter               
PV1_5   =      1.553850659E-02 / Projection distortion parameter               
PV1_6   =     -2.671488395E-02 / Projection distortion parameter               
PV1_7   =     -1.156355435E-01 / Projection distortion parameter               
PV1_8   =     -3.078435348E-02 / Projection distortion parameter               
PV1_9   =     -9.668949647E-02 / Projection distortion parameter               
PV1_10  =     -6.791696393E-02 / Projection distortion parameter               
PV2_0   =      1.037374299E-03 / Projection distortion parameter               
PV2_1   =      1.010348756E+00 / Projection distortion parameter               
PV2_2   =     -4.799733132E-03 / Projection distortion parameter               
PV2_4   =      2.926603439E-02 / Projection distortion parameter               
PV2_5   =     -1.324969193E-02 / Projection distortion parameter               
PV2_6   =      6.701375024E-03 / Projection distortion parameter               
PV2_7   =     -6.698976807E-02 / Projection distortion parameter               
PV2_8   =     -4.046026651E-02 / Projection distortion parameter               
PV2_9   =     -1.156380299E-01 / Projection distortion parameter               
PV2_10  =     -1.133623389E-02 / Projection distortion parameter
FGROUPNO=                    1 / SCAMP field group label                       
END
'''

wcs2 = pywcs.WCS(pyfits.Header(txtfile=FileBuffer(wcs2_txt)))


######################

class TestPoint(unittest.TestCase):

    def testFlatten(self):

        self.assertEquals(flatten([1, 2, [3,4], (5,6)]), [1,2,3,4,5,6])

    def testInheritance(self):

        apoint = Point((15, 27))

        self.assertTrue(isinstance(apoint, rf.Point))

    def testWCSFormat(self):
        
        apoint = Point((15, 27))

        self.assertTrue((apoint.wcs() == np.array([[15, 27]])).all())


    def testConvertForward(self):

        p1 = Point(2264.89, 2982.26)
        p2 = p1.convert(wcs1, wcs2)

        expected = np.array([[1001., 2465.48]])

        self.assertTrue((np.abs(p2.wcs() - expected) < 2).all())

        

######################


class TestCircle(unittest.TestCase):

    def setUp(self):
        self.p1 = Point([2264.89, 2982.26])
        self.rad1 = 365.23
        self.p2 = Point([1001., 2465.48])
        self.rad2 = 368.875
    

    def testInheritance(self):
        acircle = Circle(wcs1, (100,200), 15)

        self.assertTrue(isinstance(acircle.center, Point))
        self.assertEquals(acircle.wcs, wcs1)
        self.assertEquals(acircle.center, Point((100,200)))
        self.assertEquals(acircle.radius, 15)
        self.assertTrue(isinstance(acircle, rf.Circle))

    def testConvertCircle_checkforward(self):
        acircle = Circle(wcs2, self.p2, self.rad2)

        newcircle = acircle.convertTo(wcs1)


        self.assertTrue(isinstance(newcircle, Circle))
        self.assertTrue((np.abs(self.p1.wcs() - newcircle.center.wcs()) < 2).all())

        self.assertTrue(np.abs(newcircle.radius - self.rad1) < 5)

        self.assertEquals(newcircle.wcs, wcs1)


    def testConvertCircle_checkbackward(self):

        acircle = Circle(wcs1, self.p1, self.rad1)

        newcircle = acircle.convertTo(wcs2)

        self.assertTrue(isinstance(newcircle, Circle))
        self.assertTrue((np.abs(self.p2.wcs() - newcircle.center.wcs()) < 2).all())

        self.assertTrue(np.abs(newcircle.radius - self.rad2) < 5)

        self.assertEquals(newcircle.wcs, wcs2)

    def testEquals(self):

        circleA = Circle(wcs1, self.p1, self.rad1)
        circleB = Circle(wcs1, self.p1, self.rad1)
        circleC = Circle(wcs1, self.p2, self.rad2)
        circleD = circleA.convertTo(wcs2)


        self.assertEquals(circleA, circleB)
        self.assertNotEquals(circleA, circleC)
        self.assertEquals(circleA, circleD)

    def testBoundingBox(self):

        circleA = Circle(wcs1, self.p1, self.rad1)

        boundingBox = circleA.boundingBox()

        self.assertEquals(boundingBox.x, (self.p1[0] - self.rad1, self.p1[0] + self.rad1))
        self.assertEquals(boundingBox.y, (self.p1[1] - self.rad1, self.p1[1] + self.rad1))

    def testInChip(self):
        
        circleA = Circle(wcs2, self.p2, self.rad2)

        self.assertTrue(circleA.inChip())

        circleB = Circle(wcs2, (-3000,500), self.rad2)

        self.assertFalse(circleB.inChip())

    def testFromRegion(self):

        acircle = rf.Circle((1500, 300), 15)

        wcscircle = Circle(wcs1, acircle)

        self.assertEquals(acircle.center, wcscircle.center)
        self.assertEquals(acircle.radius, wcscircle.radius)
        self.assertEquals(wcscircle.wcs, wcs1)




#######################

class TestLine(unittest.TestCase):

    def setUp(self):
        
        self.line1 = rf.Line((1553.94, 2476.91), (1586.00, 2487.04))
        self.line2 = rf.Line((485.94, 3174.96), (495.98, 3141.97))

    def testInheritance(self):
        aline = Line(wcs1, (100,200), (15, 25))

        self.assertTrue(isinstance(aline.p1, Point))
        self.assertTrue(isinstance(aline.p2, Point))
        self.assertEquals(aline.wcs, wcs1)
        self.assertEquals(aline.p1, Point((100,200)))
        self.assertEquals(aline.p2, (15,25))
        self.assertTrue(isinstance(aline, rf.Line))

    def testConvertLine_checkforward(self):

        aline = Line(wcs1, self.line1.p1, self.line1.p2)
        newline = aline.convertTo(wcs2)

        self.assertTrue((np.abs(Point(self.line2.p1).wcs() - newline.p1.wcs()) < 2).all())
        self.assertTrue((np.abs(Point(self.line2.p2).wcs() - newline.p2.wcs()) < 2).all())
        


    def testConvertLine_checkbackward(self):
        aline = Line(wcs2, self.line2.p1, self.line2.p2)
        newline = aline.convertTo(wcs1)


        self.assertTrue((np.abs(Point(self.line1.p1).wcs() - newline.p1.wcs()) < 2).all())
        self.assertTrue((np.abs(Point(self.line1.p2).wcs() - newline.p2.wcs()) < 2).all())

    def testFromRegion(self):

        aline = rf.Line((500, 2300), (100, 23))

        wcsline = Line(wcs1, aline)
        
        self.assertEquals(aline.p1, wcsline.p1)
        self.assertEquals(aline.p2, wcsline.p2)
        self.assertEquals(wcsline.wcs, wcs1)



###########################

class TestIO(unittest.TestCase):

    def testParse(self):

        regionfile = '''Region file format: DS9 version 4.0
# Filename: /u/ki/dapple/subaru/MACS0025-12/W-J-V/SCIENCE/coadd_MACS0025-12_all/coadd.fits
global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source
physical
circle(7382.1,4477.8,22.8929)
circle(7336.2947,4420.5121,22.89288) # color=cyan
line(6984.8902,4435.4195,7106.2166,4359.8637) # line=0 0
'''

        wcs = wcs1

        regions = parseRegionFile(regionfile.splitlines(), wcs)

        self.assertEquals(len(regions), 3)

        for region in regions:
            self.assertEquals(region.wcs, wcs)


        self.assertTrue(isinstance(regions[0], Circle))
        self.assertEquals(regions[0].center, (7382.1,4477.8))
        self.assertEquals(regions[0].radius, 22.8929)

        self.assertEquals(regions[1].attributes['color'], 'cyan')

        
        self.assertTrue(isinstance(regions[2], Line))
        self.assertEquals(regions[2].p1, (6984.8902,4435.4195))
        self.assertEquals(regions[2].p2, (7106.2166,4359.8637))


    def testPropagateAttributes(self):

        aCircle = rf.Circle.fromStr('circle(336.2947,420.5121,22.89288) # color=cyan tag={Group 1}')

        bCircle = convertToWCS(aCircle, wcs2)

        cCircle = bCircle.convertTo(wcs1)

        regionfile = None

        try:
            afile, regionfile = tempfile.mkstemp()

            writeRegionFile(regionfile, [cCircle])
            
            regions = parseRegionFile(open(regionfile).readlines(), wcs1)

            self.assertEquals(len(regions), 1)
            self.assertEquals(regions[0].attributes['color'], 'cyan')
            self.assertEquals(regions[0].attributes['tag'], '{Group 1}')

        finally:
            if regionfile is not None and os.path.exists(regionfile):
                os.remove(regionfile)
        



#########################

def test():

    testcases = [TestCircle, TestLine, TestPoint, TestIO]

    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)


#########################

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        test()
