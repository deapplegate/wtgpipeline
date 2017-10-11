#!/usr/bin/env python
############################
# Manage bootstrapping of ML and CC methods to calculate covariance
###########################

from __future__ import with_statement
import glob, tempfile, subprocess, shutil, os, sys
import astropy, astropy.io.fits as pyfits, numpy as np
import ldac, maxlike_subaru_filehandler as msf, bashreader
import shearprofile as sp

##############################

subarudir = '/nfs/slac/g/ki/ki05/anja/SUBARU'

progs = bashreader.parseFile('progs.ini')

##############################


def createBootstrapCats(cluster, filter, image, outdir, nbootstraps = 100, startnum = 0):

    clusterdir = '%s/%s' % (subarudir, cluster)
    lensingdir = '%s/LENSING_%s_%s_aper/%s' % (clusterdir, filter, filter, image)
    lensingcat = '%s/coadd_photo2.cat' % lensingdir
    cutsfile = '%s/cc_cuts3.dat' % lensingdir

    outdir = '%s/%s' % (outdir, cluster)
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    cat = ldac.openObjectFile(lensingcat)

    zcluster = msf.parseZCluster(cluster)
    center = msf.readClusterCenters(cluster)
    r_arc, E, B = sp.calcTangentialShear(cat = cat, 
                                         center = center,
                                         pixscale = 0.2)

    r_mpc =  r_arc * (1./3600.) * (np.pi / 180. ) * sp.angulardist(zcluster)

    cat = cat.filter(np.logical_and(r_mpc > 0.750, r_mpc < 3.0))
    cat.hdu.header['EXTNAME']='STDTAB'

    try:

        tmpspace = tempfile.mkdtemp(dir = progs.tempdir)

        cat.saveas('%s/base.cat' % tmpspace)

        subprocess.check_call("./prefilter_mlcc_bootstrap.sh %s %s %s %s %s %s" \
                      % (cluster, filter, image, 
                      tmpspace, '%s/base.cat' % tmpspace, '%s/prefiltered.cat' % tmpspace), shell=True)

        cat = ldac.openObjectFile('%s/prefiltered.cat' % tmpspace, 'STDTAB')
        cat.hdu.header['EXTNAME']= 'OBJECTS'

        for i in range(startnum, startnum + nbootstraps):
    
            bootstrap = np.random.randint(0, len(cat), len(cat))

            bootcat = cat.filter(bootstrap)
            bootcat.saveas('%s/bootstrap_%d.ml.cat' % (outdir, i), overwrite=True)

            bootcat.hdu.header['EXTNAME'] = 'STDTAB'
            curcat = '%s/filter.cat' % tmpspace
            bootcat.saveas(curcat, overwrite=True)

            with open(cutsfile) as cuts:

                for j, cut in enumerate(cuts.readlines()):

                    cut = cut.strip()

                    nextcat = '%s/filter_%d.cat' % (tmpspace, j)

                    print "ldacfilter -i %s -o %s -t STDTAB -c '(%s);'" % (curcat, nextcat, cut)

                    subprocess.check_call("ldacfilter -i %s -o %s -t STDTAB -c '(%s);'" % (curcat, nextcat, cut), shell=True)

                    curcat = nextcat

            shutil.copyfile(curcat, '%s/bootstrap_%d.cc.cat' % (outdir, i))
            for filterfile in glob.glob('%s/filter*' % tmpspace):
                os.remove(filterfile)







    finally:

        shutil.rmtree(tmpspace)



    

    
#####################################


def readBootstrapMasses(workdir):

    clusters = glob.glob('%s/*' % workdir)

    masslists = {}
    for clusterdir in clusters:

        cluster = os.path.basename(clusterdir)
        
        with open('%s/cc.bootstrap' % clusterdir) as input:
            cclist = np.array([ [float(y) for y in x.split()] for x in input.readlines() ])

        with open('%s/ml.bootstrap' % clusterdir) as input:
            mllist = np.array([ [float(y) for y in x.split()] for x in input.readlines() ])

        masslists[cluster] = np.vstack([cclist[:,0], mllist[:,0]]), cclist, mllist

    return masslists





###########################################


if __name__ == '__main__':

    
    cluster  = sys.argv[1]
    filter   = sys.argv[2]
    image    = sys.argv[3]
    outdir   = sys.argv[4]

    createBootstrapCats(cluster, filter, image, outdir)
