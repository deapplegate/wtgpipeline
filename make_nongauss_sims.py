import cosmos_sim as cs
import cPickle
import shapedistro, shapedistro_residuals as sdr
import voigt_tools as voigt

bpz = ldac.openObjectFile('cosmos.2011-03-01.cat', 'STDTAB')

input = open('cosmos.parsed.2011-03-01.pdz.pkl', 'rb')
pdzrange, pdzs = cPickle.load(input)
input.close()

shapedistro_cats = sdr.loadMasterCats('/u/ki/dapple/ki06/shapedistro/psfC/twocomps/g1', 'master')
shapedistro_results = sdr.loadResults('/u/ki/dapple/ki06/shapedistro/psfC/twocomps/g1', 'master', shapedistro_cats, shapedistro.VoigtModel)
shapedistro_datavec, shapedistro_rowvecs = sdr.compileDatavector(shapedistro_results,
                                                                 'shearcal_m shearcal_c sigma gamma'.split(),
                                                                 800)



cosmos = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos.cat')
mcosmos = cs.matchById(bpz, cosmos, 'SeqNr', 'id')

cosmos30 = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos30.cat')
mcosmos30 = cs.matchById(bpz, cosmos30, 'SeqNr', 'ID')

fields = [ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/simulations/2011-03-01/field_%d.cat' % i) for i in range(100)]



class BinnedShapeSamples(object):

    def __init__(self, shapedistro, bin_selectors, distro_kwds = None):

        self.shapedistro = shapedistro
        self.bin_selectors = bin_selectors
        self.func_name = shapedistro.func_name
        self.distro_kwds = distro_kwds

        if self.distro_kwds = None:
            self.shapedistro_kwds = inspect.getargspec(self.shapedistro)[0]



    def __call__(self, g, cat, binparams, mkey = 'shearcal_m', ckey = 'shearcal_c'):

        ghats = np.zeros_like(g)

        inbins = self.bin_selectors(cat)

        for inbin, (key, binparam) in zip(inbins, binparams.iteritems()):
            

            nsamples = len(g[inbin])

            binparam['size'] = nsamples
            
                
            delta_gs = self.shapedistro(*[binparam[x] for x in self.shapedistro_kwds])

            m = binparam[mkey]
            c = binparam[ckey]

            ghats[inbin] = delta_gs + (1+m)*g[inbin] + c

        return ghats

            




def makeNonGaussSims(zs, rsrange, outputdir):

    nsamples = len(fields)
    
    shapedistro_samples = sdr.selectPosteriorSamples(shapedistro_datavec, nsamples)

    binned_distro = BinnedShapeSamples(voigt.voigtSamples, 
                                       voigtdistro.bin_selectors, 
                                       'sigma gamma size'.split())


    cs.createCutoutSuite(zs, 
                      rsrange, 
                      bpz, 
                      None,
                      None,
                      pdzrange, 
                      pdzs, 
                      outputdir, 
                      simcats = fields,
                      sourcecat = None,
                      shape_distro = 
                      shape_distro_kw_sets = 30*[{'sigma' : 0.25}]):
