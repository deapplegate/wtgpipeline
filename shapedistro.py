#!/usr/bin/env python
######################

import re, inspect
import pymc, numpy as np, scipy.special, astropy, astropy.io.fits as pyfits
import ldac, crossval
import voigt_tools as vtools

import fitmodel

###########################

data_dir='/nfs/slac/g/ki/ki06/anja/SUBARU/STEP2'

def loadMeasuredCatalog(imageSet, i, rotated = False):



    if rotated:
        filename = '%s/cats_2011-08-29/STEP2_rotated_psf%s_shear%02d.shear.cat' % (data_dir, imageSet, i)
#        filename = '%s/catalogs/STEP2_rotated_psf%s_shear%02d_weighted.cat' % (data_dir, imageSet, i)
    else:
        filename = '%s/cats_2011-08-29/STEP2_psf%s_shear%02d.shear.cat' % (data_dir, imageSet, i)
#        filename = '%s/catalogs/STEP2_psf%s_shear%02d_weighted.cat' % (data_dir, imageSet, i)

    cat = ldac.openObjectFile(filename)

    return cat.filter(cat['cl'] == 0)

#    return ldac.openObjectFile(filename)

#################################

def loadMeasuredCatalogs(psf):

    originalMeasured = []
    rotatedMeasured = []
    for i in xrange(64):
        originalMeasured.append(loadMeasuredCatalog(psf, i, rotated = False))
        rotatedMeasured.append(loadMeasuredCatalog(psf, i, rotated = True))

    return (originalMeasured, rotatedMeasured)


###########################

def readShears():

    psfs = {}
    for psf in 'A B C D E F'.split():
        psfs[psf] = [np.zeros((64,2)), np.zeros((64,2))]

    INPUT = open('%s/answers/answers' % data_dir)
    for line in INPUT.readlines():

        if re.search('PSF', line):
            continue

        entries = filter(lambda x: x != '',[x.strip() for x in line.split()])
        if len(entries) < 5:
            continue

        psf = entries[0]
        original = int(entries[1])
        rotated = int(entries[2])
        shear = np.array(map(float, entries[3:5]))

        psfs[psf][0][original] = shear
        psfs[psf][1][rotated] = shear

    INPUT.close()

    return psfs

####################################


rh_psf = {'A' : 1.66, 
          'B' : 1.66, 
          'C' : 2.03, 
          'D' : 1.93, 
          'E' : 1.93, 
          'F' : 1.95 }



###########################

def prepCats(psf, component = None):

    cats = loadMeasuredCatalogs(psf)

    trueshears = readShears()[psf]

    psfsize = rh_psf[psf]

    shear = []
    trueshear = []
    snratio = []
    size = []
    pg = []
    rg = []
    gs = []


    for j in [0,1]:
        for i in range(64):

            if component is None or component == 1:
                shear.extend(cats[j][i]['gs1'])
                trueshear.extend(len(cats[j][i])*[trueshears[j][i][0]])
                snratio.extend(cats[j][i]['snratio'])
                size.extend(cats[j][i]['rh'] / psfsize)
                pg.extend(cats[j][i]['Pgs'])
                rg.extend(cats[j][i]['rg'])
                gs.extend(np.sqrt(cats[j][i]['gs1']**2 + cats[j][i]['gs2']**2))

            if component is None or component == 2:

                shear.extend(cats[j][i]['gs2'])
                trueshear.extend(len(cats[j][i])*[trueshears[j][i][1]])
                snratio.extend(cats[j][i]['snratio'])
                size.extend(cats[j][i]['rh'] / psfsize)
                pg.extend(cats[j][i]['Pgs'])
                rg.extend(cats[j][i]['rg'])
                gs.extend(np.sqrt(cats[j][i]['gs1']**2 + cats[j][i]['gs2']**2))

    shear = np.array(shear)
    trueshear = np.array(trueshear)
    snratio = np.array(snratio)
    size = np.array(size)
    pg = np.array(pg)
    rg = np.array(rg)
    gs = np.array(gs)
    

    filter = np.logical_and(np.logical_and(snratio > 7, size > 1.15), 
                            np.logical_and(np.logical_and(rg > 1.5, rg < 5.0),
                                           np.abs(gs) < 1.4))
#    filter = np.ones(len(shear)) == 1.

    return shear[filter], trueshear[filter], snratio[filter], size[filter], pg[filter], rg[filter]

############################

def convertToCat(shear, trueshear, snratio, size, pg, rg):

    cols = [pyfits.Column(name = 'g', format = 'E', array = shear),
            pyfits.Column(name = 'true_g', format = 'E', array = trueshear),
            pyfits.Column(name = 'snratio', format = 'E', array = snratio),
            pyfits.Column(name = 'size', format = 'E', array = size),
            pyfits.Column(name = 'pg', format = 'E', array = pg),
            pyfits.Column(name = 'rg', format = 'E', array = rg)]

    cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols)))

    return cat

############################

def Gauss(x, tau):

    twopi = 2*np.pi

    half_delta2 = 0.5*(x**2)

    return np.exp(-half_delta2*tau)/np.sqrt(twopi/tau)


def SingleGaussianModel(size, snratio, g, g_true, npostsamples = 5):


    g = np.ascontiguousarray(g.astype(np.double))
    g_true = np.ascontiguousarray(g_true.astype(np.double))

    unique_g_true = np.unique(g_true)

    twopi = 2*np.pi

    ###

    shearcal_m = pymc.Uniform('shearcal_m', -1, 1)
    shearcal_c = pymc.Uniform('shearcal_c', -0.05, 0.05)
    
    @pymc.deterministic(trace=False)
    def mu(m = shearcal_m, c = shearcal_c):
        return (1+m)*g_true + c

    ###

    tau = pymc.Gamma('tau', alpha = 25*.75, beta = .75)

    @pymc.deterministic
    def sigma(tau = tau):

        return 1./np.sqrt(tau)
        
    ###

    @pymc.stochastic(observed = True)
    def data(value = g, mu = mu, tau = tau):

        half_delta2 = 0.5*(g - mu)**2

        prob = np.exp(-half_delta2*tau)/np.sqrt(twopi/tau)

        return np.sum(np.log(prob))

    ###

#    @pymc.deterministic
#    def postpred_g(g_true = unique_g_true, m = shearcal_m, c = shearcal_c,
#                   sigma = sigma, npostsamples = npostsamples):
#
#        mu = (1+m)*g_true + c
#
#        samples = sigma*np.random.standard_normal(npostsamples*len(g_true))
#
#        return (np.reshape(samples, (npostsamples, -1)) + mu).T
#
#    ###
    
    return locals()




############################

def DoubleGauss(x, alpha, tau_1, tau_2):

    twopi = 2*np.pi

    half_delta2 = 0.5*(x**2)
    
    prob = alpha*np.exp(-half_delta2*tau_1)/np.sqrt(twopi/tau_1) + (1 - alpha)*np.exp(-half_delta2*tau_2)/np.sqrt(twopi/tau_2)
    

    return prob



def DoubleGaussianModel(size, snratio, g, g_true, npostsamples = 5):


    g = np.ascontiguousarray(g.astype(np.double))
    g_true = np.ascontiguousarray(g_true.astype(np.double))

    unique_g_true = np.unique(g_true)



    twopi = 2*np.pi

    ###

    alpha = pymc.Uniform('alpha', 0.5, 1.0)

    ###

    shearcal_m = pymc.Uniform('shearcal_m', -1, 1)
    shearcal_c = pymc.Uniform('shearcal_c', -0.05, 0.05)
    
    @pymc.deterministic(trace=False)
    def mu(m = shearcal_m, c = shearcal_c):
        return (1+m)*g_true + c

    ###

    tau_1 = pymc.Gamma('tau1', alpha = 25*.75, beta = .75)
    
    tau_2 = pymc.Gamma('tau2', alpha = .25**2, beta = .25)
    
    ###

    @pymc.stochastic(observed = True)
    def data(value = g, alpha = alpha, mu = mu, tau_1 = tau_1, tau_2 = tau_2):

        half_delta2 = 0.5*(g - mu)**2

        prob = alpha*np.exp(-half_delta2*tau_1)/np.sqrt(twopi/tau_1) + (1 - alpha)*np.exp(-half_delta2*tau_2)/np.sqrt(twopi/tau_2)

        return np.sum(np.log(prob))

    ###

    @pymc.deterministic
    def postpred_g(g_true = unique_g_true, m = shearcal_m, c = shearcal_c, 
                   alpha = alpha, tau_1 = tau_1, tau_2 = tau_2, 
                   npostsamples = npostsamples):

        mu = (1+m)*g_true + c

        nsamples = npostsamples*len(g_true)

        switch = np.random.uniform(size=nsamples)

        sigma1 = 1./np.sqrt(tau_1)
        sigma2 = 1./np.sqrt(tau_2)

        samples = sigma1*np.random.standard_normal(nsamples)

        samples[switch >= alpha] = sigma2*np.random.uniform(size=len(samples[switch >= alpha]))


        return (np.reshape(samples, (npostsamples, -1)) + mu).T

    ###

    
    return locals()



#################################


def CauchyModel(size, snratio, g, g_true):

    ###

    shearcal_m = pymc.Uniform('shearcal_m', -1, 1)
    shearcal_c = pymc.Uniform('shearcal_c', -0.05, 0.05)

    @pymc.deterministic
    def alpha(m = shearcal_m, c = shearcal_c):
        return (1+m)*g_true + c

    ###

    logbeta = pymc.Uniform('logbeta', -7, 2.5)

    @pymc.deterministic
    def beta(logbeta = logbeta):
        return np.exp(logbeta)

    ###
    
    data = pymc.Cauchy('data', alpha = alpha, beta = beta, value = g, observed=True)

    ###

    return locals()


##################################


def VoigtModel(size, snratio, g, g_true, npostsamples = 5):

    g = np.ascontiguousarray(g.astype(np.double))
    g_true = np.ascontiguousarray(g_true.astype(np.double))

    unique_g_true = np.unique(g_true)


    ###

    shearcal_m = pymc.Uniform('shearcal_m', -1, 1)
    shearcal_c = pymc.Uniform('shearcal_c', -0.05, 0.05)

    @pymc.deterministic(trace = False)
    def mu(m = shearcal_m, c = shearcal_c):
        return np.ascontiguousarray((1+m)*g_true + c)

    ###

    tau = pymc.Gamma('tau1', alpha = 25*.75, beta = .75)

    @pymc.deterministic
    def sigma(tau = tau):
        return 1./np.sqrt(tau)

    ###

    loggamma = pymc.Uniform('loggamma', -7, 2.5)

    @pymc.deterministic
    def gamma(loggamma = loggamma):
        return np.exp(loggamma)
    
    ###

    @pymc.stochastic(observed=True)
    def data(value = g, mu = mu, sigma = sigma, gamma = gamma):


        return vtools.likelihood(value, mu, sigma, gamma)


    ###

#    @pymc.deterministic
#    def postpred_g(g_true = unique_g_true, m = shearcal_m, c = shearcal_c,
#                   sigma = sigma, gamma = gamma, npostsamples = npostsamples):
#
#        mu = (1+m)*g_true + c
#
#        samples = vtools.voigtSamples(sigma, gamma, npostsamples*len(g_true))
#
#        return (np.reshape(samples, (npostsamples, -1)) + mu).T
#
        

    return locals()


################################

def BentVoigtModel(size, snratio, g, g_true):

    g = np.ascontiguousarray(g.astype(np.double))
    g_true = np.ascontiguousarray(g_true.astype(np.double))


    ###

    sizepivot_x = 2.0
    sizepivotm_y = pymc.Uniform('sizepivotm_y', -.5, 0.5)
    sizeslope_m = pymc.Uniform('sizeslope_m', -6, 6)
    shearcal_c = pymc.Uniform('shearcal_c', -0.1, 0.1)


    @pymc.deterministic(trace = False)
    def shearcal_m(sizepivot_x = sizepivot_x, sizepivotm_y = sizepivotm_y, 
                   slope = sizeslope_m):

        m = np.zeros_like(size)
        m[size >= sizepivot_x] = sizepivotm_y
        m[size < sizepivot_x] = slope*(size[size < sizepivot_x] - sizepivot_x) + sizepivotm_y

        return m



    @pymc.deterministic(trace = False)
    def mu(m = shearcal_m, c = shearcal_c):
        return np.ascontiguousarray((1+m)*g_true + c)

    ###

    tau = pymc.Gamma('tau1', alpha = 25*.75, beta = .75)

    @pymc.deterministic
    def sigma(tau = tau):
        return 1./np.sqrt(tau)

    ###

    loggamma = pymc.Uniform('loggamma', -7, 2.5)

    @pymc.deterministic
    def gamma(loggamma = loggamma):
        return np.exp(loggamma)
    
    ###

    @pymc.stochastic(observed=True)
    def data(value = g, mu = mu, sigma = sigma, gamma = gamma):


        return vtools.likelihood(value, mu, sigma, gamma)

    return locals()


################################

def BentVoigtModel2(size, snratio, g, g_true):

    g = np.ascontiguousarray(g.astype(np.double))
    g_true = np.ascontiguousarray(g_true.astype(np.double))


    ###

    sizepivot_x = pymc.Uniform('sizepivot_x', 1.0, 8.0)
    sizepivotm_y = 0.
    sizeslope_m = pymc.Uniform('sizeslope_m', -6, 6)
    shearcal_c = pymc.Uniform('shearcal_c', -0.1, 0.1)


    @pymc.deterministic(trace = False)
    def shearcal_m(sizepivot_x = sizepivot_x, sizepivotm_y = sizepivotm_y, 
                   slope = sizeslope_m):

        m = np.zeros_like(size)
        m[size >= sizepivot_x] = sizepivotm_y
        m[size < sizepivot_x] = slope*(size[size < sizepivot_x] - sizepivot_x) + sizepivotm_y

        return m



    @pymc.deterministic(trace = False)
    def mu(m = shearcal_m, c = shearcal_c):
        return np.ascontiguousarray((1+m)*g_true + c)

    ###

    tau = pymc.Gamma('tau1', alpha = 25*.75, beta = .75)

    @pymc.deterministic
    def sigma(tau = tau):
        return 1./np.sqrt(tau)

    ###

    loggamma = pymc.Uniform('loggamma', -7, 2.5)

    @pymc.deterministic
    def gamma(loggamma = loggamma):
        return np.exp(loggamma)
    
    ###

    @pymc.stochastic(observed=True)
    def data(value = g, mu = mu, sigma = sigma, gamma = gamma):


        return vtools.likelihood(value, mu, sigma, gamma)

    return locals()


################################

def BentVoigtModel3(size, snratio, g, g_true):

    g = np.ascontiguousarray(g.astype(np.double))
    g_true = np.ascontiguousarray(g_true.astype(np.double))


    ###

#    sizepivot_x = pymc.Uniform('sizepivot_x', 1.0, 8.0)
    sizepivot_x = pymc.Normal('sizepivot_x', 2.0, 1./0.2**2) # tau
    sizepivotm_y = pymc.Normal('sizepivotm_y', 0.0, 1./0.08**2) # tau
    sizeslope_m = pymc.Uniform('sizeslope_m', -6, 6)
    shearcal_c = pymc.Uniform('shearcal_c', -0.1, 0.1)


    @pymc.deterministic(trace = False)
    def shearcal_m(sizepivot_x = sizepivot_x, sizepivotm_y = sizepivotm_y, 
                   slope = sizeslope_m):

        m = np.zeros_like(size)
        m[size >= sizepivot_x] = sizepivotm_y
        m[size < sizepivot_x] = slope*(size[size < sizepivot_x] - sizepivot_x) + sizepivotm_y

        return m



    @pymc.deterministic(trace = False)
    def mu(m = shearcal_m, c = shearcal_c):
        return np.ascontiguousarray((1+m)*g_true + c)

    ###

    tau = pymc.Gamma('tau1', alpha = 25*.75, beta = .75)

    @pymc.deterministic
    def sigma(tau = tau):
        return 1./np.sqrt(tau)

    ###

    loggamma = pymc.Uniform('loggamma', -7, 2.5)

    @pymc.deterministic
    def gamma(loggamma = loggamma):
        return np.exp(loggamma)
    
    ###

    @pymc.stochastic(observed=True)
    def data(value = g, mu = mu, sigma = sigma, gamma = gamma):


        return vtools.likelihood(value, mu, sigma, gamma)

    return locals()


################################


def VoigtModel_SNPowerlaw(size, snratio, g, g_true, npostsamples = 5):

    g = np.ascontiguousarray(g.astype(np.double))
    g_true = np.ascontiguousarray(g_true.astype(np.double))

    unique_g_true = np.unique(g_true)


    ###

    shearcal_m = pymc.Uniform('shearcal_m', -1, 1)
    shearcal_c = pymc.Uniform('shearcal_c', -0.05, 0.05)

    @pymc.deterministic(trace = False)
    def mu(m = shearcal_m, c = shearcal_c):
        return np.ascontiguousarray((1+m)*g_true + c)

    ###

    tau = pymc.Gamma('tau1', alpha = 25*.75, beta = .75)

    @pymc.deterministic
    def sigma(tau = tau):
        return 1./np.sqrt(tau)

    ###

    loggamma = pymc.Uniform('loggamma', -7, 2.5)

    @pymc.deterministic
    def gamma(loggamma = loggamma):
        return np.exp(loggamma)
    
    ###

    @pymc.stochastic(observed=True)
    def data(value = g, mu = mu, sigma = sigma, gamma = gamma):


        return vtools.likelihood(value, mu, sigma, gamma)


    ###

    @pymc.deterministic
    def postpred_g(g_true = unique_g_true, m = shearcal_m, c = shearcal_c,
                   sigma = sigma, gamma = gamma, npostsamples = npostsamples):

        mu = (1+m)*g_true + c

        samples = vtools.voigtSamples(sigma, gamma, npostsamples*len(g_true))

        return (np.reshape(samples, (npostsamples, -1)) + mu).T

        

    return locals()

################################


################################



def PearsonProfile(x, sig, kur):

    norm = 2**(2*kur-2)*np.abs(scipy.special.gamma(kur))**2/(np.pi*sig*scipy.special.gamma(2*kur - 1))
    prob = norm*(1 + (x/sig)**2)**(-kur)

    return prob

###

def PearsonSamples(sigma, kir, nsamples):

    xbins = np.arange(limits[0], limits[1], binsize)

    probs = voigtProfile(xbins, sigma, gamma)
    nbins = len(xbins)

    cdf = np.zeros(nbins + 1)
    cdf[1:] = np.cumsum(probs)
    cdf = cdf / cdf[nbins]


    picks = np.random.uniform(size = size)

    positions = np.searchsorted(cdf, picks, side='left')

    return xbins[positions]    


###
    

def PearsonModel(size, snratio, g, g_true, npostsamples = 5):

    ###

    unique_g_true = np.unique(g_true)

    ###

    shearcal_m = pymc.Uniform('shearcal_m', -1, 1)
    shearcal_c = pymc.Uniform('shearcal_c', -0.05, 0.05)

    @pymc.deterministic(trace=False)
    def mu(m = shearcal_m, c = shearcal_c):
        return (1+m)*g_true + c

    ###

    tau = pymc.Gamma('tau', alpha = 25*.75, beta = .75)

    @pymc.deterministic
    def sigma(tau = tau):
        return 1./np.sqrt(tau)    

    ###

    kurtosis = pymc.Uniform('kurtosis', 0.6, 10)

    ###

    @pymc.stochastic(observed=True)
    def data(value = g, mu = mu, sig = sigma, kur = kurtosis):

        x = value - mu
        norm = 2**(2*kur-2)*np.abs(scipy.special.gamma(kur))**2/(np.pi*sig*scipy.special.gamma(2*kur - 1))
        prob = norm*(1 + (x/sig)**2)**(-kur)

        return np.sum(np.log(prob))

    ###

    @pymc.deterministic
    def postpred_g(g_true = unique_g_true, m = shearcal_m, c = shearcal_c,
                   sigma = sigma, kur = kurtosis, npostsamples = npostsamples):

        mu = (1+m)*g_true + c

        samples = PearsonSamples(sigma, kur, npostsamples*len(g_true))

        return (np.reshape(samples, (npostsamples, -1)) + mu).T


    return locals()


###############


class BinnedShapeSamples(object):

    def __init__(self, shapedistro, bin_selectors, distro_kwds = None):

        self.shapedistro = shapedistro
        self.bin_selectors = bin_selectors
        self.func_name = shapedistro.func_name
        self.distro_kwds = distro_kwds

        if self.distro_kwds is None:
            self.shapedistro_kwds = inspect.getargspec(self.shapedistro)[0]



    def __call__(self, g, binvals, binparams, mkey = 'shearcal_m', ckey = 'shearcal_c'):

        ghats = np.zeros_like(g)

        for key, binparam in binparams.iteritems():
            
            inbin = reduce(np.logical_and, [self.bin_selectors[i][j](binvals[:,i]) \
                                                for i,j in enumerate(key)] )

            nsamples = len(g[inbin])

            binparam['size'] = nsamples
            
                
            delta_gs = self.shapedistro(*[binparam[x] for x in self.shapedistro_kwds])

            m = binparam[mkey]
            c = binparam[ckey]

            ghats[inbin] = delta_gs + (1+m)*g[inbin] + c

        return ghats

            

        

####################################


def makeCrossValCats(cat, nsets, selectors, dir, prefix):


    crossval_cats = crossval.makeCrossValCats(cat, nsets)

    for i, training_testing_cats in enumerate(crossval_cats):

        basename = '%s/%s.s%d' % (dir, prefix, i)

        for cattype, crossvalcat in zip('training testing'.split(), training_testing_cats):
        
            bincats = crossval.createBins(crossvalcat, selectors)

            for key, bincat in bincats.iteritems():

                if key == '':

                    catname = '%s.%s.cat' % (basename, cattype)

                else:
                    
                   catname =  '%s.%s.%s.cat' % (basename, cattype, '.'.join(map(str, key)))

                print catname

                bincat.saveas(catname, overwrite=True)





    
#[[lambda cat: cat['size'] < 2, lambda cat: cat['size'] >= 2].
#[lambda cat: at['snratio'] < 5, lambda cat: logical_and(cat['snratio'] >= 5, cat['snratio'] < 10), lambda cat: logical_and(cat['snratio'] >= 10, cat['snratio'] < 20), lambda cat: cat['snratio'] >= 20]]



#gamma.pdf(x,a) = x**(a-1)*exp(-x)/gamma(a)
# f(x \mid \alpha, \beta) = \frac{\beta^{\alpha}x^{\alpha-1}e^{-\beta x}}{\Gamma(\alpha)}


####################################################

def medianFit(gs, sets):

    ms = []
    ncounts = np.array([len(x) for x in sets])

    gs = gs[ncounts > 50]

    sets = [x for x in sets if len(x) > 50]
    if len(gs) < 5:
        return None
    for i in range(100):                   
        boot_sets = [x[np.random.randint(0, len(x), len(x))] for x in sets]
        medians = np.array([np.median(x) for x in boot_sets])
        fit = fitmodel.FitModel(gs, medians, 0.1*np.ones(len(gs)), fitmodel.LinearModel)
        fit.fit()
        ms.append(fit.par_vals['a1'])
    return ms



#############################################


def binfit(size, true_g, uniq_g, delta, binsize):

    sizes = []
    msA = []
    for i in np.arange(1.15, 4.0, binsize):
        selected = np.logical_and(size >= i, size < i + binsize)
        sets = [delta[np.logical_and(selected, true_g == x)] for x in uniq_g]
        ms = medianFit(uniq_g, sets)
        if ms is None:
            continue
        sizes.append(i + binsize / 2.)
        msA.append(ms)

    return sizes, msA
