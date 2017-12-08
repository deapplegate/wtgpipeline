#!/usr/bin/env python
#####################

import os, cPickle, sys, glob
import astropy, astropy.io.fits as pyfits
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

    masscat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([pyfits.Column(name = 'masses',
                                                                          format = 'E',
                                                                          array = masses)])))

    masscat.saveas('%s2' % resultfile, overwrite=True)



###############

if __name__ == '__main__':
    import adam_quicktools_ArgCleaner                                                                                                                                                                                                       
    argv=adam_quicktools_ArgCleaner.ArgCleaner(sys.argv)
    resultdir1 = argv[0]
    resultdir2 = argv[1]

    resultfiles = glob.glob('%s/*/%s/*.out' % (resultdir1,resultdir2,))

    for resultfile in resultfiles:

        preprocessFile(resultfile)
