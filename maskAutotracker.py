#!/usr/bin/env python
#########################
# @file maskAutotracker.py
# @author Douglas Applegate
# @date 3/11/08
#
# @brief Given a list of files, region files will be appended to exclude
#      the autotracker.
# List of images to mask should be in maindir/autotracker_mask
#########################

import sys, regionfile, os

import BonnLogger
__bonn_logger_id__ = BonnLogger.addCommand('maskAutotracker.py', 
                                           sys.argv[1:])


#########################

__cvs__id__ = "$Id: maskAutotracker.py,v 1.3 2008-07-09 01:22:15 dapple Exp $"

#########################

usage =   \
'''maskAutotracker.py path/to/date_filter dir
     eg maskAutotracker.py /path/to/2003-09-25_W-J-V SCIENCE
'''

#########################

if len(sys.argv) != 3:
    print usage
    BonnLogger.updateStatus(__bonn_logger_id__, 1)
    sys.exit(1)

maindir = sys.argv[1]
dir = sys.argv[2]

maskListFilename = '%s/autotracker_mask' % maindir
regDir = '%s/%s/reg' % (maindir, dir)

autotrackerMask = regionfile.Polygon([-1,3650,2010,3650,2010,4081,-1,4081])

if not os.path.exists(maskListFilename):
    print 'Nothing to do.'
    BonnLogger.updateStatus(__bonn_logger_id__, 0)
    sys.exit(0)

input = open(maskListFilename)
for image in input:
    image = image.strip()
    regFilename = '%s/%s.reg' % (regDir, image)
    
    regionfile.writeRegionFile(regFilename, [autotrackerMask])

input.close()

BonnLogger.updateStatus(__bonn_logger_id__, 0)

    
