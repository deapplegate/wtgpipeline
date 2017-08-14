#######
# Plot a residual histogram from a shape distro fit
######


import glob, os, re, cPickle
import numpy as np, pymc
import matplotlib, pylab
import ldac, banff, banff_tools, voigt_tools as vtools
import shapedistro as sd
from shapedistro_residuals import *



#######################

def residual(g, g_true, m, c, distro, bins = 101, range=(-5,5), subset = 5000, **othervars):

    fig = pylab.figure()
    ax = fig.add_axes([0.12, 0.14, 0.95 - 0.12, 0.95 - 0.14])

    nhistos = len(m)
    
    random_subset = np.random.randint(0, nhistos, subset)


    g_range = np.arange(range[0], range[1], 0.01)

    for i in random_subset:

        args = {}
        for key, vals in othervars.iteritems():
            args[key] = vals[i]
        
        pylab.plot(g_range, distro(g_range, **args), 'k-', alpha=0.01)

    

    all_histos = []
    for i in random_subset:

        delta = g - (1+m[i])*g_true - c[i]

        counts, edges = np.histogram(delta, bins, range)

        all_histos.append(counts)

    stacked_histos = np.sort(np.column_stack(all_histos))

    median_histo = stacked_histos[:,subset/2]

    low_histo = stacked_histos[:,int(.165*subset)]
    
    high_histo = stacked_histos[:,subset - int(.165*subset)]

    low_range = min(low_histo) / 10
    high_range = max(high_histo) * 4

    

    nonzero = low_histo > 0

    width = edges[1:] - edges[:-1]
#    width = edges[1] - edges[0]
#    pylab.bar(edges[:-1][nonzero], 
#              median_histo[nonzero], 
#              width = width, bottom = low_range)
#   

    histo_norm = (width*median_histo).sum()

    median_histo = median_histo/ histo_norm
    
#    pylab.errorbar(edges[:-1][nonzero] + width[nonzero]/2., 
#                   median_histo[nonzero], 
#                   np.array([(median_histo - low_histo)[nonzero], 
#                             (high_histo - median_histo)[nonzero]])/histo_norm,
#                   fmt = 'rs', ecolor='r', capsize=10)
#  
    pylab.plot(edges[:-1][nonzero] + width[nonzero]/2., 
                   median_histo[nonzero], 
                   'rs')
    
  
    upperlimit = np.logical_and(low_histo == 0, high_histo > 0)
  
    if upperlimit.any():
  
        pylab.errorbar(edges[:-1][upperlimit] + width[upperlimit]/2., 
                       high_histo[upperlimit], 
                       fmt = 'ro', uplims = True, ecolor='r', capsize=10)
        
  
    

    pylab.gca().set_yscale('log')
    pylab.gca().set_ylim(low_range, high_range)

    pylab.ylabel(r'$P(\delta g)$')
    pylab.xlabel(r'$\hat g - (1+m)g - c$')
    


####################

def quickCheckBurn(base, catdir, outputdir, shapemodel):

    #base includes everything except the last .i.cat/out to demark which chain


    cat = ldac.openObjectFile('%s/%s.cat' % (catdir, base))

    outputfiles = glob.glob('%s/%s.*.out' % (outputdir, base))

    mcmcs = [loadResult(cat, resfile, shapemodel) for resfile in outputfiles]

    for mcmc in mcmcs:

        pylab.plot(np.arange(len(mcmc.trace('logp_trace')[:])), mcmc.trace('logp_trace')[:], 
                   linestyle='None', marker = ',')

######################

def bootstrapMean(set, nboot=1000):

    means = []
    for i in range(nboot):
        boot = np.random.randint(0, len(set), len(set))
        bootset = set[boot]
        means.append(np.mean(bootset))

    means = np.array(means)
    mu = np.mean(means)
    hpd = pymc.utils.hpd(means, 0.32)

    return mu, hpd

###

def convertHPD2Err(means, hpds):

    errs = np.zeros((2, len(means)))
    errs[0,:] = hpds[:,1] - means
    errs[1,:] = means - hpds[:,0]

    return errs

########################

def publicationParamsSNRatio(cats1, psfRes1, labels, vars, cats2, psfRes2, colors = '#FF0000 #2424AC'.split(), linestyle1='-', marker1 = 'o', linestyle2=':', marker2='None', legend = True):


    pylab.rcParams.update({'axes.labelsize' : 16})

    golden_mean = (np.sqrt(5) - 1)/2.0
    fig_width = 5
    fig_height = fig_width*golden_mean*len(vars)
    fig_size = [fig_width,fig_height]

    fig = pylab.figure(figsize = fig_size)

    xmargin = 0.18
    ymargin = 0.1
    ystop = 0.97
    totalylength = ystop - ymargin
    ystep = totalylength / len(vars)

    cur_axis = None
    axes = []

    for plotnum, var in enumerate(vars):

        modelvar, labelvar = var

        cur_axis = pylab.axes([xmargin, ystop - (plotnum+1)*ystep , 
                               0.95 - xmargin, ystep ], sharex = cur_axis)
        axes.append(cur_axis)

        for cat, psf, label, color in zip(cats1, psfRes1, labels, colors):

            snpoints = []
            snminmax = []
            means = []
            hpds = []
            sigs = []

            for i in range(len(cat.keys())):

                bincat = cat[(i,)]
                bin = psf[(i,)]
                
                snpoints.append(np.median(bincat['snratio']))
                snminmax.append((np.min(bincat['snratio']), np.max(bincat['snratio'])))

                samples = bin[modelvar]

                mu = np.mean(samples)
                sig = np.std(samples)
                hpd = pymc.utils.hpd(samples, 0.32)

                means.append(mu)
                sigs.append(sig)
                hpds.append(hpd)


            snerrs = np.array(snminmax).T - np.array(snpoints)

            snerrs[0,:] = -snerrs[0,:]
            print '!!!!'
            print snpoints
            print snerrs

            means = np.array(means)
            hpds = np.array(hpds)
            sigs = np.array(sigs)

            weights = 1./sigs**2
            avgCor = (means[1:]*weights[1:]).sum()/weights[1:].sum()
            sigCor = np.sqrt(1./weights[1:].sum())

            errs = convertHPD2Err(means, hpds)

            cur_axis.errorbar(snpoints, means, errs, color = color, marker=marker1,
                              linestyle = linestyle1, linewidth=0.2, label = label)

            cur_axis.set_ylabel(labelvar)
            cur_axis.set_xscale('log')
            cur_axis.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(len(cur_axis.get_yticks() - 1), prune = 'both'))

            


#    for cur_axis, var in zip(axes, vars):
#        modelvar, labelvar = var
#        for cat, psf, color in zip(cats2, psfRes2,colors):
#
#            snpoints = []
#            snminmax = []
#            means = []
#            hpds = []
#            sigs = []
#
#            for i in range(len(cat.keys())):
#
#                bincat = cat[(i,)]
#                bin = psf[(i,)]
#                
#                snpoints.append(np.median(bincat['snratio']))
#                snminmax.append((np.min(bincat['snratio']), np.max(bincat['snratio'])))
#
#                samples = bin[modelvar]
#
#                mu = np.mean(samples)
#                sig = np.std(samples)
#                hpd = pymc.utils.hpd(samples, 0.32)
#
#                means.append(mu)
#                sigs.append(sig)
#                hpds.append(hpd)
#
#
#            snerrs = np.array(snminmax).T - np.array(snpoints)
#
#            snerrs[0,:] = -snerrs[0,:]
#            print '!!!!'
#            print snpoints
#            print snerrs
#
#            means = np.array(means)
#            hpds = np.array(hpds)
#            sigs = np.array(sigs)
#
#            weights = 1./sigs**2
#            avgCor = (means[1:]*weights[1:]).sum()/weights[1:].sum()
#            sigCor = np.sqrt(1./weights[1:].sum())
#
#            errs = convertHPD2Err(means, hpds)
#
#            cur_axis.plot(snpoints, means, color = color, marker=marker2,
#                              linestyle = linestyle2, linewidth=0.5)
#
#        
#    cur_axis.set_xlabel('Shape Signal to Noise')
#    pylab.xticks([6, 8,10,20,40], [6, 8,10,20,40])
#    cur_axis.set_xlim((snpoints[0] - 1, snpoints[-1]+8))
#
#    if legend:
#        cur_axis.legend(numpoints = 1, scatterpoints = 1, loc='center right')
#
        
    return fig, snpoints, means, errs



##############################

def publicationParamsSize(cats1, psfRes1, labels, vars, cats2, psfRes2, colors = '#FF0000 #2424AC'.split(), linestyle1='-', marker1 = 'o', linestyle2=':', marker2='None', legend = True):


    pylab.rcParams.update({'axes.labelsize' : 16})

    golden_mean = (np.sqrt(5) - 1)/2.0
    fig_width = 5
    fig_height = fig_width*golden_mean*len(vars)
    fig_size = [fig_width,fig_height]

    fig = pylab.figure(figsize = fig_size)

    xmargin = 0.18
    ymargin = 0.1
    ystop = 0.97
    totalylength = ystop - ymargin
    ystep = totalylength / len(vars)

    cur_axis = None
    axes = []

    for plotnum, var in enumerate(vars):

        modelvar, labelvar = var

        cur_axis = pylab.axes([xmargin, ystop - (plotnum+1)*ystep , 
                               0.95 - xmargin, ystep ], sharex = cur_axis)
        axes.append(cur_axis)

        for cat, psf, label, color in zip(cats1, psfRes1, labels, colors):

            snpoints = []
            snminmax = []
            means = []
            hpds = []
            sigs = []

            for i in range(len(cat.keys())):

                bincat = cat[(i,)]
                bin = psf[(i,)]
                
                snpoints.append(np.median(bincat['size']))
                snminmax.append((np.min(bincat['size']), np.max(bincat['size'])))

                samples = bin[modelvar]

                mu = np.mean(samples)
                sig = np.std(samples)
                hpd = pymc.utils.hpd(samples, 0.32)

                means.append(mu)
                sigs.append(sig)
                hpds.append(hpd)


            snerrs = np.array(snminmax).T - np.array(snpoints)

            snerrs[0,:] = -snerrs[0,:]
            print '!!!!'
            print snpoints
            print snerrs

            means = np.array(means)
            hpds = np.array(hpds)
            sigs = np.array(sigs)

            weights = 1./sigs**2
            avgCor = (means[1:]*weights[1:]).sum()/weights[1:].sum()
            sigCor = np.sqrt(1./weights[1:].sum())

            errs = convertHPD2Err(means, hpds)

            cur_axis.errorbar(snpoints, means, errs, color = color, marker=marker1,
                              linestyle = linestyle1, linewidth=0.2, label = label)

            cur_axis.set_ylabel(labelvar)
            cur_axis.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(len(cur_axis.get_yticks() - 1), prune = 'both'))




#    for cur_axis, var in zip(axes, vars):
#        modelvar, labelvar = var
#        for cat, psf, color in zip(cats2, psfRes2,colors):
#
#            snpoints = []
#            snminmax = []
#            means = []
#            hpds = []
#            sigs = []
#
#            for i in range(len(cat.keys())):
#
#                bincat = cat[(i,)]
#                bin = psf[(i,)]
#                
#                snpoints.append(np.median(bincat['size']))
#                snminmax.append((np.min(bincat['size']), np.max(bincat['size'])))
#
#                samples = bin[modelvar]
#
#                mu = np.mean(samples)
#                sig = np.std(samples)
#                hpd = pymc.utils.hpd(samples, 0.32)
#
#                means.append(mu)
#                sigs.append(sig)
#                hpds.append(hpd)
#
#
#            snerrs = np.array(snminmax).T - np.array(snpoints)
#
#            snerrs[0,:] = -snerrs[0,:]
#            print '!!!!'
#            print snpoints
#            print snerrs
#
#            means = np.array(means)
#            hpds = np.array(hpds)
#            sigs = np.array(sigs)
#
#            weights = 1./sigs**2
#            avgCor = (means[1:]*weights[1:]).sum()/weights[1:].sum()
#            sigCor = np.sqrt(1./weights[1:].sum())
#
#            errs = convertHPD2Err(means, hpds)
#
#            cur_axis.plot(snpoints, means, color = color, marker=marker2,
#                              linestyle = linestyle2, linewidth=0.5)
#
#        
    cur_axis.set_xlabel('Object Size / PSF Size')
#    pylab.xticks([6, 8,10,20,40], [6, 8,10,20,40])
#    cur_axis.set_xlim((snpoints[0] - 1, snpoints[-1]+8))

    if legend:
        cur_axis.legend(numpoints = 1, scatterpoints = 1, loc='lower right')


    return fig, snpoints, means, errs        




###############################

def bentvoigtcor(g, size, pivot, m_slope, m_y, c):

    m = np.zeros_like(g)
    m[size >= pivot] = m_y
    m[size < pivot] = m_slope*(size - pivot) + m_y

    gcorr = (1+m)*g + c

    return gcorr

####

def gausscor(g, m, c):

    return (1+m)*g + c

####

def gaussprofile(x, sig):

    return np.exp(-0.5*(x/sig)**2)/(np.sqrt(2*np.pi)*sig)

####

def pubSTEPResidual(data = None):

    if data is None:
        data = {}

    if 'cat' not in data:
        data['cat'] = ldac.openObjectFile('/u/ki/dapple/ki06/shapedistro/sept2011/anja/sncut.cat')


    cat = data['cat']

    pivot = 1.97
    m_y = -.028
    m_slope = 0.20
    c = -9.6e-06


    if 'resid' not in data:


        gcorr = bentvoigtcor(cat['true_g'], cat['size'], pivot, m_slope, m_y, c)
        
        resid = cat['g'] - gcorr

        data['resid'] = resid

    else:

        resid = data['resid']

    
    xdelta = np.arange(-1.5, 1.5, 0.001)
    
    if 'vsigma' not in data:

        vdb = pymc.database.pickle.load('/u/ki/dapple/ki06/shapedistro/sept2011/anja/snrestricted.bentvoigt3.out')
        gdb = pymc.database.pickle.load('/u/ki/dapple/ki06/shapedistro/sept2011/anja/snrestricted.gauss.out')

    
        vsigma = np.mean(vdb.trace('sigma')[2000:])
        vgamma = np.mean(vdb.trace('gamma')[2000:])
        gsigma = np.mean(gdb.trace('sigma')[2000:])
        
        data['vsigma'] = vsigma
        data['vgamma'] = vgamma
        data['gsigma'] = gsigma

    else:

        vsigma = data['vsigma']
        vgamma = data['vgamma']
        gsigma = data['gsigma']


    
    fig = pylab.figure()
    ax = fig.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])
    hist, edges, patches = ax.hist(resid, bins = 151, log=True, normed=True, label='Fit Residuals', histtype='step', color='k')
    ax.plot(xdelta, vtools.voigtProfile(xdelta, vsigma, vgamma), 'r-', label='Voigt Model', linewidth=1.5)
    ax.plot(xdelta, gaussprofile(xdelta, gsigma), 'b-.', label='Gaussian Model', linewidth=1.5)

    ax.set_ylim(5e-5, 1e1)
    

    ax.set_ylabel(r'$P(\delta g)$')
    ax.set_xlabel(r'Shear Residual $\delta g$')

    ax.legend(loc='lower center', numpoints=1)


    fig.savefig('publication/step_scatter.eps')


    return fig, data


#################################

def pubBModeResidual(data = None):

    if data is None:
        data = {}

    if 'bmodes' not in data:
        data['bmodes'] = cPickle.load(open('bmodes.pkl', 'rb'))


    bmodes = data['bmodes']
    
    xdelta = np.arange(-1.5, 1.5, 0.001)
    
    if 'vsigma' not in data:

        gsigma = np.std(bmodes)

        vmodel = sd.VoigtModel(None, None, bmodes, np.zeros_like(bmodes))
        map = pymc.MAP(vmodel)
        map.fit()

        vsigma = map.sigma.value
        vgamma = map.gamma.value

        
        data['vsigma'] = vsigma
        data['vgamma'] = vgamma
        data['gsigma'] = gsigma

    else:

        vsigma = data['vsigma']
        vgamma = data['vgamma']
        gsigma = data['gsigma']


    
    fig = pylab.figure()
    ax = fig.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])
    hist, edges, patches = ax.hist(bmodes, bins = 151, range=(-1.5, 1.5), log=True, normed=True, label='B-Modes from 27 Cluster Fields', histtype='step', color='k')
    ax.plot(xdelta, vtools.voigtProfile(xdelta, vsigma, vgamma), 'r-', label='Voigt Model', linewidth=1.5)
    ax.plot(xdelta, gaussprofile(xdelta, gsigma), 'b-.', label='Gaussian Model', linewidth=1.5)

    ax.set_ylim(5e-5, 1e1)
    

    ax.set_ylabel(r'$P(g_X)$')
    ax.set_xlabel(r'Shear B-mode $g_X$')

    ax.legend(loc='lower center', numpoints=1)


    fig.savefig('publication/data_bmode_scatter.eps')


    return fig, data


    
    
