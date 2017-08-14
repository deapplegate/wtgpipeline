#######################
# Implements a floating Voigt shapedistro profile [as one bin]
# with a PSF dependent M correction
#######################


import numpy as np, pymc
import nfwmodeltools, maxlike_masses as maxlike

#######################


class FloatVoigtShapedistro(maxlike.LensingModel):

    def __init__(self):

        maxlike.LensingModel.__init__(self)

        self.likelihood_func = nfwmodeltools.voigt_like

    
    ############

    def bin_selectors(self, cat):

        bins = [cat['snratio'] > 3]

        return bins

    #############

    def calcMC(self, data):

        psfSize = 2*data.psfsize * data.pixscale

        if psfSize >= 0.8:
            m = -0.064
            c = 0.0009
        elif psfSize <= 0.6:
            m = -0.090
            c = 0.0004
        else:
            m = 0.13*(psfSize - 0.6) - 0.09
            c = 0.0025*(psfSize - 0.6) + 0.0004

        return m,c

    #############

    def makeShapePrior(self, data, parts):

        #need to return a list despite having just one bin

        #assuming that nothing has covariance



        #m c sigma gamma

        m, c = self.calcMC(data)
        
        parts.shape_param_priors = np.empty((1,4), dtype=object)
        parts.shape_params = np.empty((1,), dtype=object)

        #DAMN PYMC EXCEPTS TAU NOT SIGMA!
        parts.shape_param_priors[0,0] = pymc.Normal('shape_param_0_0', m, 1./(0.05**2))  #shearcal_m
        parts.shape_param_priors[0,1] = pymc.Normal('shape_param_0_1', c, 1./(0.0004**2)) #shearcal_c
        parts.shape_param_priors[0,2] = pymc.Uniform('shape_param_0_2', 0.15, 0.2) #sigma
        parts.shape_param_priors[0,3] = pymc.Uniform('shape_param_0_3', 0.003, 0.1) #gamma

        @pymc.deterministic(name = 'shape_param_%d', trace = False)
        def sp(params = parts.shape_param_priors[0,:]):
            
                return np.hstack(params)

        parts.shape_params[0] = sp

            

    ###############

    def sampler_callback(self, mcmc):

        mcmc.use_step_method(pymc.AdaptiveMetropolis, mcmc.shape_param_priors, shrink_if_necessary = True)

            
