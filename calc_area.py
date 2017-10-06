#!/usr/bin/env python

import astropy.io.fits as pyfits, numpy, os, sys
subarudir = '/nfs/slac/g/ki/ki05/anja/SUBARU'

cluster = sys.argv[1]
filter = sys.argv[2]

min = 0
max = 5000
bins = 20
dr = float(max-min)/bins


flags = pyfits.open('%(subaru)s/%(cluster)s/%(filter)s/SCIENCE/coadd_%(cluster)s_good/coadd.flag.masked.fits' % {'subaru' : subarudir, 'cluster' : cluster, 'filter' : filter})[0].data

areafile = open('%(subaru)s/%(cluster)s/%(filter)s/SCIENCE/coadd_%(cluster)s_good/area.dat' % {'subaru' : subarudir, 'cluster' : cluster, 'filter' : filter}, 'w')

xsize = flags.shape[1]
ysize = flags.shape[0]


radii = numpy.arange(min, max, dr)


X,Y = numpy.meshgrid(xrange(flags.shape[1]), xrange(flags.shape[0]))
dist = numpy.sqrt( (X-5000)**2 + (Y-5000)**2 )
countPix = []
for center in radii:
    inArea = numpy.logical_and(numpy.logical_and(dist >= center - dr/2, 
                                                 dist < center + dr/2),
                               flags == 0)
    numPix = len(dist[inArea])
    countPix.append(numPix)

countPix = numpy.array(countPix)
#area = .04*countPix/3600  #square arcminutes
#radii = .2*radii/60 #arcminutes


areafile.write('# min max bins (pixels)\n')
areafile.write('# %d %d %d\n' % (min, max, bins))
areafile.write('# radius(pix) area(square pixels)\n')

for r, area in zip(radii, countPix):
    areafile.write('%d %d\n' % (r, area))

areafile.close()
