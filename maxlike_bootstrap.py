############################
# Manage bootstrapping of ML masses
###########################

from __future__ import with_statement
import glob, tempfile, subprocess, shutil, os
import pyfits, numpy as np
import ldac, maxlike_secure_driver as msd, bashreader

##############################


progs = bashreader.parseFile('progs.ini')

##############################


def createBootstrapCats(cluster, filter, image, indir, outdir, nbootstraps = 50):

    manager = msd.maxlike_controller.Controller(modelbuilder = msd.maxlike_masses,
                                           shapedistro = msd.nfwmodel_voigtnorm_shapedistro.VoigtnormShapedistro(),
                                           filehandler = msd.maxlike_subaru_secure_filehandler.SubaruSecureFilehandler(),
                                           runmethod = msd.maxlike_masses.SampleModelToFile())

    options, args = manager.filehandler.createOptions(cluster = cluster, filter = filter, image = image, workdir=indir)

    manager.load(options, args)

    inputcat = manager.inputcat

    for i in range(nbootstraps):
    
        bootstrap = np.random.randint(0, len(inputcat), len(inputcat))

        mlcat = inputcat.filter(bootstrap)
        mlcat.saveas('%s/%s.%s.%s.b%d.cat' % (outdir, cluster, filter, image, i), clobber=True)

    
    

