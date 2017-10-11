#!/usr/bin/env python

import kapteyn.wcs as wcs
import astropy, astropy.io.fits as pyfits, sys, re
from optparse import OptionParser
from numpy import *

class Image:
    def __init__(self, imagename):
        self.name = imagename
        header = pyfits.getheader(self.name)
        self.shape = array((header['NAXIS1'], header['NAXIS2']))
        self.proj = wcs.Projection(header)

    def pix2wcs(self, pix):
        return self.proj.toworld(pix)

    def wcs2pix(self, world):
        return self.proj.topixel(world)

    def inImage(self, world):
        pix = self.wcs2pix(world)

        return logical_and(logical_and(pix[0] >= 0, 
                                       pix[1] >= 0),
                           logical_and(pix[0] < self.shape[0],
                                       pix[1] < self.shape[1]))

class CoaddMapping:
    def __init__(self, inputlist, coadd):
        self.inputs = [Image(x) for x in inputlist]
        self.coadd = Image(coadd)

    def findContribs(self,x,y):
        '''assumes 1 pix val at a time'''


        world = self.coadd.pix2wcs((x,y))
        
        contribs = []
        for input in self.inputs:
            if input.inImage(world):
                contribs.append(input.name)

        return contribs

if __name__ == '__main__':

    parser = OptionParser(usage='''
              findCoaddInputs.py -i coadd.fits input1 input2 ...
                   Reads x,y pixel coordinates from stdin, 
                    and writes image names that contribute to stdout.''')

    parser.add_option('-i', '--input',
                      dest='coadd',
                      help='Name of coadded file',
                      default = None)

    options, images = parser.parse_args()

    if options.coadd is None:
        parser.error('Need to specifiy coadded image')

    coaddmapping = CoaddMapping(images, options.coadd)

    for line in sys.stdin.readlines():

        x,y = map(float,line.split())
        inputs = coaddmapping.findContribs(x,y)
        sys.stdout.write('%s\n' % ' '.join(inputs))
