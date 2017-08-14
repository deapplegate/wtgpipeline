#!/usr/bin/env python
#####################
# Find something to mask in a coadded image, display position matched input images for masking purposes
######################

import astropy, astropy.io.fits as pyfits, sys, re, os, time, glob, subprocess
import backref_coaddpos as br
from optparse import OptionParser
from numpy import *

######################
__cvs_id__="$Id: backmask.py,v 1.7 2010-03-23 00:36:17 dapple Exp $"
######################

######################
# XPA Commands
######################

def xpaset(command, pipe=None):

    print "command=",command

    if pipe is None:
        subprocess.check_call(('xpaset -p ds9 %s' % command).split())
    else:
        xpa = os.popen('xpaset ds9 %s' % command, 'w')
        xpa.write(pipe)
        xpa.close()

#####

def xpaget(command):

    xpa = subprocess.Popen('xpaget ds9 %s' % command, shell=True, stdout=subprocess.PIPE).stdout
    output = [x.strip() for x in xpa.readlines()]
    xpa.close()
    if len(output) == 0:
        return None
    if len(output) == 1:
        return output[0]
    return output

####################

def isDS9Running():

    xpaaccess = os.popen('xpaaccess ds9')
    answer = xpaaccess.readline()
    isRunning = answer.strip()
    xpaaccess.close()
    return isRunning == "yes"


#####

def startDS9():
#return value indicates if ds9 was started by this program
    if not isDS9Running():
	#os.system('ds9 &')
        os.system('/afs/slac/g/ki/software/local/bin/ds9 -view layout vertical -frame lock wcs &')
        
        for count in xrange(200):
            time.sleep(1)
            if isDS9Running():
		print "waited for ds9 to load for %s seconds" % (count)
                return True
            
        raise RuntimeException('Cannot Open DS9')

    return False

####

def stopDS9():

    if isDS9Running():
        xpaset('exit')

####

def matchWCS(image):

    curframe = xpaget('frame frameno')
    image.matchWCS()
    if curframe != '':
        xpaset('frame %s' % curframe)
    
####

class Image:
    def __init__(self, file, regionfile = None):
        self.file = file
        self.regionfile = regionfile
        self.frameno = None

    def isOpen(self):
        return self.frameno is not None

    def activeImage(self, newFrame=True):

        if self.isOpen():
            xpaset('frame %d' % self.frameno)
            return
    
        if newFrame:
            xpaset('frame new')
        
        self.frameno = int(xpaget('frame'))
        print "Image %s now frame %d" % (self.file, self.frameno)
        xpaset('file %s' % self.file)
        xpaset('cmap BB')
        xpaset('scale mode zscale')
        
        if self.regionfile is not None and \
                os.path.exists(self.regionfile):
            xpaset('regions load %s' % self.regionfile)
            
    def closeImage(self, saveRegions = True):
        
        if not self.isOpen():
            return
        
        print "Closing %s at frame %d" % (self.file, self.frameno)
        xpaset('frame %d' % self.frameno)
        
        if saveRegions:
            xpaset('regions strip no')
            xpaset('regions system image')
            print "Saving %s" % self.regionfile
            xpaset('regions save %s' % self.regionfile)

        xpaset('frame delete')
        self.frameno = None

    def matchWCS(self):

        self.activeImage()
        xpaset('match frames wcs')
    
######

class Regions:
    def __init__(self, readfromDS9=False):
        if readfromDS9:
            self.pix = xpaget('regions -system image')
            self.wcs = xpaget('regions -system wcs')
        else:
            self.pix = []
            self.wcs = []

    def load(self, wcs=True):
        if wcs:
            regionlist = ['fk5']
            regionlist.extend(self.wcs)
        else:
            regionlist = self.pix

        xpaset('regions', pipe=';'.join(regionlist))

    def append(self, region):
        self.pix.append(region[0])
        self.wcs.append(region[1])

    def __iter__(self):
        return zip(self.pix, self.wcs).__iter__()

    def __contains__(self, region):
        pix, wcs = region
        return pix in self.pix and wcs in self.wcs

    def __len__(self):
        return len(self.pix)

def readNewRegions(knownregions = Regions()):

    allregions = Regions(readfromDS9=True)

    newregions = Regions()
    for region in allregions:
        if region not in knownregions:
            newregions.append(region)

    return newregions, allregions
    
#################

def readCurPix():

    return array([map(float, xpaget('pan').split())])

#################

def run_backmask(coaddimage, imagedict):

    mapping = br.CoaddMapping([x.file for x in imagedict.itervalues()],
                            coaddimage.file)
    print "mapping=",mapping

    closeDS9 = startDS9()

    coaddimage.activeImage()
    knownregions = Regions(readfromDS9=True)
    while 1:
        sys.stdout.write("Enter to load Contributing Files (and plot new regions) [(q)uit]?")
        response = raw_input()
        if response == 'q':
            break
        
        coaddimage.activeImage()
        curpix = readCurPix()
        newregions, knownregions = readNewRegions(knownregions)

        contribs = mapping.findContribs(curpix)

        contribs.sort()
        print "contribs=",contribs
        print "imagedict=",imagedict
            
        for contrib in contribs:
            imagedict[contrib].activeImage()
            newregions.load()
        
        coaddimage.activeImage()
        coaddimage.matchWCS()
            
        print "Contributing files loaded"
        sys.stdout.write("Enter when done [(a)bort]?")
        response = raw_input()

        saveRegions = (response != 'a')
        for image in imagedict.itervalues():
            image.closeImage(saveRegions = saveRegions)

        coaddimage.activeImage()

    #if closeDS9
    #    stopDS9()

##########################
##########################

def constructRegionFile(image, stripSuffix):
    #assumes a lot about directory structure, and how you run this!

    if os.path.islink(image):
        realimage = os.readlink(image)
    else:
        realimage = image

    if not os.path.isabs(realimage):
        realimage = os.path.join(os.path.dirname(image),os.readlink(image))
            

    dir, filename = os.path.split(realimage)
    regiondir = '%s/reg' % dir

    base, suffix, dummy = filename.rpartition(stripSuffix)

    regionfile='%s/%s.reg' % (regiondir, base)

    return regionfile
        
############################

def loadCoaddMasking(coaddfile, allimages):
    #assumptions about filename and directory structures
    coaddir, coadd = os.path.split(coaddfile)
    coaddbase, fits = os.path.splitext(coadd)
    print '# of Input Images Detected: %d' % len(allimages)
    imagedict = {}
    for image in allimages:
        dir, filebase = os.path.split(image)
	print "filebase=",filebase
        match = re.match('(.+?_\d+)', filebase)
        base = match.group(1)
	print "base=",base
        if os.path.exists(image):
            print "Loading %s..." % image
	    print '...with region file: %s/reg/%s.reg' % (dir, base)
            imagedict[image] = Image(image, '%s/reg/%s.reg' % (dir, base))
        else:
            print "Cannot find %s!!!" % image
    coaddimage = Image(coaddfile, '%s/%s.backmask.reg' % (coaddir, coadd))
    run_backmask(coaddimage, imagedict)

##########################
##########################

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "backmask.py /path/to/coadd.fits filesuffic"
        print "   For example: backmask.py /path/to/coadd.fits input images"
        sys.exit(1)

    coadd = sys.argv[1]
    inputimages = sys.argv[2:]
    loadCoaddMasking(coadd, inputimages)
