#!/usr/bin/env python
#####################

import os, cPickle, sys, glob
import astropy, astropy.io.fits as pyfits
import process_cosmos_sims as pcs, ldac


def preprocessFile(resultfile):
    print "start"
    #for processing the results of the MaxLike files once

    massdist, masses = pcs.processFile(resultfile)
    print massdist, masses

    dir, filename = os.path.split(resultfile)

    base, ext = os.path.splitext(filename)

    outputfile = '%s/%s.pkl' % (dir, base)

    output = open(outputfile, 'wb')

    cPickle.dump(massdist, output)

    output.close()

    masscat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([pyfits.Column(name = 'masses',
                                                                          format = 'E',
                                                                          array = masses)])))

    masscat.saveas('%s2' % resultfile, overwrite=True)



###############

if __name__ == '__main__':

    resultdir = sys.argv[1]
    print resultdir

    resultfiles = glob.glob('%s/*.out' % resultdir)

    for resultfile in resultfiles:

        preprocessFile(resultfile)
