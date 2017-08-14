def compare(x, y):
    if x['SEEING'] < y['SEEING']:
        return 1    
    
    elif x['SEEING'] == y['SEEING']:
        return 0
    else:
        return -1














def calc_seeing(file,NLINES,PIXSCALE):
    binsize = 0.03 #10./NLINES
    nbins = int((3.0-0.3)/binsize+0.5)
    import numpy
    bin = numpy.zeros(nbins)
    for line in open(file,'r').readlines():
        import re
        fwhm_obj = float(re.split('\s+',line)[3])
        if 3.0 > fwhm_obj*PIXSCALE > 0.3 :
            actubin = int((fwhm_obj * PIXSCALE - 0.3)/binsize)
            bin[actubin] += 1
    max = 0
    k = 0
    for i in range(nbins):
        if bin[i]>max:
            k=i
            max = bin[i]
    fwhm = 0.3 + k*binsize
   
    print 'fwhm', fwhm 
    return fwhm

import os, sys, bashreader, commands
from utilities import *

dict = bashreader.parseFile('progs.ini')
for key in dict.keys():
    os.environ[key] = str(dict[key])

cluster='MACS2243-09'
appendix='_all' #_good'
TEMPDIR = '/tmp/'
PHOTCONF = './photconf/'
tag = 'local50'
path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':cluster}
type='all'

filters=['B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']

filter_root='W-J-V'

BASE="coadd"
file = BASE + '.fits'

if type == 'all':
    children = []
    for filter in filters:
        child = os.fork()
        if child:
            children.append(child)
        else:
            params = {'path':path, 'filter_root': filter_root, 'cluster':cluster, 'filter':filter, 'appendix':appendix, 'PHOTCONF':PHOTCONF, 'TEMPDIR': TEMPDIR}
            print params
            # now run sextractor to determine the seeing:              

            #command = 'sex /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits -c %(PHOTCONF)s/singleastrom.conf.sex \

            command = 'sex /%(path)s/%(filter)s/PHOTOMETRY/coadd_small.fits -c %(PHOTCONF)s/singleastrom.conf.sex \
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
    GAIN, PIXSCALE = get_header_info(file_header) 

    fwhms[filter] = {'FILTER':filter,'GAIN':GAIN,'PIXSCALE':PIXSCALE}

    if type == 'all':
        file_seeing = '%(TEMPDIR)s/seeing_%(filter)s.cat' % {'TEMPDIR': TEMPDIR, 'filter':filter}
        NLINES=50
        fwhms[filter]['SEEING'] = calc_seeing(file_seeing,NLINES,PIXSCALE)
    
  

if type == 'all':
    fwhms_comp=[fwhms[x] for x in fwhms.keys()] 
    fwhms_comp.sort(compare) 
    seeing_worst = fwhms_comp[0]['SEEING']
    filter_worst = fwhms_comp[0]['FILTER']
    print fwhms
    print 'SEEING', filter_worst, seeing_worst
    
    import commands

    for filter in filters: 
        print filter
        params = {'seeing_orig':float(fwhms[filter]['SEEING']), 'seeing_new':float(seeing_worst),'PIXSCALE':float(PIXSCALE), 'path':path, 'cluster': cluster, 'appendix': appendix, 'filter':filter, 'path':path, 'DATACONF': os.environ['DATACONF']}
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

            params = {'path':path, 'filter_root': filter_root, 'cluster':cluster, 'filter':filter, 'appendix':appendix, 'PHOTCONF':PHOTCONF, 'fwhm': seeing_worst, 'BASE':BASE, 'GAIN':float(fwhms[filter]['GAIN']),'DATACONF':os.environ['DATACONF'], 'tag':tag}

            #command = "sex /%(path)s/%(filter_root)s/PHOTOMETRY/coadd_small.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd_small.fits -c %(PHOTCONF)s/phot.conf.sex \
            command = "sex /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits,/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits -c %(PHOTCONF)s/phot.conf.sex \
            -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
            -CATALOG_NAME /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.all%(tag)s.cat \
            -FILTER_NAME %(DATACONF)s/default.conv,/%(path)s/%(filter)s/PHOTOMETRY/gauss.conv \
            -FILTER  Y \
            -SEEING_FWHM %(fwhm).3f \
            -DETECT_MINAREA 3 -DETECT_THRESH 5 -ANALYSIS_THRESH 5  \
            -MAG_ZEROPOINT 27.0 \
            -FLAG_TYPE MAX\
            -FLAG_IMAGE /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits,/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits \
            -SATUR_LEVEL 30000.0  \
            -MAG_ZEROPOINT 27.0 \
            -GAIN %(GAIN).3f \
            -CHECKIMAGE_NAME /%(path)s/%(filter)s/PHOTOMETRY/coadd.background.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.apertures.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.segmentation.fits\
            -CHECKIMAGE_TYPE BACKGROUND,APERTURES,SEGMENTATION\
            -WEIGHT_IMAGE /%(path)s/%(filter_root)s/PHOTOMETRY/coadd.weight.arc.fits,%(path)s/%(filter)s/PHOTOMETRY/coadd.weight.arc.fits\
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
        os.system(command)
        sys.exit(0)

    
for child in children: 
    os.waitpid(child,0)

print 'DONE!!!!'

#-PARAMETERS_NAME %(PHOTCONF)/phot.conf.sex \
#-PARAMETERS_NAME %(PHOTCONF)/singleastrom_std.param.sex%
