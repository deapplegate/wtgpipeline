#!/usr/bin/env python

from __future__ import with_statement
import sys, re, pyfits
from numpy import *

masterlistname = sys.argv[1]
images = sys.argv[2:]

objects = []
with open(masterlistname) as input:
    for line in input.readlines():
        if re.match('#', line):
            continue
        x = filter(lambda x: x != '', [x.strip() for x in line.split()])
        objects.append([float(x[0]), float(x[1]), float(x[2]), x[3], float(x[4]), float(x[5]), float(x[6])])

masterlist = rec.fromrecords(objects, names='x,y,mag,shape,rh,ratio,angle',
            formats='float64,float64,float64,|S8,float64,float64,float64')


for image in images:

    match = re.match('(.+?)\.fits', image)
    if match is None:
        print "Skipping %s" % image
        continue

    base = match.group(1)

    header = pyfits.getheader(image)
    
    xsize = header['NAXIS1']
    ysize = header['NAXIS2']
    
    coaddcenter_frame = array([header['CRPIX1'], header['CRPIX2']])
    coaddcenter_coadd = array([6000,6000])
    objs_coadd = array([masterlist.x, masterlist.y]).transpose()

    objs_frame = objs_coadd - coaddcenter_coadd + coaddcenter_frame

    inframe = logical_and(logical_and(objs_frame[:,0] > 0, 
                                      objs_frame[:,0] < xsize),
                          logical_and(objs_frame[:,1] > 0, 
                                      objs_frame[:,1] < ysize))
    
    



    with open('%s.gallist' % base, 'w') as framelist:
        for pos, other in zip(objs_frame[inframe], masterlist[inframe]):
            framelist.write('\t%s  %s\n' % ('  '.join(map(str, pos)),
                                          '  '.join(map(str, other.tolist()[2:]))))

        



