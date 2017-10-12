# simple Python script to paste LDAC MEF catalogues.
# The job is done by a few pyfits calls
#
# The script takes one command line argument.
# It is a textfile containing catalogues to be converted
# from the output FITS-LDAC SExtractor format to a
# MEF format which is used by scamp.

# HISTORY INFORMATION:
#
# 23.02.2009:
# complete rewrite of the script to treat multiple images at the same
# time. This makes it much more efficient for a large number of images
# as the Python interpreter only has to be loaded once!

import astropy.io.fits as pyfits
import sys

def PrintUsage():
  """Just print the scripts usage message"""

  print "SCRIPT NAME:"
  print "    scampcat.py - merge single frame THELI files to a scamp MEF catalogue"
  print ""
  print "SYNOPSIS:"
  print "    python scampcat.py filelist"
  print ""
  print "DESCRIPTION:"
  print "    The script transforms single frame SExtractor FITS-LDAC catalogues"
  print "    from the THELI pipeline to a Multi-Extension-Fitsfile format which"
  print "    is suitable for the 'scamp' program. The conversion is necessary if"
  print "    single-frame THELI catalogues from a multi-chip camera need to be"
  print "    run through that program. The input catalogues have to"
  print "    be in the FITS-LDAC format which is directly output by SExtractor,"
  print "    NOT the format after the 'ldacconv' program has been used!  "
  print ""
  print "    The filelist argument is an ASCII file containing, on each line,"
  print "    the catalogues to be merged to the last catalogue name in the"
  print "    corresponding line, e.g.:"
  print ""
  print "    If the filelist contains the two lines:"
  print ""
  print "    781_single.cat 782_single.cat 78_mef.cat"
  print "    581_single.cat 582_single.cat 583_single.cat 58_mef.cat"
  print ""
  print "    catalogues 781_single.cat and 782_single.cat would be merged"
  print "    into 78_mef.cat and catalogues 581_single.cat 582_single.cat "
  print "    and 583_single.cat into 58_mef.cat."
  print "    "
  print "REMARK:"
  print "    The script is for Python 2.x!"
  print "    "
  print "AUTHOR:"
  print "    Thomas Erben         (terben@astro.uni-bonn.de)"
  print ""
  print ""

  return
  
# Here the script work starts:

# sanity check for command line arguments:
if (len(sys.argv) != 2):
  PrintUsage()
  sys.exit(1)

try:
  catalog_file = open(sys.argv[1], "r")
except IOError:
  print "Error: cannot open file:", sys.argv[1]
  sys.exit(1)

for line in catalog_file:
  hdu     = pyfits.PrimaryHDU()
  hdulist = pyfits.HDUList([hdu])

  cats = line.split()

  print "creating", cats[len(cats) - 1]

  hdulisttable = []
  
  for i in range(0, len(cats) - 1):
    # we fill the individual files into a list
    # so that we can close them later. It seems that
    # pyfits needs the files until writing the hdulist!
    try:
      hdulisttable.append(pyfits.open(cats[i]))
    except IOError:
      print "Error: cannot open file:", cats[i]
      sys.exit(1)
      
    hdulist.append(hdulisttable[i][1])
    hdulist.append(hdulisttable[i][2])

  print "writing", cats[len(cats) - 1], "to disk"
  hdulist.writeto(cats[len(cats) - 1])

  # close files
  hdulist.close()

  for i in range(0, len(cats) - 1):
    hdulisttable[0].close()
    
catalog_file.close()

