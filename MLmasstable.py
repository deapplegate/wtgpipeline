#!/usr/bin/env python
########################
# 
# Output a latex format table (not including headers, just body)
#  compiling best fit information for each cluster
#
########################

import numpy as np, pymc
import compare_masses as cm
import nfwutils, shearprofile as sp


########################

class MLCluster(object):

    def __init__(self, cluster, redshift, db, burn):

        self.cluster = cluster
        self.redshift = redshift
        self.db = db
        self.burn = burn

    #######

    def getVar(self, var, *args, **kwds):

        return sp.ConfidenceRegion(self.db.trace(var, -1)[self.burn:], *args, **kwds)

    #######

    def getRs(self):

        return self.getVar('r_scale')

    #######

    def getConcentration(self):

        return self.getVar('concentration')

    #######

    def getMass(self):

        return self.getVar('mass_15mpc', useMedian = True)

    #######

    @classmethod
    def load(cls, cluster, filter, image, redshift, workdir = '/u/ki/dapple/subaru/doug/publication/baseline_2011-12-14'):

        return cls(cluster, redshift, pymc.database.pickle.load('%s/%s.%s.%s.out' % (workdir, cluster, filter, image)), 10000)


###########################


def getRs(clusterz, mass, errs):

    median_rs = nfwutils.RsMassInsideR(mass, 4.0, clusterz, 1.5)
    low_rs = nfwutils.RsMassInsideR(mass - errs[0], 4.0, clusterz, 1.5)
    high_rs = nfwutils.RsMassInsideR(mass + errs[1], 4.0, clusterz, 1.5)

    return median_rs, np.array([median_rs - low_rs, high_rs - median_rs])


#############################################

def normalStrInterval(bounds, fmt = '%2.2f', norm=1.):

    template = '$%s^{+%s}_{-%s}$' % (fmt, fmt, fmt)

    mid, (dn, up) = bounds

    return template % (mid/norm, up/norm, dn/norm)

#####

def redactedStrInterval(bounds, fmt = '%2.2f', norm=1.):

    template = '$%s^{+%s}_{-%s}$' % ('%s', fmt, fmt)

    mid, (dn, up) = bounds

    return template % ('X', up/norm, dn/norm)

############################################

def readNameTranslation():

    translation = {}

    with open('/u/ki/dapple/subaru/SUBARU.list') as input:
        for line in input.readlines():
            tokens = line.split()
            translation[tokens[0]] = tokens[1]

    with open('/u/ki/anja/MACS/macs_othernames') as input:
        for line in input.readlines():
            tokens = line.split()
            translation[tokens[0]] = tokens[1]

    return translation

#############################################

def readFilterTranslation():

    return { 'W-J-V' : '{\it V}$_{\rm J}$',
             'W-C-RC' : '{\it R}$_{\rm C}$',
             'W-C-IC' : '{\it I}$_{\rm C}$',
             'W-S-I+' : '{\it i}$^{+}$',
             'g' : '{\it g}$^{\star}$',
             'r' : '{\it r}$^{\star}$'}

        
#############################################

def table(items, mlsrcdir, output, strInterval = normalStrInterval):

    MLmasses = cm.readDougMasses(dir = mlsrcdir)
    CCmasses = cm.readAnjaMasses()

    nametranslation = readNameTranslation()

    filtertranslation = readFilterTranslation()

    redshifts = cm.readClusterRedshifts()

    cordist = np.hstack([pymc.database.pickle.load('ml_cc_rlog.out.%d' % i).trace('m', -1)[25000:] \
                             for i in range(1, 6)])

    sortlist = sorted([(redshifts[x[0]], x) for x in items])
    print sortlist

    for clusterz, (cluster, filter, image) in sortlist:

        if (cluster, filter, image) not in CCmasses:
            print 'Skipping %s %s %s' % (cluster, filter, image)
            continue



        try:
            MLcluster = MLCluster.load(cluster, filter, image, clusterz)

            values = {'cluster' : nametranslation[cluster],
                      'redshift' : clusterz,
                      'filter' : filtertranslation[filter],
                      'rs' : strInterval(MLcluster.getRs()),
                      'con' : strInterval(MLcluster.getConcentration()),
                      'mlmass' : strInterval(MLmasses[cluster, filter, image], fmt='%2.1f', norm = 1e14),
                      'ccrs' : strInterval(getRs(clusterz, *CCmasses[(cluster, filter, image)])),
                      'ccmass' : strInterval(CCmasses[(cluster, filter, image)], fmt='%2.1f', norm = 1e14)}


#                      'cccor' : strInterval(CCcluster.getCorMass(cordist), fmt='%2.1f', norm = 1e14)}

#                      'mlmass' : strInterval(MLcluster.getMass(), fmt = '%2.1f', norm = 1e14),
#                      'ccmass' : strInterval(CCcluster.getMass(), fmt = '%2.1f', norm = 1e14),




        except (KeyError, IOError):

            values = {'cluster' : nametranslation[cluster],
                      'redshift' : clusterz,
                      'filter' : filtertranslation[filter],
                      'rs' : '-',
                      'con' : '-', 
                      'mlmass' : '-',
                      'ccrs' : strInterval(getRs(clusterz, *CCmasses[(cluster, filter, image)])),
                      'ccmass' : strInterval(CCmasses[(cluster, filter, image)], fmt='%2.1f', norm = 1e14)}





#                                  'cccor' : strInterval(CCcluster.getCorMass(cordist), fmt='%2.1f', norm = 1e14)}
#        output.write('%(cluster)s & %(redshift)1.2f & %(rs)s & %(con)s & %(mlmass)s  & %(ccrs)s & %(ccmass)s & %(cccor)s \\\\ \n' % values)
        output.write('%(cluster)s & %(redshift)1.3f &  %(rs)s & %(mlmass)s & %(ccrs)s & %(ccmass)s \\\\ \n' % values)
    
                                                 
