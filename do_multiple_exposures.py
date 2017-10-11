#!/usr/bin/env python
##########################
#
# Designed to take a catalog with exposures and their
# seeing,  filter the images to the worst seeing,
# and return catalogs for photometry.
# -mta
#
##########################

from __future__ import with_statement
import re, numpy, commands, string, os, sys, commands, glob, astropy, astropy.io.fits as pyfits, subprocess
import utilities, bashreader

#################################

progs = bashreader.parseFile('progs.ini') 
TEMPDIR = '/tmp/'
PHOTCONF = './photconf/'

#################################

    
# Gets the seeing from the file
def findseeing(wantedImage,file):
    for line in open(file,'r').readlines():
        linelist = re.split('\s+',line)
        curImage = linelist[0]
        if curImage == wantedImage:
            return float(linelist[1])
    print 'fail'
    return 0.   

###########################################

class BadTagNameException(Exception): pass

def findImageTag(image):

    dirname = os.path.dirname(image)
    match = re.search('coadd_.+_(.+)', dirname)
    if match is None:
        raise BadTagNameException(dirname)
    return match.group(1)

################################

################################

def getListOfImages(path, cluster, filter):

    # relavant filters
    subarufilters=['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-I+','W-S-Z+']
    cfhtfilters=['u','g','r','i','z','B']
    specialfilters=['I','K']

    list_of_images = []


    # just to keep track
    if filter in subarufilters:
        list_of_images=glob.glob(path+'/'+filter+'/SCIENCE/coadd_'+cluster+'_SUPA*/coadd.fits')
        list_of_images.sort()
        nchar=11
        if len(list_of_images) == 0:
            print 'No images found for'+path+'/'+filter+'/SCIENCE/coadd_'+cluster+'_SUPA???????/coadd.fits'
            exit(1)


    elif filter in cfhtfilters:
        list_of_images=glob.glob(path+'/'+filter+'/SCIENCE/coadd_'+cluster+'_*[op]/coadd.fits')
        list_of_images.sort()
        nchar=7
        if len(list_of_images) == 0:
            print 'No images found for' +path+'/'+filter+'/SCIENCE/coadd_'+cluster+'_??????p/coadd.fits'  
            exit(1)
    elif filter in specialfilters:
        pass
    else:  # if we don't recognize it...
        print 'Do not recognize filter: '+filter
        exit(1)

    list_of_images.append(path+'/'+filter+'/SCIENCE/coadd_'+cluster+'_all/coadd.fits')

    return list_of_images

################################

def getHeaderData(list_of_images):

    # Loop over the images
    fwhms = {}  # to keep track of some info
    for image in list_of_images:
        # get some info        
        GAIN, PIXSCALE, EXPTIME = utilities.get_header_info(image) 

        tag=findImageTag(image)

        # get all the info together in one array
        fwhms[tag] = {'IMAGE':image,'GAIN':GAIN,'PIXSCALE':PIXSCALE, 'EXPTIME': EXPTIME}

    return fwhms

#################################

def createConvolutionKernals(list_of_images, fwhms, seeingfile, newseeing, path):

    for image in list_of_images: 

        tag=findImageTag(image)

        oldseeing=findseeing(image,seeingfile)
                        
        params = {'seeing_orig':float(oldseeing), \
                  'seeing_new':float(newseeing),\
                  'PIXSCALE':float(fwhms[tag]['PIXSCALE']), \
                  'path':path, \
                  'image':image, \
                  'path':path, \
                  'DATACONF': os.environ['DATACONF'],\
                  'tag':tag}


        # if this isn't the worst seeing image
        print newseeing, ' ', oldseeing
        if float(newseeing) > float(oldseeing):
            # gets the kernel for the the rest of the images
            command = 'python create_gausssmoothing_kernel.py %(seeing_orig).3f %(seeing_new).3f %(PIXSCALE).3f %(path)s/' % params 
            print command
            try:
                subprocess.check_call(command.split())
            except CalledProcessError:
                raise SextractorException(command)
            

            command = 'mv %(path)s/gauss.conv  %(path)s/gauss.%(tag)s.conv' % \
                params
            print command
            subprocess.check_call(command.split())

                
        else: # if it is the worst, use default
            command = 'cp %(DATACONF)s/default.conv %(path)s/gauss.%(tag)s.conv' % params 
            subprocess.check_call(command.split())

    

################################

def divideProcLoad(images, nprocs):

    nImages = len(images)
    num_per_proc = max(int(nImages / nprocs), 1)
    cur=0
    imagelists = []
    while (cur < nImages):
       end = min(cur+num_per_proc, nImages)
       imagelists.append(images[cur:end])
       cur = end

    return imagelists

#################################

def processImage(image, tag, headerInfo, seeingfile, params):

    # get it from the file, again 
    oldseeing=findseeing(image,seeingfile)

    imageroot, ext = os.path.splitext(image)

    print '!!!!!!!!!!!!!!!!' + imageroot +' ' + ext

    # parameters for the object finding
    params['image']=image
    params['GAIN']=float(headerInfo['GAIN'])
    params['tag']=tag
    params['flagimage']=imageroot+'.flag.fits'
    params['weightimage']=imageroot+'.weight.fits'


    # check that all of these flag/weight images are there 
    if len(glob.glob(params['weightimage'])) == 0:
        raise AssertionError('Cannot find ' + params['weightimage'])    
    if len(glob.glob(params['detect_image'])) == 0:
        raise AssertionError('Cannot find ' + params['detect_image'])
    if len(glob.glob(params['detect_weight_image'])) == 0:
        raise AssertionError('Cannot find ' + params['detect_weight_image'])

    # If this isn't the worst seeing, filter away!
    if params['fwhm'] != oldseeing:

        print 'filtering ' + tag
        ''' convolve image -- no background subtraction -- high detection threshold -- no dual detection '''
        command = "%(sex)s  %(image)s  -c %(PHOTCONF)s/phot.conf.sex \
        -PARAMETERS_NAME %(PHOTCONF)s/phot.param.short.sex \
        -CATALOG_NAME %(path)s/coadd.%(tag)s.cat \
        -FILTER_NAME %(path)s/gauss.%(tag)s.conv \
        -FILTER  Y \
        -SEEING_FWHM %(fwhm).3f \
        -DETECT_MINAREA 3 -DETECT_THRESH 10000 -ANALYSIS_THRESH 10000 \
        -MAG_ZEROPOINT 27.0 \
        -FLAG_TYPE OR\
        -FLAG_IMAGE /%(flagimage)s \
        -GAIN %(GAIN).3f \
        -CHECKIMAGE_NAME %(path)s/coadd.filtered.%(tag)s.fits \
        -CHECKIMAGE_TYPE FILTERED \
        -BACK_TYPE MANUAL \
        -BACK_VALUE 0.0 \
        -WEIGHT_IMAGE %(weightimage)s \
        -WEIGHT_TYPE MAP_WEIGHT" % params
    else: # if it is the worst...
        print tag, " worst seeing: measuring background RMS, then copying"
        command = "%(sex)s  %(image)s  -c %(PHOTCONF)s/phot.conf.sex \
        -PARAMETERS_NAME %(PHOTCONF)s/phot.param.short.sex \
        -CATALOG_NAME %(path)s/coadd.%(tag)s.cat \
        -FILTER_NAME %(path)s/gauss.%(tag)s.conv \
        -FILTER  N \
        -SEEING_FWHM %(fwhm).3f \
        -DETECT_MINAREA 3 -DETECT_THRESH 10000 -ANALYSIS_THRESH 10000 \
        -MAG_ZEROPOINT 27.0 \
        -FLAG_TYPE OR\
        -FLAG_IMAGE %(flagimage)s \
        -GAIN %(GAIN).3f \
        -CHECKIMAGE_NAME %(path)s/coadd.filtered.%(tag)s.fits \
        -CHECKIMAGE_TYPE FILTERED \
        -BACK_TYPE MANUAL \
        -BACK_VALUE 0.0 \
        -WEIGHT_IMAGE %(weightimage)s \
        -WEIGHT_TYPE MAP_WEIGHT" % params

        print command
        subprocess.check_call(command.split())

        command = 'cp %(image)s %(path)s/coadd.filtered.%(tag)s.fits' % params 


    print 'making filtered image'    
    print command
    subprocess.check_call(command.split())

    # Now we do the object detection.
    ''' detection images -- one flag image --- one filter -- detect on lensing band ''' 
    command = "%(sex)s %(detect_image)s,%(image)s \
    -c %(PHOTCONF)s/phot.conf.sex \
    -PARAMETERS_NAME %(PHOTCONF)s/phot.param.short.sex \
    -CATALOG_NAME %(path)s/unstacked/coadd.filtered.%(tag)s.cat \
    -FILTER_NAME %(DATACONF)s/default.conv \
    -FILTER  Y \
    -SEEING_FWHM %(fwhm).3f \
    -DETECT_MINAREA 3 -DETECT_THRESH 1.5 -ANALYSIS_THRESH 1.5 \
    -MAG_ZEROPOINT 27.0 \
    -FLAG_TYPE OR \
    -FLAG_IMAGE %(flagimage)s \
    -GAIN %(GAIN).3f \
    -CHECKIMAGE_TYPE NONE \
    -WEIGHT_IMAGE %(detect_weight_image)s,%(weightimage)s \
    -WEIGHT_TYPE MAP_WEIGHT" % params


    print 'measuring filtered image'    
    print command



    subprocess.check_call(command.split())


    # Measure actual background RMS

    command = "%(sex)s  %(image)s  -c %(PHOTCONF)s/phot.conf.sex \
        -PARAMETERS_NAME %(PHOTCONF)s/phot.param.short.sex \
        -CATALOG_NAME blank.cat \
        -CATALOG_TYPE NONE \
        -FILTER  N \
        -SEEING_FWHM %(fwhm).3f \
        -DETECT_MINAREA 5 -DETECT_THRESH 1.5 -ANALYSIS_THRESH 1.5 \
        -MAG_ZEROPOINT 27.0 \
        -FLAG_TYPE OR\
        -FLAG_IMAGE /%(flagimage)s \
        -GAIN %(GAIN).3f \
        -CHECKIMAGE_NAME %(path)s/coadd.noobjs.%(tag)s.fits \
        -CHECKIMAGE_TYPE -OBJECTS \
        -BACK_TYPE MANUAL \
        -BACK_VALUE 0.0 \
        -WEIGHT_IMAGE %(weightimage)s \
        -WEIGHT_TYPE MAP_WEIGHT" % params

    print command
    subprocess.check_call(command.split())
        
    noobjs = pyfits.open('%(path)s/coadd.noobjs.%(tag)s.fits' % params)[0].data
    weight = pyfits.open(params['weightimage'])[0].data

    if noobjs is None or weight is None:
        raise SextractorException

    selectpixels = numpy.logical_and(noobjs != 0, weight > .01)
    rms = numpy.std(noobjs[selectpixels], dtype=numpy.float128)

    with open('%(path)s/unstacked/coadd.filtered.%(tag)s.rms' % params, 'w') as output:
        output.write('# RMS of unfiltered background image\n')
        output.write('%f\n' % rms)

    





#################################

# Main code
def doit():
    # usage
    usage = '''   
    do_multiple_exposures.py    

    produces cataloges for unstacked photometery 

    usage: 

    ./do_multiple_exposures.py [detection image] [seeing file] [new seeing] [maindir] [cluster] [filter]

    example: 
    ./do_multiple_exposures.py  ${SUBARUDIR}/MACS1427+44/W-J-V/SCIENCE/coadd_MACS1427+44_all/coadd.fits \
                 seeing_MACS1427+44.cat 1.41 ${SUBARUDIR} MACS1427+44 W-C-RC ""
  

    result:
    catalogs in [maindir]/[cluster]/[filter]/PHOTOMETRY/unstacked/


    options:
    -h       this

    ''' 

    # if -h called, show usage and quit  
    if '-h' in sys.argv: 
        print usage
        exit(0)

    # an update
    print 'Finished Loading Config, utils'

    detect_image=sys.argv[1] # detection image
    seeingfile=sys.argv[2]   # file with seeings
    newseeing=sys.argv[3]    # seeing to convolve to
    maindir=sys.argv[4]      # this should be ${SUBARUDIR}
    cluster=sys.argv[5]      # full cluster name
    filter=sys.argv[6]       # full filter name
        
   

    
    # get the progs from prog.ini


    # definitions...
    path=maindir+'/'+cluster  

    # file a log for the commands run

    list_of_images = getListOfImages(path, cluster, filter)

    print 'List of images: '
    for image in list_of_images:
        print image


    fwhms = getHeaderData(list_of_images)

    # make dir if necessary
    phot_dir = '%s/%s/PHOTOMETRY/' % (path, filter)
    if not os.path.exists(phot_dir):
        os.mkdir(phot_dir)

    createConvolutionKernals(list_of_images, fwhms, seeingfile, newseeing, phot_dir)



    # printing all of the images.

    unstacked_dir = path + '/' + filter + '/PHOTOMETRY/unstacked'
    if not os.path.exists(unstacked_dir):
        os.mkdir(unstacked_dir)

    detectroot, ext = os.path.splitext(detect_image)

    params = {'path' : phot_dir, 
              'PHOTCONF':PHOTCONF, 
              'fwhm': float(newseeing), 
              'DATACONF':os.environ['DATACONF'], 
              'detect_image':detect_image,
              'detect_weight_image':detectroot+'.weight.fits',
              'sex':progs['p_sex'],
              'filter' : filter}


    #hardcode for 4 procs
#    nprocs = 1
#    image_lists = divideProcLoad(list_of_images, nprocs)
#        
#    children = [] # cleared childen
#    for imagelist in image_lists:
        # make a directory for the new cats if necessary

#        child = os.fork() # fork!
#        if child:
#            children.append(child)
#        else:
#
#            for image in imagelist:
#                tag=findImageTag(image)
#                processImage(image,tag, fwhms[tag], seeingfile, params)
#            sys.exit(0)
#    
#    for child in children: 
#        (id, status) = os.waitpid(child,0)
#        print "process %d finished with status %d" % (id, status)
#
#    print "All Children have reported"
#



    for image in list_of_images:
        tag=findImageTag(image)
        processImage(image, tag, fwhms[tag], seeingfile, params)

if __name__ == "__main__":
    doit()

