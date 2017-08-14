####################################
# Utilities for reading fit outputs
##################################
import glob, os, re
import numpy as np, pymc
import ldac, banff, banff_tools


########################

    
def gaussApprox(datavec, subset = None):

    

    means = np.mean(datavec, axis=-1)
    
    if subset is None:
        subvec = datavec
    else:
        subvec = datavec.T[np.random.randint(0, datavec.shape[1], subset)].T

    return means, np.cov(subvec)


#########


def chisq(samples, means, covmatrix):

    nsamples = samples.shape[1]

    delta = (samples.T - means)

    inv_covmatrix = np.linalg.inv(covmatrix)

    chisq_probs = np.zeros(nsamples)

    for i in range(nsamples):
        chisq_probs[i] = np.dot(delta[i], np.dot(inv_covmatrix, delta[i]))

    return np.sum(chisq_probs)


#########

def defaultNameParser(catfile, base):

    match = re.match('%s.((\d\.)+)cat' % base, catfile)
    key = tuple([int(x) for x in filter(lambda x: x != '', match.group(1).split('.'))])

    return key

    

def loadMasterCats(dir, base, nameparser = defaultNameParser):


    cats = {}
    
    
    for catfile in glob.glob('%s/%s.*.cat' % (dir, base)):

        
        dir, filename = os.path.split(catfile)
        key = nameparser(filename, base)

        cats[key] = ldac.openObjectFile(catfile)

    return cats

############

def loadResult(cat, resfile, shapemodel):

    db = pymc.database.pickle.load(resfile)
    mcmc = None
    for i in range(10):
        try:
            mcmc = pymc.MCMC(shapemodel(cat['size'], cat['snratio'],
                                    cat['g'], cat['true_g']),
                             db = db)
            break
        except pymc.ZeroProbability:
            pass
    if mcmc is None:
        raise pymc.ZeroProbability(resfile)

    return mcmc

###############
    


def loadResults(dir, base, cats, shapemodel):

    results = {}

    for resfile in glob.glob('%s/%s.*.out' % (dir, base)):

        dir, filename = os.path.split(resfile)


        match = re.match('%s.((\d\.)+)out' % base, filename)
        key = tuple([int(x) for x in filter(lambda x: x != '', match.group(1).split('.'))])
        
        if key not in results:
            results[key] = []

        cat = cats[key]

        mcmc = loadResult(cat, resfile, shapemodel)

        results[key].append(mcmc)
            

    return results

############

def compileDatavector(results, vars, burn):

    datavectors = {}
    rowstacks = {}

    for key, resvecs in results.iteritems():
        
        rawvec = {}
        
        for var in vars:
            rawvec[var] = np.hstack([res.trace(var)[burn:] for res in resvecs])

        datavectors[key] = rawvec

        rowstacks[key] = np.row_stack([rawvec[var] for var in vars])

    return datavectors, rowstacks


#############

def selectPosteriorSamples(datavectors, nsamples):

    simparams = []

    for i in range(nsamples):
        
        paramsets = {}
        
        for binkey, var_vectors in datavectors.iteritems():

            paramset = {}

            selection = None
            
            for varname, samples in var_vectors.iteritems():

                if selection is None:
                    selection = np.random.randint(0, len(samples), 1)

                paramset[varname] = samples[selection]

            paramsets[binkey] = paramset

        simparams.append(paramsets)

    return simparams


#################

def calcPostPredLogProb(cat, uniq_gs, postpredsamples):

    
    nunique = len(uniq_gs)

    logp = 0

    for i in range(nunique):

        data = np.sort(cat['g'][cat['true_g'] == uniq_gs[i]])

        deltas = banff.computeDeltas(data)

        samples = np.sort(postpredsamples[:,i,:].flatten())

        pdf = banff_tools.computePDF(samples.astype(np.double), data.astype(np.double), deltas.astype(np.double))

        logp += np.sum(np.log(pdf))


    return logp
    



