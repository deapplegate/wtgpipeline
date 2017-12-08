####################
# compare Anja's masses against mine
#####################

from __future__ import with_statement
import glob, cPickle, os, re
import numpy as np, pymc, nfwutils
import pylab, ldac, shearprofile as sp
from readtxtfile import readtxtfile
import intrinsicscatter_grid as isg
import intrinsicscatter_grid_plots as isgp
#import fitmodel as fm

#########################

def readAnjaMasses(dir = '/u/ki/dapple/subaru/doug/publication/ccmass_2012-07-31'):

    outputdata = glob.glob('%s/*out' % dir)

    masses = {}

    for data in outputdata:

        basename = os.path.basename(data)
        cluster, filter, image, out = basename.split('.')

        with open(data) as input:

            mass = None
            errlow = None
            errhigh = None

            for line in input.readlines():
                if re.match('bootstrap median mass:', line):
                    mass = float(line.split()[-1])
                if re.match('bootstrap 16th percentile:', line):
                    errlow = -float(line.split()[5][:-1])
                if re.match('bootstrap 84th percentile:', line):
                    errhigh = float(line.split()[5][:-1])

            assert(mass is not None and errlow is not None and errhigh is not None)
                    

        masses[(cluster, filter, image)] = (mass, [errlow, errhigh])

    return masses


def readCounts(file = '/u/ki/anja/ldaclensing/masses_1p5Mpc.list.lin'):

    #cluster filter coadd m500x m500xerr mlens mlens_err_up mlens_err_low

    counts = {}

    with open(file) as input:

        for line in input.readlines():
            tokens = line.split()
            cluster = tokens[0]
            filter = tokens[1]
            image = tokens[2]
            nobjs = int(tokens[6])

            counts[(cluster, filter, image)] = nobjs

    return counts



############################



def readDougMasses(dir = '/u/ki/dapple/nfs/pipeline/bonnpipeline/mlmasses', ext='mass15mpc.mass.summary.pkl', pick=1):

    masses = {}

    for inputfile in glob.glob('%s/*%s' % (dir, ext)):

        base=os.path.basename(inputfile)
        tokens = base.split('.')
        cluster = tokens[0]
        filter = tokens[1]
        image = tokens[2]

        input = open(inputfile, 'rb')
        stats = cPickle.load(input)

        try:
        
            if pick == 0:
                masses[(cluster, filter, image)] = stats['maxlike']
            elif pick == 1:
                #mass, (low, high) = stats['log10maxlike']
                #low = 10**mass - 10**(mass - low)
                #high = 10**(mass + high) - 10**mass
                #mass = 10**mass
                mass = stats['quantiles'][50]
                low =  mass - stats['quantiles'][15.8]
                high = stats['quantiles'][84.1] - mass
                
                masses[(cluster, filter, image)] = (mass, np.array([low, high]))

            elif pick == 2:

                mass = stats['quantiles'][50]
                low, high = stats['hpd68']
                
                masses[(cluster, filter, image)] = (mass, np.array([mass - low, high - mass]))


        except:

            pass

    return masses

################################

def readMLBootstraps(dir, items, bootrange, ext = 'mass15mpc.mass.summary.pkl'):

    masses = {}
    mask = {}

    for cluster in [x[0] for x in items]:

        workdir='%s/%s' % (dir, cluster)

        masses[cluster] = np.zeros(len(bootrange))
        mask[cluster] = np.ones(len(bootrange))

        for i, bootnum in enumerate(bootrange):
            inputfile = '%s/bootstrap_%d.ml.out.%s' % (workdir, bootnum, ext)

            if not os.path.exists(inputfile):
                mask[cluster][i] = 0
                masses[cluster][i] = -1
                continue
                

            stats = cPickle.load(open(inputfile, 'rb'))
            mass = stats['quantiles'][50]
            masses[cluster][i] = mass

    return masses, mask

##################################

def readMLBootstraps_diffR(dir, items, bootrange, diffR, cluster_zs):

    masses = {}
    mask = {}

    for cluster in [x[0] for x in items]:

        workdir='%s/%s' % (dir, cluster)

        masses[cluster] = np.zeros(len(bootrange))
        mask[cluster] = np.ones(len(bootrange))

        zcluster = cluster_zs[cluster]

        for i, bootnum in enumerate(bootrange):
            inputfile = '%s/bootstrap_%d.ml.out' % (workdir, bootnum)

            if not os.path.exists(inputfile):
                mask[cluster][i] = 0
                masses[cluster][i] = -1
                continue
                

            db = pymc.database.pickle.load(inputfile)
            sampled_masses = np.array([nfwutils.massInsideR(rs, c, zcluster, diffR) \
                                           for rs, c in zip(db.trace('r_scale')[3000::3], db.trace('concentration')[3000::3])])

            masses[cluster][i] = np.median(sampled_masses)

    return masses, mask

##################################


cc_regex = re.compile('^non-bootstrap mass')

def readCCSummary(dir, clusters, bootrange, ending = '.out'):

    masses = {}
    mask = {}
    
    for cluster in clusters:

        workdir='%s/%s' % (dir, cluster)

        masses[cluster] = np.zeros(len(bootrange))
        mask[cluster] = np.ones(len(bootrange))

        for i, bootnum in enumerate(bootrange):
            inputfile = '%s/bootstrap_%d.cc%s' % (workdir, bootnum, ending)

            if not os.path.exists(inputfile):
                print inputfile
                mask[cluster][i] = 0
                masses[cluster][i] = -1
                continue

            input = open(inputfile)
            for line in input.readlines():
                if cc_regex.match(line):
                    tokens = line.split()
                    mass = float(tokens[-1])
                    if mass == 0.:
                        mass = 1e13
                    masses[cluster][i] = mass
                    break
            input.close()
            


        print cluster, len(masses[cluster])
        
            

    return masses, mask


################################

def readCCSummary_diffR(dir, clusters, bootrange, diffR, cluster_zs, concentration = 4.):

    masses = {}
    mask = {}
    
    for cluster in clusters:

        workdir='%s/%s' % (dir, cluster)

        zcluster = cluster_zs[cluster]

        masses[cluster] = np.zeros(len(bootrange))
        mask[cluster] = np.ones(len(bootrange))

        for i, bootnum in enumerate(bootrange):
            inputfile = '%s/bootstrap_%d.cc.out' % (workdir, bootnum)

            if not os.path.exists(inputfile):
                print inputfile
                mask[cluster][i] = 0
                masses[cluster][i] = -1
                continue

            input = open(inputfile)
            for line in input.readlines():
                if cc_regex.match(line):
                    tokens = line.split()
                    mass = float(tokens[-1])
                    if mass == 0.:
                        mass = 1e13

                    rscale = nfwutils.RsMassInsideR(mass, concentration, zcluster, 1.5)
                    masses[cluster][i] = nfwutils.massInsideR(rscale, concentration, zcluster, diffR)
                    break
            input.close()
            


        print cluster, len(masses[cluster])
        
            

    return masses, mask


################################


def makePull(mass, errs, bootstraps, mask):

    aveSig = (errs[0] + errs[1])/2.
    pull = (bootstraps[mask == 1] - mass)/aveSig

    return pull

################################

def makeRatios(mlmasses, mlmasks, ccmasses, ccmasks):

    ratios = {}
    for cluster in mlmasses.keys():

        totalmask = np.logical_and(mlmasks[cluster] == 1, ccmasks[cluster] == 1)
        ratios[cluster] = (ccmasses[cluster] / mlmasses[cluster])[totalmask]

    return ratios

#####################################

def reduceSamples(mlmasses, mlmasks, ccmasses, ccmasks):

    reducedmlmasses = {}
    reducedccmasses = {}
    for cluster in mlmasses.keys():

        totalmask = np.logical_and(mlmasks[cluster] == 1, ccmasks[cluster] == 1)
        reducedmlmasses[cluster] = mlmasses[cluster][totalmask]
        reducedccmasses[cluster] = ccmasses[cluster][totalmask]


    return reducedmlmasses, reducedccmasses
    

#####################################

def bootstrapMedians(ratios, clusters):

    nclusters = len(clusters)

    medians = np.zeros(nclusters)
    errs = np.zeros((2, nclusters))

    for i, cluster in enumerate(clusters):

        cursample = np.sort(ratios[cluster])

        nsamples = len(cursample)

        medians[i] = np.median(cursample)
        errUp = cursample[int(0.84*nsamples)] - medians[i]
        errDown = medians[i] - cursample[int(0.16*nsamples)]
        errs[:,i] = errDown, errUp

    return medians, errs


####################################

def bootstrapMeans(ratios, clusters):

    nclusters = len(clusters)

    means = np.zeros(nclusters)
    errs = np.zeros(nclusters)

    for i, cluster in enumerate(clusters):

        cursample = ratios[cluster]

        nsamples = len(cursample)

        means[i] = np.mean(cursample)
        errs[i] = np.std(cursample)
                    

    return means, errs
            
#################################

def bootstrapSampleBias(mlmasses, mlmasks, ccmasses, ccmasks, clusters = None, ndraw = None):

    if clusters is None:
        clusters = np.array(mlmasses.keys())

    nclusters = len(clusters)
    if ndraw is None:
        ndraw = nclusters
    availableSamples = {}
    nAvailableSamples = {}
    for cluster in clusters:
        availableSamples[cluster] = np.arange(len(mlmasks[cluster]))[np.logical_and(mlmasks[cluster] == 1,
                                                                  ccmasks[cluster] == 1)]
        nAvailableSamples[cluster] = len(availableSamples[cluster])

    biases = np.zeros(10000)
    for counter in range(10000):
        curclusters = clusters[np.random.randint(0, nclusters, ndraw)]
        curpicks = np.array([availableSamples[cluster][np.random.randint(0, nAvailableSamples[cluster])] \
                              for cluster in curclusters])

        curMLpicks = np.array([mlmasses[curclusters[i]][curpicks[i]] for i in range(ndraw)])
        curCCpicks = np.array([ccmasses[curclusters[i]][curpicks[i]] for i in range(ndraw)])

        biases[counter] = np.mean(np.log(curCCpicks / curMLpicks))

    return biases
        

################################

#adam-tmp# def readClusterRedshifts(file = '/u/ki/dapple/subaru/clusters.redshifts'):
def readClusterRedshifts(file = 'clusters.redshifts'):

    redshifts = {}
    with open(file) as input:
        for line in input.readlines():
            cluster, z = line.split()
            redshifts[cluster] = float(z)

    return redshifts

###############################

def readClusterNFilter(cluster, filter):

    photcat = '/nfs/slac/g/ki/ki06/anja/SUBARU/photometry/%s/PHOTOMETRY_%s_aper/%s.slr.cat' % (cluster, filter, cluster)

    cat = ldac.openObjectFile(photcat)

    photkeys = [ key for key in cat.keys() if re.match('MAG_APER1-\w+?-COADD-.+', key)]

    return len(photkeys)

###############################

def readClusterCenters(file = '/nfs/slac/g/ki/ki05/anja/SUBARU/clusters.centers'):

    centers = {}
    with open(file) as input:
        for line in input.readlines():
            cluster, centerx, centery = line.split()
            centers[cluster] = np.array((float(centerx), float(centery)))

    return centers



################################

def buildWorklist(keys, worklist = 'referenceset'):

    with open(worklist) as input:
        toaccept = [ tuple(x.split()) for x in input.readlines() ]

    workkeys = []
    for key in keys:
        if key in toaccept:
            workkeys.append(key)

    return workkeys

###############################

def constructMassArray(aSet, worklist):

    masses = np.array([aSet[tuple(x)][0] for x in worklist]).T
    errs = np.array([aSet[tuple(x)][1] for x in worklist]).T

    if len(masses.shape) == 2:
        masses = masses[0,:]
        errs = errs[0,:,:]

    return masses, errs

###############################

def plotCentrals(loc1, loc2, format='bo'):
    
    set1 = readDougMasses(loc1)
    set2 = readDougMasses(loc2)
    
    worklist = buildWorklist(set1.keys())
    commonkeys = []
    for key in worklist:
        if key in set2:
            commonkeys.append(key)

    mass1, err1 = constructMassArray(set1, commonkeys)
    mass2, err2 = constructMassArray(set2, commonkeys)

    print mass1.shape, err1.shape
    print mass2.shape, err2.shape
    
    pylab.errorbar(mass1, mass2, err2, err1, fmt=format)


    
    return mass1, err1, mass2, err2, commonkeys


###############################

def publicationPlotMassMass(loc1, loc2, xlabel, ylabel, format = 'ko', 
                            independent = True,
                            worklist = 'referenceset'):

    if not isinstance(loc1, str):
        set1 = loc1
    else:
        set1 = readDougMasses(loc1)

    if not isinstance(loc2, str):
        set2 = loc2
    else:
        set2 = readDougMasses(loc2)
    
    worklist = buildWorklist(set1.keys(), worklist = worklist)
    commonkeys = []
    for key in worklist:
        if key in set2:
            commonkeys.append(key)

    mass1, err1 = constructMassArray(set1, commonkeys)
    mass2, err2 = constructMassArray(set2, commonkeys)



    print mass1.shape, err1.shape
    print mass2.shape, err2.shape

    
    fig = pylab.figure()
    xmarg = 0.12
    ymarg = 0.13

    ylim = 0.95
    xwidth = 0.95 - xmarg

    ax = pylab.axes([xmarg, ymarg, xwidth, ylim - ymarg])

    redshifts = readClusterRedshifts()
    redshifts = np.array([redshifts[x[0]] for x in commonkeys])

    nsamples = 50000

    xmasses = {}
    ymasses = {}

    if independent:
        ratio = []
        ratioerr = []
        for cluster, filter, image in commonkeys:

            masses1 = pymc.database.pickle.load('%s/%s.%s.%s.out' \
                  % (loc1, cluster, filter, image)).trace('mass_15mpc', 0)[3000:]
            masses2 = pymc.database.pickle.load('%s/%s.%s.%s.out' \
                  % (loc2, cluster, filter, image)).trace('mass_15mpc', 0)[3000:]

            xmasses[cluster] = masses1
            ymasses[cluster] = masses2

            bootstraps1 = np.random.randint(0, len(masses1), nsamples)
            bootstraps2 = np.random.randint(0, len(masses2), nsamples)

            ratios = np.sort(masses2[bootstraps2] / masses1[bootstraps1])

            median = ratios[int(nsamples/2)]
            ratio.append(median)
            errUp = ratios[int(0.84*nsamples)] - median
            errDown = median - ratios[int(0.16*nsamples)]
            ratioerr.append((errDown, errUp))


        ratio = np.hstack(ratio)
        ratioerr = np.array(ratioerr).T

        print ratio.shape, ratioerr.shape

        ax.errorbar(redshifts, ratio, ratioerr, fmt=format)

        minval = np.min(ratio - ratioerr[0,:])
        maxval = np.max(ratio + ratioerr[1,:])


    else:
        ratio = mass2 / mass1
        ax.plot(redshifts, ratio, format)

        minval = np.min(ratio)
        maxval = np.max(ratio)

    ax.axhline(1.0, c='k', linewidth=1.25)

    ax.set_yscale('log')
    
    ax.set_xlim(0.16, 0.72)
    ax.set_ylim(0.35, 4.5)
    
    ax.set_yticks([0.2, 0.4,  0.6,  0.8,  1.0, 2.0, 4.0, 6.0, 8.0])
    ax.set_yticklabels(['%2.1f' % x for x in [0.2, 0.4,  0.6,  0.8,  1.0, 2.0, 4.0, 6.0, 8.0]])
    
#    ax.set_yticks([1.25, 1.5, 1.75, 2.25, 2.5, 2.75, 3.25, 3.5, 3.75, 4.25, 4.5, 4.75], minor=True)
    
    ax.set_ylim(0.1, 10.)

    ax.set_xlabel('Cluster Redshift')
    ax.set_ylabel('%s / %s' % (ylabel, xlabel))


    return fig, xmasses, ymasses




###############################


def plotComparison(anjamasses, dougmasses, redshifts = readClusterRedshifts(), centers = readClusterCenters(), commonkeys = []):

    if commonkeys == []:
        commonkeys = []
        for key in dougmasses.keys():
            if key in anjamasses:
                commonkeys.append(key)

    #####################

    fig1 = pylab.figure()

    ax = fig1.add_subplot(1,1,1)

    anja_centrals = np.array([anjamasses[key][0] for key in commonkeys])
    anja_errs = np.array([anjamasses[key][1] for key in commonkeys]).T
    doug_centrals = np.array([dougmasses[key][0] for key in commonkeys])
    doug_errs = np.array([dougmasses[key][1] for key in commonkeys]).T

    ax.plot(anja_centrals, doug_centrals, 'bo')
    ax.plot([np.min(anja_centrals), np.max(anja_centrals)], [np.min(anja_centrals), np.max(anja_centrals)], 'r-')
    ax.set_xlabel('CC Mass')
    ax.set_ylabel('ML Mass')


    ###################

    ratio = doug_centrals / anja_centrals

    mean_ratio = np.mean(ratio)
    stddev_ratio = np.std(ratio)
    median_ratio = np.median(ratio)

    fig2 = pylab.figure()
    ax = fig2.add_subplot(1,1,1)
    ax.hist(doug_centrals / anja_centrals, bins=20)
    ax.text(1.4, 3.5, 'Mean: %1.2f' % mean_ratio)
    ax.text(1.4, 3.0, 'Std: %1.2f' % stddev_ratio)
    ax.text(1.4, 2.5, 'Median: %1.2f' % median_ratio)
    ax.set_xlabel('ML / CC')


    ####################

    fig3 = pylab.figure()
    ax = fig3.add_subplot(1,1,1)
    doug_errs = doug_errs - doug_centrals
    doug_errs[0,:] = -doug_errs[0,:]
    doug_frac = doug_errs / doug_centrals


    anja_errs = anja_errs - anja_centrals
    anja_errs[0,:] = -anja_errs[0,:]
    anja_frac = anja_errs / anja_centrals




    mass_sort = np.argsort(anja_centrals)

    nkeys = len(commonkeys)

    ax.axhline(1, c='k')
    ax.errorbar(np.arange(1, nkeys+1), np.ones(nkeys),  (anja_frac.T[mass_sort]).T, fmt='b,', label='CC')
    ax.errorbar(np.arange(1, nkeys+1), np.ones(nkeys),  (doug_frac.T[mass_sort]).T, fmt='r,', label='ML')
    ax.set_ylabel('Fractional Errors: CC(B), ML(R)')


    #################

    fig4 = pylab.figure()
    ax = fig4.add_subplot(2,1,1)

    present_redshifts = np.array([redshifts[key[0]] for key in commonkeys])

    ratio = doug_centrals / anja_centrals

    ax.plot(present_redshifts, ratio, 'bo')
    ax.axhline(1, c='k')
    ax.set_xlabel('Redshift')
    ax.set_ylabel('ML / CC Mass')

    fit = fm.FitModel(present_redshifts, ratio, 0.1*np.ones(len(present_redshifts)), fm.LinearModel)
    fit.fit()
    residuals = ratio - fm.LinearModel(present_redshifts, **fit.par_vals)

    redshiftrange=np.array([min(present_redshifts), max(present_redshifts)])
    ax.plot(redshiftrange, fm.LinearModel(redshiftrange, **fit.par_vals), 'r-')

    ax = fig4.add_subplot(2,1,2)
    ax.plot(present_redshifts, residuals, 'bo')
    ax.axhline(0, c='k')
    ax.text(redshiftrange[0]+0.05, 0.6, 'Mean: %1.2e' % np.mean(residuals))
    ax.text(redshiftrange[0]+0.05, 0.5, 'Median: %1.2e' % np.median(residuals))
    ax.text(redshiftrange[0]+0.05, 0.4, 'Std: %1.2f' % np.std(residuals))
    
    
    
    #####################

    fig5 = pylab.figure()
    ax = fig5.add_subplot(1,1,1)

    nfilters = np.array([readClusterNFilter(key[0], key[1]) for key in commonkeys])
    ax.plot(nfilters, doug_centrals / anja_centrals, 'bo')
    ax.axhline(1, c='k')
    ax.set_xlabel('NFilters')
    ax.set_ylabel('ML / CC Mass')


    ######################

#    fig6 = pylab.figure()
#    ax = fig6.add_subplot(1,1,1)
#    
#    present_centers = np.array([centers[key[0]] for key in commonkeys])
#    deltas = present_centers - np.array([5000,5000])
#    dR = np.sqrt(deltas[:,0]**2 + deltas[:,1]**2)
#    ax.plot(dR, doug_centrals / anja_centrals, 'bo')
#    ax.axhline(1, c='k')
#    ax.set_xlabel('ML Central Offset (Pix)')
#    ax.set_ylabel('ML / CC Mass')
#    

    

    return fig1, fig2, fig3, fig4, fig5
 

    
###############################################


def measureMLCcBootIS(sample = 'worklist', data = None, diffR = None):

    if data is None:
        data = {}

    if 'items' not in data:
        items = readtxtfile(sample)
        clusters = [x[0] for x in items]
        redshifts = readClusterRedshifts()
        properredshifts = np.array([redshifts[x] for x in clusters])
        
        data['items'] = items
        data['clusters'] = clusters
        data['redshifts'] = redshifts
        data['properredshifts'] = properredshifts
    else:
        items = data['items']
        clusters = data['clusters']
        redshifts = data['redshifts']
        properredshifts = data['properredshifts']

    if 'MLmasses' not in data or 'CCmasses' not in data:

        if diffR is None:

            if 'MLmasses' not in data:

                MLmasses, MLmask = readMLBootstraps('/u/ki/dapple/ki06/bootstrap_2012-05-17', items, np.arange(0, 200))
                data['MLmasses'] = MLmasses
                data['MLmask'] = MLmask
            else:
                MLmasses, MLmask = data['MLmasses'], data['MLmask']
                
            if 'CCmasses' not in data:
                CCmasses, CCmask = readCCSummary('/u/ki/dapple/ki06/bootstrap_2012-05-17', clusters, np.arange(0, 200))
                data['CCmasses'] = CCmasses
                data['CCmask'] = CCmask
            else:
                CCmasses, CCmask = data['CCmasses'], data['CCmask']

        else:

            print 'Using Alternative diffR'

            if 'MLmasses' not in data:

                MLmasses, MLmask = readMLBootstraps_diffR('/u/ki/dapple/ki06/bootstrap_2012-05-17', items, np.arange(0, 200), diffR, redshifts)
                data['MLmasses'] = MLmasses
                data['MLmask'] = MLmask
            else:
                MLmasses, MLmask = data['MLmasses'], data['MLmask']
                
            if 'CCmasses' not in data:
                CCmasses, CCmask = readCCSummary_diffR('/u/ki/dapple/ki06/bootstrap_2012-05-17', clusters, np.arange(0, 200), diffR, redshifts)
                data['CCmasses'] = CCmasses
                data['CCmask'] = CCmask
            else:
                CCmasses, CCmask = data['CCmasses'], data['CCmask']


            
        MLreduced = {}
        CCreduced = {}
        for key in MLmasses.keys():
            totalmask = np.logical_and(MLmask[key], CCmask[key])
            MLreduced[key] = MLmasses[key][totalmask]
            CCreduced[key] = CCmasses[key][totalmask]

        data['MLreduced'] = MLreduced
        data['CCreduced'] = CCreduced

    else:
        MLreduced, CCreduced = data['MLreduced'], data['CCreduced']

    grid, means, scatters = isg.intrinsicScatter(MLreduced, CCreduced, means = np.arange(0.5, 1.5, 0.002), scatters = np.arange(0.02, 0.2, 0.005))
    
    data['grid'] = grid
    data['means'] = means
    data['scatters'] = scatters

    figs = []


    print
    print
    print '-----'
    print 'var\tmode\t68%% +\t-\t95%% +\t-'
    print '-----'


    if 'meandist' not in data:

        means = data['means']
        scatters = data['scatters']
        
        mode, (r68, r95) = isg.getdist_1d_hist(means[0], means[1], levels = [0.68, 0.95])
        data['meandist'] = (mode, r68, r95)

        mode, (r68, r95) = isg.getdist_1d_hist(scatters[0], scatters[1], levels = [0.68, 0.95])
        data['scatterdist'] = (mode, r68, r95)



    for varname in 'mean scatter'.split():

        mode, r68, r95 = data['%sdist' % varname]

        print mode, r68, r95

        print '%s\t%2.4f\t+%2.4f\t-%2.4f\t+%2.4f\t-%2.4f' % (varname, mode, 
                                                             r68[0][1] - mode, mode - r68[0][0],
                                                             r95[0][1] - mode, mode - r95[0][0])

        x, prob = data['%ss' % varname]
        fig = isgp.plotdist_1d_hist(x, prob, mode, [r68[0], r95[0]])
        ax = fig.axes[0]
        ax.set_title(varname)

        figs.append(fig)
        fig.show()


    return figs, data



    


#########


def publicationMLCCBootCompScript(worklist = 'worklist', cosmology=None, data = None):

    items = readtxtfile(worklist)
    clusters = [x[0] for x in items]
    redshifts = readClusterRedshifts()
    properredshifts = np.array([redshifts[x] for x in clusters])


    if data is None:


        MLmasses, MLmask = readMLBootstraps('/u/ki/dapple/ki06/bootstrap_2012-05-17', items, np.arange(0, 200))

        CCmasses, CCmask = readCCSummary('/u/ki/dapple/ki06/bootstrap_2012-05-17', clusters, np.arange(00, 200))

        ratios = makeRatios(MLmasses, MLmask, CCmasses, CCmask)

        medians, errs = bootstrapMedians(ratios, clusters)

#        fit_ratio = np.hstack([pymc.database.pickle.load('ml_cc_rlog.out.%d' % i).trace('m', -1)[25000:] for i in range(1,6)])

        data = [medians, errs, properredshifts]

    else:

        medians = data[0]
        errs = data[1]
        properredshifts = data[2]
#        fit_ratio = data[3]

            
    if cosmology is not None:
        cosmoitems = readtxtfile(cosmology)
        cosmoclusters = [x[0] for x in cosmoitems]
        cosmomask = []
        for x in clusters:
            if x in cosmoclusters:
                cosmomask.append(1)
            else:
                cosmomask.append(0)
        cosmomask = np.array(cosmomask) == 1
        print cosmomask
            


    
    fig = pylab.figure()

    try:


        ax = fig.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])

        ax.axhline(1.0, c='k', linewidth=1.25)

#        ratio, ratioerr = sp.ConfidenceRegion(fit_ratio)
        ratio = 0.998
        ratioerr = [0.042, 0.044]  #m, p
        ratioerr2 = [0.081, 0.085]  #m,p
        fillx = [0.16, 0.72]


        ax.fill_between(fillx, ratio - ratioerr2[0], ratio + ratioerr2[1], facecolor = (1, .753, 0))
        ax.fill_between(fillx, ratio - ratioerr[0], ratio + ratioerr[1], facecolor = (1, 0.4, 0))
        ax.axhline(ratio, c='k', linestyle='--')

        if cosmology:
            ratio = 0.965
            ratioerr = [0.05, 0.06]  #m, p
            fillx = [0.17, 0.46]

            ax.axhline(ratio, c='k', linestyle=':')
            ax.fill_between(fillx, ratio - ratioerr[0], ratio + ratioerr[1], facecolor = 'c', alpha=0.3)
            
            ax.plot(properredshifts[cosmomask], medians[cosmomask], 'ko', markersize=10,
                    markerfacecolor = 'None', markeredgecolor = 'k')
            

        ax.errorbar(properredshifts, medians, errs, fmt='ko')

        ax.set_yscale('log')

        ax.set_xlim(0.16, 0.72)
        ax.set_ylim(0.45, 3.5)

        ax.set_yticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 2.0, 3.0])
        ax.set_yticklabels(['%2.1f' % x for x in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 2.0, 3.0]])

        ax.set_yticks([1.25, 1.5, 1.75, 2.25, 2.5, 2.75], minor=True)


        ax.set_xlabel('Cluster Redshift')
        ax.set_ylabel('CC Mass / P(z) Mass')

        fig.savefig('publication/%s.eps' % worklist)
        

    finally:

        return fig, data


#################################################


    
#################################################

def publicationCCPullScript(data = None):

    items = readtxtfile('worklist')
    clusters = [x[0] for x in items]

    if data is None:


        CCbootmasses, CCmask = readCCSummary('/u/ki/dapple/ki06/bootstrap_2011-12-14', clusters, 100)

        CCdat = readAnjaMasses()

        pulls = np.hstack([makePull(CCdat[tuple(x)][0], CCdat[tuple(x)][1], CCbootmasses[x[0]], CCmask[x[0]]) for x in items])
        
        data = pulls

    else:

        pulls = data

    fig = pylab.figure()



    ax = fig.add_axes([0.14, 0.14, 0.95 - 0.14, 0.95 - 0.14])

    ax.hist(pulls, bins=50, normed=True)

    ax.axvline(0.0, c='k', linewidth=2)

    gaussx = np.arange(-6, 6, 0.0002)
    gauss = np.exp(-0.5*gaussx**2)/np.sqrt(2*np.pi)

    ax.plot(gaussx, gauss, c='r', marker='None', linestyle='--', linewidth=1.5)

    pullMean = np.mean(pulls)
    pullStd = np.std(pulls)

    ax.text(-5.5, 0.4, 'Color Cut', fontsize=16)
    ax.text(2.5, 0.4, '$\mu = %1.3f$' % pullMean, fontsize=14)
    ax.text(2.5, 0.38, '$\sigma = %1.3f$' % pullStd, fontsize=14)

    ax.set_xlabel('Stacked $\Delta/\sigma$ for %d Clusters' % len(clusters))
    ax.set_ylabel('Probability ($\Delta/\sigma$)')

    fig.savefig('publication/ccmass_pull.eps')



    return fig, data
        
#################################################

def publicationMLPullScript(data = None):

    items = readtxtfile('worklist')
    clusters = [x[0] for x in items]

    if data is None:


        MLbootmasses, MLmask = readMLBootstraps('/u/ki/dapple/ki06/bootstrap_2011-12-14', items)

        MLdat = readDougMasses('/u/ki/dapple/subaru/doug/publication/baseline_2011-12-14')

        pulls = np.hstack([makePull(MLdat[tuple(x)][0], MLdat[tuple(x)][1], MLbootmasses[x[0]], MLmask[x[0]]) for x in items])
        
        data = pulls

    else:

        pulls = data

    fig = pylab.figure()



    ax = fig.add_axes([0.14, 0.14, 0.95 - 0.14, 0.95 - 0.14])

    ax.hist(pulls, bins=50, normed=True)

    ax.axvline(0.0, c='k', linewidth=2)

    gaussx = np.arange(-6, 6, 0.0002)
    gauss = np.exp(-0.5*gaussx**2)/np.sqrt(2*np.pi)

    ax.plot(gaussx, gauss, c='r', marker='None', linestyle='--', linewidth=1.5)

    pullMean = np.mean(pulls)
    pullStd = np.std(pulls)

    ax.text(-5.5, 0.4, 'P(z)', fontsize=16)
    ax.text(2.5, 0.4, '$\mu = %1.3f$' % pullMean, fontsize=14)
    ax.text(2.5, 0.38, '$\sigma = %1.3f$' % pullStd, fontsize=14)

    ax.set_xlabel('Stacked $\Delta/\sigma$ for %d Clusters' % len(clusters))
    ax.set_ylabel('Probability ($\Delta/\sigma$)')

    fig.savefig('publication/mlmass_pull.eps')



    return fig, data
        

######################################################

def compareSameClusters(masses, refclusters, compclusters):

    counts = cPickle.load(open('galaxy_counts_pzmethod.pkl', 'rb'))

    propercounts = []

    clusterrefs = {}
    clusters = {}
    for key in refclusters:
        cluster, filter, image = key

        clusterrefs[cluster] = key
        clusters[cluster] = []
        propercounts.append((counts[tuple(key)], cluster))

    for key in compclusters:
        cluster, filter, image = key
        if cluster in clusters:
            clusters[cluster].append(key)

    propercounts = sorted(propercounts)

    xvals = []
    yvals = []
    errs = []
    xlabels = []
    deltaCounts = []
    i=1.
    for count, cluster in propercounts:

        matches = clusters[cluster]
        if len(matches) == 0:
            continue

        refmass, referr = masses[tuple(clusterrefs[cluster])]
        
        xvals.extend(np.arange(i, i+0.1*len(matches) + 0.02, 0.1))
        i += 1.
        yvals.append(1.)
        deltaCounts.append(0.)
        for key in matches:
            match_mass = masses[tuple(key)][0]
            yvals.append(match_mass / refmass)
            deltaCounts.append(counts[tuple(key)] - count)

        errs.append(referr / refmass)
        errs.extend(len(matches)*[np.zeros(2)])

        xlabels.append(cluster)


    xvals = np.array(xvals)
    yvals = np.array(yvals)
    errs = np.array(errs).T





    fig = pylab.figure()
    ax = fig.add_axes([0.12, 0.2, 0.95-0.12, 0.95-0.2])
    ax.errorbar(xvals, yvals, errs, fmt='bo')    
    ax.set_xlim(0, len(xlabels) + 1.)
    ax.set_xticks(np.arange(1, len(xlabels) + 1.))
    ax.set_xticklabels(xlabels, rotation = 60)
    ax.set_ylabel('Ratio')
    fig.show()

    fig2 = pylab.figure()
    ax = fig2.add_axes([0.1, 0.2, 0.95 - 0.1, 0.95 - 0.2])
    ax.plot(xvals, deltaCounts, 'bo')
    ax.set_xlim(0, len(xlabels) + 1.)
    ax.set_xticks(np.arange(1, len(xlabels) + 1.))
    ax.set_xticklabels(xlabels, rotation = 60)
    ax.set_ylabel('Delta Counts')
    fig2.show()

    return fig, fig2

    

#######################################

def publicationPriorChangeScript(data = None):

    if data is None:
        
        data = {}
        
        data['ngals'] = cPickle.load(open('galaxy_counts_pzmethod.pkl', 'rb'))
        
        data['linmass'] = readDougMasses('/u/ki/dapple/subaru/doug/publication/baseline_2011-12-14')
        data['logmass'] = readDougMasses('/u/ki/dapple/subaru/doug/publication/trials_2012-02-06/logprior')

        worklist = buildWorklist(data['linmass'].keys())
        commonkeys = []
        for key in worklist:
            if key in data['logmass']:
                commonkeys.append(key)

        data['ck'] = commonkeys

        linmass, linerr = constructMassArray(data['linmass'], data['ck'])
        logmass, logerr = constructMassArray(data['logmass'], data['ck'])

        ratios = logmass / linmass
        data['ratios'] = ratios

    ratios = data['ratios']

    ngals = []
    for key in data['ck']:
        ngals.append(data['ngals'][tuple(key)])

    ngals = np.array(ngals)


    fig = pylab.figure()
    ax = fig.add_axes([0.12, 0.12, 0.95-0.12, 0.95-0.12])
    ax.plot(ngals, ratios, 'bo')

    return fig, data

                 


        






    
    

    
