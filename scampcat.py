# simple Python script to paste LDAC MEF catalogues.
# The job is done by a few pyfits calls
#
# Given N commandline arguments, the script merges
# the N-1 FITS catalogues and write the result to
# a catalog with the name of the Nth argument.

import astropy.io.fits as pyfits
import sys

hdu     = pyfits.PrimaryHDU()
hdulist = pyfits.HDUList([hdu])

for i in range(1, len(sys.argv)-1):
  hdulisttable = pyfits.open(sys.argv[i])
  hdulist.append(hdulisttable[1])
  hdulist.append(hdulisttable[2])

hdulist.writeto(sys.argv[len(sys.argv)-1])
