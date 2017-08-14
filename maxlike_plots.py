####################
# Plots for interpreting Maxlike Mass Results
####################

from __future__ import with_statement
import os, subprocess, cPickle
import numpy as np, pylab, pymc
import scipy.linalg as linalg
import matplotlib.patches as patches
import maxlike_masses as mm
import nfwmodel_voigtnorm_shapedistro as voigtnorm
import maxlike_subaru_filehandler as msf
import nfwutils, shearprofile as sp


#####################


def loadMCMC(resfile, inputcat, pdzrange, pdz, clusterdata, shapedistro):

    goodObjs = mm.createFilter(inputcat, pdzrange, pdz, clusterdata)

    model = mm.createModel(inputcat = inputcat, 
                           pdzrange = pdzrange, 
                           pdz = pdz, 
                           goodObjs = goodObjs, 
                           shapedistro = shapedistro, 
                           clusterdata = clusterdata)

    db = pymc.database.pickle.load(resfile)

    mcmc = pymc.MCMC(input = model, db = db)

    return mcmc

######################

def plotEllipseFromCov(center, cov, color, axes = pylab.gca(), zeroAxis=False):

    D = linalg.inv(-cov)

    w, vec = linalg.eigh(D)

    rmaj = np.sqrt(2.3/-w[1])   #delta Chisq = 2.3 for nu = 2, 1 sigma contour, 6.17 for 2 sigma
    rmin = np.sqrt(2.3/-w[0])

    theta = np.arctan2(vec[1,1], vec[0,1])

    print 'theta: %f' % (theta*180/np.pi)

    ellip = patches.Ellipse(center, 2*rmaj, 2*rmin, angle = theta*180/np.pi)

    axes.add_artist(ellip)
    ellip.set_facecolor('none')
    ellip.set_edgecolor(color)


    pylab.plot([center[0]], [center[1]], marker='x', markerfacecolor=color, markeredgecolor = color, axes = axes)

    
#    if zeroAxis:
#        axis = [np.inf, None, np.inf, None]
#    else:
#        axis = axes.axis()
#
#    x_width = max(np.abs(np.cos(theta)*rmaj), np.abs(np.cos((np.pi/2.) - theta)*rmin))
#    y_width = max(np.abs(np.sin(theta)*rmaj), np.abs(np.sin((np.pi/2.) - theta)*rmin))
#
#    print vec[0]
#    print theta
#    print center[0] - 1.15*x_width, center[0] + 1.15*x_width
#    print axis[0], axis[1]
#    print
#    print
#    
#    newaxis = [ min(axis[0], center[0] - 1.15*x_width),
#                max(axis[1], center[0] + 1.15*x_width),
#                min(axis[2], center[1] - 1.15*y_width),
#                max(axis[3], center[1] + 1.15*y_width)]
#
#    axes.axis(newaxis)
#    axes.figure.show()
#    return ellip, x_width, y_width
    

#
#def plotCrossVarNormApprox(xsamples, ysamples,color, axes = pylab.gca(), zeroAxis=False):
#
#
#    datavec = np.vstack([xsamples, ysamples])
#
#    center = np.mean(datavec, axis=-1)
#
#    cov = np.cov(datavec)
#
#    return plotEllipseFromCov(center, cov, color, axes, zeroAxis=zeroAxis)
#
#
#    
#####################################
#
#def plotNormPriorCrossValSummary(bintraces, shapedistro, outputPrefix = None):
#
#    for bincount, bin in enumerate(bintraces):
#
#        prior_mu, prior_cov = shapedistro.shape_params[bincount]
#
#        prior_samples = np.random.multivariate_normal(prior_mu, prior_cov, 100000)
#        
#        fig = pylab.figure()
#        
#        nvars = bin.shape[1]
#        ngraphs = nvars - 1
#
#        varranges = {}
#        for i in range(nvars):
#            varranges[i] = [np.inf,None]
#
#        for i in range(ngraphs):
#            for j in range(ngraphs):
#                
#                if i > j:
#                    continue
#
#                ax = fig.add_subplot(ngraphs, ngraphs, ngraphs*i + j + 1)
#
#                prior, prior_xwidth, prior_ywidth = \
#                    plotCrossVarNormApprox(prior_samples[:,j+1], prior_samples[:,i], 'b', ax, zeroAxis=True)
#
#                post, post_xwidth, post_ywidth \
#                    = plotCrossVarNormApprox(bin[:,j+1], bin[:,i], 'r', ax)
#
#                if i == j:
#                    ax.set_xlabel('Var %d' % (j+1))
#                    ax.set_ylabel('Var %d' % i)
#                                  
#
#
#
#                curlimits = ax.axis()
#                
#                varranges[i][0] = min(varranges[i][0], curlimits[2])
#                varranges[i][1] = max(varranges[i][1], curlimits[3])
#                varranges[j+1][0] = min(varranges[j+1][0], curlimits[0])
#                varranges[j+1][1] = max(varranges[j+1][1], curlimits[1])
#
#        for i in range(ngraphs):
#            for j in range(ngraphs):
#
#                if i > j:
#                    continue
#
#                ax = fig.add_subplot(ngraphs, ngraphs, ngraphs*i + j + 1)
#
#                newlimits = [varranges[j+1][0], varranges[j+1][1],
#                             varranges[i][0], varranges[i][1]]
#                ax.axis(newlimits)
#
#        ###################################
#
#
#
#
#        
#
#        ####################################
#
#        fig.text(0.15, 0.15, 'Shape Bin %d' % bincount)
#
#        if outputPrefix is not None:
#            fig.savefig('%s.b%d.png' % (outputPrefix, bincount))
#
#
#                
#                
#################################
#
#
#def resultPlot(mcmc, clusterdata, burn, outputPrefix = None):
#
#
#    fig = pylab.figure()
#
#    ax = fig.add_subplot(2, 1, 1)
#
#    ax.plot(np.arange(len(mcmc.trace('logp_trace')[:])), mcmc.trace('logp_trace')[:], 'b,')
#
#    ax.axvline(burn, color='r', linestyle=':')
#    ax.set_ylabel('Log P')
#    ax.set_xlabel('Step')
#
#
#    ax2 = fig.add_subplot(2,1,2)
#
#    masses = [ nfwutils.massInsideR(rs,
#                                    clusterdata['concentration'],
#                                    clusterdata['zcluster'],
#                                    clusterdata['r500']) \
#                   for rs in np.exp(mcmc.trace('log_r_scale')[burn:]) ]
#    
#    rpoints = -np.log(0.1)*np.random.random(500000) + np.log(0.1)
#
#    rmasses = [ nfwutils.massInsideR(rs,
#                                     clusterdata['concentration'],
#                                     clusterdata['zcluster'],
#                                     clusterdata['r500']) \
#                    for rs in np.exp(rpoints) ]
#
#    priorcounts, bins, faces = ax2.hist(rmasses, bins=100, alpha=0.3, color='b', normed=True)
#    
#    postcounts, bins, faces = ax2.hist(masses, bins=bins, alpha=0.3, color='r', ec='k', normed=True)
#    
#    ax2.set_xlabel('M500')
#
#    if outputPrefix:
#        fig.savefig('%s.a.png' % outputPrefix)
#    
#                    
#    return fig
#
#        
#
#    
#######################################
#
#class R500Exception(Exception): pass
#
#def makeClusterSummaryPlots(cluster, filter, image, workdir, resdir):
#
#    lensingdir = '/u/ki/dapple/subaru/%s/LENSING_%s_%s_aper/%s' % (cluster, filter, filter, image)
#
#    resfile = '%s/mlmass.voigtnorm.pkl' % lensingdir
#
#    inputcat, pdzrange, pdz, clusterdata = msf.readData(*msf.createOptions(cluster, filter, image))
#
#    mcmc = loadMCMC(resfile, inputcat, pdzrange, pdz, clusterdata, voigtnorm)
#
#    with open('/u/ki/dapple/subaru/clusters.r500x.dat') as input:
#        for line in input.readlines():
#            curcluster, r500 = line.split()
#            if curcluster == cluster:
#                clusterdata['r500'] = float(r500)
#                break
#    if 'r500' not in clusterdata:
#        raise R500Exception
#
#    plotdir = '%s/ml_plots' % lensingdir
#    if not os.path.exists(plotdir):
#        os.mkdir(plotdir)
#
#    bintraces = [mcmc.trace('shape_params_%d' % i)[10000:] for i in range(7)]
#
#    outputPrefix = '%s/%s' % (plotdir, cluster)
#
#    massSummaryPrefix='%s/%s.%s.%s' % (lensingdir, cluster, filter, image)
#    
#
#    plotNormPriorCrossValSummary(bintraces, voigtnorm, outputPrefix)
#                                 
#    resultPlot(mcmc, clusterdata, 10000, outputPrefix)
#    pylab.close('all')
#
#    summarizeMasses(mcmc, clusterdata, outputPrefix = massSummaryPrefix)
#
#    cmd = 'montage -size 4250x5500 %s.a.png %s.b[0-6].png -geometry 2125x2125 %s.summary.jpg' % (outputPrefix, outputPrefix, outputPrefix)
#    subprocess.check_call(cmd.split())
#
#    
#    
###########################################
#
#def summarizeMasses(mcmc, clusterdata, outputPrefix = None, burn=10000):
#
#    
#    masses = np.array([ nfwutils.massInsideR(rs,
#                                    clusterdata['concentration'],
#                                    clusterdata['zcluster'],
#                                    clusterdata['r500']) \
#                   for rs in np.exp(mcmc.trace('log_r_scale', 0)[burn:]) ])
#
#
#    mean = np.mean(masses)
#    stddev = np.std(masses)
#    quantiles = pymc.utils.quantiles(masses)
#    hpd68 = pymc.utils.hpd(masses, 0.32)
#    hpd95 = pymc.utils.hpd(masses, 0.05)
#
#    if outputPrefix:
#        with open('%s.mass.summary.txt' % outputPrefix, 'w') as output:
#            output.write('mean\t%f\n' % mean)
#            output.write('stddev\t%f\n' % stddev)
#            output.write('Q2.5\t%f\n' % quantiles[2.5])
#            output.write('Q25\t%f\n' % quantiles[25])
#            output.write('Q50\t%f\n' % quantiles[50])
#            output.write('Q75\t%f\n' % quantiles[75])
#            output.write('Q97.5\t%f\n' % quantiles[97.5])
#            output.write('HPD68\t%f\t%f\n' % (hpd68[0], hpd68[1]))
#            output.write('HPD95\t%f\t%f\n' % (hpd95[0], hpd95[1]))
#            output.close()
#            
#        with open('%s.mass.summary.pkl' % outputPrefix, 'wb') as output:
#            stats = {'mean' : mean,
#                     'stddev' : stddev,
#                     'quantiles' : quantiles,
#                     'hpd68' : hpd68,
#                     'hpd95' : hpd95}
#            cPickle.dump(stats, output)
#            output.close()
#
#    else:
#        
#        print 'mean\t%f\n' % mean 
#        print 'stddev\t%f\n' % stddev
#        print 'Q2.5\t%f\n' % quantiles[2.5]
#        print 'Q25\t%f\n' % quantiles[25]
#        print 'Q50\t%f\n' % quantiles[50]
#        print 'Q75\t%f\n' % quantiles[75]
#        print 'Q97.5\t%f\n' % quantiles[97.5]
#        print 'HPD68\t%f\t%f\n' % (hpd68[0], hpd68[1])
#        print 'HPD95\t%f\t%f\n' % (hpd95[0], hpd95[1])
#
#        print
#        
#
#    return masses
#
#
#
#
#########################################################
#
#def radialPlots(controller, db = None, rbins = 9, zbins = 5, nbootstraps = 500):
#
#    if isinstance(controller,  list):
#
#        g = np.hstack([c.inputcat['ghats'] for c in controller])
#        r = np.hstack([c.inputcat['r_mpc'] for c in controller])
#        z = np.hstack([c.inputcat['z_b'] for c in controller])
#        pdzrange = controller[0].pdzrange
#        pdz = np.vstack([c.pdz for c in controller])
#
#    else:
#        
#
#        g = controller.inputcat['ghats']
#        r = controller.inputcat['r_mpc']
#        z = controller.inputcat['z_b']
#        pdzrange = controller.pdzrange
#        pdz = controller.pdz
#
#    ngals = len(g)
#
#    if isinstance(rbins, int):
#        rbins = np.logspace(np.log10(np.min(r)), np.log10(np.max(r)), rbins, base = 10.)
#
#    nrbins = len(rbins) - 1
#
#    if isinstance(zbins, int):
#        zbins = np.logspace(np.log10(np.min(z)), np.log10(np.max(z)), zbins)
#    nzbins = len(zbins) - 1
#
#    weights = np.zeros((ngals, nzbins))
#    for i in range(nzbins):
#        lowZ = np.arange(len(pdzrange))[pdzrange >= zbins[i]][0]
#        highZ = np.arange(len(pdzrange))[pdzrange < zbins[i+1]][-1]
#
#        weights[:,i] = pdz[:,lowZ:highZ].sum(axis=-1)
#
#
#
#    median_ghats = np.empty((nrbins, nzbins), dtype=list)
#
#    for curr in range(nrbins):
#        for curz in range(nzbins):
#            median_ghats[curr, curz] = []
#
#    for curboot in range(nbootstraps):
#
#        bootselect = np.random.randint(0, ngals, ngals)
#
#        bootedR = r[bootselect]
#        bootedG = g[bootselect]
#        bootedWeights = weights[bootselect]
#
#        for curr in range(nrbins):
#
#            for curz in range(nzbins):
#
#                inBin = np.logical_and(np.logical_and(rbins[curr] <= bootedR, bootedR < rbins[curr+1]),
#                                       bootedWeights[:,curz] > 0.)
#
#                gInBin = bootedG[inBin]
#                weightsInBin = bootedWeights[inBin]
#
#                if len(gInBin) == 0:
#                    print 'HELL AND FIREWATER: %d %d' % (curr, curz)
#                    continue
#
#
#                sortOrder = np.argsort(gInBin)
#
#                curWeights = weightsInBin[:,curz][sortOrder].cumsum()
#                curWeights = curWeights / curWeights[-1]
#
#                median_ghats[curr, curz].append(gInBin[sortOrder][np.arange(len(gInBin))[curWeights >= 0.5][0]])
#
#    ghat = np.zeros((nrbins, nzbins))
#    ghat_err = np.zeros((2, nrbins, nzbins))
#
#    for curr in range(nrbins):
#        for curz in range(nzbins):
#            if len(median_ghats[curr, curz]) < 10:
#                ghat[curr, curz] = -9999
#            else:
#                ml, err = sp.ConfidenceRegion(median_ghats[curr, curz])
#                ghat[curr,curz] = ml
#                ghat_err[:,curr,curz] = err
#            
#
#
#    return rbins, zbins, ghat, ghat_err
#
#
#
#            
#
#    
#
#    

    

    


    
