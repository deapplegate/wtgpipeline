#!/usr/bin/env python

import pylab, numpy, sys
import plot_GalDensity as gd
import shearprofile as sp


cluster = sys.argv[1]
filter = sys.argv[2]

dR, area, z, zlow, zhigh = gd.prepData(cluster, filter)
zcluster = gd.clusterZ(cluster)

def fitrange(r, zcluster):

    if zcluster > .5:
        return numpy.logical_and(r >= 8.3, r < 12)

    if .4 < zcluster < .5: 
        return numpy.logical_and(r > 9.5, r < 14)
    return numpy.logical_and(r > 12, r < 14)


background3 = dR[numpy.logical_and(z >= 1.3*zcluster, z < 1)]
background4 = dR[numpy.logical_and(z >= 1, z < 2)]
#background5 = dR[numpy.logical_and(z >= 1.5, z < 2)]
backgrounds = [background3, background4]
labels=['1.3 *%3.2f < z < 1' % zcluster, ' 1 < z < 2']

for background, label in zip(backgrounds, labels):

    

    r, density = gd.calcDensity(background, area)

    baserange = fitrange(r, zcluster)
    baseline = numpy.sum(density[baserange]*area[:-1,1][baserange])/numpy.sum(area[:-1,1][baserange])
    contamination = (density - baseline)/density

    densities = [density]
    contaminations = [contamination]
    nelements=len(background)

    for i in xrange(1000):
        asample = numpy.random.randint(0,nelements,nelements)
        r, density = gd.calcDensity(background[asample], area)
        
        baseline = numpy.sum(density[baserange]*area[:-1,1][baserange])/numpy.sum(area[:-1,1][baserange])
        contamination = (density - baseline)/density

        densities.append(density)
        contaminations.append(contamination)

    densities = numpy.array(densities)
    contaminations = numpy.array(contaminations)

    

    aveContam = []
    contamErr = [[],[]]

    for i in xrange(len(r)):
        confidence = sp.ConfidenceRegion(contaminations[:,i])
        aveContam.append(float(confidence[0][0]))
        contamErr[0].append(float(confidence[1][0]))
        contamErr[1].append(float(confidence[2][0]))


    pylab.errorbar(r, numpy.array(aveContam), numpy.array(contamErr), label=label)


pylab.axhline(0, c='k')
pylab.axis([0,16,-.1,1.1])
pylab.legend()
pylab.xlabel('radius (arcmin)')
pylab.ylabel('Fraction Cluster Contamination')
pylab.title(cluster)
#pylab.show()
pylab.savefig('%s.contamination.maglimit.deltaz.png' % cluster)


