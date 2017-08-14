#!/usr/bin/env python

import ldac, dappleutils, sys, os, pyfits

filteredIDs = dappleutils.readtxtfile(sys.argv[1])

filteredIDcat = ldac.LDACCat(pyfits.new_table(pyfits.ColDefs([pyfits.Column(name='SeqNr', format='J', array=filteredIDs[:,0])])))

fullCat = ldac.openObjectFile(sys.argv[2])

filteredCat = dappleutils.matchById(filteredIDcat, fullCat)

base, ext = os.path.splitext(sys.argv[2])

outputname = '%s.filtered%s' % (base, ext)

filteredCat.saveas(outputname, clobber=True)


