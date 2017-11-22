#!/usr/bin/env python
#######################
# Plots for shearratio flat universe approx
#######################

import sys, cPickle, subprocess, os
import pylab, numpy as np
import shearratio as sr, nfwutils
import maxlike_secure_bentstep3_voigt_driver as driver
from readtxtfile import readtxtfile

#######################

def plotOneCluster(cluster, filter, image, workdir = '/u/ki/dapple/ki06/catalog_backup_2012-02-08', 
                   outdir = '/u/ki/dapple/subaru/doug/publication/baseline_2012-02-08', data = None):

    if data is None:
        data = {}

    if 'controller' not in data:

        controller = driver.makeController()
        options, args = controller.modelbuilder.createOptions(zcut = None)
        options, args = controller.filehandler.createOptions(options = options, args = args, 
                                                         workdir = workdir, 
                                                         incatalog = '%s/%s.%s.%s.lensingbase.cat' % (workdir, cluster, filter, image),
                                                         cluster = cluster, filter = filter, image = image,
                                                         shapecut = True, 
                                                         redseqcat = '%s/%s.%s.%s.redsequence.cat' % (workdir, cluster, filter, image))

        controller.load(options, args)

        data['controller'] = controller

    else:

        controller = data['controller']

    if 'rs' not in data:

        stats = cPickle.load(open('%s/%s.%s.%s.out.mass15mpc.mass.summary.pkl' % (outdir, cluster, filter, image)))
        mass = stats['quantiles'][50]

        rs = nfwutils.RsMassInsideR(mass, 4.0, controller.zcluster, 1.5)

        data['rs'] = rs
        
    else:

        rs = data['rs']

    if 'median' not in data:

        scaledZ, estimators = sr.scaleShear(controller, rs, 4.0)

        bins = np.unique(np.hstack([np.linspace(0., 1., 3.), np.linspace(1., np.max(scaledZ), 5.)]))

        scaledZbins, weights, aveEst = sr.calcZBinWeights(scaledZ, controller.pdz, estimators, bins)

    
        median, sig1, sig2 = sr.calcBinDistro(scaledZbins, weights, aveEst)

        data['bins'] = bins
        data['median'] = median
        data['sig1'] = sig1
        data['sig2'] = sig2

    else:

        bins = data['bins']
        median = data['median']
        sig1 = data['sig1']
        sig2 = data['sig2']

        
    
    fig = pylab.figure()
    ax = fig.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])

    bincenters = (bins[1:] + bins[:-1])/2.
    
    ax.errorbar(bincenters, median, sig2, fmt='bo')
    ax.errorbar(bincenters, median, sig1, fmt='ro')

    xplot = np.arange(0., np.max(bins), 0.01)
    ax.plot(xplot, sr.shearScaling(xplot), 'k-', linewidth=1.5)

    ax.set_xlabel('Scaled Redshift')
    ax.set_ylabel('Lensing Power')
    ax.set_title('%s %s %s' % (cluster, filter, image))
    fig.savefig('notes/shearratio/%s.%s.%s.pdf' % (cluster, filter, image))

    return fig, data


########################


def stackClusters(data = None, doPlot = True, cosmology = nfwutils.std_cosmology):

    workdir = '/u/ki/dapple/ki06/catalog_backup_2012-02-08'
    outdir = '/u/ki/dapple/subaru/doug/publication/baseline_2012-02-08'

    if data is None:
        data = {}

    if 'items' not in data:
        data['items'] =  readtxtfile('worklist')
    items = data['items']

    if 'zbins' not in data:
        data['zbins'] = np.unique(np.hstack([np.linspace(0., 1., 3.), np.linspace(1., 5., 10.), np.linspace(5., 10., 5.)]))
    zbins = data['zbins']
    bincenters = (zbins[1:] + zbins[:-1])/2.

    if 'clusters' not in data:
        clusters = {}
        for cluster, filter, image in items:
            key = (cluster, filter, image)
            clusters[key] = {}
            controller = driver.makeController()
            options, args = controller.modelbuilder.createOptions()
            options, args = controller.filehandler.createOptions(options = options, args = args, 
                             workdir = workdir, 
                             incatalog = '%s/%s.%s.%s.lensingbase.cat' % (workdir, cluster, filter, image),
                             cluster = cluster, filter = filter, image = image,
                             shapecut = True, 
                             redseqcat = '%s/%s.%s.%s.redsequence.cat' % (workdir, cluster, filter, image))

            controller.load(options, args)

            stats = cPickle.load(open('%s/%s.%s.%s.out.mass15mpc.mass.summary.pkl' % (outdir, cluster, filter, image)))
            mass = stats['quantiles'][50]

            rs = nfwutils.RsMassInsideR(mass, 4.0, controller.zcluster, 1.5)
            
            scaledZ, estimators = sr.scaleShear(controller, rs, 4.0, cosmology = cosmology)

            bins, weights, aveshear = sr.calcZBinWeights(scaledZ, controller.pdz, estimators, zbins)

            clusters[key]['weights'] = weights
            clusters[key]['shears'] = aveshear

        data['clusters'] = clusters

    else:
        clusters = data['clusters']

    
    if 'median' not in data:
        allweights = np.vstack([clusters[tuple(item)]['weights'] for item in items])
        allshears = np.vstack([clusters[tuple(item)]['shears'] for item in items])

        median, sig1, sig2 = sr.calcBinDistro(zbins, allweights, allshears)

        data['median'] = median
        data['sig1'] = sig1
        data['sig2'] = sig2

    else:
        
        median = data['median']
        sig1 = data['sig1']
        sig2 = data['sig2']

    
    if doPlot:

        fig = pylab.figure()
        ax = fig.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])

        ax.errorbar(bincenters, median, sig2, fmt='bo')
        ax.errorbar(bincenters, median, sig1, fmt='ro')

        xplot = np.arange(0., np.max(zbins), 0.01)
        ax.plot(xplot, sr.shearScaling(xplot), 'k-', linewidth=1.5)

        ax.set_xlabel('Scaled Redshift')
        ax.set_ylabel('Lensing Power')
        ax.set_title('All Cluster Stack -- Restricted to Fit Data')
        fig.savefig('notes/shearratio/stack_restricted_manypoints.pdf')

        return fig, data

    return data


    
####################################################

def calcBootstrapCovar(bootstrap):

    sourcedir = '/u/ki/dapple/ki06/catalog_backup_2012-02-08'
    bootdir = '/u/ki/dapple/ki06/bootstrap_2012-02-08'


    data = {}

    if 'items' not in data:
        data['items'] =  readtxtfile('worklist')
    items = data['items']

    if 'zbins' not in data:
        data['zbins'] = np.unique(np.hstack([np.linspace(0., 1., 3.), np.linspace(1., 5., 10.), np.linspace(5., 10., 5.)]))
    zbins = data['zbins']
    bincenters = (zbins[1:] + zbins[:-1])/2.

    if 'clusters' not in data:
        clusters = {}
        for cluster, filter, image in items:
            key = (cluster, filter, image)
            clusters[key] = {}

            clusterdir='%s/%s' % (bootdir, cluster)

            i = bootstrap

            controller = driver.makeController()
            options, args = controller.modelbuilder.createOptions()
            options, args = controller.filehandler.createOptions(options = options, args = args, 
                                                                 workdir = sourcedir, 
                         incatalog = '%s/bootstrap_%d.ml.cat' % (clusterdir, i),
                         cluster = cluster, filter = filter, image = image)

            controller.load(options, args)

            stats = cPickle.load(open('%s/bootstrap_%d.ml.out.mass15mpc.mass.summary.pkl' % (clusterdir, i)))
            mass = stats['quantiles'][50]

            rs = nfwutils.RsMassInsideR(mass, 4.0, controller.zcluster, 1.5)

            scaledZ, estimators = sr.scaleShear(controller, rs, 4.0)

            bins, weights, aveshear = sr.calcZBinWeights(scaledZ, controller.pdz, estimators, zbins)

            clusters[key]['weights'] = weights
            clusters[key]['shears'] = aveshear



        data['clusters'] = clusters

    else:
        clusters = data['clusters']

    
    if 'medians' not in data:

        clusterboot = np.random.randint(0, len(items), len(items))
        
        allweights = np.vstack([clusters[tuple(items[j])]['weights'] for j in clusterboot])
        allshears =  np.vstack([clusters[tuple(items[j])]['shears']  for j in clusterboot])

        median, sig1, sig2 = sr.calcBinDistro(zbins, allweights, allshears)

        data['median'] = median
        data['sig1'] = sig1
        data['sig2'] = sig2


    return data

################################

def launchScan():

    omega_l = np.arange(0.6, 0.85, 0.02)

    if not os.path.exists('shearratio_cosmoscan'):
        os.mkdir('shearratio_cosmoscan')

    for ol in omega_l:
        subprocess.check_call('bsub -q xlong ./shearratio_plots_scan.py %4.3f shearratio_cosmoscan' % ol, shell=True)

################################

def loadScan():

    omega_l = np.arange(0.6, 0.85, 0.02)

    if not os.path.exists('shearratio_cosmoscan'):
        os.mkdir('shearratio_cosmoscan')

    entries = []

    for ol in omega_l:
        input = open('shearratio_cosmoscan/scan_%4.3f.pkl' % ol, 'rb')
        data = cPickle.load(input)
        input.close()
        entries.append((data['zbins'], data['median']))

    return omega_l, entries

###############################

def calcProbs(entries, covar):

    invcovar = np.linalg.inv(covar)

    probs = np.zeros(len(entries))

    for i, (zbins, median) in enumerate(entries):
        mask = median == 0.
        bincenters = (zbins[:-1] + zbins[1:])/2.
        expected = sr.shearScaling(bincenters)
        delta = median - expected
        delta[mask] = 0.
        probs[i] = np.exp(-0.5*np.dot(delta, np.dot(invcovar, delta)))

    probs = probs/np.sum(probs)

    return probs
    

################################

def launchBootstraps():

    bootstraps = np.arange(30, 230)

    if not os.path.exists('shearratio_bootstraps'):
        os.mkdir('shearratio_bootstraps')

    for boot in bootstraps:
        subprocess.check_call('bsub -q xlong ./shearratio_plots.py %d shearratio_bootstraps' % boot, shell=True)

################################

def loadBootstraps():

    #warning, there will be some 0. bins; ignoring for now, not sure what to do with them
    bootstraps = np.arange(30, 230)

    medians = []

    for i in bootstraps:
        try:
            data = cPickle.load(open('shearratio_bootstraps/scan_%d.pkl' % i, 'rb'))
            medians.append(data['median'])
        except IOError:
            continue


    mean_ghat, covar = sr.calcCovariance(medians)

    return mean_ghat, covar

#################################


if __name__ == '__main__':

#    bootstrap = int(sys.argv[1])
#    outdir = sys.argv[2]
#    
#    data = calcBootstrapCovar(bootstrap)
#
#    output = open('%s/scan_%d.pkl' % (outdir, bootstrap), 'wb')
#    cPickle.dump(data, output)
#    output.close()
#

    omega_l = float(sys.argv[1])
    outdir = sys.argv[2]

    cosmology = nfwutils.Cosmology(1-omega_l, omega_l)

    data = stackClusters(doPlot = False, cosmology = cosmology)

    output = open('%s/scan_%4.3f.pkl' % (outdir, omega_l), 'wb')
    cPickle.dump(data, output)
    output.close()
    
