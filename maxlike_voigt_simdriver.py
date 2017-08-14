#!/usr/bin/env python
####################
# Example driver for maxlike sim masses
####################

import maxlike_controller, maxlike_masses, nfwmodel_voigtnorm_shapedistro, maxlike_sim_filehandler
import numpy as np, pymc

###################################

nvs = nfwmodel_voigtnorm_shapedistro.VoigtnormShapedistro()

    

def makeSplitPrior(parts):

    parts.shape_params = np.empty(parts.nshapebins, dtype=object)
    parts.shape_params_mv = np.empty(parts.nshapebins, dtype=object)
    parts.shape_params_fixed = np.empty(parts.nshapebins, dtype=object)

    for i, shapeparams in enumerate(parts.shapedistro_params):

        parts.shape_params_mv[i] = pymc.MvNormalCov('shape_params_mv_%d' % i,
                                                    shapeparams[1],
                                                    shapeparams[2], trace=False)

        parts.shape_params_fixed[i] = shapeparams[0]

        @pymc.deterministic(name='shape_params_%d' % i, trace=True)
        def sp(fixed = parts.shape_params_fixed[i], mv = parts.shape_params_mv[i]):

            return np.hstack([fixed, mv])

        parts.shape_params[i] = sp





##################

class SimVoigtShapeDistro(object):

    def __init__(self):

        self.likelihood_func = nvs.likelihood_func

        self.mu = np.array([0.18, 0.016])
        self.cov = nvs.shape_params[4][1][2:4,2:4]
        self.fixed = np.array([0.,0.])
        
        self.shape_params = [[self.fixed, self.mu, self.cov]]
        

        self.makeShapePrior = makeSplitPrior

    ########################


    def sampler_callback(self, mcmc):

        mcmc.use_step_method(pymc.AdapticeMetropolis, mcmc.shape_params_mv[0], cov = self.cov,shrink_if_necessary = True)


    #########################

    def bin_selectors(self, cat):

        return [np.ones(len(cat)) == 1]

    #########################

    def addOffsetCallback(self, option, opt, value, parser):

        self.mu += np.array(value)
        
        

    ########################

    def addCLOps(self, parser):

        parser.add_option('--offset', help='offsets applied to shape distributions [sigma gamma]. Expects 2 floats',
                          action='callback', callback=self.addOffsetCallback, type='float', nargs=2)


    


###############################


controller = maxlike_controller.Controller(modelbuilder = maxlike_masses,
                                           shapedistro = SimVoigtShapeDistro(),
                                           filehandler = maxlike_sim_filehandler,
                                           runmethod = maxlike_masses.ScanModelToFile())


###############################

if __name__ == '__main__':

    controller.run_all()




