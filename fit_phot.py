#!/usr/bin/env python
#####################

# Calibrates a given filter

#####################

import sys, os, optparse, re, unittest, inspect
import numpy, astropy, astropy.io.fits as pyfits
if __name__ == '__main__':
    import matplotlib
    matplotlib.use('PS')
    from matplotlib import pylab
    pylab.ioff()
else:
    import pylab

import ldac, utilities, leastsq, photometry_db



#####################

__cvs_id__ = "$Id: fit_phot.py,v 1.25 2010-10-05 22:36:03 dapple Exp $"


##################################################
### Photometry Global Database
##################################################

class Phot_db(object):
    '''Provide lazy, proxy access to the photometry database of choice'''
    def __init__(self, db, *args, **keywords):
        self.db = db
        self.instance = None
        self.args = args
        self.keywords = keywords
    def __getattr__(self, name):
        if self.instance is None:
            self.instance = self.db(*self.args, **self.keywords)
        return getattr(self.instance, name)

__default_photometry_db__ = Phot_db(photometry_db.Photometry_db)

#########################################
### DEFAULTS
#########################################

__default_fluxtype__ = 'APER1'


##########################################
### DEFINED FILTER INFORMATION
##########################################

__3sec_zp__ = 25

filter_info = {
    'B':{'sdss_filter':'g','color1':'gmr','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0, 'color1cut' : lambda x : x < .8}, 
    'U':{'sdss_filter':'g', 'color1':'gmr','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0, 'color1cut': lambda x : numpy.logical_and(x > 0.25, x < 1.0)}, 
    'W-J-B':{'sdss_filter':'g','color1':'gmr','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0, 'color1cut' : lambda x : numpy.logical_and(x < .75,x>0.2)}, 
    'W-J-V':{'sdss_filter':'g','color1':'gmr','color2':'rmi','EXTCOEFF':-0.1202,'COLCOEFF':0.0, 'color1cut' : lambda x : numpy.logical_and(x < 1.0, x >0.35)}, 
    'W-C-RC':{'sdss_filter':'r','color1':'rmi','color2':'gmr','EXTCOEFF':-0.0925,'COLCOEFF':0.0, 'color1cut' : lambda x : x < 0.44}, 
    'W-C-IC':{'sdss_filter':'i','color1':'rmi','color2':'imz','EXTCOEFF':-0.02728,'COLCOEFF':0.0, \
              'color1cut' : lambda x : numpy.logical_and( x < 1,x>0)}, 
    'W-S-I+':{'sdss_filter':'i','color1':'rmi','color2':'imz','EXTCOEFF':-0.02728,'COLCOEFF':0.0, 'color1cut' : lambda x : x < 0.6}, 
    'I':{'sdss_filter':'i','color1':'imz','color2':'rmi','EXTCOEFF':-0.02728,'COLCOEFF':0.0, 'color1cut' : lambda x : x < 0.6}, 
    'W-S-Z+':{'sdss_filter':'z','color1':'imz','color2':'rmi','EXTCOEFF':0.0,'COLCOEFF':0.0, 'color1cut' : lambda x : numpy.logical_and(x < 0.8, x > 0.2)}, 
    'u':{'sdss_filter':'u','color1':'umg','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0, 'color1cut' : lambda x : numpy.isfinite(x)}, 
    'g':{'sdss_filter':'g','color1':'gmr','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0, 'color1cut' : lambda x : numpy.isfinite(x)},
    'r':{'sdss_filter':'r','color1':'rmi','color2':'umg','EXTCOEFF':-0.0925,'COLCOEFF':0.0, 'color1cut' : lambda x : numpy.isfinite(x)},
    'i':{'sdss_filter':'i','color1':'imz','color2':'rmi','EXTCOEFF':-0.02728,'COLCOEFF':0.0, 'color1cut' : lambda x : numpy.isfinite(x)},
    'z':{'sdss_filter':'z','color1':'imz','color2':'rmi','EXTCOEFF':0.0,'COLCOEFF':0.0, 'color1cut' : lambda x : numpy.isfinite(x)}
    }

#I_SUBARU   =  i_SDSS   (-0.276)*(r_SDSS - i_SDSS) + 0.020
#Fit to Pickles Stellar Template Library
colorterms = {#'SUBARU-10_1-1-W-C-IC': (0.40280557662545879, 0.44855074031464925),
 'SUBARU-10_1-1-W-C-IC': (0.276, 0.020),
 'SUBARU-10_1-1-W-C-RC': (0.30587358225815486, 0.42517900392093094),
 'SUBARU-10_1-1-W-J-B': (-0.24078726421577926, 0.26136672075848993),
 'SUBARU-10_1-1-W-J-V': (0.59960441249635976, 0.2194019839308905),
 'SUBARU-10_1-1-W-S-I+': (0.074485, 0.328308),
 'SUBARU-10_1-1-W-S-Z+': (0.044574463739716047, 0.37674513156137274),
# 'SUBARU-10_2-1-W-C-IC': (0.40280557662545879, 0.44855074031464925),
 'SUBARU-10_2-1-W-C-IC': (0.276, 0.020),
 'SUBARU-10_2-1-W-C-RC': (0.30587358225815486, 0.42517900392093094),
 'SUBARU-10_2-1-W-J-B': (-0.24078726421577926, 0.26136672075848993),
 'SUBARU-10_2-1-W-J-V': (0.59960441249635976, 0.2194019839308905),
 'SUBARU-10_2-1-W-S-I+': (0.074485, 0.328308),
 'SUBARU-10_2-1-W-S-Z+': (0.044574463739716047, 0.37674513156137274),
 'SUBARU-10_1-2-W-C-RC': (0.30587358225815486, 0.42517900392093094),
 'SUBARU-10_1-2-W-J-B': (-0.24078726421577926, 0.26136672075848993),
 'SUBARU-10_1-2-W-J-V': (0.59960441249635976, 0.2194019839308905),
 'SUBARU-10_1-2-W-S-I+': (0.074485, 0.328308),
 'SUBARU-10_1-2-W-S-Z+': (0.044574463739716047, 0.37674513156137274),
 'SUBARU-10_2-2-W-C-IC': (0.40280557662545879, 0.44855074031464925),
 'SUBARU-10_2-2-W-C-RC': (0.30587358225815486, 0.42517900392093094),
 'SUBARU-10_2-2-W-J-B': (-0.24078726421577926, 0.26136672075848993),
 'SUBARU-10_2-2-W-J-V': (0.59960441249635976, 0.2194019839308905),
 'SUBARU-10_2-2-W-S-I+': (0.074485, 0.328308),
 'SUBARU-10_2-2-W-S-Z+': (0.044574463739716047, 0.37674513156137274),
 'SUBARU-10_3-1-W-C-IC': (0.279459, 0.145487),
 'SUBARU-10_3-1-W-C-RC': (0.301447, 0.425181),
 'SUBARU-10_3-1-W-J-B': (-0.211061, 0.136693),
 'SUBARU-10_3-1-W-J-V': (0.593218, 0.136693),
 'SUBARU-10_3-1-W-S-Z+': (0.076176, 0.341251),
 'SUBARU-8-1-W-C-IC': (0.264017, 0.145487),
 'SUBARU-8-1-W-C-RC': (0.29517895168989122, 0.42517900813547471),
 'SUBARU-8-1-W-J-B': (-0.23759822513479578, 0.26136672003092487),
 'SUBARU-8-1-W-J-V': (0.59222754271066269, 0.21940198721395668),
 'SUBARU-8-1-W-S-Z+': (0.039680091339973099, 0.37674513161790629),
 'SUBARU-8-2-W-C-IC': (0.258385, 0.145487),
 'SUBARU-8-2-W-C-RC': (0.29716045031934651, 0.42517900572453288),
 'SUBARU-8-2-W-J-B': (-0.091763, 0.339650),
 'SUBARU-8-2-W-J-V': (0.6116458875238111, 0.21940198507480779),
 'SUBARU-8-2-W-S-Z+': (0.014494538164775472, 0.3767451323829949),
 'SUBARU-8-4-W-C-IC': (0.260918, 0.145487),
 'SUBARU-8-4-W-C-RC': (0.29956356433016157, 0.42517900741658754),
 'SUBARU-8-4-W-J-B': (-0.27545711721961763, 0.26136672054131793),
 'SUBARU-8-4-W-J-V': (0.60061067325937401, 0.21940198472543423),
 'SUBARU-8-4-W-S-Z+': (0.04000067443408889, 0.37674513335575216),
 'SUBARU-9-1-W-C-IC': (0.264017, 0.145487),
 'SUBARU-9-1-W-C-RC': (0.29517895168989122, 0.42517900813547471),
 'SUBARU-9-1-W-J-B': (-0.23759822513479578, 0.26136672003092487),
 'SUBARU-9-1-W-J-V': (0.59222754271066269, 0.21940198721395668),
 'SUBARU-9-1-W-S-Z+': (0.039680091339973099, 0.37674513161790629),
 'SUBARU-9-2-W-C-IC': (0.258385, 0.145487),
 'SUBARU-9-2-W-C-RC': (0.29716045031934651, 0.42517900572453288),
 'SUBARU-9-2-W-J-B': (-0.091763, 0.339650),
 'SUBARU-9-2-W-J-V': (0.6116458875238111, 0.21940198507480779),
 'SUBARU-9-2-W-S-Z+': (0.014494538164775472, 0.3767451323829949),
 'SUBARU-9-4-W-C-IC': (0.260918, 0.145487),
 'SUBARU-9-4-W-C-RC': (0.29956356433016157, 0.42517900741658754),
 'SUBARU-9-4-W-J-B': (-0.27545711721961763, 0.26136672054131793),
 'SUBARU-9-4-W-J-V': (0.60061067325937401, 0.21940198472543423),
 'SUBARU-9-4-W-S-Z+': (0.04000067443408889, 0.37674513335575216),
 'SUBARU-9-8-W-C-IC': (0.260918, 0.145487),
 'SUBARU-9-8-W-C-RC': (0.29956356433016157, 0.42517900741658754),
 'SUBARU-9-8-W-J-B': (-0.27545711721961763, 0.26136672054131793),
 'SUBARU-9-8-W-J-V': (0.60061067325937401, 0.21940198472543423),
 'SUBARU-9-8-W-S-Z+': (0.04000067443408889, 0.37674513335575216),
 'WHT-0-1-B': (0.34601698954778792, 0.080284105865396194),
 'WHT-0-1-U': (1.7302077394178275, 0.42729437531924919)}
#subaru-9-8 faked, assuming like 9-4, assuming 10_x-2 is like 10_x-1



##################################
### UTILITIES
##################################

def stdCalibrationCuts(cat, mag, sdss_names, colorcut_function):

    peakvals = cat['SEx_BackGr'] + cat['SEx_MaxVal']
    
    colorcut = colorcut_function(cat[sdss_names.sdss_color])

    detected = numpy.logical_and(
        numpy.logical_and( numpy.abs(mag) < 90,
                           numpy.abs(cat[sdss_names.sdss_mag]) < 90), 
        numpy.abs(cat[sdss_names.sdss_color]) < 90)

    # detected = numpy.logical_and(detected,cat[sdss_names.sdss_mag]<18)

    #    print 'detected = '
    #    print detected

    # if 0:
    if 1. in cat['Clean']:
        print "using clean set"
#        good_detection = numpy.logical_and(
#            numpy.logical_and(peakvals < 20000,
#                              cat['SEx_Flag']<2),
#            cat['Clean'] == 1)
        good_detection =  cat['Clean'] == 1

    else:
        print "using unclean set"
#        good_detection = numpy.logical_and(
#            numpy.logical_and(peakvals < 20000,
#                              cat['SEx_Flag']==0),
        good_detection = cat['Clean'] != 1
        #        good_detection =  numpy.logical_and( cat['SEx_Flag']==0, \
        #                                      cat['Clean'] != 1)


    print len(cat)
#    print  cat['SEx_Flag']
#    print cat['Clean']
    
    return numpy.logical_and( numpy.logical_and( detected,
                                                 good_detection),
                              colorcut)


#######################

def basicCalCuts(cat, mag, sdss_names, colorcut_function):

    detected = numpy.logical_and(mag < 90, mag > -90)
    color = cat[sdss_names.sdss_color]
    sdssmag = cat[sdss_names.sdss_mag]
    goodSDSS = numpy.logical_and(numpy.logical_and(color > -50, color < 50), numpy.logical_and(sdssmag < 90, sdssmag > -90))

    return numpy.logical_and(detected, goodSDSS)

#######################

def looseCalibrationCuts(cat, mag, sdss_names, colorcut_function):

    peakvals = cat['SEx_BackGr'] + cat['SEx_MaxVal']
    
    colorcut = colorcut_function(cat[sdss_names.sdss_color])

    detected = numpy.logical_and(
        numpy.logical_and( numpy.abs(mag) < 90,
                           numpy.abs(cat[sdss_names.sdss_mag]) < 90), 
        numpy.abs(cat[sdss_names.sdss_color]) < 90)

    detected = numpy.logical_and(detected,numpy.abs(cat[sdss_names.sdss_mag]) < 23)
    detected = numpy.logical_and(detected,numpy.abs(mag) < 23)

    #    print 'detected = '
    #    print detected

    print "using unclean set"
    good_detection = numpy.logical_and(
        numpy.logical_and(peakvals < 20000,
                          cat['SEx_Flag']==0),
        cat['Clean'] != 1)

    print len(cat)
#    print  cat['SEx_Flag']
#    print cat['Clean']
    
    return numpy.logical_and( numpy.logical_and( detected,
                                                 good_detection),
                              colorcut)


#######################

class SDSSNames(object):
    def __init__(self, filterInfo):
        self.sdss_filter = filterInfo['sdss_filter']
        self.sdss_mag = '%smag' % self.sdss_filter
        self.sdss_magerr = '%serr' % self.sdss_filter
        self.sdss_color = filterInfo['color1']
        self.sdss_color_err = '%serr' % self.sdss_color

#######################

class FitResults(object):
    def __init__(self, zp, zperr, colorterm, colorterm_err, fixedcolor):
        self.zp = float(zp)
        self.zperr = float(zperr)
        self.colorterm = float(colorterm)
        if colorterm_err is None:
            self.colorterm_err = colorterm_err
        else:
            self.colorterm_err = float(colorterm_err)
        self.fixedcolor = fixedcolor

    def __str__(self):
        if self.fixedcolor:
            return 'zp = %5.3f +- %3.3f' % (self.zp, self.zperr)
        else:
            return 'zp = %5.3f +- %3.3f\tcolorterm = %5.3f +- %3.3f' % (self.zp, self.zperr,
                                                                        self.colorterm, self.colorterm_err)

######################

class CalibrationData(object):
    def __init__(self, mag, mag_err, refmag, refmag_err, color, colorerr, colorterm = None):
        self.mag = mag
        self.mag_err = mag_err
        self.refmag = refmag
        self.refmag_err = refmag_err
        self.color = color
        self.colorerr = colorerr
        self.colorterm = colorterm

#        print 'colorterm = ', colorterm

    ################

    def vals(self):

        if self.colorterm is None:
            return self.refmag - self.mag
        return self.refmag - self.mag - self.colorterm*self.color

    ################

    def errs(self):
        if self.colorterm is None:
            return numpy.sqrt(self.mag_err**2 + \
                                  self.refmag_err**2)
        return numpy.sqrt(self.refmag_err**2 + \
                              self.mag_err**2 + \
                              (self.colorterm**2)*self.colorerr**2)

    #################

    def calibrate(self):

        if(len(self.mag) < 4):
            sys.stderr.write("Not Enough Data to do Photometry\n")
            return
        

        if self.colorterm is None:
            return self.calibrate_freecolor()
        else:
            return self.calibrate_fixedcolor()

    ##################

    def calibrate_fixedcolor(self):

        vals = self.vals()
        errs = self.errs()

        weights = 1./errs**2
        weightsum = weights.sum()
        zp = (weights*vals).sum(dtype=numpy.float64)/weightsum
        zperr = numpy.sqrt(1./weightsum)


        return FitResults(zp, zperr, self.colorterm, colorterm_err = None, fixedcolor=True)

    ########################

    def calibrate_freecolor(self):


        vals = self.vals()
        errs = self.errs()
    
        params, chisq, covar, isCon = leastsq.linear_leastsq(self.color, vals, errs, fullOutput=True)

        colorterm = params[0]
        colorterm_err = numpy.sqrt(covar[0][0])
        zp = params[1]
        zperr = numpy.sqrt(covar[1][1])

        
        return FitResults(zp, zperr, colorterm, colorterm_err, fixedcolor=False)
        

        

#######################

########################

def saveCalibration(cluster, filter, fitResults, photometry_db = __default_photometry_db__, specification = {}):

    

    db_calib = photometry_db.registerPhotometricCalibration(
        cluster = cluster,
        filter = filter,
        fitresults = fitResults,
        **specification)

        

    photometry_db.updateCalibration(cluster, filter = filter, calibration = db_calib, **specification)


##################################
### USER-CALLABLE FUNCTIONS
##################################



def standardCalibration(cluster, filter, cat, fluxtype = __default_fluxtype__, plotdir=None, freecolor=False, photometry_db = __default_photometry_db__, specification = {}, cuts = stdCalibrationCuts):

    
    instrum, config, chipid, stdfilter = utilities.parseFilter(filter)

    mag_name = 'SEx_MAG_%s-%s' % (fluxtype, filter)
    magerr_name = 'SEx_MAGERR_%s-%s' % (fluxtype, filter)
    

    filterInfo = filter_info[stdfilter]
    sdss_names = SDSSNames(filterInfo)

    allfits = []

        
    goodObjs = cat.filter(cuts(cat, cat[mag_name], sdss_names, filterInfo['color1cut']))


        

    print ' we have '+str(len(goodObjs))+' good Objects'

        
    if freecolor:

        calibrationData = CalibrationData(mag = goodObjs[mag_name],
                                          mag_err = goodObjs[magerr_name],
                                          refmag = goodObjs[sdss_names.sdss_mag],
                                          refmag_err = goodObjs[sdss_names.sdss_magerr],
                                          color = goodObjs[sdss_names.sdss_color],
                                          colorerr = goodObjs[sdss_names.sdss_color_err])

    else:
        
        if filter not in colorterms:
            sys.stderr.write('Unknown Filter, Skipping: %s\n' % filter)
            return
        
        colorterm = colorterms[filter]
        
        calibrationData = CalibrationData(mag = goodObjs[mag_name],
                                          mag_err = goodObjs[magerr_name],
                                          refmag = goodObjs[sdss_names.sdss_mag],
                                          refmag_err = goodObjs[sdss_names.sdss_magerr],
                                          color = goodObjs[sdss_names.sdss_color],
                                          colorerr = goodObjs[sdss_names.sdss_color_err],
                                          colorterm = colorterm[0])
        

    fitresults = calibrationData.calibrate()

    if fitresults is None:
        sys.stderr.write('Error in Calibration of %s %s' % (cluster, filter))
        return

    allfits.append(fitresults)

    aperture_filter = filter

    print '%s %s: %s' % (cluster, aperture_filter, str(fitresults))

    if photometry_db:

        saveCalibration(cluster, filter=aperture_filter, fitResults = fitresults, photometry_db = photometry_db, specification = specification)

    if plotdir is not None:

        if not os.path.exists(plotdir):
            os.mkdir(plotdir)
        if freecolor:
            title = 'Calibration withh Free Color'
        else:
            title = 'Calibration with Fixed Pickles Color'
        print 'making residual'
        plotCalibrationResiduals(calibrationData, fitresults,
                                 title = 'Sloan - Sub vs. Sloan',
                                 color_label=sdss_names.sdss_color,
                                 residual_label='%s - %s - %3.2f - %3.3f*%s' % (sdss_names.sdss_mag,
                                                                        aperture_filter, 
                                                                        fitresults.zp,
                                                                        fitresults.colorterm,
                                                                        sdss_names.sdss_color))

        pylab.show()
        pylab.savefig('%s/%s.ps' % (plotdir, aperture_filter))
        pylab.clf()
        print 'making plot  '

        plotCalibrationPull(calibrationData, fitresults,
                                 title = title,
                                 color_label=sdss_names.sdss_color,
                                 residual_label='%s - %s - %3.2f - %3.3f*%s' % (sdss_names.sdss_mag,
                                                                        aperture_filter, 
                                                                        fitresults.zp,
                                                                        fitresults.colorterm,
                                                                        sdss_names.sdss_color))

        pylab.show()
        pylab.savefig('%s/%s_%s.ps' % (plotdir, aperture_filter,'pull'))
        pylab.clf()


        plotCalibrationMag(calibrationData, fitresults,
                                 title = title,
                                 color_label=sdss_names.sdss_mag,
                                 residual_label='%s - %s - %3.2f - %3.3f*%s' % (sdss_names.sdss_mag,
                                                                        aperture_filter, 
                                                                        fitresults.zp,
                                                                        fitresults.colorterm,
                                                                        sdss_names.sdss_color))

        pylab.show()
        pylab.savefig('%s/%s_%s.ps' % (plotdir, aperture_filter,'mag'))
        pylab.clf()


        makeCutPlots(cat, fitresults, sdss_names, mag_name, magerr_name, filterInfo['color1cut'],colorterm)
        pylab.savefig('%s/%s_%s.ps' % (plotdir, aperture_filter,'cuts'))
        pylab.clf()

        xcat=goodObjs['SEx_Xpos']
        ycat=goodObjs['SEx_Ypos']


        plotMagPosition(calibrationData, fitresults, xcat, ycat,
                        title = 'Sloan - Subaru vs. Sloan mag',
                        color_label=sdss_names.sdss_mag)
        pylab.savefig('%s/%s_%s.ps' % (plotdir, aperture_filter,'position'))
        pylab.clf()


    return allfits

        


##########################

def threeSecondCalibration(cluster, stdfilter, filterPrefix, cat, plotdir = None, freecolor=False, photometry_db = __default_photometry_db__, specification = {}, cuts = stdCalibrationCuts):
    
    filter='%s-%s' % (filterPrefix, stdfilter)
    filterInfo = filter_info[stdfilter]
    sdss_names = SDSSNames(filterInfo)
    
    mag_name = 'SEx_MAG_AUTO'
    magerr_name ='SEx_MAGERR_AUTO'

    goodObjs = cat.filter(cuts(cat, cat[mag_name], sdss_names, filterInfo['color1cut']))

    
    print 'goodobjs = ', len(goodObjs)

    if freecolor:

        calibrationData = CalibrationData(mag = goodObjs[mag_name] - __3sec_zp__,
                                          mag_err = goodObjs[magerr_name],
                                          refmag = goodObjs[sdss_names.sdss_mag],
                                          refmag_err = goodObjs[sdss_names.sdss_magerr],
                                          color = goodObjs[sdss_names.sdss_color],
                                          colorerr = goodObjs[sdss_names.sdss_color_err])

    else:

        if filter not in colorterms:
            sys.stderr.write('Unknown Filter, Skipping: %s\n' % filter)
            return

        colorterm = colorterms[filter]

        calibrationData = CalibrationData(mag = goodObjs[mag_name] - __3sec_zp__,
                                          mag_err = goodObjs[magerr_name],
                                          refmag = goodObjs[sdss_names.sdss_mag],
                                          refmag_err = goodObjs[sdss_names.sdss_magerr],
                                          color = goodObjs[sdss_names.sdss_color],
                                          colorerr = goodObjs[sdss_names.sdss_color_err],
                                          colorterm = colorterm[0])


    fitresults = calibrationData.calibrate()

    if fitresults is None:
        sys.stderr.write('Error in Calibration of %s %s' % cluster, filter)
        return

    aperture_filter = '%s_3sec' % filter

    print '%s %s: %s' % (cluster, aperture_filter, str(fitresults))

    if photometry_db:

        saveCalibration(cluster, filter=aperture_filter, fitResults =fitresults, photometry_db = photometry_db, specification = specification)

    if plotdir is not None:

        if not os.path.exists(plotdir):
            os.mkdir(plotdir)
        if freecolor:
            title = 'Calibration withh Free Color'
        else:
            title = 'Calibration with Fixed Pickles Color'
        plotCalibrationResiduals(calibrationData, fitresults,
                                 title = title,
                                 color_label=sdss_names.sdss_color,
                                 residual_label='%s - %s - %3.2f - %3.3f*%s' % (sdss_names.sdss_mag,
                                                                        aperture_filter, 
                                                                        fitresults.zp,
                                                                        fitresults.colorterm,
                                                                        sdss_names.sdss_color))

        pylab.show()
        pylab.savefig('%s/%s.ps' % (plotdir, aperture_filter))
        pylab.clf()

        
        plotCalibrationPull(calibrationData, fitresults,
                            title = title,
                            color_label=sdss_names.sdss_color,
                            residual_label='%s - %s - %3.2f - %3.3f*%s' % (sdss_names.sdss_mag,
                                                                           aperture_filter, 
                                                                           fitresults.zp,
                                                                           fitresults.colorterm,
                                                                           sdss_names.sdss_color))
        
        pylab.show()
        pylab.savefig('%s/%s_%s.ps' % (plotdir, aperture_filter,'pull'))
        pylab.clf()


        plotCalibrationMag(calibrationData, fitresults,
                           title = 'Sloan - Subaru vs. Sloan mag',
                           color_label=sdss_names.sdss_mag,
                           residual_label='%s - %s - %3.2f' % (sdss_names.sdss_mag,
                                                               aperture_filter, 
                                                               fitresults.zp))

        pylab.show()
        pylab.savefig('%s/%s_%s.ps' % (plotdir, aperture_filter,'mag'))
        pylab.clf()

        makeCutPlots(cat, fitresults, sdss_names, mag_name, magerr_name, filterInfo['color1cut'],colorterm )
        pylab.savefig('%s/%s_%s.ps' % (plotdir, aperture_filter,'cuts'))
        pylab.clf()



        xcat=goodObjs['SEx_Xpos']
        ycat=goodObjs['SEx_Ypos']
        

        plotMagPosition(calibrationData, fitresults, xcat, ycat,
                        title = 'Sloan - Subaru vs. Sloan mag',
                        color_label=sdss_names.sdss_mag)
        pylab.savefig('%s/%s_%s.ps' % (plotdir, aperture_filter,'position'))
        pylab.clf()

    return fitresults
        
##########################


def specialCalibration(maindir, cluster, filter, photometry_db = __default_photometry_db__, specification = {}):

    instrum, config, chipid, stdfilter = utilities.parseFilter(filter)

    imagefile = '%(maindir)s/%(cluster)s/%(filter)s/SCIENCE/coadd_%(cluster)s_all/coadd.fits' % { \
        'maindir' : maindir,
        'cluster' : cluster,
        'filter' : stdfilter}
    
    zp = pyfits.getval(imagefile, 'MAGZP')

    print zp
    
    if photometry_db:
        calib = photometry_db.registerSpecialFiltersCalibration(cluster = cluster, filter = filter, file=imagefile, zp=zp, **specification)

        photometry_db.updateCalibration(cluster, filter = filter, calibration = calib, **specification)

    

    return zp




###################################################
### MAIN
###################################################


def main(argv = sys.argv, 
         standardCalibration = standardCalibration, 
         threeSecondCalibration = threeSecondCalibration,
         specialCalibration = specialCalibration,
         photometry_db = __default_photometry_db__):

    ###
    
    def parse_spec(option, opt, value, parser):

        key, val = value.split('=')
        
        if not hasattr(parser.values, 'specification'):
            setattr(parser.values, 'specification', {})
            
        parser.values.specification[key] = val

       
    ###

    
    parser = optparse.OptionParser()
    parser.add_option('-c', '--cluster', dest='cluster', help='Cluster name')
    parser.add_option('-i', '--inputcat',
                      dest='catfile',
                      help='catalog for use in calibration')
    parser.add_option('-f', '--filtername',
                      dest='filter',
                      help='Filter to calibrate')
    parser.add_option('-p', '--plotdir',
                       dest='plotdir',
                       help='Directory to save plots')
    parser.add_option('-t', '--chipid',
                      dest='chipid',
                      help='Chip id used in measurement')
    parser.add_option('-3', '--threesec',
                      dest='threesec',
                      action='store_true',
                      help='Treat as a 3second exposure',
                      default=False)
    parser.add_option('-s', '--special',
                      dest='special',
                      action='store_true',
                      help='Treat as a special exposure',
                      default=False)
    parser.add_option('-m', '--maindir',
                      dest='maindir',
                      help='subaru directory')
    parser.add_option('--free-color',
                      dest='freecolor',
                      action='store_true',
                      help='Allow color term to be free!',
                      default=False)
    parser.add_option('--no-save',
                      dest='saveCalib',
                      action='store_false',
                      help='Do not save fits to database',
                      default = True)
    parser.add_option('--spec', dest='specification',
                      action='callback',
                      type= 'string', 
                      help='key=val set determines the uniqueness of this calibration',
                      default = {},
                      callback = parse_spec)
    parser.add_option('-n', '--fluxtype',
                      dest='fluxtype',
                      help='Type of flux/mag to calibrate, ie. FLUX_(XXXX)',
                      default=__default_fluxtype__)
                      

    options, args = parser.parse_args(argv)

    print "Called with:"
    print options

    if not options.special and options.catfile is None:
        parser.error('Need to specify catalog file!')
    if options.cluster is None:
        parser.error('Need to specify cluster!')
    if options.filter is None:
        parser.error('Need to specify filter')
    
    if options.threesec and options.special:
        parser.error('Cannot treat as 3sec and special')
        
    if options.threesec and not options.chipid:
        parser.error('Need a config type for this obs')

    if options.special and options.maindir is None:
        parser.error('Need to specify main directory')

    if not options.saveCalib:
        photometry_db = None


    if options.special:
        specialCalibration(options.maindir, 
                           options.cluster, options.filter, 
                           photometry_db = photometry_db, specification = options.specification)
    else:



        cat = ldac.openObjectFile(options.catfile, 'PSSC')



        if options.threesec:
            threeSecondCalibration(options.cluster, 
                                   options.filter, 
                                   options.chipid,
                                   cat,
                                   plotdir = options.plotdir,
                                   freecolor=options.freecolor,
                                   photometry_db = photometry_db,
                                   specification = options.specification)

        else:

            standardCalibration(options.cluster, options.filter, cat, 
                                fluxtype = options.fluxtype,
                                plotdir=options.plotdir,freecolor=options.freecolor,
                                photometry_db = photometry_db,
                                specification = options.specification,
                                cuts = basicCalCuts)






############
# Plotting
###########



def plotCalibrationResiduals(calibrationData, fitResults,
                             color_label = None, 
                             residual_label = None, 
                             title = None):

    color = calibrationData.color
    if fitResults.fixedcolor:
        residuals = calibrationData.vals() - fitResults.zp
    else:
        residuals = calibrationData.vals() - fitResults.colorterm*calibrationData.color - fitResults.zp
    errs = calibrationData.errs()

    pylab.errorbar(color, residuals, errs, fmt='b.')
    #pylab.axis([0,10000,-1.,1.])
    pylab.axhline(0, color='r')
    if color_label:
        pylab.xlabel(color_label)
    if residual_label:
        pylab.ylabel(residual_label)
    if title:
        pylab.title(title)


#######################

def plotCalibrationPull(calibrationData, fitResults,
                        color_label = None, 
                        residual_label = None, 
                        title = None):

    color = calibrationData.color
    if fitResults.fixedcolor:
        residuals = calibrationData.vals() - fitResults.zp
    else:
        residuals = calibrationData.vals() - fitResults.colorterm*calibrationData.color - fitResults.zp
    errs = calibrationData.errs()

    pulls = residuals / errs
    pylab.hist(pulls,bins=100,range=(-8,8))
    

    
#    pylab.errorbar(color, residuals, errs, fmt='b.')
#    pylab.axhline(0, color='r')
    if color_label:
        pylab.xlabel(residual_label)
    if title:
        pylab.title(title)
    print 'made pull plot'
    pylab.show()

########################

def plotCalibrationMag(calibrationData, fitResults,
                        color_label = None, 
                        residual_label = None, 
                        title = None):


    if fitResults.fixedcolor:
        residuals = calibrationData.vals() - fitResults.zp
    else:
        residuals = calibrationData.vals() - fitResults.colorterm*calibrationData.color - fitResults.zp
    errs = calibrationData.errs()


    smag = calibrationData.refmag

    # print sub_m_sln

    # print 'smag = '
    # print smag

    pylab.errorbar(smag, residuals, errs, fmt='b.')
    # pylab.axis([0,10000,-1.,1.])
    pylab.axhline(0, color='r')
    if color_label:
        pylab.xlabel(color_label)
    if residual_label:
        pylab.ylabel(residual_label)
    if title:
        pylab.title(title)

    print 'made mag plot'
    pylab.show()
########################    

def plotMagPosition(calibrationData, fitResults,xcat,ycat,
                    color_label = None, 
                    residual_label = None,
                    title = None):

    if fitResults.fixedcolor:
        residuals = calibrationData.vals() - fitResults.zp
    else:
        residuals = calibrationData.vals() - fitResults.colorterm*calibrationData.color - fitResults.zp
    errs = calibrationData.errs()


    pylab.subplot(2,1,1)
    pylab.errorbar(xcat, residuals, errs, fmt='b.')
    pylab.axis([0,10000,-0.4,0.4])
    pylab.axhline(0, color='r')
    if color_label:
        pylab.xlabel('x position')
    if residual_label:
        pylab.ylabel('')
    if title:
        pylab.title('')
    pylab.subplot(2,1,2)
    pylab.errorbar(ycat, residuals, errs, fmt='b.')
    pylab.axis([0,10000,-0.8,0.8])
    pylab.axhline(0, color='r')
    if color_label:
        pylab.xlabel('y position')
    if residual_label:
        pylab.ylabel(residual_label)
    if title:
        pylab.title('')

    



    print 'made mag plot'
    pylab.show()
    

    



########################
def makeCutPlots(cat, results, names, mag_name, magerr_name ,color_function , colorterm, iaper = -1):
    cuts=[]

    pylab.figure(1)
    cuts.append( (numpy.logical_not(color_function(cat[names.sdss_color])))) # color cut 

    peakvals = cat['SEx_BackGr'] + cat['SEx_MaxVal']
    cuts.append(numpy.logical_not(peakvals < 20000))    # Saturation Cut
    cuts.append(numpy.logical_not(cat['SEx_Flag']==0))  # Flag
    cuts.append(numpy.logical_not(cat['Clean'] == 1))  # Clean
    
    titles=[]
    titles.append('colorcut')
    titles.append('Saturation Cut')
    titles.append('Flag')
    titles.append('Clean')

    for i in range(len(cuts)):
        
        print 'iaper is', iaper
        if iaper>=0:
            theseobjs = cat.filter(numpy.logical_and(cuts[i],numpy.abs(cat[mag_name][:,iaper])<80))
            cutData = CalibrationData(mag = theseobjs[mag_name][:,iaper],
                                      mag_err = theseobjs[magerr_name][:,iaper],
                                      refmag = theseobjs[names.sdss_mag],
                                      refmag_err = theseobjs[names.sdss_magerr],
                                      color = theseobjs[names.sdss_color],
                                      colorerr = theseobjs[names.sdss_color_err],
                                      colorterm = colorterm[0])
        else:
            theseobjs = cat.filter(numpy.logical_and(cuts[i],numpy.abs(cat[mag_name])<80))
            cutData = CalibrationData(mag = theseobjs[mag_name]  - __3sec_zp__,
                                      mag_err = theseobjs[magerr_name],
                                      refmag = theseobjs[names.sdss_mag],
                                      refmag_err = theseobjs[names.sdss_magerr],
                                      color = theseobjs[names.sdss_color],
                                      colorerr = theseobjs[names.sdss_color_err],
                                      colorterm = colorterm[0])


        
            

       
        smag = cutData.refmag
        sub_m_sln = cutData.mag  - (cutData.refmag -results.zp )        
        errs = cutData.errs()
        # print titles[i]
        print 'smag = ',smag
        print 'sub_m_sln = ', sub_m_sln
        print 'err = ', errs      

        smag2=[]
        sub2=[]
        err2=[]

        for j in range(len(smag)):
            if smag[j]>0:
                smag2.append(smag[j])
                sub2.append(sub_m_sln[j])
                err2.append(errs[j])


        smag=smag2
        sub_m_sln=sub2
        errs = err2
                
        if len(smag):
            pylab.subplot(2,3,i+1)
            pylab.errorbar(smag, sub_m_sln, errs, fmt='b.')
            pylab.axhline(0, color='r')
            
            pylab.xlabel(names.sdss_mag,fontsize='small')
                
            pylab.ylabel(titles[i])
        


            
        pylab.show()
  


################################
### TESTING
################################

class TestingDBEntry(object):

    def __init__(self, id, **fields):
        self.id = id
        self.fields = fields

    def __getattr__(self, name):
        if name in self.fields:
            return self.fields[name]
        raise AttributeError

###

class TestingDatabase(object):

    def __init__(self):

        self.reset()

    def reset(self):
        self.photoentries = []
        self.calibrations = []
        self.specialentries = []

    def registerPhotometricCalibration(self, cluster, fitresults, **specification):
        self.photoentries.append(TestingDBEntry(len(self.photoentries), cluster = cluster, fitresults = fitresults, **specification))
        return self.photoentries[-1]

    def registerSpecialFiltersCalibration(self, cluster, file, zp, **specification):
        self.specialentries.append(TestingDBEntry(len(self.specialentries), cluster = cluster, file = file, zp = zp, **specification))
        return self.specialentries[-1]

    def updateCalibration(self, cluster, calibration, **specification):
        self.calibrations.append(TestingDBEntry(len(self.calibrations), cluster = cluster, calibration = calibration, **specification))
        
####################

class TestRegularCalib(unittest.TestCase):

    def setUp(self):

        self.db = TestingDatabase()

    
    ####

    def testStdZP(self):

        filterName = 'SUBARU-10_2-1-W-J-V'

        pickles = ldac.openObjectFile('Pickles.cat', 'PICKLES')
        pickles_sdss = ldac.openObjectFile('Pickles.cat', 'SDSS')
        sample = numpy.random.randint(0, len(pickles), 100)

        targetZP = 27.15
        
        seqnr = pyfits.Column(name = 'SeqNr', format = 'K', array = numpy.arange(100))
        mags = pyfits.Column(name = 'SEx_MAG_APER1-%s' % filterName, 
                             format = 'E', 
                             array = pickles[filterName][sample] + targetZP)
        magerrs = pyfits.Column(name = 'SEx_MAGERR_APER1-%s' % filterName, 
                                format = 'E', 
                                array = 0.05 * numpy.ones(100))
        
        sdss = pyfits.Column(name = 'gmag', format = 'E', array = pickles_sdss['gp'][sample])
        sdsserr = pyfits.Column(name = 'gerr', format = 'E', array = 0.1 * numpy.ones(100))
        sdsscolor = pyfits.Column(name = 'gmr', format = 'E', array = pickles_sdss['gp'][sample] - pickles_sdss['rp'][sample])
        sdsscolorerr = pyfits.Column(name = 'gmrerr', 
                                format = 'E', 
                                array = numpy.sqrt(2)*0.1*numpy.ones(100))
        

        clean = pyfits.Column(name = 'Clean', format = 'K', array = numpy.ones(100))
        backgr = pyfits.Column(name = 'SEx_BackGr', format = 'E', array = numpy.ones(100))
        maxval = pyfits.Column(name = 'SEx_MaxVal', format = 'E', array = numpy.ones(100))
        flag = pyfits.Column(name = 'SEx_Flag', format = 'K', array = numpy.zeros(100))

        cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([mags, magerrs, clean,
                                                            backgr, maxval, flag, 
                                                            sdss, sdsserr, sdsscolor, 
                                                            sdsscolorerr])))




        
        allfits = standardCalibration('TestCluster', filterName, cat, photometry_db = None, plotdir = None)

        self.assertEquals(len(allfits), 1)
        
        fitresult = allfits[0]
        
        self.assertTrue(fitresult.fixedcolor)

        self.assertTrue(numpy.abs(fitresult.zp + targetZP) < 0.25)
        
    ###

    def testStdDatabase(self):

        clustername = 'TestCluster'
        filtername = 'SUBARU-10_2-1-W-J-V'

        pickles = ldac.openObjectFile('Pickles.cat', 'PICKLES')
        pickles_sdss = ldac.openObjectFile('Pickles.cat', 'SDSS')
        sample = numpy.random.randint(0, len(pickles), 100)

        targetZP = 27.15
        
        seqnr = pyfits.Column(name = 'SeqNr', format = 'K', array = numpy.arange(100))
        mags = pyfits.Column(name = 'SEx_MAG_APER1-%s' % filtername, 
                             format = 'E', 
                             array = pickles[filtername][sample] + targetZP)
        magerrs = pyfits.Column(name = 'SEx_MAGERR_APER1-%s' % filtername, 
                                format = 'E', 
                                array = 0.05 * numpy.ones(100))
        
        sdss = pyfits.Column(name = 'gmag', format = 'E', array = pickles_sdss['gp'][sample])
        sdsserr = pyfits.Column(name = 'gerr', format = 'E', array = 0.1 * numpy.ones(100))
        sdsscolor = pyfits.Column(name = 'gmr', format = 'E', array = pickles_sdss['gp'][sample] - pickles_sdss['rp'][sample])
        sdsscolorerr = pyfits.Column(name = 'gmrerr', 
                                format = 'E', 
                                array = numpy.sqrt(2)*0.1*numpy.ones(100))
        

        clean = pyfits.Column(name = 'Clean', format = 'K', array = numpy.ones(100))
        backgr = pyfits.Column(name = 'SEx_BackGr', format = 'E', array = numpy.ones(100))
        maxval = pyfits.Column(name = 'SEx_MaxVal', format = 'E', array = numpy.ones(100))
        flag = pyfits.Column(name = 'SEx_Flag', format = 'K', array = numpy.zeros(100))

        cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([mags, magerrs, clean,
                                                            backgr, maxval, flag, 
                                                            sdss, sdsserr, sdsscolor, 
                                                            sdsscolorerr])))




        
        allfits = standardCalibration(clustername, filtername, cat, photometry_db = self.db, plotdir = None)

        
        self.assertEquals(len(self.db.photoentries), 1)
        
        photocalib = self.db.photoentries[0]
        self.assertEquals(sorted('cluster fitresults filter'.split()), sorted(photocalib.fields.keys()))
        self.assertEquals(photocalib.cluster, clustername)
        self.assertEquals(photocalib.filter, filtername)
        self.assertEquals(photocalib.fitresults, allfits[0])
        
        self.assertEquals(len(self.db.calibrations), 1)
        
        calib = self.db.calibrations[0]
        self.assertEquals(sorted('cluster calibration filter'.split()), sorted(calib.fields.keys()))
        self.assertEquals(calib.cluster, clustername)
        self.assertEquals(calib.calibration, photocalib)
        self.assertEquals(calib.filter, filtername)

    ####

    def testAltMagDatabase(self):

        clustername = 'TestCluster'
        filtername = 'SUBARU-10_2-1-W-J-V'

        pickles = ldac.openObjectFile('Pickles.cat', 'PICKLES')
        pickles_sdss = ldac.openObjectFile('Pickles.cat', 'SDSS')
        sample = numpy.random.randint(0, len(pickles), 100)

        targetZP = 27.15
        
        seqnr = pyfits.Column(name = 'SeqNr', format = 'K', array = numpy.arange(100))
        mags = pyfits.Column(name = 'SEx_MAG_ISO-%s' % filtername, 
                             format = 'E', 
                             array = pickles[filtername][sample] + targetZP)
        magerrs = pyfits.Column(name = 'SEx_MAGERR_ISO-%s' % filtername, 
                                format = 'E', 
                                array = 0.05 * numpy.ones(100))
        
        sdss = pyfits.Column(name = 'gmag', format = 'E', array = pickles_sdss['gp'][sample])
        sdsserr = pyfits.Column(name = 'gerr', format = 'E', array = 0.1 * numpy.ones(100))
        sdsscolor = pyfits.Column(name = 'gmr', format = 'E', array = pickles_sdss['gp'][sample] - pickles_sdss['rp'][sample])
        sdsscolorerr = pyfits.Column(name = 'gmrerr', 
                                format = 'E', 
                                array = numpy.sqrt(2)*0.1*numpy.ones(100))
        

        clean = pyfits.Column(name = 'Clean', format = 'K', array = numpy.ones(100))
        backgr = pyfits.Column(name = 'SEx_BackGr', format = 'E', array = numpy.ones(100))
        maxval = pyfits.Column(name = 'SEx_MaxVal', format = 'E', array = numpy.ones(100))
        flag = pyfits.Column(name = 'SEx_Flag', format = 'K', array = numpy.zeros(100))

        cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([mags, magerrs, clean,
                                                            backgr, maxval, flag, 
                                                            sdss, sdsserr, sdsscolor, 
                                                            sdsscolorerr])))


        
        allfits = standardCalibration(clustername, filtername, cat, fluxtype = 'ISO', photometry_db = self.db, plotdir = None)

        
        self.assertEquals(len(self.db.photoentries), 1)
        
        photocalib = self.db.photoentries[0]
        self.assertEquals(sorted('cluster fitresults filter'.split()), sorted(photocalib.fields.keys()))
        self.assertEquals(photocalib.cluster, clustername)
        self.assertEquals(photocalib.filter, filtername)
        self.assertEquals(photocalib.fitresults, allfits[0])
        
        self.assertEquals(len(self.db.calibrations), 1)
        
        calib = self.db.calibrations[0]
        self.assertEquals(sorted('cluster calibration filter'.split()), sorted(calib.fields.keys()))
        self.assertEquals(calib.cluster, clustername)
        self.assertEquals(calib.calibration, photocalib)
        self.assertEquals(calib.filter, filtername)

    #####

    def testOtherSpecificationsDatabase(self):

        clustername = 'TestCluster'
        filtername = 'SUBARU-10_2-1-W-J-V'

        pickles = ldac.openObjectFile('Pickles.cat', 'PICKLES')
        pickles_sdss = ldac.openObjectFile('Pickles.cat', 'SDSS')
        sample = numpy.random.randint(0, len(pickles), 100)

        targetZP = 27.15
        
        seqnr = pyfits.Column(name = 'SeqNr', format = 'K', array = numpy.arange(100))
        mags = pyfits.Column(name = 'SEx_MAG_APER1-%s' % filtername, 
                             format = 'E', 
                             array = pickles[filtername][sample] + targetZP)
        magerrs = pyfits.Column(name = 'SEx_MAGERR_APER1-%s' % filtername, 
                                format = 'E', 
                                array = 0.05 * numpy.ones(100))
        
        sdss = pyfits.Column(name = 'gmag', format = 'E', array = pickles_sdss['gp'][sample])
        sdsserr = pyfits.Column(name = 'gerr', format = 'E', array = 0.1 * numpy.ones(100))
        sdsscolor = pyfits.Column(name = 'gmr', format = 'E', array = pickles_sdss['gp'][sample] - pickles_sdss['rp'][sample])
        sdsscolorerr = pyfits.Column(name = 'gmrerr', 
                                format = 'E', 
                                array = numpy.sqrt(2)*0.1*numpy.ones(100))
        

        clean = pyfits.Column(name = 'Clean', format = 'K', array = numpy.ones(100))
        backgr = pyfits.Column(name = 'SEx_BackGr', format = 'E', array = numpy.ones(100))
        maxval = pyfits.Column(name = 'SEx_MaxVal', format = 'E', array = numpy.ones(100))
        flag = pyfits.Column(name = 'SEx_Flag', format = 'K', array = numpy.zeros(100))

        cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([mags, magerrs, clean,
                                                            backgr, maxval, flag, 
                                                            sdss, sdsserr, sdsscolor, 
                                                            sdsscolorerr])))




        
        allfits = standardCalibration(clustername, filtername, cat, photometry_db = self.db, plotdir = None, 
                                      specification = {'myspec' :'custom'})

        
        self.assertEquals(len(self.db.photoentries), 1)
        
        photocalib = self.db.photoentries[0]
        self.assertEquals(sorted('cluster fitresults filter myspec'.split()), sorted(photocalib.fields.keys()))
        self.assertEquals(photocalib.cluster, clustername)
        self.assertEquals(photocalib.filter, filtername)
        self.assertEquals(photocalib.fitresults, allfits[0])
        self.assertEquals(photocalib.myspec, 'custom')
        
        
        self.assertEquals(len(self.db.calibrations), 1)
        
        calib = self.db.calibrations[0]
        self.assertEquals(sorted('cluster calibration filter myspec'.split()), sorted(calib.fields.keys()))
        self.assertEquals(calib.cluster, clustername)
        self.assertEquals(calib.calibration, photocalib)
        self.assertEquals(calib.filter, filtername)
        self.assertEquals(calib.myspec, 'custom')




    #####

    def testThreeSec(self):

        clustername = 'TestCluster'
        filtername = 'SUBARU-10_2-1-W-J-V'

        pickles = ldac.openObjectFile('Pickles.cat', 'PICKLES')
        pickles_sdss = ldac.openObjectFile('Pickles.cat', 'SDSS')
        sample = numpy.random.randint(0, len(pickles), 100)

        targetZP = 27.15
        
        seqnr = pyfits.Column(name = 'SeqNr', format = 'K', array = numpy.arange(100))
        mags = pyfits.Column(name = 'SEx_MAG_AUTO', 
                             format = 'E', 
                             array = pickles[filtername][sample] + targetZP)
        magerrs = pyfits.Column(name = 'SEx_MAGERR_AUTO', 
                                format = 'E', 
                                array = 0.05 * numpy.ones(100))
        
        sdss = pyfits.Column(name = 'gmag', format = 'E', array = pickles_sdss['gp'][sample])
        sdsserr = pyfits.Column(name = 'gerr', format = 'E', array = 0.1 * numpy.ones(100))
        sdsscolor = pyfits.Column(name = 'gmr', format = 'E', array = pickles_sdss['gp'][sample] - pickles_sdss['rp'][sample])
        sdsscolorerr = pyfits.Column(name = 'gmrerr', 
                                format = 'E', 
                                array = numpy.sqrt(2)*0.1*numpy.ones(100))
        

        clean = pyfits.Column(name = 'Clean', format = 'K', array = numpy.ones(100))
        backgr = pyfits.Column(name = 'SEx_BackGr', format = 'E', array = numpy.ones(100))
        maxval = pyfits.Column(name = 'SEx_MaxVal', format = 'E', array = numpy.ones(100))
        flag = pyfits.Column(name = 'SEx_Flag', format = 'K', array = numpy.zeros(100))

        cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([mags, magerrs, clean,
                                                            backgr, maxval, flag, 
                                                            sdss, sdsserr, sdsscolor, 
                                                            sdsscolorerr])))



        print self.db
        fit = threeSecondCalibration(clustername, 'W-J-V', 'SUBARU-10_2-1', cat, photometry_db = self.db, plotdir = None)

        
        self.assertEquals(len(self.db.photoentries), 1)
        
        photocalib = self.db.photoentries[0]
        self.assertEquals(sorted('cluster fitresults filter'.split()), sorted(photocalib.fields.keys()))
        self.assertEquals(photocalib.cluster, clustername)
        self.assertEquals(photocalib.filter, '%s_3sec' % filtername)
        self.assertEquals(photocalib.fitresults, fit)
        
        self.assertEquals(len(self.db.calibrations), 1)
        
        calib = self.db.calibrations[0]
        self.assertEquals(sorted('cluster calibration filter'.split()), sorted(calib.fields.keys()))
        self.assertEquals(calib.cluster, clustername)
        self.assertEquals(calib.calibration, photocalib)
        self.assertEquals(calib.filter, '%s_3sec' % filtername)


    #####

    def testThreeSec(self):

        clustername = 'TestCluster'
        filtername = 'SUBARU-10_2-1-W-J-V'

        pickles = ldac.openObjectFile('Pickles.cat', 'PICKLES')
        pickles_sdss = ldac.openObjectFile('Pickles.cat', 'SDSS')
        sample = numpy.random.randint(0, len(pickles), 100)

        targetZP = 27.15
        
        seqnr = pyfits.Column(name = 'SeqNr', format = 'K', array = numpy.arange(100))
        mags = pyfits.Column(name = 'SEx_MAG_AUTO', 
                             format = 'E', 
                             array = pickles[filtername][sample] + targetZP)
        magerrs = pyfits.Column(name = 'SEx_MAGERR_AUTO', 
                                format = 'E', 
                                array = 0.05 * numpy.ones(100))
        
        sdss = pyfits.Column(name = 'gmag', format = 'E', array = pickles_sdss['gp'][sample])
        sdsserr = pyfits.Column(name = 'gerr', format = 'E', array = 0.1 * numpy.ones(100))
        sdsscolor = pyfits.Column(name = 'gmr', format = 'E', array = pickles_sdss['gp'][sample] - pickles_sdss['rp'][sample])
        sdsscolorerr = pyfits.Column(name = 'gmrerr', 
                                format = 'E', 
                                array = numpy.sqrt(2)*0.1*numpy.ones(100))
        

        clean = pyfits.Column(name = 'Clean', format = 'K', array = numpy.ones(100))
        backgr = pyfits.Column(name = 'SEx_BackGr', format = 'E', array = numpy.ones(100))
        maxval = pyfits.Column(name = 'SEx_MaxVal', format = 'E', array = numpy.ones(100))
        flag = pyfits.Column(name = 'SEx_Flag', format = 'K', array = numpy.zeros(100))

        cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([mags, magerrs, clean,
                                                            backgr, maxval, flag, 
                                                            sdss, sdsserr, sdsscolor, 
                                                            sdsscolorerr])))



        print self.db
        fit = threeSecondCalibration(clustername, 'W-J-V', 'SUBARU-10_2-1', cat, photometry_db = self.db, plotdir = None, 
                                     specification = {'myspec2' : 'custom'})

        
        self.assertEquals(len(self.db.photoentries), 1)
        
        photocalib = self.db.photoentries[0]
        self.assertEquals(sorted('cluster fitresults filter myspec2'.split()), sorted(photocalib.fields.keys()))
        self.assertEquals(photocalib.cluster, clustername)
        self.assertEquals(photocalib.filter, '%s_3sec' % filtername)
        self.assertEquals(photocalib.fitresults, fit)
        self.assertEquals(photocalib.myspec2, 'custom')
        
        self.assertEquals(len(self.db.calibrations), 1)
        
        calib = self.db.calibrations[0]
        self.assertEquals(sorted('cluster calibration filter myspec2'.split()), sorted(calib.fields.keys()))
        self.assertEquals(calib.cluster, clustername)
        self.assertEquals(calib.calibration, photocalib)
        self.assertEquals(calib.filter, '%s_3sec' % filtername)
        self.assertEquals(calib.myspec2, 'custom')



    ##############


class TestSpecialCalib(unittest.TestCase):

    def setUp(self):

        self.db = TestingDatabase()

        self.maindir = '/tmp'
        self.cluster = 'testcluster'
        self.stdfilter = 'K'
        self.filter = 'SPECIAL-0-1-%s' % self.stdfilter
        self.zp = 27.11

        self.imagedir = '%(maindir)s/%(cluster)s/%(filter)s/SCIENCE/coadd_%(cluster)s_all' % {'maindir' : self.maindir,
                                                                                              'cluster' : self.cluster,
                                                                                              'filter' : self.stdfilter}
        self.imagefile = '%s/coadd.fits' % self.imagedir
        
        if not os.path.exists(self.imagedir):
            os.makedirs(self.imagedir)

        if not os.path.exists(self.imagefile):
            hdu = pyfits.PrimaryHDU(numpy.ones((100,100)))
            hdu.header['MAGZP']= self.zp
            hdu.writeto(self.imagefile, overwrite=True)

    #####

    def tearDown(self):

        if os.path.exists(self.imagefile):
            os.remove(self.imagefile)
            
        if os.path.exists(self.imagedir):
            os.removedirs(self.imagedir)

    ######

    def testSpecialCalib(self):

        
        zp = specialCalibration(self.maindir, self.cluster, self.filter, photometry_db = self.db)

        self.assertEquals(zp, self.zp)

        self.assertEquals(len(self.db.photoentries), 0)

        self.assertEquals(len(self.db.specialentries), 1)
        
        specialcalib = self.db.specialentries[0]
        self.assertEquals(sorted('cluster filter file zp'.split()), sorted(specialcalib.fields.keys()))
        self.assertEquals(specialcalib.cluster, self.cluster)
        self.assertEquals(specialcalib.filter, self.filter)
        self.assertEquals(specialcalib.zp, self.zp)
        self.assertEquals(specialcalib.file, self.imagefile)
        
        self.assertEquals(len(self.db.calibrations), 1)
        
        calib = self.db.calibrations[0]
        self.assertEquals(sorted('cluster calibration filter'.split()), sorted(calib.fields.keys()))
        self.assertEquals(calib.cluster, self.cluster)
        self.assertEquals(calib.calibration, specialcalib)
        self.assertEquals(calib.filter, self.filter)


###############

class FunctionTrapper(object):

    def __init__(self):

        self.calls = []

    def __call__(self, *args, **kw):
        self.calls.append((args, kw))

####

class TestMain(unittest.TestCase):

    def setUp(self):

        self.db = TestingDatabase()

        self.catfile = 'fitphot.testcat.cat'
        
        if not os.path.exists(self.catfile):
            hdu = pyfits.BinTableHDU.from_columns(pyfits.ColDefs([pyfits.Column(name = 'SeqNr', format='K', array = numpy.arange(100))]))
            hdu.header['EXTNAME']= 'PSSC'
            hdu.writeto(self.catfile)
            self.cat = ldac.LDACCat(hdu)

        else:
            raise IOError

    ###

    def tearDown(self):

        if os.path.exists(self.catfile):
            os.remove(self.catfile)

    ###

    def testStdCalib(self):

        stdCal = FunctionTrapper()

        commandline = ('./fit_phot.py -c testcluster -i %s -f SUBARU-10_2-1-W-J-V --fluxtype ISO --spec fluxtype=iso --spec myspec=custom' % self.catfile).split()

        main(argv = commandline, 
             standardCalibration = stdCal, 
             threeSecondCalibration = None, 
             specialCalibration = None, 
             photometry_db = self.db)

        self.assertEquals(len(stdCal.calls), 1)

        args, kw = stdCal.calls[0]

        expectedArgs, varargname, varkwname, defaults = inspect.getargspec(standardCalibration)

        compiledArgs = {}
        for key, val in zip(reversed(expectedArgs), reversed(defaults)):
            compiledArgs[key] = val

        for key, val in zip(expectedArgs, args):
            compiledArgs[key] = val

        compiledArgs.update(kw)

        

        self.assertEquals(compiledArgs['cluster'], 'testcluster')
        self.assertEquals(compiledArgs['filter'], 'SUBARU-10_2-1-W-J-V')
        self.assertEquals(compiledArgs['fluxtype'],  'ISO')
        self.assertEquals(compiledArgs['plotdir'],  None)
        self.assertEquals(compiledArgs['freecolor'], False)
        self.assertEquals(compiledArgs['photometry_db'], self.db)
        self.assertEquals(compiledArgs['specification'], {'myspec' : 'custom', 'fluxtype' : 'iso'})

    
    #############

    def test3Sec(self):

        threeSecCal = FunctionTrapper()

        commandline = ('./fit_phot.py -c testcluster -i %s -t SUBARU-10_2-1 -f W-J-V --spec fluxtype=iso --spec myspec=custom -3' % self.catfile).split()

        main(argv = commandline, 
             standardCalibration = None, 
             threeSecondCalibration = threeSecCal,  
             specialCalibration = None, 
             photometry_db = self.db)

        self.assertEquals(len(threeSecCal.calls), 1)

        args, kw = threeSecCal.calls[0]

        expectedArgs, varargname, varkwname, defaults = inspect.getargspec(threeSecondCalibration)

        compiledArgs = {}
        for key, val in zip(reversed(expectedArgs), reversed(defaults)):
            compiledArgs[key] = val

        for key, val in zip(expectedArgs, args):
            compiledArgs[key] = val

        compiledArgs.update(kw)

        

        self.assertEquals(compiledArgs['cluster'], 'testcluster')
        self.assertEquals(compiledArgs['stdfilter'], 'W-J-V')
        self.assertEquals(compiledArgs['filterPrefix'], 'SUBARU-10_2-1')
        self.assertEquals(compiledArgs['plotdir'],  None)
        self.assertEquals(compiledArgs['freecolor'], False)
        self.assertEquals(compiledArgs['photometry_db'], self.db)
        self.assertEquals(compiledArgs['specification'], {'fluxtype':'iso', 'myspec':'custom'})
        

    #############

    def testSpecial(self):

        specialCal = FunctionTrapper()

        commandline = './fit_phot.py -c testcluster -m ./ -f K --spec fluxtype=ISO --spec myspec=custom -s'.split()

        main(argv = commandline, 
             standardCalibration = None, 
             threeSecondCalibration = None,  
             specialCalibration = specialCal, 
             photometry_db = self.db)

        self.assertEquals(len(specialCal.calls), 1)

        args, kw = specialCal.calls[0]

        expectedArgs, varargname, varkwname, defaults = inspect.getargspec(specialCalibration)

        compiledArgs = {}
        for key, val in zip(reversed(expectedArgs), reversed(defaults)):
            compiledArgs[key] = val

        for key, val in zip(expectedArgs, args):
            compiledArgs[key] = val

        compiledArgs.update(kw)



        self.assertEquals(compiledArgs['maindir'], './')
        self.assertEquals(compiledArgs['cluster'], 'testcluster')
        self.assertEquals(compiledArgs['filter'], 'K')
        self.assertEquals(compiledArgs['photometry_db'], self.db)
        self.assertEquals(compiledArgs['specification'], {'myspec':'custom', 'fluxtype':'ISO'})
        
        
        
        





#####################

def test():

    testcases = [TestRegularCalib, TestSpecialCalib, TestMain]
    
    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)


                      
                       
################################
### COMMAND LINE EXECUTABLE
################################

if __name__ == '__main__':

    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        test()
    else:
        main()

    
