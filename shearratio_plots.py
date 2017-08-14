#!/usr/bin/env python
#######################
# Plots for shearratio flat universe approx
#######################

import sys, cPickle, subprocess, os
import pylab, numpy as np
import shearratio as sr, nfwutils
import maxlike_secure_bentstep3_voigt_driver as driver
from dappleutils import readtxtfile

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

    
        median, sig1, sig2, maxlike_ests = sr.bootstrapBinDistro(scaledZbins, weights, aveEst)

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

    xplot = np.arange(0.01, np.max(bins), 0.01)
    ax.plot(xplot, sr.shearScaling(xplot), 'k-', linewidth=1.5)

    ax.set_xlabel('Scaled Redshift')
    ax.set_ylabel('Lensing Power')
    ax.set_title('%s %s %s' % (cluster, filter, image))
    fig.savefig('notes/shearratio/%s.%s.%s.pdf' % (cluster, filter, image))

    return fig, data


########################


def stackClusters(data = None, cosmology = nfwutils.std_cosmology, outdir = '/u/ki/dapple/subaru/doug/publication/baseline_2012-05-17'):

    workdir = '/u/ki/dapple/ki06/catalog_backup_2012-05-17'

    if data is None:
        data = {}

    if 'items' not in data:
        data['items'] =  readtxtfile('worklist')
    items = data['items']


    if 'clusters' not in data:
        clusters = {}
        for cluster, filter, image in items:
            key = (cluster, filter, image)
            clusters[key] = {}
            controller = driver.makeController()
            options, args = controller.modelbuilder.createOptions(zcut= None)
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

            clusters[key]['scaledZ'] = scaledZ
            clusters[key]['estimators'] = estimators
            clusters[key]['pdz'] = controller.pdz

        data['clusters'] = clusters

    else:
        clusters = data['clusters']



    maxScaledZ = -1
    for key in clusters.keys():
        localMax = np.max(clusters[key]['scaledZ'])
        maxScaledZ = max(localMax, maxScaledZ)


    if 'zbins' not in data:
        zbins = np.unique(np.hstack([np.linspace(0., 1., 3.), np.logspace(0.1, np.log10(maxScaledZ), 12.)]))
        data['zbins'] = np.hstack([zbins[:-3], zbins[-1]])
    zbins = data['zbins']
    bincenters = (zbins[1:] + zbins[:-1])/2.

    for key in clusters.keys():

        bins, weights, aveshear = sr.calcZBinWeights(clusters[key]['scaledZ'], clusters[key]['estimators'], zbins)

        clusters[key]['weights'] = weights
        clusters[key]['shears'] = aveshear


    
    if 'maxlike' not in data:
        allweights = np.vstack([clusters[tuple(item)]['weights'] for item in items])
        allshears = np.vstack([clusters[tuple(item)]['shears'] for item in items])



        pointest = sr.calcBinDistro(zbins, allweights, allshears)


        data['pointest'] = pointest


        maxlike, sig1, sig2, maxlike_ests = sr.bootstrapBinDistro(zbins, allweights, allshears)

        data['maxlike'] = maxlike
        data['sig1'] = sig1
        data['sig2'] = sig2
        data['maxlike_ests'] = maxlike_ests

    else:
        
        maxlike = data['maxlike']
        sig1 = data['sig1']
        sig2 = data['sig2']
        


    fig = pylab.figure()
    ax = fig.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])

    ax.errorbar(bincenters, maxlike, sig2, fmt='bo')
    ax.errorbar(bincenters, maxlike, sig1, fmt='ro')

    xplot = np.arange(0.01, np.max(zbins), 0.01)
    ax.plot(xplot, sr.shearScaling(xplot), 'k-', linewidth=1.5)

    ax.set_xlabel('$x = \omega_s/\omega_l$')
    ax.set_ylabel('$\gamma(z)/\gamma(\infty)$')
    ax.set_title('All Cluster Stack -- Maxlike Point Est')
    fig.savefig('notes/shearratio/stack_maxlike.pdf')

    return fig, data

#################################
#
#def stackClustersEDS(data = None):
#
#    workdir = '/u/ki/dapple/ki06/catalog_backup_2012-02-08'
#    outdir = '/u/ki/dapple/subaru/doug/publication/baseline_2012-02-08'
#
#
#
#    if data is None:
#        data = {}
#
#    if 'items' not in data:
#        data['items'] =  readtxtfile('worklist')
#    items = data['items']
#
#    if 'zbins' not in data:
#        data['zbins'] = np.unique(np.hstack([np.linspace(0., 1., 3.), np.linspace(1., 6., 20.)]))
#    zbins = data['zbins']
#    bincenters = (zbins[1:] + zbins[:-1])/2.
#
#    if 'clusters' not in data:
#        clusters = {}
#        for cluster, filter, image in items:
#            key = (cluster, filter, image)
#            clusters[key] = {}
#            controller = driver.makeController()
#            options, args = controller.modelbuilder.createOptions()
#            options, args = controller.filehandler.createOptions(options = options, args = args, 
#                             workdir = workdir, 
#                             incatalog = '%s/%s.%s.%s.lensingbase.cat' % (workdir, cluster, filter, image),
#                             cluster = cluster, filter = filter, image = image,
#                             shapecut = True, 
#                             redseqcat = '%s/%s.%s.%s.redsequence.cat' % (workdir, cluster, filter, image))
#
#            controller.load(options, args)
#
#            stats = cPickle.load(open('%s/%s.%s.%s.out.mass15mpc.mass.summary.pkl' % (outdir, cluster, filter, image)))
#            mass = stats['quantiles'][50]
#
#            rs = nfwutils.RsMassInsideR(mass, 4.0, controller.zcluster, 1.5)
#            
#            scaledZ, estimators = sr.scaleShear(controller, rs, 4.0, cosmology = cosmology)
#
#            bins, weights, aveshear = sr.calcZBinWeights(scaledZ, controller.pdz, estimators, zbins)
#
#            clusters[key]['weights'] = weights
#            clusters[key]['shears'] = aveshear
#
#        data['clusters'] = clusters
#
#    else:
#        clusters = data['clusters']
#
#    
#    if 'maxlike' not in data:
#        allweights = np.vstack([clusters[tuple(item)]['weights'] for item in items])
#        allshears = np.vstack([clusters[tuple(item)]['shears'] for item in items])
#
#
#        pointest = sr.calcBinDistro(zbins, allweights, allshears)
#
#
#        data['pointest'] = pointest
#
#
#        maxlike, sig1, sig2, maxlike_ests = sr.bootstrapBinDistro(zbins, allweights, allshears)
#
#        data['maxlike'] = maxlike
#        data['sig1'] = sig1
#        data['sig2'] = sig2
#        data['maxlike_ests'] = maxlike_ests
#
#    else:
#        
#        maxlike = data['maxlike']
#        sig1 = data['sig1']
#        sig2 = data['sig2']
#        
#
#
#    fig = pylab.figure()
#    ax = fig.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])
#
#    ax.errorbar(bincenters, maxlike, sig2, fmt='bo')
#    ax.errorbar(bincenters, maxlike, sig1, fmt='ro')
#
#    xplot = np.arange(0.01, np.max(zbins), 0.01)
#    ax.plot(xplot, sr.shearScaling(xplot), 'k-', linewidth=1.5)
#
#    ax.set_xlabel('Scaled Redshift')
#    ax.set_ylabel('Lensing Power')
#    ax.set_title('All Cluster Stack -- EdS Cosmology')
#    fig.savefig('notes/shearratio/stack_restricted_eds.pdf')
#
#    return fig, data
#
#
#######################################################



#######################################################

def publicationStack(data = None):

    if data is None:
        data = {}

    if 'standard' not in data:
        stddata = {}
        stdfig, stddata = stackClusters(data = stddata)
        data['standard'] = stddata
    else:
        stddata = data['standard']
    
    if 'eds' not in data:
        edsdata = {}
        edsfig, edsdata = stackClusters(data = edsdata, cosmology = nfwutils.Cosmology(omega_m = 1.0, omega_l = 0.0), outdir = '/u/ki/dapple/subaru/doug/publication/eds_cosmos_2012-05-17')
        data['eds'] = edsdata
    else:
        edsdata = data['eds']

    stdzbins = stddata['zbins']
    stdbincenters = (stdzbins[1:] + stdzbins[:-1])/2.

    edszbins = edsdata['zbins']
    edsbincenters = (edszbins[1:] + edszbins[:-1])/2.

    

        
    stdmaxlike = stddata['maxlike']
    stdsig1 = stddata['sig1']
    stdsig2 = stddata['sig2']

    edsmaxlike = edsdata['maxlike']
    edssig1 = edsdata['sig1']
    edssig2 = edsdata['sig2']

    
    
    fig = pylab.figure()
    ax = fig.add_axes([0.125, 0.12, 0.95 - 0.125, 0.95 - 0.12])

    xplot = np.arange(0.01, np.max(np.hstack([stdzbins, edszbins])), 0.01)

    ax.axhline(0.0, linestyle=':', linewidth=1.25, color='k')
    ax.plot(xplot, sr.shearScaling(xplot), 'k-', linewidth=1.5, label='Expected Scaling')


    ax.errorbar(edsbincenters, edsmaxlike, edssig1, fmt='rs', mfc = 'None',label='$\mathbf{\Omega_{\Lambda} = 0.0}$', elinewidth=1.5,
                markeredgewidth=1.5, markeredgecolor='r', marker='None')
    ax.plot(edsbincenters, edsmaxlike, 'rs', markerfacecolor='None', markeredgecolor='r', markeredgewidth=1.5)

    ax.errorbar(stdbincenters, stdmaxlike, stdsig1, fmt='bo', label='$\mathbf{\Omega_{\Lambda} = 0.7}$', elinewidth=1.5, markeredgewidth=1.5,
                markeredgecolor='b', marker='None')
    ax.plot(stdbincenters, stdmaxlike, 'bo')


    thexrange = (0., 5.0)
    theyrange = (-0.15, 1.75)

    ax.legend(loc='upper left', numpoints=1)

    ax.set_xlabel('$x = \omega_s/\omega_l$', size='x-large')
    ax.set_ylabel('$\gamma_t(x)/\gamma_t(x=\infty)$', size='x-large')

    fig.savefig('publication/pubstack.pdf')

    ######

    fig2 = pylab.figure()

    ax = fig2.add_axes([0.125, 0.12, 0.95 - 0.125, 0.95 - 0.12])

    ax.axhline(0.0, linestyle=':', linewidth=1.25, color='k')
    ax.plot(xplot, sr.shearScaling(xplot), 'k-', linewidth=1.5, label='Expected Scaling')

    ax.errorbar(stdbincenters, stdmaxlike, stdsig1, fmt='bo', label='$\mathbf{\Omega_{\Lambda} = 0.7}$', elinewidth=1.5, markeredgewidth=1.5,
                markeredgecolor='b', marker='None')
    ax.plot(stdbincenters, stdmaxlike, 'bo')

    ax.set_xlim(*thexrange)
    ax.set_ylim(*theyrange)

    ax.text(0.3, 1.5, '$\mathbf{\Omega_{\Lambda} = 0.7}$', size='xx-large', weight='bold')

    ax.set_xlabel('$x = \omega_s/\omega_l$ ', size='x-large')
    ax.set_ylabel('$\gamma_t(x)/\gamma_t(x=\infty)$', size='x-large')



    fig2.savefig('publication/pubstack_lcdm.pdf')


    ###################


    fig3 = pylab.figure()

    ax = fig3.add_axes([0.125, 0.12, 0.95 - 0.125, 0.95 - 0.12])

    ax.axhline(0.0, linestyle=':', linewidth=1.25, color='k')
    ax.plot(xplot, sr.shearScaling(xplot), 'k-', linewidth=1.5, label='Expected Scaling')

    ax.errorbar(edsbincenters, edsmaxlike, edssig1, fmt='bo', label='$\mathbf{\Omega_{\Lambda} = 0.0}$', elinewidth=1.5, markeredgewidth=1.5,
                markeredgecolor='b', marker='None')
    ax.plot(edsbincenters, edsmaxlike, 'bo')

    ax.set_xlim(*thexrange)
    ax.set_ylim(*theyrange)

    ax.text(0.3, 1.5, '$\mathbf{\Omega_{\Lambda} = 0.0}$', size='xx-large', weight='bold')


    ax.set_xlabel('$x = \omega_s/\omega_l$', size='x-large')
    ax.set_ylabel('$\gamma_t(x)/\gamma_t(x=\infty)$', size='x-large')



    fig3.savefig('publication/pubstack_eds.pdf')


    return fig, fig2, fig3, data


    
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
        subprocess.check_call('bsub -q xlong ./shearratio_plots.py %4.3f shearratio_cosmoscan' % ol, shell=True)

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
        data = cPickle.load(open('shearratio_bootstraps/scan_%d.pkl' % i, 'rb'))
        medians.append(data['median'])

    mean_ghat, covar = sr.calcCovariance(medians)

    return mean_ghat, covar

#################################


if __name__ == '__main__':

    bootstrap = int(sys.argv[1])
    outdir = sys.argv[2]
    
    data = calcBootstrapCovar(bootstrap)

    output = open('%s/scan_%d.pkl' % (outdir, bootstrap), 'wb')
    cPickle.dump(data, output)
    output.close()

    
