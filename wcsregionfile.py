#!/usr/bin/env python
#######################

import sys, unittest, inspect, tempfile, os
import astropy, astropy.io.fits as pyfits
import astropy.wcs as pywcs
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
        self.txt = txt
        self.txt_lines = txt.splitlines()
    def readlines(self):
        return self.txt_lines[:-1]
    def read(self):
        return self.txt

#########################

def parseRegionFile(txtlines, wcs):

    regions = rf.parseRegionFile(txtlines)

    return [ convertToWCS(region, wcs) for region in regions ]

#########################

def writeRegionFile(filename, regions, overwrite = True):

    rf.writeRegionFile(filename, regions, overwrite = overwrite)


##########################

wcs1_cards=[('SIMPLE', True, ''),
('BITPIX', -32, ''),
('NAXIS', 2, ''),
('NAXIS1', 10000, ''),
('NAXIS2', 10000, ''),
('EXTEND', True, ''),
('EQUINOX', 2000.0, ''),
('RADECSYS', 'FK5', ''),
('CTYPE1', 'RA---TAN', ''),
('CUNIT1', 'deg', ''),
('CRVAL1', 2.600700000E+02, ''),
('CRPIX1', 5000, ''),
('CDELT1', -5.555555638e-05, ''),
('CTYPE2', 'DEC--TAN', ''),
('CUNIT2', 'deg', ''),
('CRVAL2', 3.560750000E+01, ''),
('CRPIX2', 5000, ''),
('CDELT2', 5.555555638e-05, ''),
('FGROUPNO', 1, '')]
wcs1_header = pyfits.Header(cards=wcs1_cards)
wcs1 = pywcs.WCS(header=wcs1_header)
