#!/usr/bin/env python
########################

import os
import numpy as np, pymc, scipy.integrate

########################

class IntrinsicScatter2(object):

    def __init__(self, xmasses, ymasses, norm = 1e15, **keywords):

        #x and y are dictionaries  cluster -> samples, with len(x[cluster]) == len(y[cluster])
        # assume that the joint probability distribution is well described by multivariate guassian

        self.norm = norm

        self.means = {}
        self.covars = {}
        self.groups = xmasses.keys()
        self.cache = {}

        for group in self.groups:
            data = np.row_stack([xmasses[group], ymasses[group]]) / norm
            self.means[group] = np.mean(data, axis=-1)
            self.covars[group] = np.cov(data)           

        self.x0 = np.array([self.means[group][0] for group in self.groups])
        self.y0 = np.array([self.means[group][1] for group in self.groups])
        self.a2 = np.array([self.covars[group][0,0] for group in self.groups])
        self.c2 = np.array([self.covars[group][1,1] for group in self.groups])
        self.b = np.array([self.covars[group][0,1] for group in self.groups])
                           



        for i in range(60):
            
            try:
                self.buildPriors(**keywords)
                self.likelihood()
                return
            except pymc.ZeroProbability:
                pass

        raise pymc.ZeroProbability


    ########################

    def buildPriors(self, **keywords):
        
        if 'log10_intrinsic_scatter' in keywords:
            log10_val = keywords['log10_intrinsic_scatter']
        else:
            log10_val = np.random.uniform(-4, 0)
        self.log10_intrinsic_scatter = pymc.Uniform('log10_intrinsic_scatter', -4, 0, value = log10_val)
        
        @pymc.deterministic(name = 'intrinsic_sigma')
        def intrinsic_sigma(log10_scatter = self.log10_intrinsic_scatter):
            return 10**log10_scatter

        self.intrinsic_sigma = intrinsic_sigma

        if 'm_angle' in keywords:
            m_angle_val = keywords['m_angle']
        else:
            m_angle_val = np.random.uniform(np.pi/8., 3*np.pi/8.)
        self.m_angle = pymc.Uniform('m_angle', np.pi/8, 3*np.pi/8., value = m_angle_val)

        @pymc.deterministic(name = 'm')
        def m(m_angle = self.m_angle):
            return np.tan(m_angle)

        self.m = m



    ###########################

    def buildMCMC(self, filename = None):

        if filename is None:
            mcmc = pymc.MCMC(self)
        elif os.path.exists(filename):
            mcmc = pymc.MCMC(self, db = pymc.database.pickle.load(filename))
        else:
            mcmc = pymc.MCMC(self, db = 'pickle', dbname = filename)

        return mcmc


    ######################

    def likelihood(self):

##       Cached Likelihood, assumed normal point err, lognorm scatter, & implicit marginalization
#        @pymc.potential(name = 'likelihood')
#        def yhat(m = self.m, log10sigma = self.log10_intrinsic_scatter):
#
#            m = round(m, 4)
#            log10sigma = round(log10sigma, 4)
#
#            key = (m, log10sigma)
#            if key not in self.cache:
#
#                sigma = 10**log10sigma
#
#
#                val = np.sum(np.array([np.log(integral(m, sigma, self.means[x][0], self.means[x][1], self.covars[x])) \
#                                           for x in self.groups]))
#
#                if not isinstance(val, float):
#                    print '!!!!!!!!!!!!!!!!!!'
#                    print m, log10sigma, val
#                
#
#                self.cache[key] = val
#
#
#            return self.cache[key]

##      normal err,, normal instrinsic scatter, & explicit marginalization
        @pymc.potential(name = 'likelihood')
        def yhat(m = self.m, sigma = self.intrinsic_sigma):

            convolved_sigma = self.c2 - 2*self.b*m + self.a2*m**2 + sigma**2


            return pymc.normal_like(self.y0, m*self.x0, 1./convolved_sigma**2)


        self.yhat = yhat



#################

def integral(m, sig, x0, y0, cov, mult = 3, err = 1e-6):

    mu = np.array([x0,y0])
    invcov = np.linalg.inv(cov)

    def integrand(y, x):

        delta = np.array([x,y]) - mu
        return np.exp(-0.5*(np.log(y/(m*x))**2)/sig**2 - 0.5*np.dot(delta, np.dot(invcov, delta))) / y


    sqrcov = np.sqrt(cov)

    norm = 1./np.sqrt(8*np.pi**3*sig*np.linalg.det(cov))
    
    return scipy.integrate.dblquad(integrand, np.max(1e-6, x0 - mult*sqrcov[0,0]), x0 + mult*sqrcov[0,0], lambda x: np.max(1e-6, y0 - mult*sqrcov[1][1]), lambda x: y0+mult*sqrcov[1][1], epsabs = err, epsrel=err)[0] * norm




###################

def integrand(m, sig, x0, y0, cov, x, y):

    mu = np.array([x0,y0])
    invcov = np.linalg.inv(cov)
    
    delta = np.array([x,y]) - mu
    return np.exp(-0.5*(np.log(y/(m*x))**2)/sig**2 - 0.5*np.dot(delta, np.dot(invcov, delta))) / y

#####


def approx(m, sig, x0, y0, cov):

    det = np.sqrt(1./(cov[0,0]*cov[1,1] - cov[1,0]*cov[0,1]))

    I0 = 1.
    Ixx = cov[0,0]
    Ixy = cov[0,1]
    Iyy = cov[1,1]

#    Ixxxx = 3*cov[0,0]**2
#    Ixxxy = 3*cov[0,0]*cov[0,1]
#    Ixxyy = (2*cov[0,1]**2 + cov[0,0]*cov[1,1])
#    Ixyyy = 3*cov[1,1]*cov[0,1]
#    Iyyyy = 3*cov[1,1]**2

    theLog = np.log(y0/(m*x0))
    theExp = np.exp(-0.5*theLog**2/sig**2)

    K0 = theExp

    Kxx = -theExp*(sig**2 + sig**2*theLog - theLog**2) / (np.sqrt(2*np.pi)*sig**5**y0*x0**2)
    Kyy = theExp*(-sig**2 + +2*sig**4 + 3*sig**2*theLog + theLog**2) / (np.sqrt(2*np.pi)*sig**5*y0**3)
    Kxy = theExp*(-sig**2 + sig**2*theLog + theLog**2) / (np.sqrt(2*np.pi)*sig**5*x0*y0**2)

#    Kxxxx = theExp*(3*sig**4 - 11*sig**6 - 6*sig**4*(-3+sig**2)*theLog + sig**2*(-6+11*sig**2)*theLog**2 - 6*sig**2*theLog**3 + theLog**4)/(sig**8*x0**4)
#    Kyyyy = theExp*(3*sig**4 - 11*sig**6 + 6*sig**4*(-3+sig**2)*theLog + sig**2*(-6+11*sig**2)*theLog**2 + 6*sig**2*theLog**3 + theLog**4)/(sig**8*y0**4)
#    Kxxxy = theExp*(sig**4*(-3+2*sig**2) - 9*sig**4*theLog - 2*sig**2*(-3+sig**2)*theLog**2 + 3*sig**2*theLog**3 - theLog**4) / (sig**8*x0**3*y0)
#    Kxyyy = theExp*(sig**4*(-3+2*sig**2) + 9*sig**4*theLog - 2*sig**2*(-3+sig**2)*theLog**2 - 3*sig**2*theLog**3 - theLog**4) / (sig**8*x0*y0**3)
#    Kxxyy = theExp*(sig**4*(3+sig**2) - sig**2*(6+sig**2)*theLog**2 + theLog**4)/(sig**8*x0**2*y0**2)


    return K0*I0 + 0.5*(Kxx*Ixx + Kyy*Iyy + 2*Kxy*Ixy) 

#+ (Kxxxx*Ixxxx + 4*Kxxxy+Ixxxy + 6*Kxxyy*Ixxyy + 4*Kxyyy*Ixyyy + Kyyyy*Iyyyy)/(4*3*2)

###########

def logN(m, sig, x, y):

    return np.exp(-0.5*(np.log(y/(m*x))**2)/sig**2) / (y*sig*np.sqrt(2*np.pi))


########################


def MCInt(m, sig, x0, y0, cov, npoints = 100000, mult = 5.):


    def integrand(y, x):

        #centered on x0,y0, delta around that 

        e1 = np.exp(pymc.lognormal_like(y+y0, np.log(m*(x+x0)), 1./sig**2))
        e2 = np.exp(pymc.mv_normal_cov_like(np.array([x,y]), np.array([0,0]), cov))
        return e1*e2

    sqrcov = np.sqrt(cov)

    xs = np.random.uniform(- mult*sqrcov[0,0], mult*sqrcov[0,0], size=npoints)
    ys = np.random.uniform(- mult*sqrcov[1,1], mult*sqrcov[1,1], size=npoints)

    return np.sum(np.array([integrand(cy,cx) for (cy,cx) in zip(ys,xs)]))/npoints



##################

def dic(mcmc, burn):



    # Find mean deviance
    nsamples = len(mcmc.deviance.trace()[burn:])
    deviances = np.zeros(nsamples)
    for i in range(burn, nsamples):
        mcmc.remember(i)
        deviances[i] = -2*mcmc.yhat.logp
    mean_deviance = np.mean(deviances)

    
    # Set values of all parameters to their mean
    for stochastic in mcmc.stochastics:

        # Calculate mean of paramter
        mean_value = np.mean(stochastic.trace()[burn:])

        # Set current value to mean
        stochastic.value = mean_value

    
    for i, cluster in enumerate(mcmc.xmasses.keys()):
        aveXmass = np.mean(mcmc.xmasses[cluster])
        aveYmass = np.mean(mcmc.ymasses[cluster])
        dist = (mcmc.xmasses[cluster] - aveXmass)**2 + (mcmc.ymasses[cluster] - aveYmass)**2
        index = np.arange(len(mcmc.xmasses[cluster]))[dist == np.min(dist)]
        mcmc.data_indexs[i].value = index
        
        
    

    # Calculate deviance at the means    
    deviance_at_mean = -2*mcmc.yhat.logp

    # Return twice deviance minus deviance at means
    return 2*mean_deviance - deviance_at_mean
