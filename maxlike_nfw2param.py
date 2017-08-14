#!/usr/bin/env python
#######################
# Run a ML pdz fit for an nfw model
########################

from __future__ import with_statement
import cPickle
import numpy as np, pymc, pyfits
import nfwmodel2param as tools, varcontainer
import nfwutils, shearprofile as sp, ldac
import maxlike_bentstep_voigt as mbv
import maxlike_masses

##########################


class NFW2Param(mbv.BentVoigtShapedistro):

    def makeModelPrior(self, manager, parts):

        super(NFW2Param, self).makeModelPrior(manager, parts)

        parts.amp = pymc.Uniform('amp', 0.05, 1.2)


    def makeLikelihood(self, datamanager, parts):

        inputcat = datamanager.inputcat

        pdz = datamanager.pdz

        parts.r_mpc = np.ascontiguousarray(inputcat['r_mpc'].astype(np.float64))
        parts.ghats = np.ascontiguousarray(inputcat['ghats'].astype(np.float64))
        parts.pdz = np.ascontiguousarray(pdz.astype(np.float64))


        parts.D_lens = nfwutils.angulardist(datamanager.zcluster)


        parts.zcluster = datamanager.zcluster
        parts.pdzrange = datamanager.pdzrange

        parts.betas = np.ascontiguousarray(nfwutils.beta_s(parts.pdzrange, parts.zcluster).astype(np.float64))
        parts.nzbins = len(parts.betas)


        parts.data = None
        for i in range(10):

            try:

                @pymc.stochastic(observed=True, name='data_%d' % i)
                def data(value = parts.ghats, 
                         amp = parts.amp,
                         log_r_scale = parts.log_r_scale,
                         shearcal_m = parts.shearcal_m,
                         shearcal_c = parts.shearcal_c,
                         sigma = parts.sigma,
                         gamma = parts.gamma,
                         r_mpc = parts.r_mpc, 
                         pdz = parts.pdz, 
                         betas = parts.betas):
                    
                    
                    return tools.bentvoigt_like(log_r_scale, 
                                                r_mpc, 
                                                value, 
                                                betas, 
                                                pdz, 
                                                shearcal_m,
                                                shearcal_c,
                                                sigma,
                                                gamma,
                                                amp)





                parts.data = data


                break
            except pymc.ZeroProbability:
                pass

        if parts.data is None:
            raise ModelInitException


##########################################
##########################################

class SampleModelToFile(maxlike_masses.SampleModelToFile):

    
    def run(self, manager):


        model = manager.model
        nsamples = manager.options.nsamples
        outputFile = manager.options.outputFile
        burn = manager.options.burn


        manager.mcmc = pymc.MCMC(input = model, db='pickle', dbname=outputFile)


        try:
            manager.shapedistro.sampler_callback(mcmc)
        except:
            #doesn't have it, doesn't matter
            pass


        manager.mcmc.sample(nsamples)

        manager.masses = np.array([ nfwutils.massInsideR_amp(np.exp(manager.mcmc.trace('log_r_scale')[i:i+1]),
                                                             manager.mcmc.trace('amp')[i:i+1],
                                                             manager.mcmc.zcluster,
                                                             manager.r500)[0] \
                                        for i in range(burn, nsamples)])
        



