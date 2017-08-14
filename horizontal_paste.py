#!/usr/bin/env python

import sys, pyfits, re
from optparse import OptionParser
from numpy import *

########################

__cvs_id__ = "$Id: horizontal_paste.py,v 1.2 2009-01-28 20:05:28 dapple Exp $"

########################

parser = OptionParser(usage='horizontal_paste.py file1 file2 ...',
                      description='Pastes together a set of files, in order, horizontally. The header from the first file is used as the final header. All images must have the same vertical length.')

parser.add_option('-o', '--outfile', dest='out',
                  default=None,
                  help='Name of file to write to. Defaults to appending .combined.fits to the first filename')

options, images = parser.parse_args()

if len(images) == 0:
    parser.print_help()
    sys.exit(1)

if len(images) == 1:
    parser.error("Only one image. Nothing to do!")

if options.out is None:
    match = re.match('(.+)\.fits$', images[0])
    if match is None:
        outfile = '%s.combined.fits' % images[0]
    else:
        outfile = '%s.combined.fits' % match.group(1)
else:
    outfile = options.out

############################################

primaryImageName = images[0]
primaryImageFile = pyfits.open(primaryImageName)
primaryImage = primaryImageFile[0]
primaryImageHeader = primaryImageFile[0].header

final_xsize = primaryImage.header['NAXIS1']
final_ysize = primaryImage.header['NAXIS2']

for image in images[1:]:
    
    xsize = pyfits.getval(image, 'NAXIS1')
    ysize = pyfits.getval(image, 'NAXIS2')

    if ysize != final_ysize:
        raise AssertionError, "Vertical Dimension for %s does not match!" % image

    final_xsize += xsize

####################################################

final_image = zeros((final_ysize, final_xsize),dtype=float32);

cur_x = 0
end_x = primaryImage.header['NAXIS1']
final_image[:,cur_x:end_x] = primaryImage.data
cur_x = end_x

primaryImageFile.close()

for image in images[1:]:

    data = pyfits.getdata(image)
    end_x += data.shape[1]

    assert end_x <= final_xsize, \
        "Violation of image size constraints: %s" % image

    final_image[:,cur_x:end_x] = data
    cur_x = end_x

finalHeader = primaryImageHeader
finalHeader['NAXIS1'] = final_xsize
finalHDU = pyfits.PrimaryHDU(data = final_image, header = finalHeader)
finalHDU.writeto(outfile, output_verify='ignore', clobber=True)
