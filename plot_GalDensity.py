#!/usr/bin/env python

import pyfits, numpy, ldac, pylab, sys, os
import dappleutils as du
import shearprofile as sp

subarudir = '/nfs/slac/g/ki/ki05/anja/SUBARU'

def calcDensity(dR, area, z=None):    
    
    counts, radii = numpy.histogram(dR, bins=area[:,0])
    
    dr = radii[1] - radii[0]
                        
    density = 3600*(counts / area[:-1,1])/0.04

    return 0.2*(area[:-1,0] + .5*(area[1,0] - area[0,0]))/60, density


def bootstrapDensity(dR, area, z=None):

    r, density = calcDensity(dR, area)

    densities = [density]

    nelements=len(dR)

    for i in xrange(1000):
        asample = numpy.random.randint(0,nelements,nelements)
        r, density = calcDensity(dR[asample], area)
        densities.append(density)

    densities = numpy.array(densities)

    aveDensity = []
    densityErr = [[],[]]

    for i in xrange(len(r)):
        confidence = sp.ConfidenceRegion(densities[:,i])
        aveDensity.append(float(confidence[0][0]))
        densityErr[0].append(float(confidence[1][0]))
        densityErr[1].append(float(confidence[2][0]))

    return r, numpy.array(aveDensity), numpy.array(densityErr)

def zstrata(dR, area, z, zlow, zhigh, zcluster):

    sigma = z - zlow
    cluster_dist = z - zcluster
    nsigma = cluster_dist / sigma

#    background1 = dR[numpy.logical_and(z >= 1.1*zcluster, z < 1.3*zcluster)]
#    background2 = dR[numpy.logical_and(z >= 1.3*zcluster, z < 1.5*zcluster)]
    background3 = dR[numpy.logical_and(z >= 1.3*zcluster, z < 1)]
    background4 = dR[numpy.logical_and(z >= 1, z < 2)]
#    background5 = dR[numpy.logical_and(z >= 1.5, z < 2)]
    background6 = dR[numpy.logical_and(z >= 2, z < 3)]
#    background7 = dR[z >= 3]

    densities = {}


#    densities['1: %3.2f < z < %3.2f' % (1.1*zcluster, 1.3*zcluster)] = bootstrapDensity(background1, area)
#    densities['2: %3.2f < z < %3.2f' % (1.3*zcluster, 1.5*zcluster)] = bootstrapDensity(background2, area)
    densities['3: %3.2f < z < 1' % (1.3*zcluster)] = bootstrapDensity(background3, area)
    densities['4: 1 < z < 2'] = bootstrapDensity(background4, area)
#    densities['5: 1.5 < z < 2'] = bootstrapDensity(background5, area)
#    densities['6: 2 < z < 3'] = bootstrapDensity(background6, area)
#    densities['7: 3 < z'] = bootstrapDensity(background7, area)

    return densities

def sigmastrata(dR, area, z, zlow, zhigh, zcluster):

    sigma = z - zlow
    cluster_dist = z - zcluster
    nsigma = cluster_dist / sigma

#    background1 = dR[numpy.logical_and(nsigma >= 1, nsigma < 2)]
#    background2 = dR[numpy.logical_and(nsigma >= 2, nsigma < 3)]
#    background3 = dR[numpy.logical_and(nsigma >= 3, nsigma < 4)]
#    background4 = dR[nsigma >= 4]

    background1 = dR[nsigma >= 1]
    background2 = dR[nsigma >= 2]
    background3 = dR[nsigma >= 3]
    background4 = dR[nsigma >= 4]

    densities = {}


    densities['1 - 2 sigma'] = bootstrapDensity(background1, area)
    densities['2 - 3 sigma'] = bootstrapDensity(background2, area)
    densities['3 - 4 sigma'] = bootstrapDensity(background3, area)
    densities['4 < sigma'] = bootstrapDensity(background4, area)


    return densities

    

def prepData(cluster, filter):

    cat = ldac.openObjectFile('%s/%s/LENSING/%s_fbg.filtered.cat' % (subarudir, cluster, cluster))

    cat = cat.filter(numpy.logical_and(numpy.logical_and(cat['BPZ_Z_B_MAX-MIN_Z'] < 0.8,
                                                         cat['BPZ_ODDS'] > 0.95),
                                       cat['MAG_AUTO'] < 23.85))

#    cat = cat.filter(numpy.logical_and(cat['BPZ_Z_B_MAX-MIN_Z'] < 0.8,
#                                       cat['BPZ_ODDS'] > 0.95))

    coords = numpy.column_stack([cat['Xpos'], cat['Ypos']])
    dX = coords - numpy.array([5000,5000])
    dR = numpy.sqrt(dX[:,0]**2 + dX[:,1]**2)

    
    area = du.readtxtfile('%s/%s/%s/SCIENCE/coadd_%s_good/area.dat' % (subarudir, cluster, filter, cluster))
    
    return dR, area, cat['Z_BEST'], cat['BPZ_Z_B_MIN'], cat['BPZ_Z_B_MAX'], cat['MAG_AUTO']


def clusterZ(cluster):

    redshift = os.popen("grep %s %s/clusters.redshifts | awk '{print $2}'" % (cluster, subarudir)).read()
    redshift = float(redshift.strip())

    return redshift
    



if __name__ == '__main__':

    import pylab

    cluster = sys.argv[1]
    filter = sys.argv[2]
    if len(sys.argv) > 3:
        print 'Using sigma strata'
        strataname = 'sigmastrata'
        strata = sigmastrata
    else:
        strataname = 'zstrata'
        strata = zstrata

    dR, area, z, zlow, zhigh, mag = prepData(cluster, filter)

    totalArea = .04*numpy.sum(area/3600)

#    pylab.hist(mag, bins=24, range=(20,28))
#    pylab.xlabel('mag_auto (zeropoint arbitrary)')
#    pylab.title(cluster)
#    pylab.savefig('%s.magauto.png' % cluster)
#    pylab.clf()


    pylab.hist(z, bins=40, range=(0,4))
    pylab.xlabel('z (photometric)')
    pylab.title(cluster)
    pylab.savefig('%s.zdist.maglimit.png' % cluster)
    pylab.clf()

    clusterz = clusterZ(cluster)

    dR_lensing = dR[z > 1.3*clusterz]

    print '%s Average Density: %f' % (cluster, len(dR_lensing) / totalArea)

    densities = strata(dR, area, z, zlow, zhigh, clusterz)

    keys = densities.keys()

    keys.sort()

    r = None
    for key in keys:
        density = densities[key]
        pylab.errorbar(density[0], density[1], density[2], label=key)
        r = density[0]

    pylab.legend()
    pylab.xlabel('radius (arcmin)')
    pylab.ylabel('density (per sqr arcmin)')
    pylab.title(cluster)

    pylab.savefig('%s.galdensity.%s.maglimit.png' % (cluster, strataname))

    pylab.clf()

    pylab.hist(0.2*dR/60, bins=r)
    pylab.xlabel('r (arcmin)')
    pylab.title(cluster)
    pylab.savefig('%s.numcounts.maglimit.png' % cluster)
    pylab.clf()

    

#    for key in keys:
#        density = densities[key]
#        baseline = numpy.average(density[1][numpy.logical_and(density[0] >= 10, density[0] <= 14)])
#        contamination = (density[1] - baseline)/density[1]
#        pylab.plot(density[0], contamination, label=key)
#
#    pylab.axhline(0, c='k')
#    pylab.axis([0,16,-.1,1.1])
#    pylab.legend()
#    pylab.xlabel('radius (arcmin)')
#    pylab.ylabel('Fraction Cluster Contamination')
#    pylab.title(cluster)
#
#    pylab.savefig('%s.contamination.maglimit.png' % cluster)
