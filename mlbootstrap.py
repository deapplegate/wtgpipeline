#########################
# Process bootstraps from ML masses
#########################

from __future__ import with_statement
import ldac, cPickle, glob, pymc, numpy as np
import maxlike_plots as mp, maxlike_subaru_filehandler as msf

subarudir = '/nfs/slac/g/ki/ki05/anja/SUBARU/'
workdir = '/lustre/ki/orange/dapple/bootstrapmasses'
workdir2 = '/nfs/slac/g/ki/ki05/anja/SUBARU/bootstrapmasses'


def loadClusterBootstraps(cluster, filter, image, workdir = workdir):

    bootstraps = []
    for bootstrap in glob.glob('%s/%s.%s.%s.b*.summary.pkl' % (workdir, cluster, filter, image)):

        with open(bootstrap, 'rb') as input:
            bootstraps.append(cPickle.load(input))

    return bootstraps


def loadClusterBootstrapSamples(cluster, filter, image):

    dbs = []
    for bootstrap in glob.glob('%s/%s.%s.%s.b*.out' % (workdir, cluster, filter, image)):
        dbs.append(pymc.database.pickle.load(bootstrap))

    return dbs

                


def loadFullSample(cluster, filter, image):

    db = pymc.database.pickle.load('%s/%s/LENSING_%s_%s_aper/%s/mlmass.voigtnorm.baseline.pkl' % (subarudir, cluster, filter, filter, image))

    return db




###################################

class ModelInitException(Exception): pass

def buildModel(tobuild, samples):

    model = None
    for i in range(10):

        try:
            model = tobuild(samples)
            break
        except pymc.ZeroProbability:
            continue

    if model is None:
        raise ModelInitException()

    return model

###################################


def GaussModel(samples):

    
    mu = pymc.Uniform('mu', 1, 50)
    tau = pymc.Gamma('tau', 0.5, 2.5)

    data = pymc.Normal('data', mu, tau, value = samples, observed = True)

    return locals()


####################################

def SkewModel(samples):

    mu = pymc.Uniform('mu', 1, 50)
    tau = pymc.Gamma('tau', 0.5, 2.5)
    alpha = pymc.Uniform('alpha', -10, 10)

    data = pymc.SkewNormal('data', mu, tau, alpha, value = samples, observed = True)

    return locals()

####################################

def compare(samples):

    samples = np.array(samples) / 1e14

    gauss = pymc.MCMC(buildModel(GaussModel, samples))
    gauss.sample(13000, 3000)
    
    skew = pymc.MCMC(buildModel(SkewModel, samples))
    skew.sample(13000, 3000)

    delta = gauss.dic() - skew.dic()

    return gauss, skew, delta


##############################


def report(keys, report):

    models = {}
    output = open(report, 'w')
    print "Cluster\tFilter\tImage\tML DIC\tBootstrap DIC\t (Note: Positive Values == Skew Preferred)"
    output.write("Cluster\tFilter\tImage\tML DIC\tBootstrap DIC\t (Note: Positive Values == Skew Preferred)\n")
    for key in keys:
        cluster, filter, image = key

        if image != 'good':
            continue

        clusterdata = {'zcluster' : msf.parseZCluster(cluster),
                       'r500' : msf.readR500(cluster),
                       'concentration' : 4.0}

#        baselinedb = loadFullSample(*key)
#        
#        baselinemasses = mp.summarizeMasses(baselinedb, clusterdata, burn = 10000)[::10]
#
#        gauss, skew, baseline_delta = compare(baselinemasses)

        
        try:
            bootstraps = loadClusterBootstraps(cluster, filter, image, workdir)
        except:
            try:
                bootstraps = loadClusterBootstraps(cluster, filter, image, workdir2)
            except:
                print 'FAIL on %s %s %s' % (cluster, filter, image)
                continue
            
        bootstrapmasses = np.array([b['mean'] for b in bootstraps])

        bgauss, bskew, bootstrap_delta = compare(bootstrapmasses)

        baseline_delta = 0.

        print cluster, filter, image, baseline_delta, bootstrap_delta
        output.write('%s %s %s %f %f\n' % (cluster, filter, image, baseline_delta, bootstrap_delta))
        output.flush()

#        models[key] = ((gauss, skew), (bgauss, bskew))
        models[key] = (bgauss, bskew)

    output.close()


    return models
            
