###################
# Plots asked for by Anja for her Mar 2012 ESO proposal
###################

import publication_plots as pp
import cPickle
from readtxtfile import readtxtfile
import pylab, numpy as np
import nfwutils, compare_masses as cm
import maxlike_secure_bentstep3_voigt_driver as driver


###################

def precisionZ(data = None):
    #mass precision as a function of redshift

    if data is None:
        data = {}

    if 'fracerrs' not in data:

        items = [tuple(x) for x in readtxtfile('worklist')]


        allmasses = cm.readDougMasses('/u/ki/dapple/subaru/doug/publication/baseline_2012-05-17')

        redshifts = cm.readClusterRedshifts()

        clusters = [x[0] for x in items]

        properz = np.array([redshifts[x] for x in clusters])

        masses, errs = cm.constructMassArray(allmasses, items)


        fracerrs = errs / masses

        aveerrs = np.mean(fracerrs, axis=0)

        data['aveerrs'] = aveerrs
        data['properz'] = properz

        ccitems = [tuple(x) for x in readtxtfile('referenceset')]
        
        ccmasses = cm.readAnjaMasses()
        clusters = [x[0] for x in ccitems]
        ccproperz = np.array([redshifts[x] for x in clusters])
        data['ccproperz'] = ccproperz
        
        masses, errs = cm.constructMassArray(ccmasses, ccitems)
        
        fracerrs = errs/masses
        
        ccaveerrs = np.mean(fracerrs, axis=0)

        data['ccaveerrs'] = ccaveerrs
                   

    else:

        aveerrs = data['aveaerrs']
        properz = data['properz']
        
        ccaveerrs = data['ccaveerrs']
        ccproperz = data['ccproperz']

    
    fig = pylab.figure()
    ax = fig.add_axes([0.12, 0.12, 0.95-0.12, 0.95-0.12])
    ax.plot(ccproperz, ccaveerrs, 'bo', label = 'Color-Cut', mfc = 'None', mew = 1.0, mec='b')
    ax.plot(properz, aveerrs, 'rD', label = 'P($z$)')
    ax.set_xlabel('Cluster Redshift')
    ax.set_ylabel('Fractional Statistical Uncertainty M(r$<$1.5Mpc)')
    ax.set_xlim([0.14, 0.72])
    ax.legend(loc='upper left', numpoints = 1)

    fig.savefig('publication/aveerr_redshift.eps')
    

    return fig, data

    
##########################


def galdensity(data = None):

    if data is None:
        data = {}

    
    if 'ngals' not in data:

        

        ngals = cPickle.load(open('galaxy_counts_pzmethod.pkl', 'rb'))
        data['ngals'] = ngals
        


        items = [tuple(x) for x in readtxtfile('worklist')]
        clusters = [x[0] for x in items]

        redshifts = cm.readClusterRedshifts()
        properz = np.array([redshifts[x] for x in clusters])
        data['properz'] = properz

        Dl = np.array([nfwutils.angulardist(z) for z in properz])
        data['Dl'] = Dl

        inner_rad = np.arctan2(0.75, Dl) * (180./np.pi) * 60
        outer_rad = np.arctan2(3., Dl) * (180 / np.pi) * 60
        area = np.pi*(outer_rad**2 - inner_rad**2)
        data['area'] = area

        propercounts = np.array([ngals[x] for x in items])
        
        density = propercounts / area
        data['density'] = density

    else:

        properz = data['properz']
        density = data['density']
    

    fig = pylab.figure()
    ax = fig.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])
    ax.plot(properz, density, 'bo')
    ax.set_xlabel('Cluster Redshift')
    ax.set_ylabel('Input Galaxy Density')

    return fig, data


######################################


def lostgals(data = None):

    if data is None:

        data = {}

    items = readtxtfile('worklist')
    del items[-1]
    clusters = [x[0] for x in items]


    if 'properz' not in data:




        redshifts = cm.readClusterRedshifts()
        properz = np.array([redshifts[x] for x in clusters])
        data['properz'] = properz
    else:
        properz = data['properz']

    if 'properbase' not in data:

        basecuts = {}
        for cluster, filter, image in items:

            controller = driver.makeController()

            options, args = controller.modelbuilder.createOptions()
            options, args = controller.filehandler.createOptions(options = options, args = args,
                                                     workdir = '/u/ki/dapple/ki06/catalog_backup_2012-02-08',
                                                     incatalog = '/u/ki/dapple/ki06/catalog_backup_2012-02-08/%s.%s.%s.lensingbase.cat' % (cluster, filter, image),
                                                     cluster = cluster, filter = filter, image = image,
                                                     redseqcat = '/u/ki/dapple/ki06/catalog_backup_2012-02-08/%s.%s.%s.redsequence.cat' % (cluster, filter, image), shapecut = True)

            controller.load(options, args)

            basecuts[cluster] = controller.ngalaxies
        data['basecuts'] = basecuts
        properbase = np.array([basecuts[x[0]] for x in items])
        data['properbase'] = properbase

    else:

        properbase = data['properbase']

    if 'properloose' not in data:

        loosecuts = {}
        for cluster, filter, image in items:

            controller = driver.makeController()

            options, args = controller.modelbuilder.createOptions(deltaz95high = 9999, zbhigh = 9999)
            options, args = controller.filehandler.createOptions(options = options, args = args,
                                                     workdir = '/u/ki/dapple/ki06/catalog_backup_2012-02-08',
                                                     incatalog = '/u/ki/dapple/ki06/catalog_backup_2012-02-08/%s.%s.%s.lensingbase.cat' % (cluster, filter, image),
                                                     cluster = cluster, filter = filter, image = image,
                                                     redseqcat = '/u/ki/dapple/ki06/catalog_backup_2012-02-08/%s.%s.%s.redsequence.cat' % (cluster, filter, image), shapecut = True)

            controller.load(options, args)

            loosecuts[cluster] = controller.ngalaxies
        data['loosecuts'] = loosecuts
        properloose = np.array([loosecuts[x[0]] for x in items])
        data['properloose'] = properloose

    else:
        
        properloose = data['properloose']

    if 'ratio' not in data:

        ratio = 1 - (properbase.astype('float64') / properloose)
        data['ratio'] = ratio

    else:

        ratio = data['ratio']

    fig = pylab.figure()
    ax = fig.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])
    ax.plot(properz, ratio, 'bo')
    ax.set_xlim([0.16, 0.72])

    ax.set_xlabel('Cluster Redshift')
    ax.set_ylabel('Fraction of Catalog Discarded')

    return fig, data
        
        
        
######################################

