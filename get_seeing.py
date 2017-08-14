#!/usr/bin/env python
##########################
#
#  Designed to measure the seeing in images, 
#  and produce a file with:
#  [exposure name1] [seeing1]
#  [exposure name2] [seeing2] 
#  ...
#
##########################

import os, sys, commands, glob, numpy, re, commands, string, tempfile
import utilities, bashreader

# Calculates seeing

###########################################

class BadTagNameException(Exception): pass

def findImageTag(image):

    dirname = os.path.dirname(image)
    match = re.search('coadd_.+_(.+)', dirname)
    if match is None:
        raise BadTagNameException(dirname)
    return match.group(1)

################################



# Main code.
def doit():
    usage = '''
get_seeing.py

    gets the seeing for all exposures

usage:

   get_seeing.py [maindir] [cluster] [ending] [list of filters:optional]

   example:
        ./get_seeing.py ${SUBARUDIR} MACS1427+44 
        ./get_seeing.py ${SUBARUDIR} MACS1427+44 "_t1"
        ./get_seeing.py ${SUBARUDIR} MACS1427+44 "" W-J-V W-J-B 

    If no filters given, all filters will be included, otherwinse only the listed filters will be considered.
    
    result:
         file seeing_[clustername].cat in local directory with list of exposures and seeing.


options:
    -h       this

    '''
    # if -h called, or not enough args, show usage and quit
    if ('-h' in sys.argv) or len(sys.argv) <3:
        print usage
        exit(0)



    # set up directory structure:
    maindir=sys.argv[1]       # this should be ${SUBARUDIR} 
    cluster=sys.argv[2]       # full cluster name    

    if (len(sys.argv) == 3):
        filterlist=['all']
    else:
        filterlist = sys.argv[3:]

        
    # get the progs from prog.ini
    dict = bashreader.parseFile('progs.ini')

    # definitions...
    path=maindir+'/'+cluster


    TEMPDIR = tempfile.mkdtemp(dir='/tmp')
    PHOTCONF = './photconf/'

    # different filters...
    subarufilters=['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-I+','W-S-Z+']
    cfhtfilters=['u','g','r','i','z']

    # for the case of all filters
    if filterlist[0]=='all':
         list_of_images = glob.glob(path+'/W-?-??/SCIENCE/coadd_'+cluster+'_SUPA*/coadd.fits')
         list_of_images.extend(glob.glob(path+'/W-?-??/SCIENCE/coadd_'+cluster+'_all/coadd.fits'))
         list_of_images.extend(glob.glob(path+'/W-?-?/SCIENCE/coadd_'+cluster+'_SUPA*/coadd.fits'))
         list_of_images.extend(glob.glob(path+'/W-?-?/SCIENCE/coadd_'+cluster+'_all/coadd.fits'))
         list_of_images.extend(glob.glob(path+'/?/SCIENCE/coadd_'+cluster+'_*p/coadd.fits'))
         list_of_images.extend(glob.glob(path+'/?/SCIENCE/coadd_'+cluster+'_all/coadd.fits'))
         list_of_images.extend(glob.glob(path+'/W-?-?_*_CALIB/SCIENCE/coadd_'+cluster+'_all/coadd.fits'))
         list_of_images.extend(glob.glob(path+'/W-?-??_*_CALIB/SCIENCE/coadd_'+cluster+'_all/coadd.fits'))
         

             
         

    else : # for specific filters
        list_of_images=[]
        for f in filterlist:
            thislist = glob.glob(path+'/'+f+'/SCIENCE/coadd_'+cluster+'_SUPA*/coadd.fits')
            thislist.append(path+'/'+f+'/SCIENCE/coadd_'+cluster+'_all/coadd.fits')
            thislist.extend(glob.glob(path+'/'+f+'/SCIENCE/coadd_'+cluster+'_*p/coadd.fits'))


            list_of_images = list_of_images + thislist

            
    print "Measuring the seeing of ..."
    for image in list_of_images:
        print image

    # if no images, quit
    if len(list_of_images)==0:
        print 'no images '
        exit(1)

    
    children = []   # this is supposed to make it faster
    #                 its the parallel mechanism
    for image in list_of_images:        
        child = os.fork()  # forking!
        if child:
            children.append(child)  # children processes.
        else:            
            flagimage=image[:-4]+'flag.fits' # assumes the flag file is coadd.flag.fits
            if len(flagimage) == 0:          # if we can't find it
                print 'Can not find '+flagimage
                exit(1)

            tag = findImageTag(image)

            params = {'path':path, 
                      'cluster':cluster, 
                      'PHOTCONF':PHOTCONF, 
                      'TEMPDIR': TEMPDIR,
                      'image':image,
                      'flagimage':flagimage,
                      'tag':tag}

                            
            # now run sextractor to determine the seeing:              
            command = 'sex %(image)s \
            -c %(PHOTCONF)s/singleastrom.conf.sex \
            -FLAG_IMAGE %(flagimage)s \
            -FLAG_TYPE MAX \
            -CATALOG_NAME %(TEMPDIR)s/seeing_%(tag)s.cat \
            -FILTER_NAME %(PHOTCONF)s/default.conv \
            -CATALOG_TYPE "ASCII" \
            -DETECT_MINAREA 10 -DETECT_THRESH 10. \
            -ANALYSIS_THRESH 5 \
            -PARAMETERS_NAME %(PHOTCONF)s/singleastrom.ascii.param.sex' %  params 


            print command
            sys.stderr.write(command + '\n')
            os.system(command)
            sys.exit(0)

            
    for child in children: 
        os.waitpid(child,0)
    
    # Got seeing
    
############################################
#  Now we are just going to organize it a bit
#  
############################################    
    openfile =  open('seeing_'+cluster+'.cat','w')
    # now we order the seeings, find which is the worst.    
    fwhms = {} 
    for image in list_of_images:
        # get some info
        try:
            GAIN, PIXSCALE, EXPTIME = utilities.get_header_info(image) 
        except Exception:
            sys.stderr.write('Skipping %s!' % image)
            continue

        tag = findImageTag(image)

        # get all the info together in one array
        fwhms[tag] = {'IMAGE':image,'GAIN':GAIN,'PIXSCALE':PIXSCALE, 'EXPTIME': EXPTIME}

        # the output cat from above
        file_seeing = '%(TEMPDIR)s/seeing_%(tag)s.cat' % {'TEMPDIR': TEMPDIR,'tag':tag}

        # gets seeing
        fwhms[tag]['SEEING'] = utilities.calc_seeing(file_seeing,PIXSCALE)  
        print 'image', tag, fwhms[tag]['SEEING'] 

        openfile.write(tag+' '+ str(fwhms[tag]['SEEING']) + ' \n')

    fwhms_comp=[fwhms[x] for x in fwhms.keys()] # list of fwhm's 
    fwhms_comp.sort(utilities.compare)                    # sort
    seeing_worst = fwhms_comp[0]['SEEING']      # worst
    image_worst = fwhms_comp[0]['IMAGE']        # worst image

    
    print ' worst SEEING', image_worst, seeing_worst

    [ os.remove('%s/%s' % (TEMPDIR,file)) for file in os.listdir(TEMPDIR) ]
    os.rmdir(TEMPDIR)



if __name__ == "__main__":
    doit()

