#!/usr/bin/env python
#############################
# @file regionfile.py
# @author Douglas Applegate
# @date 3/11/08
#
# @brief Utilities for managing a region file
##############################

import sys, inspect, os, re, unittest, math, numpy

#############################

__cvs_id__ = "$Id: regionfile.py,v 1.16 2010-11-12 20:33:56 dapple Exp $"

##############################

class FormatError(Exception): pass

class Region(object): 

    @classmethod
    def fromStr(cls, astr):
        return None

    def toPolygon(self):
        return self

##############################

class Coordinate(object):

    def __init__(self, index):
        self.index = index

    def __get__(self, instance, owner=None):
        return instance[self.index]

    def __set__(self, instance, value):
        instance[self.index] = value

class Point(list):

    x = Coordinate(0)
    y = Coordinate(1)

    def __init__(self, *args):

        if len(args) == 1:
            coords = args[0]
        else:
            coords = args[0:2]

        list.__init__(self, coords)

    ########

    def __eq__(self, other):

        return self[0] == other[0] and self[1] == other[1]


##############################

region_regex = re.compile('(\w+={.+?}|\w+=\w+)')


class Attributes(dict):

    def __init__(self, **keywords):

        for key, val in keywords.iteritems():
                
            self[key] =  val

    @classmethod
    def fromStr(cls, txtline):


        components = txtline.split('#')
        if len(components) < 2:
            return cls()

        region_spec, attributes = components

        matches = region_regex.findall(attributes)

        if matches is None or matches == []:
            return cls()

        attributes = {}
        for attribute_pair in matches:
            
            key, val = attribute_pair.split('=')

            attributes[key] = val

        return cls(**attributes)

    def __str__(self):

        if len(self) == 0:
            return ''

        astr = '#'
        for key, val in self.iteritems():
            astr += ' %s=%s' % (key, val)
            
        return astr
            



###############################



def _shiftArray(array, shift):

    if shift == 0:
        return array

    shift = shift % len(array)

    result = numpy.zeros_like(array)
    result[0:-shift] = array[shift:]
    result[-shift:] = array[0:shift]

    return result

####

polygon_regex = re.compile('(?:polygon|POLYGON)\((.+)\)')

class Polygon(Region):

    def __init__(self, vertices):

        self.vertices = vertices

    ###

    def __str__(self):

        return 'POLYGON(%s)' % ','.join(map(str,self.vertices))

    ###

    def __repr__(self):
        return str(self)

    ###

    def __eq__(self, other):


        if len(self.vertices) != len(other.vertices):
            return False

        thisVertices = numpy.array(self.vertices)
        otherVertices = numpy.array(other.vertices)

        for i in xrange(0,len(thisVertices),2):
            
            curPermutation = _shiftArray(thisVertices, i)

            if (numpy.abs(curPermutation - otherVertices) < 10**(-5)).all():
                return True

        return False

    ###

    @classmethod
    def fromStr(cls, str):

        match = polygon_regex.match(str)
        if match is None:
            return None

        coords = map(float, match.group(1).split(','))

        return cls(coords)

        
###############################

class Box(Region):

    def __init__(self, center, size, angle):
        self.center = Point(center)
        self.size = size
        self.angle = angle

    ###

    def __str__(self):

        return 'box(%f,%f,%f,%f,%f)' % (self.center[0], self.center[1],
                                        self.size[0], self.size[1],
                                        self.angle)

    ###

    def __eq__(self, other):

        return self.center == other.center and \
            self.size == other.size and \
            self.angle == other.angle

    ###

    def toPolygon(self):

        dx = self.size[0]/2.
        dy = self.size[1]/2.
        angle = self.angle*math.pi/180.

        center = numpy.array(self.center)

        points = numpy.vstack([numpy.array([-dx,-dy]),
                               numpy.array([ dx,-dy]),
                               numpy.array([ dx, dy]),
                               numpy.array([-dx, dy])]).transpose()

        rotation = numpy.array([[math.cos(angle),-math.sin(angle)],
                                [math.sin(angle),math.cos(angle)]])

        rotated = numpy.dot(rotation, points).transpose() + center

        return Polygon(rotated.flatten().tolist())

    ###

    @classmethod
    def fromStr(cls, astring):

        match = re.match('box\((.+)\)', astring)
        if match is None:
            return None

        rawVals = [float(x.strip()) for x in match.group(1).split(',')]
        if len(rawVals) != 5:
            return None

        return cls([rawVals[0],rawVals[1]],
                   [rawVals[2], rawVals[3]],
                   rawVals[4])


################################################

circle_regex = re.compile('circle\((.+)\)')

class Circle(Region):

    def __init__(self, center, radius, *args, **keywords):
        self.center = Point(center)
        self.radius = radius
        if len(args) == 1:
            self.attributes = args[0]
        elif 'attributes' in keywords:
            self.attributes = keywords['attributes']
        else:
            self.attributes = Attributes(**keywords)

    @classmethod
    def fromStr(cls, str):

        match = circle_regex.match(str)
        if match is None:
            return None

        coords = map(float, match.group(1).split(','))

        acircle = Circle(coords[0:2], coords[2], Attributes.fromStr(str))

        return acircle

    def __str__(self):

        return 'circle(%f,%f,%f) %s' % (self.center[0], self.center[1], self.radius, str(self.attributes))

    def __eq__(self, other):

        return self.center == other.center and self.radius == other.radius

    def toPolygon(self):

        xref = self.radius*numpy.cos(numpy.arange(0,2*numpy.pi,2*numpy.pi/50)) + self.center[0]
        yref = self.radius*numpy.sin(numpy.arange(0,2*numpy.pi,2*numpy.pi/50)) + self.center[1]

        return Polygon(numpy.column_stack([xref, yref]).flatten())

        

################################################

line_regex = re.compile('line\((.+)\)')

class Line(Region):

    def __init__(self, p1, p2):

        self.p1 = Point(p1)
        self.p2 = Point(p2)

    @classmethod
    def fromStr(cls, str):

        match = line_regex.match(str)
        if match is None:
            return None

        coords = map(float, match.group(1).split(','))

        return Line(coords[0:2], coords[2:4])

    def __repr__(self):

        return 'line(%f,%f,%f,%f)' % (self.p1[0], self.p1[1], self.p2[0], self.p2[1])

    def __eq__(self, other):

        return self.p1 == other.p1 and self.p2 == other.p2
        
        

        
###########################################################################
###########################################################################

comment_regex = re.compile('^#')

def parseRegionFile(txtlines):

    parsers = []
    curModule = sys.modules[globals()['__name__']]
    for (name,member) in inspect.getmembers(curModule):
        if inspect.isclass(member) and issubclass(member, Region):
            parsers.append(member.fromStr)

    regions = []
    for i, line in zip(xrange(len(txtlines)), txtlines):
        if comment_regex.match(line):
            continue
        for parser in parsers:
            region = parser(line)
            if region is not None:
                regions.append(region)
                continue

    return regions

    

######################################

def writeRegionFile(filename, regions, overwrite = False):
    '''
    @brief Given a filename and a list of regions,
            create a ds9 region file
    
    @param filename name of region file to append or a file descriptor
    @param regions a list of region objects
    '''
    

    if len(regions) == 0:
        return

    preamble = ['# # Region file format: DS9 version 4.0\n',
                '# # Filename: SKYFLAT_norm_10.fits\n',
                '# global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source\n']
    

    strRegions = '\n'.join(map(str, regions))

    if type(filename) == type('a'):
        if os.path.exists(filename) and not overwrite:
            output = open(filename, 'a')
        else:
            output = open(filename, 'w')
            output.writelines(preamble)
        
        output.writelines(strRegions)
        output.write('\n')
        output.close()

    else:
        filename.writelines(preamble)
        filename.writelines(strRegions)
        filename.write('\n')

        
########################################################################
########################################################################

class TestCircle2Polygon(unittest.TestCase):

    def testSimpleCircle(self):
        circle = Circle((0,0), 1)

        xref = numpy.cos(numpy.arange(0,2*numpy.pi,2*numpy.pi/15))
        yref = numpy.sin(numpy.arange(0,2*numpy.pi,2*numpy.pi/15))

        reference = Polygon(numpy.column_stack([xref, yref]).flatten())

        self.assertEquals(circle.toPolygon(), reference)

    def testRadius(self):

        circle = Circle((0,0), 5.5)

        xref = 5.5*numpy.cos(numpy.arange(0,2*numpy.pi,2*numpy.pi/15))
        yref = 5.5*numpy.sin(numpy.arange(0,2*numpy.pi,2*numpy.pi/15))

        reference = Polygon(numpy.column_stack([xref, yref]).flatten())

        self.assertEquals(circle.toPolygon(), reference)

    def testOffset(self):

        circle = Circle((7.3,-2), 5.5)

        xref = 5.5*numpy.cos(numpy.arange(0,2*numpy.pi,2*numpy.pi/15)) + 7.3
        yref = 5.5*numpy.sin(numpy.arange(0,2*numpy.pi,2*numpy.pi/15)) - 2

        reference = Polygon(numpy.column_stack([xref, yref]).flatten())

        self.assertEquals(circle.toPolygon(), reference)
        
        

class TestBox2Polygon(unittest.TestCase):

    def testSimpleBox(self):

        box = Box(Point(0,0),(1,1),0)
        reference = Polygon([-.5,-.5,.5,-.5,.5,.5,-.5,.5])
        self.assertEquals(box.toPolygon(), reference)

    def testRotatedBox(self):

        box = Box(Point(0,0),(2,1),90)
        reference = Polygon([-.5,-1,.5,-1,.5,1,-.5,1])
        self.assertEqual(box.toPolygon(), reference)

    def testOffsetRotatedBox(self):

        box = Box(Point(1,2),(2,1),90)
        reference = Polygon([.5,1,1.5,1,1.5,3,.5,3])
        self.assertEqual(box.toPolygon(), reference)


##############

class TestShiftArray(unittest.TestCase):

    def setUp(self):
        self.a = numpy.array([1,2,3,4])

    def testNoShift(self):
        self.assertTrue((self.a == _shiftArray(self.a, 0)).all())

    def testShift1(self):
        self.assertTrue((numpy.array([2,3,4,1]) == \
                             _shiftArray(self.a, 1)).all())

    def testShift3(self):
        self.assertTrue((numpy.array([4,1,2,3]) == \
                             _shiftArray(self.a, 3)).all())

    def testNegative(self):
        self.assertTrue((numpy.array([3,4,1,2]) == \
                             _shiftArray(self.a, -2)).all())

    def testModulus(self):
        self.assertTrue((numpy.array([2,3,4,1]) == \
                             _shiftArray(self.a, 5)).all())

###################

class TestCircle(unittest.TestCase):

    def testCenterFormat(self):

        acircle = Circle([100.5,200], 10.6)

        self.assertTrue(isinstance(acircle.center, Point))

    def testGroupTag(self):

        acircle = Circle([100.5, 200], 10.6, tag='{Group 1}')

        self.assertEquals(acircle.attributes['tag'], '{Group 1}')

    def testFromString(self):

        center = Point([100.5,200])
        radius = 10.6
        string = 'circle(%f,%f,%f) # color=cyan' % (center[0], center[1], radius)

        acircle = Circle.fromStr(string)

        self.assertEquals(acircle.center, center)
        self.assertEquals(acircle.radius, radius)
        self.assertEquals(acircle.attributes['color'], 'cyan')

    def testToString(self):

        acircle = Circle(Point([100.5,200]), 10.6)

        astr = str(acircle)

        match = re.match('^circle\((.+)\)', astr)
        self.failIf(match is None)

        coords = map(float, match.group(1).split(','))
        self.assertEquals(coords, [100.5,200,10.6])

    def testToStringWithAttributes(self):

        acircle = Circle(Point([100.5,200]), 10.6, color='cyan', tag='{Group 1}')

        astr = str(acircle)

        match = re.match('^circle\((.+)\)', astr)
        self.failIf(match is None)

        coords = map(float, match.group(1).split(','))
        self.assertEquals(coords, [100.5,200,10.6])

        parts = astr.split('#')

        self.assertEquals(len(parts), 2)

        region_spec, attributes = parts

        matches = region_regex.findall(attributes)

        self.failIf(matches is None or matches == [])

        attributes = {}

        for attribute_pair in matches:
            
            key, val = attribute_pair.split('=')

            attributes[key] = val

        self.assertTrue('color' in attributes)
        self.assertEquals(attributes['color'], 'cyan')
        
        self.assertTrue('tag' in attributes)
        self.assertEquals(attributes['tag'], '{Group 1}')

        
        

    def testEquals(self):

        circle1 = Circle(Point([100.5,200]), 10.6)
        circle2 = Circle(Point([100.5,200]), 10.6)
        circle3 = Circle(Point([100.5, 200]), 15)
        circle4 = Circle(Point([14.3, 200]), 10.6)

        self.assertEquals(circle1, circle2)
        self.assertNotEqual(circle1, circle3)
        self.assertNotEqual(circle1, circle4)

#######################

class TestLine(unittest.TestCase):

    def testStorage(self):

        aline = Line([100.1, 50.5], [200.1, 17.2])

        self.assertTrue(isinstance(aline.p1, Point))
        self.assertTrue(isinstance(aline.p2, Point))
        

    def testFromString(self):

        astr = 'line(100.1,50.5,200.1,17.2) # line=0 0'

        aline = Line.fromStr(astr)

        self.assertEquals(aline.p1, Point([100.1, 50.5]))
        self.assertEquals(aline.p2, Point([200.1, 17.2]))

    def testToString(self):

        aline = Line(Point([100.1, 50.5]), Point([200.1, 17.2]))

        astr = str(aline)

        match = re.match('^line\((.+)\)$', astr)
        self.failIf(match is None)

        coords = map(float, match.group(1).split(','))
        self.assertEquals(coords, [100.1, 50.5, 200.1, 17.2])

    def testEquals(self):

        line1 = Line(Point([100.5,200]),  Point([10.6, 17.2]))
        line2 = Line(Point([100.5,200]),  Point([10.6, 17.2]))
        line3 = Line(Point([100.5, 200]),   Point([15, 17.2]))

        self.assertEquals(line1, line2)
        self.assertNotEqual(line1, line3)



###########################

class TestParseRegionFile(unittest.TestCase):

    def testParseRegionFile(self):

        regionfile = '''Region file format: DS9 version 4.0
# Filename: /u/ki/dapple/subaru/MACS0025-12/W-J-V/SCIENCE/coadd_MACS0025-12_all/coadd.fits
global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source
physical
circle(7382.1,4477.8,22.8929)
circle(7336.2947,4420.5121,22.89288) # color=cyan
line(6984.8902,4435.4195,7106.2166,4359.8637) # line=0 0
polygon(6983.6644,4343.9132,7100.5572,4343.9132,7176.033,4270.5761,7100.5572,4227.0204,6983.6644,4227.0204)
box(7426.7067,4227.6326,123.61511,83.568544,0)
'''

        regions = parseRegionFile(regionfile.splitlines())

        self.assertEquals(len(regions), 5)
        self.assertEquals(regions[0], Circle([7382.1,4477.8],22.8929))
        self.assertEquals(regions[1], Circle([7336.2947,4420.5121],22.89288))
        self.assertEquals(regions[1].attributes['color'], 'cyan')
        self.assertEquals(regions[2], Line([6984.8902,4435.4195],[7106.2166,4359.8637]))
        self.assertEquals(regions[3], Polygon([6983.6644,4343.9132,7100.5572,4343.9132,7176.033,4270.5761,7100.5572,4227.0204,6983.6644,4227.0204]))
        self.assertEquals(regions[4], Box([7426.7067,4227.6326],[123.61511,83.568544],0))

    def testOddRegionFile(self):

        regionfile = '''Region file format: DS9 version 4.0
# Filename: /u/ki/dapple/subaru/MACS0025-12/W-J-V/SCIENCE/coadd_MACS0025-12_all/coadd.fits
circle(7382.1,4477.8,22.8929)
circle(7336.2947,4420.5121,22.89288) # color=cyan
line(6984.8902,4435.4195,7106.2166,4359.8637) # line=0 0
polygon(6983.6644,4343.9132,7100.5572,4343.9132,7176.033,4270.5761,7100.5572,4227.0204,6983.6644,4227.0204)
box(7426.7067,4227.6326,123.61511,83.568544,0)
'''

        regions = parseRegionFile(regionfile.splitlines())

        self.assertEquals(len(regions), 5)
        self.assertEquals(regions[0], Circle([7382.1,4477.8],22.8929))
        self.assertEquals(regions[1], Circle([7336.2947,4420.5121],22.89288))
        self.assertEquals(regions[1].attributes['color'], 'cyan')
        self.assertEquals(regions[2], Line([6984.8902,4435.4195],[7106.2166,4359.8637]))
        self.assertEquals(regions[3], Polygon([6983.6644,4343.9132,7100.5572,4343.9132,7176.033,4270.5761,7100.5572,4227.0204,6983.6644,4227.0204]))
        self.assertEquals(regions[4], Box([7426.7067,4227.6326],[123.61511,83.568544],0))
        

    

#############################

class TestPolygon(unittest.TestCase):

    def setUp(self):

        self.vertices = [6983.6644,4343.9132,7100.5572,4343.9132,7176.033,4270.5761,7100.5572,4227.0204,6983.6644,4227.0204]

    def testFromStr(self):

        polygon = Polygon.fromStr('polygon(%s)' % ','.join(map(str, self.vertices)))

        self.assertEquals(polygon.vertices, self.vertices)

        polygon = Polygon.fromStr('POLYGON(%s)' % ','.join(map(str, self.vertices)))

        self.assertEquals(polygon.vertices, self.vertices)
        

    def testToStr(self):

        apolygon = Polygon(self.vertices)

        astr = str(apolygon)

        match = re.match('POLYGON\((.+)\)', astr)
        coords = map(float, match.group(1).split(','))

        self.failIf(match is None)
        self.assertEquals(coords, self.vertices)

    def testLoop(self):

        apolygon = Polygon(self.vertices)
        astr = str(apolygon)
        newpolygon = Polygon.fromStr(astr)
        self.assertEquals(self.vertices, newpolygon.vertices)

                                  
##############################

class TestBox(unittest.TestCase):

    def testFromString(self):

        astr = 'box(100.5,210,25,37.2,15) # color=cyan'

        abox = Box.fromStr(astr)

        self.assertEquals(abox.center, [100.5, 210])
        self.assertEquals(abox.size, [25, 37.2])
        self.assertEquals(abox.angle, 15)


    def testToString(self):

        abox = Box(Point([100.1, 50.5]), [200.1, 17.2], 15.1)

        astr = str(abox)

        match = re.match('^box\((.+)\)$', astr)
        self.failIf(match is None)

        coords = map(float, match.group(1).split(','))
        self.assertEquals(coords, [100.1, 50.5, 200.1, 17.2, 15.1])

    def testCenterFormat(self):

        abox = Box([100.1, 50.5], [200.1, 17.2], 15.1)

        self.assertTrue(isinstance(abox.center, Point))

###########################

class TestPoint(unittest.TestCase):

    def testAccessors(self):

        apoint = Point(15, 27)
        bpoint = Point([15,27])

        self.assertEquals(apoint, [15,27])
        self.assertEquals(apoint, (15,27))
        self.assertEquals(apoint, numpy.array([15, 27]))
        self.assertEquals(apoint.x, 15)
        self.assertEquals(apoint.y, 27)
        self.assertEquals(apoint[0], 15)
        self.assertEquals(apoint[1], 27)
        self.assertEquals(apoint, bpoint)

###########################

class TestAttributes(unittest.TestCase):

    def testTag(self):

        aregion = Attributes(tag='{Group 1}', color='red' )
        
        self.assertEquals(aregion['tag'], '{Group 1}')
        self.assertEquals(aregion['color'], 'red')

    def testParseAttributes(self):
        
        regionstr = 'circle(2234.9358,1767.0683,179.85811) # color=red width=2 tag={Group 6}'

        aregion = Attributes.fromStr(regionstr)

        self.assertEquals(aregion['color'], 'red')
        self.assertEquals(aregion['width'], '2')
        self.assertEquals(aregion['tag'], '{Group 6}')

    def testNoAttributes(self):

        regionstr = 'circle(2234.9358,1767.0683,179.85811)'


        aregion = Attributes.fromStr(regionstr)

        self.assertEquals(len(aregion), 0)

        
    def testToStr(self):

        aregion = Attributes(color='cyan', tag='{Group 1}')

        self.assertEquals(str(aregion), '# color=cyan tag={Group 1}')


        
        


###########################



if __name__ == '__main__':

    testcases = [TestCircle2Polygon, TestBox2Polygon, TestShiftArray, TestBox, TestCircle, 
                 TestLine, TestParseRegionFile, TestPolygon, TestPoint, TestAttributes]
    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)

