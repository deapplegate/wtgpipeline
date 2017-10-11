#!/usr/bin/env python
#######################

import os, glob, re, astropy, astropy.io.fits as pyfits, pywcs, wcsregionfile as wrf, sys

#######################

__cvs_id__ = "$Id: wcsconvertregions.py,v 1.5 2010-04-05 19:56:26 dapple Exp $"

#######################

def findInputImages(coaddimage, ext):

    coadd_dir = os.path.dirname(coaddimage)
    science_dir = os.path.normpath(os.path.join(coadd_dir, '..'))

    images = glob.glob('%s/*%s.fits' % (science_dir, ext))

    return images


#######################

def findLocalFiles(image, ext, regiondir):

    science_dir, imagefile = os.path.split(image)

    match = re.match('(.+?_\d\d?)%s' % ext, imagefile)
    if match is None:
        return None

    base = match.group(1)

    headerdir = glob.glob('%s/headers_scamp_photom_*' % science_dir)[0]

    scampheaderfile = '%s/%s.head' % (headerdir, base)
    outputregionfile = '%s/%s.reg' % (regiondir, base)

    return scampheaderfile, outputregionfile

###################################

def makeRegionFileDir(coaddimage):

    coadd_dir = os.path.dirname(coaddimage)
    science_dir = os.path.normpath(os.path.join(coadd_dir, '..'))

    regionfiledir = '%s/starsuppression' % science_dir
    if not os.path.exists(regionfiledir):
        os.mkdir(regionfiledir)

    return regionfiledir


##########################

class FileBuffer(object):

    def __init__(self, lines):
        self.lines = lines
    def readlines(self):
        return self.lines

def constructImageWCS(image, scampheaderfile):

    imageheader = pyfits.getheader(image)

    if os.path.exists(scampheaderfile):
        scampheaderbuffer = FileBuffer(open(scampheaderfile).readlines()[:-1])

        imageheader.fromTxtFile(scampheaderbuffer)

    image_wcs = pywcs.WCS(imageheader)

    return image_wcs

############################

def processConversion(regions, image, scampheaderfile, outputregionfile):

    if regions is None:
        return

    image_wcs = constructImageWCS(image, scampheaderfile)

    image_regions = [ x.convertTo(image_wcs) for x in regions ]

    wrf.writeRegionFile(outputregionfile, image_regions, overwrite=True)

#############################

def main(argv = sys.argv):

    if len(argv) != 4:
        print "wcsconvertregions.py coaddimage regionfile extension"
        sys.exit(1)


    coaddimage = argv[1]
    regionfile = argv[2]
    extension =  argv[3]

    coadd_wcs = pywcs.WCS(pyfits.getheader(coaddimage))
    regions = wrf.parseRegionFile(open(regionfile).readlines(), coadd_wcs)

    images = findInputImages(coaddimage, extension)

    regionfiledir = makeRegionFileDir(coaddimage)

    for image in images:
        scampheader, outputregion = findLocalFiles(image, extension, regionfiledir)
        processConversion(regions, image, scampheader, outputregion)

#################################

if __name__ == '__main__':
    sys.path.append('/u/ki/awright/InstallingSoftware/pythons/')
    from adam_quicktools_ArgCleaner import ArgCleaner
    args=ArgCleaner(sys.argv)
    print "args=", args
    import pyregion
    main(args)
