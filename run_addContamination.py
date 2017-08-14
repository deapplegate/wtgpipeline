#!/usr/bin/env python

import sys, os
import ldac
import cosmos_sim as cs
import cPickle
import shearprofile as sp
import numpy as np

outputdir = sys.argv[1]
contam = float(sys.argv[2])
sourcebpzfile = sys.argv[3]
sourcepdzfile = sys.argv[4]
catfiles = sys.argv[5:]

sourcebpz = ldac.openObjectFile(sourcebpzfile, 'STDTAB')

input = open(sourcepdzfile, 'rb')
pdzrange, sourcepdz = cPickle.load(input)
input.close()


for catfile in catfiles:

    dir, filename = os.path.split(catfile)

    print filename

    base, ext = os.path.splitext(filename)

    simcat = ldac.openObjectFile(catfile)

    zcluster = simcat.hdu.header['Z']

    r500 = sp.NFWRdelta(500., simcat.hdu.header['CONCEN'], simcat.hdu.header['R_S'])

    input = open('%s/%s.pdz' % (dir,base), 'rb')
    pdzrange, simpdz = cPickle.load(input)
    input.close()


    finalcat, finalpdz = cs.addContamination(sourcebpz, sourcepdz, np.ones(len(sourcebpz)), 
                                             np.ones(len(sourcebpz)), simcat, simpdz, r500, 
                                             zcluster, f500 = contam, shape_distro_kw = {'sigma' : 0.25})


    finalcat.saveas('%s/%s' % (outputdir, filename), clobber=True)
    
    output = open('%s/%s.pdz' % (outputdir, base), 'wb')
    cPickle.dump((pdzrange, finalpdz), output)
    output.close()
