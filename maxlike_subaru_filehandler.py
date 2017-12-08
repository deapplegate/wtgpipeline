#############################
# Handles loading files for a simulation run
#############################

from __future__ import with_statement
import ldac, cPickle, os, subprocess, copy, sys, re
import numpy as np
import astropy.io.fits as pyfits
import shearprofile as sp, bashreader
import maxlike_general_filehandler, varcontainer, utilities

#############################

__cvs_id__ = "$Id$"

#############################

subarudir = '/nfs/slac/g/ki/ki05/anja/SUBARU'


############################

class NoRedshiftException(Exception): pass

def parseZCluster(cluster, basedir=subarudir):

    #adam-tmp# redshiftfile = '%s/clusters.redshifts' % basedir
    redshiftfile = 'clusters.redshifts'

    with open(redshiftfile) as f:

        for line in f.readlines():

            tokens = line.split()
            cur_cluster = tokens[0]
            redshift = float(tokens[1])

            if cur_cluster == cluster:
                return redshift

    raise NoRedshiftException(cluster)

#############################

def calcNearestNeighborCut(options, cat, psfsize, ldaclensing):

    curdir = os.getcwd()

    os.chdir(ldaclensing)

    progs = bashreader.parseFile('progs.ini')
    
    temp_inputcatfile = utilities.getTempFile(dir=progs.tempdir, suffix='.cat')
    temp_outputcatfile = utilities.getTempFile(dir=progs.tempdir, suffix='.cat')
    print cat.sourcefile
    hdulist = pyfits.open(cat.sourcefile)
    newhdus = [pyfits.PrimaryHDU()]
    for hdu in hdulist[1:]:
        if hdu.header['EXTNAME'] == 'OBJECTS':
            newhdus.append(cat.hdu)
        elif hdu.header['EXTNAME'] == 'FIELDS':
            fieldstable = ldac.LDACCat(hdu)
            fieldstable['OBJECT_COUNT'][:] = np.array([len(cat)])
            newhdus.append(fieldstable.hdu)
    hdulist = pyfits.HDUList(newhdus)
    hdulist.writeto(temp_inputcatfile, overwrite=True)
    
    stringvals = copy.copy(options)
    stringvals.inputcatfile = temp_inputcatfile
    stringvals.outputcatfile = temp_outputcatfile

    #BASH script hardcodes what the comparison catalog is. Bewarned!
    command = './cut_nearest_neighbours_cc.sh %(cluster)s %(filter)s %(image)s %(inputcatfile)s %(outputcatfile)s %(psfsize)2.4f' % stringvals


    try:

        subprocess.check_call(command.split())

        outputcat = ldac.openObjectFile(temp_outputcatfile)

        ids = {}
        for id in cat['SeqNr']:
            ids[id] = False
        for id in outputcat['SeqNr']:
            ids[id] = True

        nearest_neighbor_cut = np.array([ids[id] for id in cat['SeqNr']])

    finally:
    
        #if os.path.exists(temp_inputcatfile):
        #    os.remove(temp_inputcatfile)
        #if os.path.exists(temp_outputcatfile):
        #    os.remove(temp_outputcatfile)
        os.chdir(curdir)

    return nearest_neighbor_cut


#############################

class R500Exception(Exception): pass


def readR500(cluster, basedir=subarudir):

    r500 = None
    with open('%s/clusters.r500x.dat' % basedir) as input:
        for line in input.readlines():
            curcluster, cur_r500, cur_r500err = line.split()
            if curcluster == cluster:
                r500 = float(cur_r500)
                break
    if r500 is None:
        raise R500Exception

    return r500

#############################

def readPSFSize(basedir, cluster, filter, image):

    psfsize = None
    with open('%s/cluster.seeing.dat' % basedir) as input:
        for line in input.readlines():
            line = line.strip()
            curcluster, curfilter, curimage, curpsfsize = line.split()
            if curcluster == cluster and \
                    curfilter == filter and \
                    curimage == image:
                psfsize = float(curpsfsize)
                break
    if psfsize is None:
        raise WeirdnessException

    return psfsize
    


#############################

def readClusterCenters(cluster, basedir=subarudir):

    center = None
    with open('%s/clusters.centers' % basedir) as input:
        for line in input.readlines():
            curcluster, centerx, centery = line.split()
            if curcluster == cluster:
                center = (float(centerx), float(centery))
                break
    if center is None:
        raise WeirdnessException

    return center


#############################

def getStdOut(cmd):
    
    return subprocess.Popen(cmd, stdout=PIPE).communicate()[0]
    

def readRedSeqCut(lensdir):
    
    blue=getStdOut("awk '{if($1~\"bluemag\") print $2}' %s/redseq_all.params" % lensdir)
    green=getStdOut("awk '{if($1~\"greenmag\") print $2}' %s/redseq_all.params" % lensdir)
    rscut=getStdOut("awk '{if($1~\"'%s'-'%s'\") print $0}' %s/cc_cuts3.dat" % (blue, green, lensdir))

    
    #TEMP FILE; RUN LDACFILTER; MATCH UP SEQNR TO MAKE TRUE/FALSE ARRAY
    

    

        

#############################


class WeirdnessException(Exception): pass

##############################



class SubaruFilehandler(object):

    def __init__(self):

        self.cuts = [self.dataCuts]


    def addCLOps(self, parser):

        parser.add_option('--nearestneighbor', dest='nearestneighbor',
                          help = 'Turns off the nearest neighbor cut', default = True, 
                          action='store_false')
        parser.add_option('-c', '--cluster', dest='cluster',
                          help='Cluster name')
        parser.add_option('-f', '--filter', dest='filter',
                          help='Detection and lensing filter')
        parser.add_option('-v', '--image', dest='image',
                          help='Lensing image, (eg. good, gabodsid3088)')
        parser.add_option('--ldaclensing', dest='ldaclensing',
                          help='location of the ldaclensing directory', default='../ldaclensing')
        parser.add_option('--snlow', dest='snlow',
                          help='Lower bound on snratio value', type='float', default = 3)
        parser.add_option('--snhigh', dest='snhigh',
                          help='Upper bound on snratio value', type='float', default = 9999)
        parser.add_option('--oddscut', dest='oddscut',
                          help = 'What is the lower limit for BPZ ODDS  value?',
                          type='float', default = 0.)
        parser.add_option('--minmag', dest='minmag',
                          help = 'Minimum I+ magnitude to accept',
                          type='float', default = 25.)
        parser.add_option('--redseqcat', dest='redseqcat',
                          help = 'Catalog with only red sequence members',
                          default = None)
        parser.add_option('--shapecut', dest='shapecut',
                          help = 'Turn on shape quality cuts',
                          default = False, action = 'store_true')
        parser.add_option('--rhcut', dest='rhcut',
                          help = 'Rh Cut, relative to size of PSF',
                          default = 1.15, type= 'float')

    #############################

    def createOptions(self, cluster, filter, image, ldaclensing='../ldaclensing', 
                      snlow = 3, snhigh = 9999, oddscut = 0., minmag = 25., rhcut = 1.15,
                      nearestneighbor = True, redseqcat = None, shapecut = False,
                      options = None, args = None):

        if options is None:
            options = varcontainer.VarContainer()
        options.cluster = cluster
        options.filter = filter
        options.image = image
        options.ldaclensing = ldaclensing
        options.snlow = snlow
        options.snhigh = snhigh
        options.oddscut = oddscut
        options.minmag = minmag
        options.rhcut = rhcut
        options.nearestneighbor = nearestneighbor
        options.redseqcat = redseqcat
        options.shapecut = shapecut

        return options, None

    #############################


    def dataCuts(self, manager):

        inputcat = manager.inputcat
        lensingcat = manager.lensingcat
        options = manager.options


        rhcut = inputcat['size'] > options.rhcut
        rgcut = np.logical_and(lensingcat['rg'] > 1.5, lensingcat['rg'] < 5)
        clcut = lensingcat['cl'] == 0
        flagscut = np.logical_or(np.logical_and(lensingcat['IMAFLAGS_lensimage'] == 1, 
                                                lensingcat['REL_AVE_WEIGHT1'] >= 0.5),
                                 lensingcat['IMAFLAGS_lensimage'] < 1)

        detectmagcut = lensingcat['MAG_APER1-SUBARU-COADD-1-%s' % options.filter] > 22

        if 'MAG_APER1-SUBARU-COADD-1-W-S-I+' in lensingcat:
            imagcut = lensingcat['MAG_APER1-SUBARU-COADD-1-W-S-I+'] < options.minmag
        else:
            imagcut = lensingcat['HYBRID_MAG_APER-SUBARU-10_2-1-W-S-I+'] < options.minmag

        sncut = np.logical_and(options.snlow <=inputcat['snratio'],
                               inputcat['snratio'] < options.snhigh)

        nfiltcut = inputcat['nfilt'] > 4
        if not nfiltcut.any():
            nfiltcut = inputcat['nfilt'] >= 4


        shapecut = np.ones(len(inputcat)) == 1
        if options.shapecut:
            shapecut = lensingcat['Pgs'] > 0.1
    

        oddscut = manager.inputcat['odds'] > options.oddscut

        nearestneighbor = np.ones(len(inputcat)) == 1
        if options.nearestneighbor:
            nearestneighbor = manager.nearestneighbors['neighbors'] == 0

        redseqcut = np.ones(len(inputcat)) == 1
        if options.redseqcat is not None:
            manager.open('redseqcat', options.redseqcat, ldac.openObjectFile)
            inputIds = {}
            for id in inputcat['SeqNr']:
                inputIds[id] = True
            for id in manager.redseqcat['SeqNr']:
                inputIds[id] = False
            redseqcut = np.array([inputIds[id] for id in inputcat['SeqNr']])

        basic_cuts = reduce(np.logical_and, [rhcut, rgcut, clcut, flagscut, 
                                             detectmagcut, imagcut, sncut, 
                                             oddscut, nearestneighbor, redseqcut,
                                             nfiltcut, shapecut])



        return basic_cuts

    ######################

    def buildFileNames(self, manager, newoptions):

        options = manager.options

        clusterdir = '%s/%s' % (subarudir, options.cluster)
        photdir = '%s/PHOTOMETRY_%s_aper' % (clusterdir, options.filter)
        lensingdir = '%s/LENSING_%s_%s_aper/%s' % (clusterdir, options.filter, options.filter, options.image)


        newoptions.lensingcat = '%s/coadd_photo.cat' % lensingdir

        newoptions.bpzfile = '%s/%s.APER1.1.CWWSB_capak.list.all.bpz.tab' % (photdir, options.cluster)

        newoptions.inputPDZ = '%s/pdz.cat' % photdir

        newoptions.neighborcat = '%s/neighbors.cat' % lensingdir
        


    ######################


    def readData(self, manager):

        options = manager.options

        newoptions = varcontainer.VarContainer()
        newoptions.update(options)


        self.buildFileNames(manager, newoptions)


        manager.open('lensingcat', newoptions.lensingcat, ldac.openObjectFile)

        if options.nearestneighbor is True:
            nncat = ldac.openObjectFile(newoptions.neighborcat)
            manager.nearestneighbors = nncat.matchById(manager.lensingcat)

        newoptions.psfsize = readPSFSize(options.workdir, options.cluster, options.filter, options.image)

        newoptions.zcluster = parseZCluster(options.cluster)
        newoptions.r500 = readR500(options.cluster)
        newoptions.centerx, newoptions.centery = readClusterCenters(options.cluster)

        newoptions.pixscale = 0.2

        newoptions.xcol = 'Xpos'
        newoptions.ycol = 'Ypos'

        newoptions.g1col = 'gs1'
        newoptions.g2col = 'gs2'

        newoptions.sizecol = 'rh'

        newoptions.centerx = 5000
        newoptions.centery = 5000


        newoptions.snratio = 'snratio_scaled1'


        newoptions.zbcol = 'BPZ_Z_B'

        manager.replace('options', newoptions)

        maxlike_general_filehandler.readData(manager)


   


    
    
    
