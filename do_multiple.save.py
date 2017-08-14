def compare(x, y):
    if x['SEEING'] < y['SEEING']:
        return 1    
    
    elif x['SEEING'] == y['SEEING']:
        return 0
    else:
        return -1

def get_header_info(file):
    print file
    GAIN = commands.getoutput("dfits " + file + " | fitsort -d GAIN | awk '{print $2}' ")
    CDELT1 = commands.getoutput("dfits " + file + " | fitsort -d CDELT1 | awk '{print $2}' ")
    CDELT2 = commands.getoutput("dfits " + file + " | fitsort -d CDELT2 | awk '{print $2}' ")
    print CDELT1, CDELT2
    PIXSCALE = (abs(float(CDELT1)) + abs(float(CDELT2))) / (2.0) * 3600.0
   
    print PIXSCALE 
    
    return GAIN, PIXSCALE


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

dict = bashreader.parseFile('progs.ini')
for key in dict.keys():
    os.environ[key] = str(dict[key])

cluster='MACS2243-09'
appendix='_all' #_good'
TEMPDIR = '/tmp/'
PHOTCONF = './photconf/'
tag = 'local50'
path='/nfs/slac/g/ki/ki05/anja/SUBARU/%(cluster)s/' % {'cluster':cluster}

filters=['B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']

filter_root='W-J-V'

BASE="coadd"
file = BASE + '.fits'

children = []
for filter in filters:
    child = os.fork()
    if child:
        children.append(child)
    else:
        params = {'path':path, 'filter_root': filter_root, 'cluster':cluster, 'filter':filter, 'appendix':appendix, 'PHOTCONF':PHOTCONF, 'TEMPDIR': TEMPDIR}
        print params
        # now run sextractor to determine the seeing:              
        command = 'sex /%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits -c %(PHOTCONF)s/singleastrom.conf.sex \
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
    file_seeing = '%(TEMPDIR)s/seeing_%(filter)s.cat' % {'TEMPDIR': TEMPDIR, 'filter':filter}
    NLINES=50

    fwhms[filter] = {'SEEING':calc_seeing(file_seeing,NLINES,PIXSCALE),'FILTER':filter,'GAIN':GAIN,'PIXSCALE':PIXSCALE}
  
fwhms_comp=[fwhms[x] for x in fwhms.keys()] 
fwhms_comp.sort(compare) 
seeing_worst = fwhms_comp[0]['SEEING']
filter_worst = fwhms_comp[0]['FILTER']
print fwhms
print 'SEEING', filter_worst, seeing_worst

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
    

import commands
      

children = [] 
for filter in filters: 
    os.system("mkdir /" + path + "/" + filter + "/PHOTOMETRY/")
    os.system("rm /" + path + "/" + filter + "/PHOTOMETRY/" + BASE + ".all" + tag + ".cat")

    child = os.fork()
    if child:
        children.append(child)
    else:
        params = {'path':path, 'filter_root': filter_root, 'cluster':cluster, 'filter':filter, 'appendix':appendix, 'PHOTCONF':PHOTCONF, 'fwhm': seeing_worst, 'BASE':BASE, 'GAIN':float(fwhms[filter]['GAIN']),'DATACONF':os.environ['DATACONF'], 'tag':tag}
        print params

        command = "rm /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.all.cat" % {'path':path, 'filter':filter}
        print command 
        os.system(command)

        command = "sex /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits,/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.fits -c %(PHOTCONF)s/phot.conf.sex \
            -PARAMETERS_NAME %(PHOTCONF)s/phot.param.sex \
            -CATALOG_NAME /%(path)s/%(filter)s/PHOTOMETRY/%(filter)s.all%(tag)s.cat \
            -FILTER_NAME %(DATACONF)s/default.conv,/%(path)s/%(filter)s/PHOTOMETRY/gauss.conv \
            -FILTER  Y \
            -SEEING_FWHM %(fwhm).3f \
            -DETECT_MINAREA 5 -DETECT_THRESH 1.5. -ANALYSIS_THRESH 1.5  \
            -MAG_ZEROPOINT 27.0 \
            -FLAG_TYPE MAX\
            -FLAG_IMAGE /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits,/%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.flag.fits \
            -SATUR_LEVEL 30000.0  \
            -MAG_ZEROPOINT 27.0 \
            -GAIN %(GAIN).3f \
            -CHECKIMAGE_NAME /%(path)s/%(filter)s/PHOTOMETRY/coadd.background.fits,/%(path)s/%(filter)s/PHOTOMETRY/coadd.apertures.fits\
            -CHECKIMAGE_TYPE BACKGROUND,APERTURES\
            -WEIGHT_IMAGE /%(path)s/%(filter_root)s/PHOTOMETRY/coadd.weight.arc.fits,%(path)s/%(filter)s/PHOTOMETRY/coadd.weight.arc.fits\
            -WEIGHT_TYPE MAP_WEIGHT" % params

        #-WEIGHT_IMAGE /%(path)s/%(filter_root)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits,%(path)s/%(filter)s/SCIENCE/coadd_%(cluster)s%(appendix)s/coadd.weight.fits\
        print command
        os.system(command)
        sys.exit(0)

    
for child in children: 
    os.waitpid(child,0)

print 'DONE!!!!'

#-PARAMETERS_NAME %(PHOTCONF)/phot.conf.sex \
#-PARAMETERS_NAME %(PHOTCONF)/singleastrom_std.param.sex%
