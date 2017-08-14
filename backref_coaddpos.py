#!/usr/bin/env python

import pywcs
import pyfits, sys, re
from optparse import OptionParser
from numpy import *

class ScampHeaderBuffer(object):
    def __init__(self, headerfile):
        self.file = open(headerfile)
    def close(self):
        self.file.close()
    def readlines(self):
        lines = self.file.readlines()
        return lines[:-1]  #gets rid of 'end' at end of header txt file


class Image:
    def __init__(self, imagename, headerfile=None):
        self.name = imagename

        header = pyfits.getheader(self.name)
        if headerfile is not None:
            header.fromTxtFile(ScampHeaderBuffer(headerfile))

        self.shape = array((header['NAXIS1'], header['NAXIS2']))
        self.wcs = pywcs.WCS(header)

    def pix2wcs(self, pix):
        return self.wcs.wcs_pix2sky(pix, 1)

    def wcs2pix(self, world):
        return self.wcs.wcs_sky2pix(world, 1)

    def inImage(self, world):
        pix = self.wcs2pix(world)[0]

        return logical_and(logical_and(pix[0] >= 0, 
                                       pix[1] >= 0),
                           logical_and(pix[0] < self.shape[0],
                                       pix[1] < self.shape[1]))

class CoaddMapping:
    def __init__(self, inputlist, coadd, headerlist = None):
        if headerlist is None:
            self.inputs = [Image(x) for x in inputlist]
        else:
            self.inputs = [Image(x,h) for x,h in zip(inputlist, headerlist)]

        self.coadd = Image(coadd)

    def findContribs(self,pix):

        world = self.coadd.pix2wcs(pix)

        contribs = []
        for input in self.inputs:
            if input.inImage(world):
                contribs.append(input.name)

        return contribs

if __name__ == '__main__':

    parser = OptionParser(usage='''
              coaddinputs.py -i coadd.fits input1 input2 ...
                   Reads x,y pixel coordinates from stdin, 
                    and writes image names that contribute to stdout.''')

    parser.add_option('-i', '--input',
                      dest='coadd',
                      help='Name of coadded file',
                      default = None)

    options, images = parser.parse_args()

    if options.coadd is None:
        parser.error('Need to specifiy coadded image')

    coaddmap = CoaddMapping(images, options.coadd)

    for line in sys.stdin.readlines():

        pix = array([map(float,line.split())])
        inputs = coaddmap.findContribs(pix)
        sys.stdout.write('%s\n' % ' '.join(inputs))
