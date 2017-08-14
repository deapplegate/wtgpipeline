#!/usr/bin/env python
#####################

import os, cPickle, sys, glob
import pyfits
import process_cosmos_sims as pcs, ldac


def preprocessFile(resultfile):

    #for processing the results of the MaxLike files once

    massdist, masses = pcs.processFile(resultfile)

    dir, filename = os.path.split(resultfile)

    base, ext = os.path.splitext(filename)

    outputfile = '%s/%s.pkl' % (dir, base)

    output = open(outputfile, 'wb')

    cPickle.dump(massdist, output)

    output.close()

    masscat = ldac.LDACCat(pyfits.new_table(pyfits.ColDefs([pyfits.Column(name = 'masses',
                                                                          format = 'E',
                                                                          array = masses)])))

    masscat.saveas('%s2' % resultfile, clobber=True)



###############

if __name__ == '__main__':

    resultdir = sys.argv[1]

    resultfiles = glob.glob('%s/*.out' % resultdir)

    for resultfile in resultfiles:

        preprocessFile(resultfile)
