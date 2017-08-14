#!/usr/bin/env python
import os, sys, bashreader, commands
from utilities import *
from config_bonn import appendix, cluster, tag, arc, filters, filter_root, appendix_root

dict = bashreader.parseFile('progs.ini')
for key in dict.keys():
    os.environ[key] = str(dict[key])


TEMPDIR = '/tmp/'
PHOTCONF = './photconf/'
path='/nfs/slac/g/ki/ki05/anja/SUBARU/%s/' % cluster
#type='each'
type='all'

filecommand = open('record.analysis','w')

BASE="coadd"
image = BASE + '.fits'

print 'Finished Loading Config, utils'

if type == 'all' or type == 'each':
    children = []
    for filter in filters:
        child = os.fork()
        if child:
            children.append(child)
        else:
            params = {'path':path, 
                      'filter_root': filter_root, 
                      'cluster':cluster, 
                      'filter':filter,
                      'appendix':appendix, 
                      'PHOTCONF':PHOTCONF, 
                      'TEMPDIR': TEMPDIR}
            print params
            # now run sextractor to determine the seeing:              
            command = 'sex %(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits -c %(PHOTCONF)s/singleastrom.conf.sex \
                        -FLAG_IMAGE /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits \
                        -FLAG_TYPE MAX\
                        -CATALOG_NAME %(TEMPDIR)s/seeing_%(filter)s.cat \
                        -FILTER_NAME %(PHOTCONF)s/default.conv\
                        -CATALOG_TYPE "ASCII" \
                        -DETECT_MINAREA 10 -DETECT_THRESH 10.\
                        -ANALYSIS_THRESH 5 \
                        -PARAMETERS_NAME %(PHOTCONF)s/singleastrom.ascii.param.sex' %  params 
            print command
            os.system(command)
            sys.exit(0)
    for child in children: 
        os.waitpid(child,0)
    
    print 'DONE W/ SEEING'
    
fwhms = {} 
for filter in filters:
    file_header = '/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits' % {'TEMPDIR': TEMPDIR, 'filter':filter, 'path': path, 'cluster': cluster, 'appendix':appendix}
    GAIN, PIXSCALE, EXPTIME = get_header_info(file_header) 
    print GAIN, PIXSCALE

    fwhms[filter] = {'FILTER':filter,'GAIN':GAIN,'PIXSCALE':PIXSCALE, 'EXPTIME': EXPTIME}

    if type == 'all' or type == 'each':
        file_seeing = '%(TEMPDIR)s/seeing_%(filter)s.cat' % {'TEMPDIR': TEMPDIR, 'filter':filter}
        NLINES=50
        print 'filter', filter
        fwhms[filter]['SEEING'] = calc_seeing(file_seeing,PIXSCALE)


if type == 'all' or type == 'each':
    fwhms_comp=[fwhms[x] for x in fwhms.keys()] 
    fwhms_comp.sort(compare) 
    seeing_worst = fwhms_comp[0]['SEEING']
    filter_worst = fwhms_comp[0]['FILTER']
    print fwhms
    print 'SEEING', filter_worst, seeing_worst
    for x in fwhms.keys():
        print x, fwhms[x]

    
    import commands

    for filter in filters: 
        print filter

        params = {'seeing_orig':float(fwhms[filter]['SEEING']), 'seeing_new':float(seeing_worst),'PIXSCALE':float(PIXSCALE), 'path':path, 'cluster': cluster, 'appendix': appendix, 'filter':filter, 'path':path, 'DATACONF': os.environ['DATACONF']}

        command = 'mkdir %(DATACONF)s/default.conv %(path)s/%(filter)s/PHOTOMETRY/' % params 
        os.system(command)
        if filter != filter_worst:
            print params
            command = 'python create_gausssmoothing_kernel.py %(seeing_orig).3f %(seeing_new).3f %(PIXSCALE).3f %(path)s/%(filter)s/PHOTOMETRY/' % params 
            print command
            os.system(command)
        else:
            command = 'cp %(DATACONF)s/default.conv %(path)s/%(filter)s/PHOTOMETRY/gauss.conv' % params 
            os.system(command)
    

      

children = [] 
for filter in filters: 
    os.system("mkdir /" + path + "/" + filter + "/PHOTOMETRY/")
    os.system("rm /" + path + "/" + filter + "/PHOTOMETRY/" + BASE + ".all" + tag + ".cat")

    child = os.fork()
    if child:
        children.append(child)
    else:

        command = "rm /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.all.cat" % {'path':path, 'filter':filter}
        print command 
        os.system(command)

        if type == 'all':

            params = {'path':path, 
                      'filter_root': filter_root, 
                      'appendix_root':appendix_root,
                      'cluster':cluster, 
                      'filter':filter, 
                      'appendix':appendix, 
                      'PHOTCONF':PHOTCONF, 
                      'fwhm': seeing_worst, 
                      'BASE':BASE, 
                      'GAIN':float(fwhms[filter]['GAIN']),
                      'DATACONF':os.environ['DATACONF'], 
                      'tag':tag}

            if filter != filter_worst:
                ''' convolve image -- no background subtraction -- high detection threshold -- no dual detection '''                 
                command = "sex /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits -c %(PHOTCONF)s/phot.conf.sex \
                -PARAMETERS_NAME %(PHOTCONF)s/phot.param.short.sex \
                -CATALOG_NAME /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.all%(tag)s.cat \
                -FILTER_NAME /%(path)s/%(filter)s/PHOTOMETRY/gauss.conv \
                -FILTER  Y \
                -SEEING_FWHM %(fwhm).3f \
                -DETECT_MINAREA 3 -DETECT_THRESH 10000 -ANALYSIS_THRESH 10000 \
                -MAG_ZEROPOINT 27.0 \
                -FLAG_TYPE OR\
                -FLAG_IMAGE /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits \
                -GAIN %(GAIN).3f \
                -CHECKIMAGE_NAME /%(path)s/%(filter)s/PHOTOMETRY/coadd.filtered.fits\
                -CHECKIMAGE_TYPE FILTERED\
                -BACK_TYPE MANUAL\
                -BACK_VALUE 0.0\
                -WEIGHT_IMAGE /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits \
                -WEIGHT_TYPE MAP_WEIGHT" % params
            else: 
                command = 'cp /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits /%(path)s/%(filter)s/PHOTOMETRY/coadd.filtered.fits' % params 
            
            print command
            print 'making filtered image'
            os.system(command)

            ''' detection images -- one flag image --- one filter -- detect on lensing band ''' 
            command = "sex /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix_root)s/coadd.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.filtered.fits -c %(PHOTCONF)s/phot.conf.sex \
            -PARAMETERS_NAME %(PHOTCONF)s/phot.param.short.sex \
            -CATALOG_NAME /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.all%(tag)s.cat \
            -FILTER_NAME %(DATACONF)s/default.conv \
            -FILTER  Y \
            -SEEING_FWHM %(fwhm).3f \
            -DETECT_MINAREA 3 -DETECT_THRESH 1.5 -ANALYSIS_THRESH 1.5 \
            -MAG_ZEROPOINT 27.0 \
            -FLAG_TYPE OR\
            -FLAG_IMAGE /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits \
            -GAIN %(GAIN).3f \
            -CHECKIMAGE_NAME /%(path)s/%(filter)s/PHOTOMETRY/coadd.background.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.apertures.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.segmentation.fits\
            -CHECKIMAGE_TYPE BACKGROUND,APERTURES,SEGMENTATION\
            -WEIGHT_IMAGE /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix_root)s/coadd.weight.fits,/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits \
            -WEIGHT_TYPE MAP_WEIGHT" % params

            print command
            print 'measuring filtered image'
            os.system(command)

            #command = "sex /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits,/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits -c %(PHOTCONF)s/phot.conf.sex \
            #-PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
            #-CATALOG_NAME /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.all%(tag)s.cat \
            #-DETECT_MINAREA 10 -DETECT_THRESH 10 -ANALYSIS_THRESH 10 \
            #-MAG_ZEROPOINT 27.0 \
            #-FLAG_TYPE MAX\
            #-FLAG_IMAGE '' \
            #-GAIN %(GAIN).3f \
            #-WEIGHT_IMAGE /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits,'' \
            #-WEIGHT_TYPE MAP_WEIGHT" % params



        elif type == 'each':                                                                                                                                                                                                                                         
            params = {'path':path, 'filter_root': filter_root, 'cluster':cluster, 'filter':filter, 'appendix':appendix, 'PHOTCONF':PHOTCONF, 'fwhm': seeing_worst, 'BASE':BASE, 'GAIN':float(fwhms[filter]['GAIN']),'DATACONF':os.environ['DATACONF'], 'tag':tag}
                                                                                                                                                                                                                                                                  
            command = "sex /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits -c %(PHOTCONF)s/phot.conf.sex \
            -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
            -CATALOG_NAME /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.each%(tag)s.cat \
            -FILTER_NAME %(DATACONF)s/default.conv \
            -FILTER  Y \
            -SEEING_FWHM %(fwhm).3f \
            -DETECT_MINAREA 3 -DETECT_THRESH 3 -ANALYSIS_THRESH 3 \
            -MAG_ZEROPOINT 27.0 \
            -FLAG_TYPE OR\
            -FLAG_IMAGE /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits \
            -GAIN %(GAIN).3f \
            -WEIGHT_IMAGE /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits \
            -WEIGHT_TYPE MAP_WEIGHT" % params

        elif type == 'arc':

            params = {'path':path, 'filter_root': filter_root, 'cluster':cluster, 'filter':filter, 'appendix':appendix, 'PHOTCONF':PHOTCONF, 'BASE':BASE, 'GAIN':float(fwhms[filter]['GAIN']),'DATACONF':os.environ['DATACONF'], 'tag':tag}


            #command = "sex /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits,/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits -c %(PHOTCONF)s/phot.conf.sex \

            commandA = "sex /%(path)s/%(filter_root)s/PHOTOMETRY/coadd.small.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.small.fits -c %(PHOTCONF)s/phot.conf.sex \
            -PHOT_APERTURES 70,100 \
            -BACK_SIZE 10 \
            -BACK_FILTERSIZE 2 \
            -BACKPHOTO_TYPE GLOBAL \
            -BACK_TYPE AUTO \
            -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
            -CATALOG_NAME /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.arc.all%(tag)s.cat \
            -FILTER_NAME %(DATACONF)s/default.conv,%(DATACONF)s/default.conv\
            -FILTER  Y \
            -DETECT_MINAREA 3 -DETECT_THRESH 0.5 -ANALYSIS_THRESH 0.5  \
            -MAG_ZEROPOINT 27.0 \
            -INTERP-TYPE NONE\
            -FLAG_TYPE MAX\
            -FLAG_IMAGE \"\"\
            -SATUR_LEVEL 30000.0  \
            -MAG_ZEROPOINT 27.0 \
            -GAIN %(GAIN).3f \
            -CHECKIMAGE_NAME /%(path)s/%(filter)s/PHOTOMETRY/coadd.arc.background.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.arc.apertures.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.arc.segmentation.fits\
            -CHECKIMAGE_TYPE BACKGROUND,APERTURES,SEGMENTATION\
            -WEIGHT_IMAGE /%(path)s/%(filter_root)s/PHOTOMETRY/coadd.weight.arc.small.fits,%(path)s/%(filter)s/PHOTOMETRY/coadd.weight.arc.small.fits\
            -WEIGHT_TYPE NONE" % params

            params['BACK_VALUE'] = 0
            if filter == 'W-J-V':
                params['BACK_VALUE'] = -0.02

            commandB = "sex /%(path)s/%(filter_root)s/PHOTOMETRY/coadd_small.sub.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd_small.sub.fits -c %(PHOTCONF)s/phot.conf.sex \
            -PHOT_APERTURES 70,100 \
            -BACK_SIZE 64 \
            -BACK_FILTERSIZE 3 \
            -BACKPHOTO_TYPE GLOBAL \
            -BACK_TYPE MANUAL \
            -BACK_VALUE -0.02 \
            -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
            -CATALOG_NAME /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.arc.all%(tag)s.cat \
            -FILTER_NAME %(DATACONF)s/default.conv,%(DATACONF)s/default.conv\
            -FILTER  Y \
            -DETECT_MINAREA 3 -DETECT_THRESH 0.5 -ANALYSIS_THRESH 0.5  \
            -MAG_ZEROPOINT 27.0 \
            -INTERP-TYPE NONE\
            -FLAG_TYPE MAX\
            -FLAG_IMAGE \"\"\
            -SATUR_LEVEL 30000.0  \
            -MAG_ZEROPOINT 27.0 \
            -GAIN %(GAIN).3f \
            -CHECKIMAGE_NAME /%(path)s/%(filter)s/PHOTOMETRY/coadd.arc.apertures.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.arc.segmentation.fits\
            -CHECKIMAGE_TYPE APERTURES,SEGMENTATION\
            -WEIGHT_IMAGE /%(path)s/%(filter_root)s/PHOTOMETRY/coadd.weight.arc.small.fits,%(path)s/%(filter)s/PHOTOMETRY/coadd.weight.arc.small.fits\
            -WEIGHT_TYPE MAP_WEIGHT" % params
                
            command = commandB

        #-WEIGHT_IMAGE /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits,%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits\
        print command
        filecommand.write(command + '\n')
        sys.exit(0)

    
for child in children: 
    os.waitpid(child,0)

print 'DONE!!!!'

#-PARAMETERS_NAME %(PHOTCONF)/phot.conf.sex \
#-PARAMETERS_NAME %(PHOTCONF)/singleastrom_std.param.sex%
