#!/usr/bin/env python

# Python script to create run/set WEB pages
#
# Joerg Dietrich (04.10.2004)

# 2006-01-18 Omit the check for "imred" in the HISTORY keywords of images
#             creates by imcombflat
# 2006-01-16 Account for changed length of suffix
# 2006-01-15 Make ending (e.g. wcs or new) configurable for
#            CoaddHistClass. New option is "-d" or "--ending"
# 2006-01-15 fix assumption that chip is always a single digit number
#            in getRun()when determining frameBase.
# 2005-06-23 use only nochips not chips in __main__, cast nochips to
#            int when parsing options
# 2005-03-17 run science pages: Try to work with chips.cat5 if cat6 is
#            missing, ignore missing e1 e2 catalog entries
# 2005-03-14 Write -1 instead of en-dash when night is non-photometric
#            but standards are available
#            Ignore missing frames in run science page generation
#            Use the new ZPCHOICE header keyword
# 2005-03-03 Replaced imcombine with imcomb(flat) to match newer flips
#            scripts in GetCalType and readFlipsCal
# 2005-02-27 Entries in the co-addition overview are now sorted alpha-
#            betically
# 2005-02-24 Fixed reference date for caldate
# 2005-02-17 Make cut levels of ConvertMosaic more flexibel
# 2005-02-16 CoaddHist now also uses ConvertMosaic instead of it own
#            routine to convert fits to jpg
#            Convert Mosaic only uses the inner 1e6 pixels to get
#            statistics
#            Deleted superfluous functions addFrameNode() and
#            convertCoadd()
# 2005-02-11 New calib type: preprocess with function to parse
#            header readPreprocessCal()
# 2005-02-06 Re-arrange links to sci frames in coadd set page.
#            They are now grouped by runs and sorted in a table
# 2005-01-13 Always create phot info pages when possible, not only
#            when solution was accepted.
#            Properly handle frames without ZP and COEFF information
# 2005-01-12 Create Pages with info about photometric calibration
# 2004-11-25 Really ignore ZP if it is -1
# 2004-11-25 Bug fixes for reading exp. times from catalogs
# 2004-11-23 First try to read exp. time of calibration files
#            from chip_?.cat, instead of image (the latter is
#            kept only for compatibility with old catalogs)             
# 2004-11-12 Ignore ZP if it is -1
# 2004-10-24 Fix a bug in non-update mode
# 2004-10-21 Added update mode for run SCIENCE pages
#            Read SCIENCE image ZPs from image header
#            Fixed a NameError in singleFrameTable
# 18.10.2004 statistics for calibration files are read from
#            catalogs named chip_%d_stat.cat (instead of chip_%d.cat).
#            Hence these catalogs can clearly be distinguished from the
#            astrometry catalogs of science frames.

import getopt
import glob
import os
import pwd
import random
import string
import sys
import tempfile
import time

from math         import fabs
import astropy.io.fits as pyfits
import numarray

import libxml2
import xml.utils
from xml.dom.DOMImplementation  import implementation
from xml.dom.ext                import ReleaseNode

from WEBLib import *

PipeWWW = os.getenv('PIPEWWW')
pipelogVersion = "0.3.12"

def AddFooterNode(document):
    footerNode = document.createElement("footer")

    versionNode = document.createElement("version")
    textNode = document.createTextNode(pipelogVersion)
    versionNode.appendChild(textNode)
    footerNode.appendChild(versionNode)

    authorNode = document.createElement("user")
    textNode = document.createTextNode(pwd.getpwuid(os.getuid())[0])
    authorNode.appendChild(textNode)
    footerNode.appendChild(authorNode)

    timeNode = document.createElement("time")
    timeTup = time.localtime()
    textNode = document.createTextNode("%04d-%02d-%02d %02d:%02d:%02d" %
                                       (timeTup[0], timeTup[1], timeTup[2], timeTup[3], timeTup[4], timeTup[5]))
    timeNode.appendChild(textNode)
    footerNode.appendChild(timeNode)
    return footerNode

    
# Take fits file and output path as arguments
# Convert fits to jpg in output path
# automagically determines sensible cut levels
# We cut the percent/2 percentiles at the top and bottom
# if no fixed level is provided
def ConvertMosaic(fits, outPath, percent=5, levels=[None, None]):

    print "\nConversion from FITS to JPG"
    print "Infile: ", fits

    if (not levels[0]) and (not levels[1]):
        # Compute the cut levels
        fimg = pyfits.open(fits)
        data = fimg[0].data
        nElem = data.nelements()
        lData = numarray.reshape(data, nElem)
        if nElem > 2e6:
            # Sample a million pixels from within the image
            lData = lData[int(nElem/2-5e5):int(nElem/2+5e5)]
            nElem = lData.nelements()
    
        lData.sort()
        # Get the 2.5 percentiles (default: percent = 5)
        percent /= 200.
        if not levels[0]:
            minVal = lData[int(nElem*percent)]
        else:
            minVal = levels[0]
        if not levels[1]:
            maxVal = lData[int(nElem*(1-percent))-1]
        else:
            maxVal = levels[1]
        fimg.close()
    else:
        minVal = levels[0]
        maxVal = levels[1]
    
    psFile = tempfile.mktemp(".ps")
    wipfileName = tempfile.mktemp(".wip")
    wipfile = open(wipfileName, "w")
    
    wipfile.write("device %s/ps\n" % (psFile, ))
    wipfile.write("image %s\n" % (fits,))
    wipfile.write("winadj 0 nx 0 ny\n")
    wipfile.write("halftone %f %f\n" % (minVal, maxVal))
    wipfile.close()
    
    cmd = "wip -d /ps < %s >/dev/null " % (wipfileName, )
    os.system(cmd)

    os.remove(wipfileName)

    jpgFile = os.path.join(outPath, "images", os.path.split(fits)[1][:-5]+".jpg")
    cmd = "convert -rotate 90 %s %s" % (psFile, jpgFile)
    os.system(cmd)
    print "Outfile: ", jpgFile
    print

    if not os.path.isfile(jpgFile):
        return "Creation of %s failed" % (jpgFile,), None

    os.remove(psFile)
    return "ok", jpgFile


# Take fits file and output path as arguments
# Convert fits to jpg in output path
# automagically determines sensible cut levels
# We cut the percent/2 percentiles at the top and bottom
# if no fixed level is provided
def ConvertMosaicLarge(fits, outPath, percent=5, levels=[None, None]):

    print "\nConversion from FITS to JPG"
    print "Infile: ", fits

    tmpFile = tempfile.mktemp(".fits")
    cmd = "album -b 4 1 1 %s > %s" % (fits, tmpFile)
    os.system(cmd)

    if (not levels[0]) and (not levels[1]):
        # Compute the cut levels
        fimg = pyfits.open(tmpFile)
        data = fimg[0].data
        nElem = data.nelements()
        lData = numarray.reshape(data, nElem)
        if nElem > 2e6:
            # Sample a million pixels from within the image
            lData = lData[int(nElem/2-5e5):int(nElem/2+5e5)]
            nElem = lData.nelements()
    
        lData.sort()
        # Get the 2.5 percentiles (default: percent = 5)
        percent /= 200.
        if not levels[0]:
            minVal = lData[int(nElem*percent)]
        else:
            minVal = levels[0]
        if not levels[1]:
            maxVal = lData[int(nElem*(1-percent))-1]
        else:
            maxVal = levels[1]
        fimg.close()
    else:
        minVal = levels[0]
        maxVal = levels[1]
    
    psFile = tempfile.mktemp(".ps")
    wipfileName = tempfile.mktemp(".wip")
    wipfile = open(wipfileName, "w")
    
    wipfile.write("device %s/ps\n" % (psFile, ))
    wipfile.write("image %s\n" % (tmpFile,))
    wipfile.write("winadj 0 nx 0 ny\n")
    wipfile.write("halftone %f %f\n" % (minVal, maxVal))
    wipfile.close()
    
    cmd = "wip -d /ps < %s >/dev/null " % (wipfileName, )
    os.system(cmd)

    os.remove(wipfileName)

    jpgFile = os.path.join(outPath, "images", os.path.split(fits)[1][:-5]+".jpg")
    cmd = "convert -rotate 90 %s %s" % (psFile, jpgFile)
    os.system(cmd)
    print "Outfile: ", jpgFile
    print

    if not os.path.isfile(jpgFile):
        return "Creation of %s failed" % (jpgFile,), None

    os.remove(psFile)
    os.remove(tmpFile)
    return "ok", jpgFile


#    print "\nConversion from FITS to JPG"
#    print "Infile: ", fits
#
#    tmpFile = tempfile.mktemp(".fits")
#    cmd = "album -b 8 1 1 %s > %s" % (fits, tmpFile)
#    os.system(cmd)
#
#    tiffFile =  tempfile.mktemp(".tiff")
#
#    cmd = "stiff %s -NEGATIVE Y -BINNING 4 -OUTFILE_NAME %s" % (tmpFile, tiffFile)
#    os.system(cmd)
#
#    jpgFile = os.path.join(outPath, "images", os.path.split(fits)[1][:-5]+".jpg")
#    cmd = "convert %s %s" % (tiffFile, jpgFile)
#    os.system(cmd)
#    
#    print "Outfile: ", jpgFile
#    print
#
#    if not os.path.isfile(jpgFile):
#        return "Creation of %s failed" % (jpgFile,), None
#
#    os.remove(tmpFile)
#    os.remove(tiffFile)
#    
#    return "ok", jpgFile



def AddImgNode(runDir, document, parentNode, type, prefix, webDir):
    
    fitsMosaic = os.path.join(runDir, type, "BINNED", "%s_mos.fits" % (prefix, ))
    if os.path.exists(fitsMosaic):
        status, jpgPath = ConvertMosaic(fitsMosaic, webDir)
    else:
        return "No such file: %s" % (fitsMosaic, )

    if status != "ok":
        return status
    imgNode = document.createElement("img")
    imgPath = os.path.join("images", os.path.split(jpgPath)[1])
    imgNode.setAttribute("source", imgPath)
    parentNode.appendChild(imgNode)
    return "ok" 


def ConvertDocument(webDir, prefix, document, xslt):
    xmlFile = os.path.join(webDir, "%s.xml" % (prefix, ))
    htmlFile = os.path.join(webDir, "%s.html" % (prefix, ))
    xsltFile = os.path.join("%s" % (PipeWWW, ), xslt)
    f = open(xmlFile, "w")
    xml.dom.ext.PrettyPrint(document, f)
    f.close()
    cmd = "xsltproc %s %s > %s"  % (xsltFile, xmlFile, htmlFile)
    os.system(cmd)
    return


def GetHeaderVal(file, head):
    try:
        fimg = pyfits.open(file)
    except IOError:
        print "No such file or directory: %s" % (file, )
        return None
    hdr = fimg[0].header
    for hdrTup in hdr.items():
        if hdrTup[0] == head:
            val = hdrTup[1]
            fimg.close()
            return val

    return None
    
# Take a (large) numarray, return the median value
def GetMedian(data):
    n = data.nelements()
    lData = numarray.reshape(data, n)
    lData.sort()
    return lData[int(n/2)]

# Take a numarray, cut of the lowest and highest 2.5%
# and compute the stdev
def GetCutStdev(data):
    n = data.nelements()
    lData = numarray.reshape(data, n)
    lData.sort()
    cData = lData[int(n*0.025):int(n*0.975)]
    return cData.stddev()


class CoaddHistClass:
    def __init__(self, fieldDir, filter, extension, webBase, ident,
                 ending="wcs", nochips=8):
        self.fieldDir = fieldDir
        self.coaddDir = os.path.join(fieldDir, filter)
        self.filter = filter
        self.extension = extension
        base, self.field = os.path.split(fieldDir)
        if not self.field:
            # Split again because last time we only got the trailing /
            self.field = os.path.split(base)[1]
        self.webDir = os.path.join(webBase, self.field, filter)
        self.noChips = nochips
        self.ident = ident
        self.ending = ending
        self.createDirs()
        return
    
    def createDirs(self):
        dirList = [self.webDir, os.path.join(self.webDir, "images")]
        for dir in dirList:
            if not os.path.exists(dir):
                os.makedirs(dir)
        return

    def makeCoaddIndex(self):

        cwd = os.getcwd()
        os.chdir(self.coaddDir)
        dList = glob.glob("coadd_*")
        dList.sort()
        
        document = implementation.createDocument(None, None, None)
        rootElement = document.createElement("document")
        title = "%s (%s-band) Co-Addition Overview" % (self.field, self.filter)
        rootElement.setAttribute("title", title)
        tableNode = AddTableToDoc(document, "Co-additions for this field",
                                  ["Identifier", "Seeing/arcsec", "ZP/mag", "Exp. Time/s", "Selection criteria"],
                                  ["left", "right", "right", "right", "left"])
        for d in dList:
            dID = string.split(d, "_", 1)[1]
            recordNode = document.createElement("record")
            AddTextFieldToRecord(document, recordNode, d, (("link", d), ))
            fitsFile = "%s/%s_%s.%s.swarp.fits" % (d, self.field, self.filter, dID)
            val = GetHeaderVal(fitsFile, "SEEING")
            if val:
                val = round(val, 2)
            AddTextFieldToRecord(document, recordNode, val)
            val = GetHeaderVal(fitsFile, "MAGZP")
            if val:
                val = round(val, 2)
            AddTextFieldToRecord(document, recordNode, val)
            val = GetHeaderVal(fitsFile, "TEXPTIME")
            if val:
                val = round(val, 1)
            else:
                val = GetHeaderVal(fitsFile, "EXPTIME")
                if val:
                  val = round(val, 1)  
            AddTextFieldToRecord(document, recordNode, val)
            i = 1
            cond = ""
            while 1:
                val = GetHeaderVal(fitsFile, "COND%d" % (i, ))
                if not val:
                    break
                
                cond += val
                i += 1
            AddTextFieldToRecord(document, recordNode, cond)
            tableNode.appendChild(recordNode)
        
        rootElement.appendChild(tableNode)

        diagNode = document.createElement("diagPlots")
        plotList = glob.glob("/%s/%s/plots/%s*.ps" % (self.fieldDir, self.filter, self.filter))
        
        for plot in plotList:
            status, pngPath = self.convertPlot(plot)
            if not status == "ok":
                print status

            if pngPath:
                imgNode = document.createElement("img")
                imgPath = os.path.join("images", os.path.split(pngPath)[1])
                imgNode.setAttribute("source", imgPath)
                diagNode.appendChild(imgNode)
        rootElement.appendChild(diagNode)

        footerNode = AddFooterNode(document)
        rootElement.appendChild(footerNode)
        
        document.appendChild(rootElement)
        xmlFile = os.path.join(self.webDir, "index.xml")
        htmlFile = os.path.join(self.webDir, "index.html")
        f = open(xmlFile, "w")
        xml.dom.ext.PrettyPrint(document, f)
        f.close()
        ReleaseNode(document)
        cmd = "xsltproc %s/coaddlist.xslt %s > %s" % (PipeWWW, xmlFile, htmlFile)
        os.system(cmd)
        os.chdir(cwd)

        return dList
        

    def makeCoaddPage(self, dir):

        cwd = os.getcwd()
        os.chdir(dir)
        coaddWeb = os.path.join(self.webDir, "coadd_"+self.ident)
        if not os.path.exists(coaddWeb):
            os.makedirs(coaddWeb)
        frameList = glob.glob("*%s.%s.fits" % (self.extension, self.ending))
        fitsFile = os.path.join(dir,
                                "%s_%s.%s.swarp.fits" % (self.field, self.filter, self.ident))
        status, jpgPath = ConvertMosaicLarge(fitsFile, self.webDir, 2)
        if not status == "ok":
            print status

        title = "%s_%s %s" % (self.field, self.filter, self.ident)
        document = implementation.createDocument(None, None, None)
        rootElement = document.createElement("document")
        rootElement.setAttribute("title", title)
        if jpgPath:
            imgNode = document.createElement("img")
            imgPath = os.path.join("../images", os.path.split(jpgPath)[1])
            imgNode.setAttribute("source", imgPath)
            rootElement.appendChild(imgNode)

        fitsFile = os.path.join(dir,
                                "%s_%s.%s.swarp.weight.fits"
                                % (self.field, self.filter, self.ident))
        status, jpgPath = ConvertMosaicLarge(fitsFile, self.webDir, 0, levels=[0, None])

        if not status == "ok":
            print status

        if jpgPath:
            imgNode = document.createElement("img")
            imgPath = os.path.join("../images", os.path.split(jpgPath)[1])
            imgNode.setAttribute("source", imgPath)
            rootElement.appendChild(imgNode)

        diagNode = document.createElement("diagPlots")
        plotList = glob.glob("../postcoadd/plots/%s_%s.%s*" %
                             (self.field, self.filter, self.ident))

        setPlotList = glob.glob("../plots/coadd_%s*.ps" % (self.ident, ))
        print "setPlotList: ", setPlotList
        plotList = setPlotList + plotList
        
        for plot in plotList:
            status, pngPath = self.convertPlot(plot)
            if not status == "ok":
                print status

            if pngPath:
                imgNode = document.createElement("img")
                imgPath = os.path.join("../images", os.path.split(pngPath)[1])
                imgNode.setAttribute("source", imgPath)
                diagNode.appendChild(imgNode)
        rootElement.appendChild(diagNode)
                

        suffix = "*_1%s.%s.fits" % (self.extension, self.ending)
        frameList = glob.glob(suffix)
        sciNode = document.createElement("runList")
        runList = []
        frameDict = {}
        for frame in frameList:
            run = self.getRun(frame)
            if not run in runList:
                runList.append(run)
                frameDict[run] = []
            frameDict[run].append(frame)
        runList.sort()
        tableNode = AddTableToDoc(document, "Runs and Exposures",
                                  ["No.", "Run", "Exposure"],
                                  ["right", "left", "left"])
        i = 1
        for run in runList:
            print run
            recordNode = document.createElement("record")
            AddTextFieldToRecord(document, recordNode, "")
            AddTextFieldToRecord(document, recordNode, run,
                                 [("link", os.path.join("..", "..", "..", self.filter, run))])
            AddTextFieldToRecord(document, recordNode, "")
            tableNode.appendChild(recordNode)
            frameDict[run].sort()
            for frame in frameDict[run]:
                print frame
                print suffix
                frameEntry = frame[:-(len(suffix)-1)]
#                frameEntry = frame[:-12]
                recordNode = document.createElement("record")
                AddTextFieldToRecord(document, recordNode, str(i))
                i += 1
                AddTextFieldToRecord(document, recordNode, "")
                link = os.path.join("..", "..", "..", self.filter, run, "science_frames",
                                    string.lower(frameEntry)+".html")
                AddTextFieldToRecord(document, recordNode, frameEntry,
                                     [("link", link)])
                tableNode.appendChild(recordNode)
        sciNode.appendChild(tableNode)

        footerNode = AddFooterNode(document)
        rootElement.appendChild(footerNode)
        rootElement.appendChild(sciNode)
        document.appendChild(rootElement)
        xmlFile = os.path.join(coaddWeb, "index.xml")
        htmlFile = os.path.join(coaddWeb, "index.html")
        f = open(xmlFile, "w")
        xml.dom.ext.PrettyPrint(document, f)
        f.close()
        ReleaseNode(document)
        cmd = "xsltproc %s/coaddframe.xslt %s > %s" % (PipeWWW, xmlFile, htmlFile)
        os.system(cmd)

        os.chdir(cwd)
        return

    def getRun(self, frame):
        cwd = os.getcwd()
        os.chdir(self.fieldDir)
        os.chdir("../%s/" % (self.filter, ))

        frameBase = string.join(string.split((frame), "_")[:-1])
        globExp = "run_*/SCIENCE_%s/ORIGINALS/%s*" % (self.filter, frameBase)
        lList = glob.glob(globExp)
        if len(lList) != 1:
            print "\nCould not uniquely identify frame:", frame
            print lList
            os.chdir(cwd)
            return ""

        run = string.split(lList[0], "/")[0]
        return run
    
    def convertPlot(self, psFile):
        if not os.path.isfile(psFile):
            return "No such file: %s" %(psFile,), None

        fileName = os.path.split(psFile)[1]
        pngOut = os.path.join(self.webDir, "images", fileName[:-3]+".png")
        cmd = "gs -sOutputFile=%s -sDEVICE=png16 -dNOPAUSE -dBATCH %s" % (pngOut, psFile)
        #cmd = "convert -density 144x144 -rotate 90 %s %s" % (psFile, pngOut)
        os.system(cmd)
        print cmd
        if not os.path.isfile(pngOut):
            return "Creation of %s failed" % (pngOut), None
        
        return "ok", pngOut
    



##############################################################
#
# Class to generate the run logs for SCIENCE frames
#
##############################################################
class ScienceHistory:
    def __init__(self, baseDir, filter, run, webBase, extension, nochips=8):
        self.runDir = os.path.join(baseDir, filter, run)
        self.webDir = os.path.join(webBase, filter, run)
        self.noChips = nochips
        self.run = run
        self.extension = extension
        self.filter = filter
        
        self.cwd = os.getcwd()
        self.createDirs()
        return

    def createDirs(self):
        dirList = [self.webDir, os.path.join(self.webDir, "images"),
                   os.path.join(self.webDir, "science_frames", "images"),
                   os.path.join(self.webDir, "standard"),
                   os.path.join(self.webDir, "standard", "images")]
        for dir in dirList:
            if not os.path.exists(dir):
                os.makedirs(dir)
        return


    def sciListPage(self, type, singlePages="yes"):
        nightList = []
        document = implementation.createDocument(None, None, None)
        rootElement = document.createElement("document")
        rootElement.setAttribute("title", "%s exposures in run %s" % (string.upper(type), self.run))
        tableNode = AddTableToDoc(document, "List of %s exposures" % (type, ),
                                  ["Exposure", "Object", "Exp. Time/s", "Seeing/\"", "Background/(1/s)", "<e1>", "<e2>", "ZP/mag"],
                                  ["left", "left", "right", "right", "right", "right", "right", "right"])
        sciFrameListList = self.getSciFrames(type)
        for sciFrameList in sciFrameListList:
            recordNode = document.createElement("record")
            for val in sciFrameList:
                if sciFrameList.index(val) == 0:
                    AddTextFieldToRecord(document, recordNode, val,
                                         [("link", os.path.join("science_frames", string.lower(val[:-4]+"html")))])
                    if singlePages == "yes":
                        print "Creating single page for", val
                        self.createSingleSci(type, val)
                else:
                    AddTextFieldToRecord(document, recordNode, val)
            # Add ZP from Image Header
            imgPath = os.path.join(self.runDir, type, sciFrameList[0][:-5]+"_1"+self.extension+".fits")
            zp = GetHeaderVal(imgPath, "ZP")
            coeff = GetHeaderVal(imgPath, "COEFF")
            nightID = GetHeaderVal(imgPath, "GABODSID")
            zpChoice = GetHeaderVal(imgPath, "ZPCHOICE")
            if not nightID:
                continue
            if not nightID in nightList:
                solFile = os.path.join(self.runDir, "STANDARD_%s" % (self.filter,), "calib",
                               "night_%d_%s_result.asc" % (nightID, self.filter))
                if os.path.exists(solFile):
                    self.createPhotPage(nightID, zp, coeff, zpChoice)
                    link = os.path.join("standard", "night_%d.html" % (nightID,))
                else:
                    link = None
                    
                nightList.append(nightID)

            if zp and float(zp) > -0.9:
                AddTextFieldToRecord(document, recordNode, "%.2f" % (round(float(zp), 2), ), [("link", link)])
#                AddTextFieldToRecord(document, recordNode, "%.2f" % (round(float(zp), 2)))
            elif link:
                AddTextFieldToRecord(document, recordNode, "-1", [("link", link)])
            else:
                AddTextFieldToRecord(document, recordNode, "-")
            tableNode.appendChild(recordNode)
        rootElement.appendChild(tableNode)

        footerNode = AddFooterNode(document)
        rootElement.appendChild(footerNode)
        document.appendChild(rootElement)
        ConvertDocument(self.webDir, string.lower(type), document, "calframes.xslt")
        ReleaseNode(document)
        os.chdir(self.cwd)
        return


    def createPhotPage(self, night, zp, coeff, zpChoice=None):
        stdPageDir = os.path.join(self.webDir, "standard")
        pipe = os.popen("caldate -d 31/12/1998 -i %d" % (night,))
        result = pipe.read()
        pipe.close()
        civNight = string.split(result)[2]

        document = implementation.createDocument(None, None, None)
        rootElement = document.createElement("document")
        rootElement.setAttribute("title", "Photometric solutions for night %d (%s)"
                                 % (night, civNight))
        tableNode = AddTableToDoc(document, "Photometric Solutions",
                                  ["ZP/mag", "Ext. Coeff.", "Col. Term", "Type", "Selected"],
                                  ["right", "right", "right", "left", "left"])
        solFile = os.path.join(self.runDir, "STANDARD_%s" % (self.filter,), "calib",
                               "night_%d_%s_result.asc" % (night, self.filter))
        f = open(solFile, "r")
        i = 0
        solType=["Z-K-C", "Z---C", "Z----"] 
        for sol in f.readlines():
            recordNode = document.createElement("record")
            zpSol, coeffSol, ctSol = string.split(sol)
            if not zpChoice:
                # It's really crappy that we have to find the accepted solution again
                # by comparing with all solutions. This is bound to fail at some point
                try:
                    if fabs(float(zpSol)-zp) < 1e-4 and fabs(float(coeffSol)-coeff) <1e-4:
                        selected = "yes"
                        attr = [("mode", "b")]
                    else:
                        selected = "no"
                        attr = []
                # Older version did not always insert ZP and COEFF, they might be None ...
                except TypeError:
                    selected = "no"
                    attr = []
            else:
                # New version write to the header which solution was chosen
                if zpChoice == i+1:
                    selected = "yes"
                    attr = [("mode", "b")]
                else:
                    selected = "no"
                    attr = []
                    
            AddTextFieldToRecord(document, recordNode,
                                     "%.2f" % (round(float(zpSol), 2), ), attr)
            AddTextFieldToRecord(document, recordNode,
                                     "%.2f" % (round(float(coeffSol), 2), ), attr)
            AddTextFieldToRecord(document, recordNode,
                                     "%.2f" % (round(float(ctSol), 2), ), attr)
            AddTextFieldToRecord(document, recordNode, solType[i], attr)
            AddTextFieldToRecord(document, recordNode, selected, attr)
            i += 1
            tableNode.appendChild(recordNode)
            
        rootElement.appendChild(tableNode)

        plotNode = document.createElement("photcal")
        plotNode.setAttribute("heading", "Plot of photometric solutions")
        psFile = os.path.join(self.runDir, "STANDARD_%s" % (self.filter,), "calib",
                               "night_%d_%s_result.ps" % (night, self.filter))
        status, pngPath = self.convertPhotCalPlot(psFile)
        if status != "ok":
            ReleaseNode(document)
            print status
            return
        imgNode = document.createElement("img")
        imgPath = os.path.join("images", os.path.split(pngPath)[1])
        imgNode.setAttribute("source", imgPath)
        plotNode.appendChild(imgNode)
        rootElement.appendChild(plotNode)
        
        footerNode = AddFooterNode(document)
        rootElement.appendChild(footerNode)
        document.appendChild(rootElement)
        ConvertDocument(stdPageDir, "night_%d" % (night,), document, "calframes.xslt")
        ReleaseNode(document)
        return


    def convertPhotCalPlot(self, psPath):
        if not os.path.isfile(psPath):
            return "No such file: %s" %(psPath,), None
        
        psFile = os.path.split(psPath)[1]
        pngOut = os.path.join(self.webDir, "standard", "images", psFile[:-3]+".png")
        cmd = "convert -density 144x144 -rotate 90 %s %s" % (psPath, pngOut)
        os.system(cmd)
        if not os.path.isfile(pngOut):
            return "Creation of %s failed" % (pngOut), None
        return "ok", pngOut

    
    def createSingleSci(self, type, frame):
        sciPageDir = os.path.join(self.webDir, "science_frames")
        
        document = implementation.createDocument(None, None, None)
        rootElement = document.createElement("document")
        rootElement.setAttribute("title", frame)
        mosaicNode = document.createElement("mosaic")
        mosaicNode.setAttribute("heading", "Binned Mosaic for %s" % (frame, ))
        status = AddImgNode(self.runDir, document, mosaicNode, type, frame[:-5], sciPageDir)
        if status != "ok":
            ReleaseNode(document)
            print status
            return
        rootElement.appendChild(mosaicNode)

        psfNode = document.createElement("mosaic")
        psfNode.setAttribute("heading", "PSF Pattern for %s" % (frame, ))
        psFile = os.path.join(self.runDir, type, "cat", "PSFcheck", frame[:-5]+".ps")
        status, pngPath = self.convertPSFPlot(psFile)
        if status != "ok":
            ReleaseNode(document)
            print status
            return
        imgNode = document.createElement("img")
        imgPath = os.path.join("images", os.path.split(pngPath)[1])
        imgNode.setAttribute("source", imgPath)
        psfNode.appendChild(imgNode)
        rootElement.appendChild(psfNode)

        footerNode = AddFooterNode(document)
        rootElement.appendChild(footerNode)
        document.appendChild(rootElement)
        ConvertDocument(sciPageDir, string.lower(frame[:-5]), document, "calframes.xslt")
        ReleaseNode(document)

        return


    def convertPSFPlot(self, psPath):
        if not os.path.isfile(psPath):
            return "No such file: %s" %(psPath,), None
        
        psFile = os.path.split(psPath)[1]
        pngOut = os.path.join(self.webDir, "science_frames", "images", psFile[:-3]+".png")
        cmd = "gs -sOutputFile=%s -sDEVICE=pngmono -dNOPAUSE -dBATCH %s >/dev/null" % (pngOut, psPath)
        #cmd = "convert -density 144x144 -rotate 90 %s %s" % (psPath, pngOut)
        os.system(cmd)
        if not os.path.isfile(pngOut):
            return "Creation of %s failed" % (pngOut), None
        return "ok", pngOut

        
    def getSciFrames(self, type):
        catPath = os.path.join(self.runDir, type, "cat", "chips.cat6")
        if not os.path.exists(catPath):
            catPath = os.path.join(self.runDir, type, "cat", "chips.cat5")
            if not os.path.exists(catPath):
                print "No such catalog found: ", catPath
                return []
        ftab = pyfits.open(catPath)
        tabHDU = ftab["STATS"]
        tabDat = tabHDU.data
        frameList = []
        for row in range(len(tabDat)):
            imgList = []
            imgList.append(tabDat[row].field("IMAGENAME")+".fits")
            imgList.append(tabDat[row].field("OBJECT"))
            imgList.append("%.2f" % (round(tabDat[row].field("EXPTIME"), 2), ))
            imgList.append("%.2f" % (round(tabDat[row].field("SEEING"), 2), ))
            imgList.append("%.2f" % (round(tabDat[row].field("BACKGR"), 2), ))
            try:
                imgList.append("%.3f" % (round(tabDat[row].field("e1"), 3), ))
                imgList.append("%.3f" % (round(tabDat[row].field("e2"), 3), ))
            except NameError:
                imgList.append("N/A")
                imgList.append("N/A")
                
            frameList.append(imgList)
        return frameList
            


################################################################
#
# Class to create the log pages for BIAS, DARK, and FLATS
#
###############################################################
class CalibHistory:
    def __init__(self, baseDir, filter, run, webBase, nochips=8):

        self.runDir = os.path.join(baseDir, filter, run)
        self.webDir = os.path.join(webBase, filter, run)
        self.noChips = nochips
        self.filter = filter
        self.run = run
        
        self.cwd = os.getcwd()
        self.createDirs()
        return

    def createDirs(self):
        dirList = [self.webDir, os.path.join(self.webDir, "images")]
        for dir in dirList:
            if not os.path.exists(dir):
                os.makedirs(dir)
        return



    def indexPage(self):
        document = implementation.createDocument(None, None, None)
        rootElement = document.createElement("document")
        rootElement.setAttribute("title", "Contents of run %s, filter %s" % (self.run, self.filter))

        for files in ["BIAS", "DARK", "SCIENCE_%s" % (self.filter, ),
                      "SKYFLAT_%s" % (self.filter, ),
                      "DOMEFLAT_%s" % (self.filter, ),
                      "STANDARD_%s" % (self.filter, )]:
            checkPath = os.path.join(self.webDir, string.lower(files)+".html")
            if not os.path.exists(checkPath):
                continue
            filesNode = document.createElement("files")
            filesNode.setAttribute("link", string.lower(files)+".html")
            textNode = document.createTextNode(files)
            filesNode.appendChild(textNode)
            rootElement.appendChild(filesNode)

        footerNode = AddFooterNode(document)
        rootElement.appendChild(footerNode)
        document.appendChild(rootElement)
        ConvertDocument(self.webDir, "index", document, "runindex.xslt")
        ReleaseNode(document)
        return
                      

    def calFramePage(self, type):
        document = implementation.createDocument(None, None, None)
        rootElement = document.createElement("document")
        rootElement.setAttribute("title", "%s frames in run %s" % (string.upper(type), self.run))
        mosaicNode = document.createElement("mosaic")
        mosaicNode.setAttribute("heading", "Master %s frame" % (string.upper(type), ))
        status = self.addImgNode(document, mosaicNode, type)
        if status != "ok":
            ReleaseNode(document)
            print status
            return
        rootElement.appendChild(mosaicNode)
        masterFrameNode = AddTableToDoc(document, "Master %s frames" % (type, ),
                                        ["Frame", "mean", "median", "stdev", "min", "max"],
                                        ["left", "right", "right", "right", "right", "right"])
        chipFrameNodes = []
        for chip in range(1, self.noChips+1):
            frameName = "%s_%d.fits" % (type, chip)
            calFrame = os.path.join(self.runDir, type, frameName)
            if not os.path.exists(calFrame):
                print "No such calibration file: ", calFrame
                continue
            fimg=pyfits.open(calFrame)
            dat=fimg[0].data
            recordNode = document.createElement("record")
            AddTextFieldToRecord(document, recordNode, frameName)
            AddTextFieldToRecord(document, recordNode, "%.2f" % (round(dat.mean(), 2)), )
            median = GetMedian(dat)
            AddTextFieldToRecord(document, recordNode, "%.2f" % (round(median, 2)), )
            AddTextFieldToRecord(document, recordNode, "%.2f" % (round(GetCutStdev(dat), 2)), )
            AddTextFieldToRecord(document, recordNode, "%.2f" % (round(dat.min(), 2)), )
            AddTextFieldToRecord(document, recordNode, "%.2f" % (round(dat.max(), 2)), )
            masterFrameNode.appendChild(recordNode)

            calDict = {}
            catFile = os.path.join(self.runDir, type, "cat", "chip_%d_stat.cat" % (chip, ))
            if os.path.exists(catFile):
                ftab = pyfits.open(catFile)
                tabHDU = ftab["STATS"]
                tabDat = tabHDU.data
                for row in range(len(tabDat)):
                    try:
                        exptime = tabDat[row].field("EXPTIME")
                    except:
                        exptime = None
                    calDict[tabDat[row].field("FITSFILE")] = {"mode"   : tabDat[row].field("Mode"),
                                                              "median" : tabDat[row].field("Median"),
                                                              "mean"   : tabDat[row].field("Mean"),
                                                              "stdev"  : tabDat[row].field("Stdev"),
                                                              "exptime": exptime}
                ftab.close()
            singleFrameNode = self.singleFrameTable(type, fimg[0].header, chip, calDict, document)
            chipFrameNodes.append(singleFrameNode)
            fimg.close()
        rootElement.appendChild(masterFrameNode)

        for singleFrameTable in chipFrameNodes:
            rootElement.appendChild(singleFrameTable)

        footerNode = AddFooterNode(document)
        rootElement.appendChild(footerNode)        
        document.appendChild(rootElement)
        ConvertDocument(self.webDir, string.lower(type), document, "calframes.xslt")
        ReleaseNode(document)
        os.chdir(self.cwd)
        return


    def singleFrameTable(self, type, header, chip, calDict, document):
        tableNode = AddTableToDoc(document, "%s frames in %s_%d.fits" % (type, type, chip),
                                  ["Frame", "Exp. Time/s", "mode", "median", "mean", "stdev"],
                                  ["left", "right", "right", "right", "right", "right"])

        singleCalList = self.getCalFits(header)
        for singleCal in singleCalList:
            recordNode = document.createElement("record")
            AddTextFieldToRecord(document, recordNode, singleCal)
            calFitsFile = os.path.join(self.runDir, type, singleCal)
            expTime = calDict[singleCal]["exptime"]
            if not expTime and os.path.exists(calFitsFile):
                expTime = GetHeaderVal(calFitsFile, "EXPTIME")
            elif not os.path.exists(calFitsFile):
                print "Error: No such calibration file: ", calFitsFile

            try:
                AddTextFieldToRecord(document, recordNode, "%.2f" % (round(float(expTime), 2), ))
            except:
                AddTextFieldToRecord(document, recordNode, "-")
                
            try:
                mode = "%.2f" % (round(calDict[singleCal]["mode"], 2), )
            except KeyError:
                mode = "-"
            try:
                median = "%.2f" % (round(calDict[singleCal]["median"], 2), )
            except KeyError:
                median = "-"
            try:
                mean = "%.2f" % (round(calDict[singleCal]["mean"], 2), )
            except KeyError:
                mean = "-"
            try:
                stdev = "%.2f" % (round(calDict[singleCal]["stdev"], 2), )
            except KeyError:
                stdev = "-"

            AddTextFieldToRecord(document, recordNode, mode)
            AddTextFieldToRecord(document, recordNode, median)
            AddTextFieldToRecord(document, recordNode, mean)
            AddTextFieldToRecord(document, recordNode, stdev)
            tableNode.appendChild(recordNode)

        return tableNode


    def addImgNode(self, document, parentNode, type):
        
        fitsMosaic = os.path.join(self.runDir, type, "BINNED", "%s_mos.fits" % (type, ))
        if os.path.exists(fitsMosaic):
            status, jpgPath = ConvertMosaic(fitsMosaic, self.webDir)
        else:
            return "No such file: %s" % (fitsMosaic, )

        if status != "ok":
            return status
        imgNode = document.createElement("img")
        imgPath = os.path.join("images", os.path.split(jpgPath)[1])
        imgNode.setAttribute("source", imgPath)
        parentNode.appendChild(imgNode)
        return "ok"


    def getCalFits(self, hdr):
        bType = self.getCalType(hdr)
        if bType == "flips":
            bList = self.readFlipsCal(hdr)
        elif bType == "eclipse":
            bList = self.readEclipseCal(hdr)
        elif bType == "preprocess":
            bList = self.readPreprocessCal(hdr)
        else:
            print "Error:"
            print "  Could not determine whether the file was written by flips or eclipse" 
            print
            return []
        return bList

    
    # Determine whether frames were processed with
    # flips or eclipse
    def getCalType(self, hdr):

        haveImcombine  = 0
        haveImred      = 0
        havePreprocess = 0

        for hdrTup in hdr.items():
            if hdrTup[0] != "HISTORY":
                continue

            if string.find(hdrTup[1], "imcombflat") != -1:
                haveImcombine = 1
            elif string.find(hdrTup[1], "imred") != -1:
                haveImred = 1
            elif string.find(hdrTup[1], "preprocess") != -1:
                havePreprocess = 1

            if haveImred or haveImcombine or havePreprocess:
                break

        if haveImcombine:
            return "flips"
        elif haveImred:
            return "eclipse"
        elif havePreprocess:
            return "preprocess"
        # Unrecognized frame generator
        return

    
    def readFlipsCal(self, hdr):
        bList = []
        for hdrTup in hdr.items():
            if hdrTup[0] != "HISTORY" or \
                   string.find(hdrTup[1], "imcomb") == -1 or \
                   string.find(hdrTup[1], "output image") != -1:
                continue

            if string.find(hdrTup[1], ".fits") == -1:
                continue

            valList = string.split(hdrTup[1])
            for item in valList:
                if string.find(item, ".fits") == -1:
                    continue
                bList.append(item)
                continue
        return bList

    def readEclipseCal(self, hdr):
        bList = []
        for hdrTup in hdr.items():
            if hdrTup[0] != "HISTORY" or \
                   string.find(hdrTup[1], "imred") == -1:
                continue

            if string.find(hdrTup[1], ".fits") == -1:
                continue

            valList = string.split(hdrTup[1])
            for item in valList:
                if string.find(item, ".fits") == -1:
                    continue
                bList.append(item)
                continue
        return bList

    def readPreprocessCal(self, hdr):
        bList = []
        for hdrTup in hdr.items():
            if hdrTup[0] != "HISTORY" or \
                   string.find(hdrTup[1], "preprocess") == -1:
                continue

            if string.find(hdrTup[1], ".fits") == -1:
                continue

            valList = string.split(hdrTup[1])
            for item in valList:
                if string.find(item, ".fits") == -1:
                    continue
                bList.append(item)
                continue
        return bList

#####################################################################################
#
# END OF CLASS
#
#####################################################################################

def usage():
    print "Usage:"
    print "pipelog.py -a action -f filter -e extension -o webDir -b baseDir" 
    print "           -r (run|field) -w what [-n nochips -u]"
    print
    print "  -a, --action=STRING      specify which pages to create"
    print "                           (runindex|runcalib|runscience|setpages)"
    print "  -f, --filter=STRING      set the filter to FILTER, e.g. B or R"
    print "  -e, --extension=STRING   set the image extension, e.g. OFCSF"
    print "  -o, --webbase=DIRECTORY  specify the base directory of the web pages"
    print "  -b, --basedir=STRING     set the base directory of the data"
    print "  -r, --run=STRING         specify the run (run pages) or the set (set pages)"
    print "  -i, --ident=STRING       for character identifier for co-addition"
    print "  -w, --what=STRING        type of calibration to create pages for"
    print "  -d, --ending=STRING      ending of the images to be co-added, e.g., wcs or new (wcs)"
    print "  -n, --nochips=INT        set the number of the chips the camera has (8)"
    print "  -u, --update             update the science index page (only in runscience mode)"
    print 
    print "-w must be used in runcalib mode."
    print "-e must be set in runscience and setpages mode."
    print "-i must be used for setpages node."
    print "The number of chips defaults to 8."
    print
    print "Author:"
    print "  Joerg Dietrich <dietrich@astro.uni-bonn.de>" 
    
if __name__=="__main__":

    try:
        opts, args = getopt.getopt(sys.argv[1:], "a:f:e:o:b:r:i:w:n:ud:",
                                   ["action=", "filter=", "extension=", "webbase=",
                                    "basedir=", "run=", "ident=", "what=", "nochips=",
                                    "update", "ending"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    nochips = 8
    ending = "wcs"
    
    action = filter = extension = webDir = baseDir = run = ident = None
    singlePages = "yes"
    for o, a in opts:
        if o in ("-a", "--action"):
            action = a
        if o in ("-f", "--filter"):
            filter = a
        if o in ("-e", "--extension"):
            extension = a
        if o in ("-o", "--webbase"):
            webDir = a
        if o in ("-b", "--basedir"):
            baseDir = a
        if o in ("-r", "--run"):
            run = a
        if o in ("-i", "--ident"):
            ident = a
        if o in ("-w", "--what"):
            calType = a
        if o in ("-n", "nochips"):
            nochips = int(a)
        if o in ("-d", "ending"):
            ending = a
        if o in ("-u", "update"):
            singlePages="no"

    if not action or (action == "setpages" and (not extension or not ident))\
           or (action == "runscience" and not extension):
        usage()
        sys.exit(1)

    if action not in ("runindex", "runcalib", "runscience", "setpages"):
        usage()
        sys.exit(1)
        
    if action == "runindex":
        InstCalHist = CalibHistory(baseDir, filter, run, webDir, nochips)
        InstCalHist.indexPage()
        del(InstCalHist)
    elif action == "runcalib":
        InstCalHist = CalibHistory(baseDir, filter, run, webDir, nochips)
        InstCalHist.calFramePage(calType)
        del(InstCalHist)
    elif action == "runscience":
        InstSciHist = ScienceHistory(baseDir, filter, run, webDir, extension, nochips)
        InstSciHist.sciListPage("SCIENCE_%s" % (filter, ), singlePages)
        del(InstSciHist)
    elif action == "setpages":
        fieldDir = os.path.join(baseDir, run)
        InstSetHist = CoaddHistClass(fieldDir, filter, extension, webDir,
                                     ident, ending, nochips)
        dList = InstSetHist.makeCoaddIndex()
    
        d = os.path.join(fieldDir, filter, "coadd_"+ident)
        InstSetHist.makeCoaddPage(d)
