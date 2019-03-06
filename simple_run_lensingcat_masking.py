#!/usr/bin/env python
#adam-does# this is like run_lensingcat_masking.py, but instead of compiling all the different masks, it just uses coadd.flag.fits, which I've now got working properly

########################
#
# Process a cluster, remaking the lensing catalog with proper IMAFLAGS_ISO values
#
########################

from __future__ import with_statement
import sys, os, re, glob
import astropy, astropy.io.fits as pyfits
import make_edgemask, convertRegion2Poly, extract_object_cats, compile_masking

########################

__cvs_id__ = "$Id: run_lensingcat_masking.py,v 1.2 2010-12-14 18:58:24 dapple Exp $"

########################


class MissingFileException(Exception): pass
def fileExists(file):
    if not os.path.exists(file):
        raise MissingFileException(file)

####

polygon_regex = re.compile('^polygon')
def unconverted(file):
    with open(file) as input:
        for line in input.readlines():
            if polygon_regex.match(line):
                return True
    return False

###

exposure_regex = re.compile('^(\w+?)_')
def collectExposures(dir):
    images = glob.glob('%s/*.sub.fits' % dir)
    exposures = []
    for image in images:
        dir, base = os.path.split(image)
        match = exposure_regex.match(base)
        if match is not None:
            exposure = match.group(1)
            if exposure not in exposures:
                exposures.append(exposure)

    return exposures

###

def olderthan(inQuestion, comparisons):

    questionDate = os.path.getmtime(inQuestion)
    for comparison in comparisons:
        compDate = os.path.getmtime(comparison)
        if compDate < questionDate:
            return True
    return False

######

def main(argv = sys.argv):

    cluster = argv[0]
    detect_filter = argv[1]
    lensing_filter = argv[2]
    mode = argv[3]
    image = argv[4]
    print ' cluster=',cluster , ' detect_filter=',detect_filter , ' lensing_filter=',lensing_filter , ' mode=',mode , ' image=',image

    forceRemake = False
    #adam-old# if len(argv) > 6:
    if argv[-1]=='remake':
        forceRemake = True

    ################
    print ' forceRemake=',forceRemake

    data_root=os.environ['SUBARUDIR']
    clusterdir = data_root+'/%s' % cluster

    detect_image = '%(clusterdir)s/%(detect_filter)s/SCIENCE/coadd_%(cluster)s_all/coadd.fits' % locals()
    lensing_image = '%(clusterdir)s/%(lensing_filter)s/SCIENCE/coadd_%(cluster)s_%(image)s/coadd.fits' % locals()
   
    if not os.path.exists(lensing_image):
        lensing_image = '%(clusterdir)s/%(lensing_filter)s/SCIENCE/coadd_%(cluster)s_all/coadd.fits' % locals()


    if mode == 'iso':

        detect_image = '%(clusterdir)s/%(detect_filter)s/SCIENCE/coadd_%(cluster)s_all/detection.filtered.fits' % locals()


    fileExists(detect_image)
    fileExists(lensing_image)

    detect_dir, detect_file = os.path.split(detect_image)
    detect_base, detect_ext = os.path.splitext(detect_file)
    detect_weight = '%(detect_dir)s/%(detect_base)s.weight%(detect_ext)s' % locals()

    fileExists(detect_weight)

    lensing_dir, lensing_file = os.path.split(lensing_image)
    lensing_base, lensing_ext = os.path.splitext(lensing_file)
    lensing_weight='%(lensing_dir)s/%(lensing_base)s.weight%(lensing_ext)s' % locals()
    lensing_flag='%(lensing_dir)s/%(lensing_base)s.flag.fits' % locals()
    print ' lensing_flag=',lensing_flag

    fileExists(lensing_weight)
    fileExists(lensing_flag)

    #adam: deleting edgemask and polygons/reg masks

    compiledFlag = '%(clusterdir)s/masks/%(lensing_base)s_%(lensing_filter)s_%(image)s.flag.fits' % locals()

    if forceRemake or not os.path.exists(compiledFlag):

        print 'cp %(lensing_flag)s %(compiledFlag)s' % locals()
        ooo=os.system('cp %(lensing_flag)s %(compiledFlag)s' % locals()) 
	if ooo!=0: raise Exception('THIS COMMAND FAILED WITH os.system: cp %(lensing_flag)s %(compiledFlag)s' % locals())

    flag_catalog = '%(clusterdir)s/LENSING_%(detect_filter)s_%(lensing_filter)s_%(mode)s/%(image)s/flagandweightvals.cat' % locals()


    if forceRemake or not os.path.exists(flag_catalog) or olderthan(flag_catalog, [detect_image, detect_weight, lensing_image, lensing_weight, compiledFlag]):


        extract_object_cats.sextractor(detect = detect_image, image = lensing_weight, config = extract_object_cats.DETECT_OBJS_CONFIG,
                                       catalog_name = '%s0' % flag_catalog,
                                       gain = '1.0',
                                       weight_type = ['MAP_WEIGHT', 'NONE'],
                                       weight_image = [detect_weight, 'NONE'],
                                       flag_image = compiledFlag,
                                       checkimage_type = 'BACKGROUND',
                                       checkimage_name = 'background.fits',
                                       back_type = ['AUTO','MANUAL'],
                                       back_value = ['0.0', '0.0'],
                                       backphoto_type = 'GLOBAL')

        extract_object_cats.ldacconv('%s0' % flag_catalog, flag_catalog)
                                       


if __name__ == '__main__':
    #adam: clean the args first
    from adam_quicktools_ArgCleaner import ArgCleaner
    argv=ArgCleaner(args=sys.argv)
    main(argv=argv)
