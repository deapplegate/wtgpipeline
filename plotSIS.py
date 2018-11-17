#!/usr/bin/env python

#import matplotlib
#matplotlib.use('PS')
#from matplotlib import pylab
import pylab


from math import pi
import pylab
import sys, os
import ldac, numpy
import shearprofile as sp
import shearprofileplots as spp


cluster = sys.argv[1]

back_bins = 2

emode = True
if len(sys.argv) > 2:
    if sys.argv[2] == 'b' or 'B':
        emode = False

subarudir = "/nfs/slac/g/ki/ki05/anja/SUBARU"

back_catfile = "%(subaru)s/%(cluster)s/LENSING/%(cluster)s_fbg.filtered.cat" % { 'subaru' : subarudir,
                                                                  'cluster' : cluster }

redshift = os.popen("grep %s %s/clusters.redshifts | awk '{print $2}'" % (cluster, subarudir)).read()
redshift = float(redshift.strip())

sigma_v = os.popen("cat %(subaru)s/%(cluster)s/LENSING/%(cluster)s_fbg_sisfit.ml.dat | awk '{print $2}'" % { 'subaru' : subarudir, 'cluster' : cluster }).read()
sigma_v = float(sigma_v.strip())
print sigma_v

X = pi/(3600*180)  #convert arcseconds to radians

back_cat = ldac.openObjectFile(back_catfile)

minZ = min(back_cat['Z_BEST'])
maxZ = max(back_cat['Z_BEST'])

zstep = float(maxZ - minZ)/back_bins

for curbin in xrange(back_bins):

    z_low = minZ + curbin*zstep
    z_high = z_low + zstep

    inBin = numpy.logical_and(back_cat['Z_BEST'] >= z_low, back_cat['Z_BEST'] < z_high)

    curGals = back_cat.filter(inBin)

    r, E , B, phi = sp.calcTangentialShear(curGals, (5000,5000), .2)
    beta=sp.beta(curGals["Z_BEST"],redshift, calcAverage = False)
    kappacut = sp.calcWLViolationCut(r, beta, sigma_v = 1300)
    curGals = curGals.filter(kappacut)

    aprofile = sp.easyprofile(curGals, (1,3000), bins=8, center=(5000,5000), logbin = False)

    pylab.subplot(back_bins,1,curbin+1)

    if emode:

        spp.plotprofile((0,3000), aprofile.r, aprofile.E, aprofile.Eerr)

        aveBeta = sp.beta(curGals['Z_BEST'], redshift)
        aveBeta2 = sp.beta2(curGals['Z_BEST'], redshift)

        coords = numpy.zeros((len(aprofile.r), 2))
        coords[:,0] = sp.pix2arcsec(aprofile.r)*X
        coords[:,1] = aveBeta

        g = sp.SIS_ML(coords, sigma_v**2, stepcor = 1.082)

        pylab.plot(.2*aprofile.r, g, 'r-')

        pylab.axis([.2,3000*.2,-.1, .25])

        
    else:
        spp.plotprofile((0,3000), aprofile.r, aprofile.B, aprofile.Berr)
        pylab.axis([.2, 3000*.2, -.1, .1])

    pylab.text(2000, .15, '%3.2f - %3.2f' % (z_low, z_high))
    pylab.xlabel('')
    pylab.ylabel('')


pylab.xlabel('r (arcseconds)')
if emode:
    pylab.ylabel('g_t')
else:
    pylab.ylabel('g_x')

pylab.show()
if emode:
    pylab.savefig('%s.emode.profile.ps' % cluster)
else:
    pylab.savefig('%s.bmode.profile.ps' % cluster)


    

