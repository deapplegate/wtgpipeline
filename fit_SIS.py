#! /usr/bin/env python

import ldac
from numpy import *
import shearprofile as sp
import sys
import os, subprocess

import pylab


if len(sys.argv) != 6:
    sys.stderr.write("wrong number of arguments!\n")
    sys.exit(1)
catfile= sys.argv[1]
clusterz=float(sys.argv[2])
center=  map(float,sys.argv[3].split(','))
pixscale=float(sys.argv[4]) # arcsec / pix
clustername=sys.argv[5]


catalog= ldac.openObjectFile(catfile)

r, E = sp.calcTangentialShear(catalog, center, pixscale)

beta=sp.beta(catalog["Z_BEST"],clusterz, calcAverage = False)

kappacut = sp.calcWLViolationCut(r, beta, sigma_v = 1300)
radiuscut = r > 60  #arcseconds
largeradiuscut = r < 500
zcut = logical_and(catalog['Z_BEST'] > 1.2*clusterz, catalog['Z_BEST'] < 1.2)


cleancut = logical_and(kappacut, logical_and(radiuscut, logical_and(largeradiuscut,zcut)))

cleancat = catalog.filter(cleancut)

samples =  sp.simpleBootstrap(cleancat, clusterz, pixscale, center, beta[cleancut])


r500x = float(subprocess.Popen("grep %s /nfs/slac/g/ki/ki05/anja/SUBARU/clusters.r500x.dat | awk '{print $2}'" % clustername, stdout=subprocess.PIPE, shell=True).communicate()[0])

mass = lambda sigma2,r500x: 2*sigma2*r500x/4.3e-09

masses = [ mass(sigma2, r500x) for sigma2 in samples]

confidenceRegion = sp.ConfidenceRegion(masses)

filebase,ext=os.path.splitext(catfile)

#output = open(filebase+"_profile.dat", 'w')
#for i in xrange(len(r_as)):
#    output.write("%f  %f  %f  %f  %f\n" % (r_as[i], E[i], Err[i], B[i], Berr[i]))
#output.close()

#veldisp = sqrt( confidenceRegion[0][0] * 4.3e-09 / (3*r500x) )
#veldisperr = (veldisp / 2) * ((confidenceRegion[1][0]+confidenceRegion[2][0])/confidenceRegion[0][0])
#

output = open(filebase+"_sisfit.ml.dat", 'w')

samples = array(samples)
samples[samples < 0] = 0.


veldispersions = sqrt(samples)


veldisp_confidenceregion = sp.ConfidenceRegion(veldispersions[veldispersions > 0])

output = open(filebase+"_sisfit.sigma.dat", 'w')



output.write("M500: %e -%e %e\n" % (confidenceRegion[0][0], confidenceRegion[1][0], confidenceRegion[2][0]))
output.write("sigma: %e  -%e %e\n" % (veldisp_confidenceregion[0][0], veldisp_confidenceregion[1][0], veldisp_confidenceregion[2][0]))
output.close()

#sys.stderr.write("sigma: %e  -%e %e\n" % (veldisp_confidenceregion[0][0], veldisp_confidenceregion[1][0], veldisp_confidenceregion[2][0]))
#
#pylab.hist(veldispersions[veldispersions > 0], bins=50)
#pylab.show()
#
print '%s %e -%e %e' % (clustername, confidenceRegion[0][0], confidenceRegion[1][0], confidenceRegion[2][0])


