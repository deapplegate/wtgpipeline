#!/usr/bin/env python

import ldac, dappleutils, sys, os, astropy, astropy.io.fits as pyfits

filteredIDs = dappleutils.readtxtfile(sys.argv[1])

filteredIDcat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([pyfits.Column(name='SeqNr', format='J', array=filteredIDs[:,0])])))

fullCat = ldac.openObjectFile(sys.argv[2])

filteredCat = dappleutils.matchById(filteredIDcat, fullCat)

base, ext = os.path.splitext(sys.argv[2])

outputname = '%s.filtered%s' % (base, ext)

filteredCat.saveas(outputname, overwrite=True)


