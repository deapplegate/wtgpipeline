#!/usr/bin/env python
########################

import os
import numpy as np, pymc
import varcontainer

########################


class IntrinsicScatter(object):

    ##############
    
    def __init__(self, x, y, ysigma, norm=1e15):

        self.x = x/norm
        self.y = y/norm
        self.ysigma = ysigma/norm


        self.buildPriors()
        self.ratioLikelihood()

    ##############

    def buildMCMC(self, filename = None):

        if filename is None:
            mcmc = pymc.MCMC(self)
        elif os.path.exists(filename):
            mcmc = pymc.MCMC(self, db = pymc.database.pickle.load(filename))
        else:
            mcmc = pymc.MCMC(self, db = 'pickle', dbname = filename)

        return mcmc

    ##############
        
    def buildPriors(self):

        self.log10_intrinsic_scatter = pymc.Uniform('log10_intrinsic_scatter', -4, 0)

        @pymc.deterministic(name = 'intrinsic_sigma')
        def intrinsic_sigma(log10_scatter = self.log10_intrinsic_scatter):
            return 10**log10_scatter

        self.intrinsic_sigma = intrinsic_sigma


    ###########################

    def ratioLikelihood(self):

        self.m_angle = pymc.Uniform('m_angle', np.pi/8, 3*np.pi/8.)
    
        @pymc.deterministic(name = 'm')
        def m(m_angle = self.m_angle):
            return np.tan(m_angle)

        self.m = m

        @pymc.potential(name = 'yhat')
        def yhat(x = self.x, y = self.y, ysigma = self.ysigma,  m = self.m, sigma = self.intrinsic_sigma):
            yhat = m*x
            return np.sum([pymc.normal_like(yhat[i], y[i], 1./(ysigma[i]**2 + sigma**2)) for i in range(len(y))])
        self.yhat = yhat

    
    
##############################


    

    
