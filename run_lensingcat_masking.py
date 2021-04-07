#!/usr/bin/env python
#adam-example# ipython -i -- ./run_lensingcat_masking.py ${cluster} ${filter} ${filter} aper ${lens}
#     cluster = argv[0]
#    detect_filter = argv[1]
#    lensing_filter = argv[2]
#    mode = argv[3]
#    image = argv[4]
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
    if len(argv) > 6:
        forceRemake = True

    ################

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

    fileExists(lensing_weight)
    fileExists(lensing_flag)

    edgemask = '%(clusterdir)s/masks/%(lensing_base)s_%(lensing_filter)s_%(image)s.edgemask.fits' % locals()
    edgemaskreg = '%(clusterdir)s/masks/%(lensing_base)s_%(lensing_filter)s_%(image)s.edgemask.reg' % locals()
    
    if forceRemake or not os.path.exists(edgemask):
        if os.path.exists(edgemaskreg):
            make_edgemask.makeEdgemask(lensing_flag, edgemask, edgemaskreg)
        else:
            make_edgemask.makeEdgemask(lensing_flag, edgemask)

    fileExists(edgemask)

    polygons = '%(clusterdir)s/masks/%(lensing_base)s_%(lensing_filter)s_%(image)s.mask.reg' % locals()
    fileExists(polygons)
    if unconverted(polygons):
        convertedPolygons = '%(clusterdir)s/masks/%(lensing_base)s_%(lensing_filter)s_%(image)s.conv.mask.reg' % locals()
        convertRegion2Poly.doFile(polygons, convertedPolygons)
        polygons = convertedPolygons
    fileExists(polygons)

    exposures = collectExposures(lensing_dir)
    exposure_flags = [ '%(clusterdir)s/%(lensing_filter)s/SCIENCE/coadd_%(cluster)s_%(exposure)s/coadd.flag.fits' % locals() for exposure in exposures ]
    print exposure_flags

    ringmask = '%(clusterdir)s/masks/%(lensing_base)s_%(lensing_filter)s_%(image)s.rings.fits' % locals()
    if forceRemake or not os.path.exists(ringmask) or olderthan(ringmask, exposure_flags):
        compile_masking.combineRings(exposure_flags, ringmask)


    compiledFlag = '%(clusterdir)s/masks/%(lensing_base)s_%(lensing_filter)s_%(image)s.flag.fits' % locals()

    if forceRemake or not os.path.exists(compiledFlag) or olderthan(compiledFlag, [lensing_weight, lensing_flag, edgemask, polygons, ringmask]):

        compile_masking.compileMasking(weightfile        =  lensing_weight,
                                       flagfile          =  lensing_flag  ,
                                       edgemaskfile      =  edgemask      ,
                                       polygonfile       =  polygons      ,
                                       ringfile          =  ringmask      ,
                                       outputflagfile    =  compiledFlag)

    flag_catalog = '%(clusterdir)s/LENSING_%(detect_filter)s_%(lensing_filter)s_%(mode)s/%(image)s/flagandweightvals.cat' % locals()


    if forceRemake or not os.path.exists(flag_catalog) or olderthan(flag_catalog, [detect_image, detect_weight, lensing_image, lensing_weight, compiledFlag]):


        extract_object_cats.sextractor(detect = detect_image, image = lensing_weight, config = extract_object_cats.DETECT_OBJS_CONFIG,
                                       catalog_name = '%s0' % flag_catalog,
                                       gain = '1.0',
                                       weight_type = ['MAP_WEIGHT', 'NONE'],
                                       weight_image = [detect_weight, 'NONE'],
                                       flag_image = compiledFlag,
                                       back_type = ['AUTO','MANUAL'],
                                       back_value = ['0.0', '0.0'],
                                       backphoto_type = 'GLOBAL')
					#why make this useless checkimage?
                                       #checkimage_type = 'BACKGROUND',
                                       #checkimage_name = 'background.fits',

        extract_object_cats.ldacconv('%s0' % flag_catalog, flag_catalog)
                                       


if __name__ == '__main__':
    #adam: clean the args first
    from adam_quicktools_ArgCleaner import ArgCleaner
    argv=ArgCleaner(args=sys.argv)
    main(argv=argv)
