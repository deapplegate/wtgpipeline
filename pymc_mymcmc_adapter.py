###############################
# Convert a pymc model to something runnable by
#    mymc.
###############################

import numpy as np
from mpi4py import MPI
import pymc, mymc, maxlike_masses as mm


###############################

class CompositeParameter(mymc.Parameter):
    def __init__(self, masterobj, index, width = 0.1):
        self.masterobj = masterobj
        self.index = index
        self.name = '%s_%d' % (self.masterobj.__name__, self.index)

        self.width = width*np.abs(self())

    def get_value(self):
        return self.masterobj.value[self.index]

    def set(self, value):
        curval = np.copy(self.masterobj.value)   #to not disturb pymc caching mechanism
        curval[self.index] = value
        self.masterobj.value = curval

    value = property(get_value, set)


##############################

class WrapperParameter(mymc.Parameter):
    def __init__(self, masterobj, width = 0.1):
        self.masterobj = masterobj
        self.name = self.masterobj.__name__

        self.width = width*np.abs(self())

    def get_value(self):
        return self.masterobj.value

    def set(self, value):
        self.masterobj.value = value

    value = property(get_value, set)




#################################

class DerivedWrappedParameter(mymc.DerivedParameter):
    def __init__(self, masterobj):
        self.masterobj = masterobj
        self.name = self.masterobj.__name__
    def get_value(self):
        return self.masterobj.value
    value = property(get_value)


##################################

class DerivedAttribute(mymc.DerivedParameter):
    def __init__(self, masterobj, attr):
        self.masterobj = masterobj
        self.attr = attr
        self.name = self.attr
    def get_value(self):
        return getattr(self.masterobj, self.attr)
    value = property(get_value)
        
#################################


class MyMCRunner(object):

    def run(self, manager):

        self.mpi_rank = MPI.COMM_WORLD.Get_rank()

        parameters = []
        deterministics = []

        model = manager.model
        options = manager.options


        for s in model.stochastics:
            if s.observed:
                continue

            if s.value.shape == ():

                print s.__name__, ' single'
                parameters.append(WrapperParameter(s))

            else:
                print s.__name__, ' multiple ', len(s.value)
                for i in np.arange(len(s.value)):
                    parameters.append(CompositeParameter(s, i))
            
        for d in model.deterministics:
            if d.keep_trace:
                deterministics.append(DerivedWrappedParameter(d))

        deterministics.append(DerivedAttribute(model, 'logp'))

        def posterior(thing):
            try:
                logp = model.logp
            except pymc.ZeroProbability:
                logp = -np.infty
            return logp

        space = mymc.ParameterSpace(parameters, posterior)

        trace = mymc.ParameterSpace(deterministics + parameters)

        step = mymc.Slice()

        updater = mymc.MultiDimSequentialUpdater(space, step, options.adapt_every, options.adapt_after, parallel = MPI.COMM_WORLD)

        manager.engine = mymc.Engine([updater], trace)

        manager.chainfile = open('%s' % options.outputFile, 'w')
        manager.textout = mymc.headerTextBackend(manager.chainfile, trace)

        manager.chain = mymc.dictBackend()


        
        backends = [manager.textout, manager.chain]

        manager.engine(options.nsamples, None, backends)
                                     
                    


    ############

    def addCLOps(self, parser):


        parser.add_option('-s', '--nsamples', dest='nsamples',
                          help='Number of MCMC samples to draw or scan model', default=None, type='int')
        parser.add_option('--adaptevery', dest='adapt_every',
                          help = 'Adapt MCMC chain every X steps', default = 100, type='int')
        parser.add_option('--adaptafter', dest='adapt_after',
                          help = 'Start adapting MCMC chain aftter X steps', default = 100, type='int')
        parser.add_option('--burn', dest='burn',
                          help='Number of MCMC samples to discard before calculated mass statistics', 
                          default=10000, type=int)




    #############

    def dump(self, manager):

        mm.dumpMasses(np.array(manager.chain['mass_15mpc'][manager.options.burn:]), '%s.mass15mpc' % manager.options.outputFile)

    
    #############

    def finalize(self, manager):

        manager.chainfile.close()
