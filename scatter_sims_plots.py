####################################
import numpy as np
import pylab, pymc
import scatter_sims as ss, compare_masses as cm
import nfwutils
from dappleutils import readtxtfile
import intrinsicscatter_grid as isg
import intrinsicscatter_grid_plots as isgp
import intrinsicscatter as isc

####################################

def publicationContamComparePlot(contam0fracbias, contam1fracbias, contam2fracbias, redshifts):

    fig = pylab.figure()
    ax = fig.add_axes([0.15, 0.12, 0.95 - 0.15, 0.95 - 0.12])
    
#    c0mean, c0err = ss.bootstrapMean(contam0fracbias)
    c1mean, c1err = ss.bootstrapMean(contam1fracbias)
#    c2mean, c2err = ss.bootstrapMean(contam2fracbias)

#    ax.errorbar(redshifts - 0.005, c1mean, c1err, fmt='bo', label='0\% Contamination')
#    ax.errorbar(redshifts, c1mean, c1err, fmt='rs', label='10\% Contamination')
    ax.errorbar(redshifts, c1mean, c1err, fmt='bs', label='10\% Contamination')

#    ax.errorbar(redshifts + 0.005, c2mean, c2err, fmt='g^', label='20\% Contamination')
    
    ax.axhline(0.0, c='k')

    ax.set_xlim(0.16, 0.72)
    ax.set_ylim(-0.08, 0.08)

    ax.set_xlabel('Cluster Redshift')
    ax.set_ylabel(r'Fractional Mass Bias')

#    ax.legend(loc='lower left', numpoints = 1, ncol=2)

    return fig

#####################################

def ML5filterContamCompareScript(data = None):

    if data is None:
        data = {}

    if 'worklist' not in data:
        data['worklist'] = readtxtfile('simclusterlist')
        data['clusters'] = [x[0] for x in data['worklist']]

    worklist = data['worklist']
    clusters = data['clusters']

    if 'redshifts' not in data:
        data['redshifts'] = cm.readClusterRedshifts()
        redshifts = data['redshifts']
        data['properredshifts'] = np.array([redshifts[x] for x in clusters])

    redshifts = data['redshifts']
    properredshifts = data['properredshifts']


    if 'fracbiases' not in data:
        subdirs = ['%sBVRIZ' % x for x in ['', 'contam0p10/', 'contam0p20/']]

        data['fracbiases'] = ss.processFracBiasData('/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17-highdensity', 
                                            subdirs, clusters, redshifts)
    fracbiases = data['fracbiases']



    fig = publicationContamComparePlot(fracbiases[0], fracbiases[1], fracbiases[2], properredshifts)

    ax = fig.axes[0]
    ax.text(0.2, 0.06, r'$B_{\mathrm J}V_{\mathrm J}r^+i^+z^+$', fontsize=16)

    fig.savefig('publication/clustersims_bvriz_contam_compare.eps')

    return fig, data


###########################################

def load5v6simdata(worklist):


    clusters = [x[0] for x in worklist]
    redshifts = cm.readClusterRedshifts()
    properredshifts = np.array([redshifts[x] for x in clusters])
        
    subdirs = ['contam0p10/%s' % x for x in ['BVRIZ', 'APER']]
        
    fracbiases = ss.processFracBiasData('/u/ki/dapple/nfs12/cosmos/simulations/publication/highsn/cluster3', subdirs, clusters, redshifts)
    
    data = [fracbiases[0], fracbiases[1], properredshifts]
    
    return data
    
    

###########################################

def ML5v6filterCompareScript(data = None):

    if data is None:

        worklist = readtxtfile('simclusterlist')
        data = load5v6simdata(worklist)
    
    Bfracbias = data[0]
    Afracbias = data[1]
    properredshifts = data[2]

    fig = pylab.figure()
    ax = fig.add_axes([0.14, 0.12, 0.95 - 0.14, 0.95 - 0.12])
    
    Bmean, Berr = ss.bootstrapMean(Bfracbias)
    Amean, Aerr = ss.bootstrapMean(Afracbias)
    
    ax.errorbar(properredshifts - 0.0025, Bmean, Berr, fmt='bo', label=r'$BVr^+i^+z^+$')
    ax.errorbar(properredshifts + 0.0025, Amean, Aerr, fmt='rs', label=r'$uBVr^+i^+z^+$')
    
    ax.axhline(0.0, c='k')

    ax.set_xlim(0.16, 0.72)
    ax.set_ylim(-0.15, 0.08)

    ax.set_xlabel('Cluster Redshift')
    ax.set_ylabel(r'Fractional Mass Bias within 1.5 Mpc')

    ax.legend(loc='lower left', numpoints = 1, ncol=1)
    
    ax.text(0.2, 0.06, r'10\% Contamination', fontsize=16)

    fig.savefig('publication/clustersims_bvriz_aper_compare.eps')


    return fig, data
        

#############################################


def MLUbandRatioScript(data = None):

    simlist = readtxtfile('simclusterlist')
    noUlist = readtxtfile('noUlist')
    
    worklist = [x for x in simlist if x in noUlist]
    del worklist[-1]
    clusters = [x[0] for x in worklist]


    if data is None:


        redshifts = cm.readClusterRedshifts()
        properredshifts = np.array([redshifts[x] for x in clusters])

        noUsim_masses, noUsim_errs, noUsim_grid, scale_radii = ss.readMLMasses('/u/ki/dapple/nfs12/cosmos/simulations/publication/highsn/cluster3', 'contam0p10/BVRIZ', clusters)

        Usim_masses, Usim_errs, Usim_grid, scale_radii = ss.readMLMasses('/u/ki/dapple/nfs12/cosmos/simulations/publication/highsn/cluster3', 'contam0p10/APER', clusters)


        noUmasses, noUmask = cm.readMLBootstraps('/u/ki/dapple/ki06/bootstrap_2011-12-14', worklist, np.arange(100))
        Umasses, Umask = cm.readMLBootstraps('/u/ki/dapple/ki06/bootstrap_U_2012-02-03', worklist, np.arange(100))
                
        data = [noUsim_grid, Usim_grid, properredshifts, noUmasses, noUmask, Umasses, Umask]

    else:
        
        noUsim_grid = data[0]
        Usim_grid = data[1]
        properredshifts = data[2]
        noUmasses = data[3]
        noUmask = data[4]
        Umasses = data[5]
        Umask = data[6]

    

    simRatio = noUsim_grid / Usim_grid
    simMean, simErr = ss.bootstrapMean(simRatio.T)

    dataRatios = cm.makeRatios(Umasses, Umask, noUmasses, noUmask)
    dataMeans, dataErrs = cm.bootstrapMeans(dataRatios, clusters)

    fig = pylab.figure()
    ax = fig.add_axes([0.14, 0.12, 0.95 - 0.14, 0.95 - 0.12])

    ax.errorbar(properredshifts + 0.0025, dataMeans, dataErrs, fmt='rs', label='Data')
    ax.errorbar(properredshifts - 0.0025, simMean, simErr, fmt='bo', label = 'Simulations')

    ax.axhline(1.0, c='k', linewidth=1.5)

    ax.set_xlim(0.16, 0.72)
    ax.set_ylim(0.85, 1.35)

    ax.set_xlabel('Cluster Redshift')
    ax.set_ylabel('Mass without U-band / Mass with U-band')

    ax.legend(loc='upper left', numpoints=1)

    fig.savefig('publication/dropU_comp.eps')


    return fig, data

    
    
#########################################################


def CCSimBiasPlotScript(data = None):

    if data is None:

        data = readtxtfile('/nfs/slac/g/ki/ki06/anja/SUBARU/cosmos_cats/simulations/publication/highsn/cluster2/cc_masses/masses_concat_anja.dat')

    # ${cluster} ${zcluster} ${truemass} ${meanmass} ${emean} ${beta} ${beta2} ${nshells} ${nobjects}

    
    clusters = [x[0] for x in data]
    redshifts = np.array([float(x[1]) for x in data])
    truemass =  np.array([float(x[2]) for x in data])
    meanmass =  np.array([float(x[3]) for x in data])
    errmass =   np.array([float(x[4]) for x in data])

    fig = pylab.figure()
    ax = fig.add_axes([0.14, 0.14, 0.95 - 0.14, 0.95 - 0.14])

    fracbias = (meanmass - truemass) / truemass
    fracerr = errmass / truemass




    ax.axhline(0.0, c='k', linewidth=1.5)

    mean = 0.007
    err = 0.0022
    fillx = np.array([0.16, 0.72])
    ax.fill_between(fillx, mean - err, mean+err, facecolor='r', alpha=0.1)
    ax.axhline(mean, c='k', linestyle='--', alpha=0.5)

    ax.errorbar(redshifts, fracbias, fracerr, fmt='bo')

    ax.set_xlim(0.16, 0.72)
    ax.set_ylim(-0.08, 0.08)
    
    ax.set_xlabel('Cluster Redshift')
    ax.set_ylabel(r'Fractional Mass Bias within 1.5 Mpc')

    ax.text(0.2, 0.06, r'Color Cuts', fontsize=16)

    fig.savefig('publication/clustersims_cc_compare.eps')

    return fig, data


###############################################################


def MLPointEstScript(data = None):


    if data is None:

        worklist = readtxtfile('simclusterlist')
        clusters = [x[0] for x in worklist]
        redshifts = cm.readClusterRedshifts()
        properredshifts = np.array([redshifts[x] for x in clusters])

        subdirs = ['contam0p10/BVRIZ']

#        MLfracbias = ss.processFracBiasData('/u/ki/dapple/nfs12/cosmos/simulations/publication/highsn/cluster3', 
#                                            subdirs, clusters, redshifts)[0]
#
#        
#        Apointmass, Apointgrid, scale_radii = ss.readPointMasses('/u/ki/dapple/nfs12/cosmos/simulations/publication/highsn/cluster3', 'contam0p10/newman/APER', clusters)
        Bpointmass, Bpointgrid, scale_radii = ss.readPointMasses('/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17', 'contam0p10/newman/BVRIZ', clusters)

        truemasses = [nfwutils.massInsideR(scale_radii[x], 4., redshifts[x], 1.5) for x in clusters]

#        Apointfracbias = ss.calcFracBias(Apointgrid, truemasses)
        Bpointfracbias = ss.calcFracBias(Bpointgrid, truemasses)

        data = [None, Bpointfracbias, properredshifts]

    else:

#        Apointfracbias = data[0]
        Bpointfracbias = data[1]
        properredshifts = data[2]

  
    fig = pylab.figure()

    try:


        ax = fig.add_axes([0.15, 0.12, 0.95 - 0.15, 0.95 - 0.12])

        ax.axhline(0.0, c='k', linewidth=1.25)


        
#        Apointmean, Apointerr = ss.bootstrapMean(Apointfracbias)
        Bpointmean, Bpointerr = ss.bootstrapMean(Bpointfracbias)

        ax.errorbar(properredshifts, Bpointmean, Bpointerr, fmt='bo', label=r'$BVr^+i^+z^+$')
#        ax.errorbar(properredshifts+0.0025, Apointmean, Apointerr, fmt='rs', label=r'$uBVr^+i^+z^+$')

        ax.text(0.166, 0.135, r'$BVr^+i^+z^+$ Photo-Z Point Est', fontsize=16)

        ax.set_xlim(0.16, 0.72)
        ax.set_ylim(-0.05, 0.15)


        ax.set_xlabel('Cluster Redshift', fontsize=16)
        ax.set_ylabel(r'Fractional Mass Bias within 1.5 Mpc')

#        ax.legend(loc='lower right', numpoints = 1, ncol=2)

        fig.savefig('publication/clustersims_pointest_compare.eps')

    finally:

        return fig, data

###################################        

def PointEstPzScript(data = None):


    if data is None:

        worklist = readtxtfile('simclusterlist')
        clusters = [x[0] for x in worklist]
        redshifts = cm.readClusterRedshifts()
        properredshifts = np.array([redshifts[x] for x in clusters])

        subdirs = ['contam0p10/BVRIZ']

        MLfracbias = ss.processFracBiasData('/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17-highdensity', 
                                            subdirs, clusters, redshifts)[0]

        

        Bpointmass, Bpointgrid, scale_radii = ss.readPointMasses('/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17', 'contam0p10/newman/BVRIZ', clusters)

        truemasses = [nfwutils.massInsideR(scale_radii[x], 4., redshifts[x], 1.5) for x in clusters]


        Bpointfracbias = ss.calcFracBias(Bpointgrid, truemasses)

        data = [MLfracbias, Bpointfracbias, properredshifts]

    else:

        MLfracbias = data[0]
        Bpointfracbias = data[1]
        properredshifts = data[2]

  
    fig = pylab.figure()

    try:


        ax = fig.add_axes([0.15, 0.12, 0.96 - 0.15, 0.95 - 0.12])

        ax.axhline(0.0, c='k', linewidth=1.25)


        
        Apointmean, Apointerr = ss.bootstrapMean(MLfracbias)
        Bpointmean, Bpointerr = ss.bootstrapMean(Bpointfracbias)

        ax.errorbar(properredshifts-0.0025, Bpointmean, Bpointerr, fmt='cs', label=r'Point Estimators', color='#BFBFD4')
        ax.errorbar(properredshifts+0.0025, Apointmean, Apointerr, fmt='ro', label=r'P(z) Method')



        ax.set_xlim(0.16, 0.72)
        ax.set_ylim(-0.08, 0.19)


        ax.set_xlabel('Cluster Redshift')
        ax.set_ylabel(r'Fractional Mass Bias within 1.5 Mpc')

#        ax.text(0.2, 0.12, r'$BVr^{+}i^{+}z^{+}$ Photo-$z$ Point Est', fontsize=16)

        ax.legend(loc='upper left', numpoints = 1, ncol=1)

        fig.savefig('publication/clustersims_pointest_pz_compare.eps')

    finally:

        return fig, data




#####################################################################

def fitOffsetScript(data = None):

    if data is None:
        data = {}

    worklist = readtxtfile('worklist')
    clusters = [x[0] for x in worklist]

    workdir = '/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17-highdensity/'
    subdirs = ['%sBVRIZ' % x for x in ['', 'contam0p10/', 'contam0p20/']]
    concentration = 4.
    mradius = 1.5
    redshifts = cm.readClusterRedshifts()

    figs = []

    for subdir in subdirs:

        if subdir not in data:
            
            data[subdir] = {}

        curdata = data[subdir]
        
        if 'masses' not in curdata:

            curdata['masses'], errs, massgrid, curdata['scale_radii'] = ss.readMLMasses(workdir, subdir, clusters)

        masses = curdata['masses']
        scale_radii = curdata['scale_radii']



        if 'grid' not in curdata:

            refmasses = {}

            for cluster in clusters:
        
                refmasses[cluster] = nfwutils.massInsideR(scale_radii[cluster], concentration, redshifts[cluster], mradius)*np.ones_like(masses[cluster])


            curdata['grid'], curdata['means'], curdata['scatters'] = isg.intrinsicScatter(refmasses, masses, means = 1. + np.arange(-0.08, 0.08, 0.0001), scatters = np.arange(0.005, 0.05, 0.0025))

            means = curdata['means']
            scatters = curdata['scatters']


            mode, (r68, r95) = isg.getdist_1d_hist(means[0], means[1], levels = [0.68, 0.95])
            curdata['meandist'] = (mode, r68, r95)

            mode, (r68, r95) = isg.getdist_1d_hist(scatters[0], scatters[1], levels = [0.68, 0.95])
            curdata['scatterdist'] = (mode, r68, r95)


    

        for varname in 'mean scatter'.split():

            mode, r68, r95 = curdata['%sdist' % varname]

            print mode, r68, r95

            print '%s\t%2.4f\t+%2.4f\t-%2.4f\t+%2.4f\t-%2.4f' % (varname, mode, 
                                                                 r68[0][1] - mode, mode - r68[0][0],
                                                                 r95[0][1] - mode, mode - r95[0][0])

            x, prob = curdata['%ss' % varname]
            fig = isgp.plotdist_1d_hist(x, prob, mode, [r68[0], r95[0]])
            ax = fig.axes[0]
            ax.set_title('%s %s' % (subdir, varname))

            figs.append(fig)
            fig.show()



    return figs, data

    


##########################################################


def fitAltOffsetScript(data = None):

    if data is None:
        data = {}

    worklist = readtxtfile('worklist')
    clusters = [x[0] for x in worklist]

    workdir = '/u/ki/dapple/nfs12/cosmos/simulations/clusters_2012-05-17-highdensity/'
    subdirs = ['%sBVRIZ' % x for x in ['', 'contam0p10/', 'contam0p20/']]
    concentration = 4.
    mradius = 1.5
    redshifts = cm.readClusterRedshifts()

    figs = []

    for subdir in subdirs:

        if subdir not in data:
            
            data[subdir] = {}

        curdata = data[subdir]
        
        if 'masses' not in curdata:

            curdata['masses'], errs, massgrid, curdata['scale_radii'] = ss.readMLMasses(workdir, subdir, clusters)

        masses = curdata['masses']
        scale_radii = curdata['scale_radii']



        if 'grid' not in curdata:

            refmasses = {}

            for cluster in clusters:
        
                refmasses[cluster] = nfwutils.massInsideR(scale_radii[cluster], concentration, redshifts[cluster], mradius)*np.ones_like(masses[cluster])


            curdata['grid'], curdata['means'], curdata['scatters'] = isg.intrinsicScatter(refmasses, masses, means = 1. + np.arange(-0.08, 0.08, 0.0001), scatters = np.arange(0.005, 0.05, 0.0025))

            means = curdata['means']
            scatters = curdata['scatters']


            mode, (r68, r95) = isg.getdist_1d_hist(means[0], means[1], levels = [0.68, 0.95])
            curdata['meandist'] = (mode, r68, r95)

            mode, (r68, r95) = isg.getdist_1d_hist(scatters[0], scatters[1], levels = [0.68, 0.95])
            curdata['scatterdist'] = (mode, r68, r95)


    

        for varname in 'mean scatter'.split():

            mode, r68, r95 = curdata['%sdist' % varname]

            print mode, r68, r95

            print '%s\t%2.4f\t+%2.4f\t-%2.4f\t+%2.4f\t-%2.4f' % (varname, mode, 
                                                                 r68[0][1] - mode, mode - r68[0][0],
                                                                 r95[0][1] - mode, mode - r95[0][0])

            x, prob = curdata['%ss' % varname]
            fig = isgp.plotdist_1d_hist(x, prob, mode, [r68[0], r95[0]])
            ax = fig.axes[0]
            ax.set_title('%s %s' % (subdir, varname))

            figs.append(fig)
            fig.show()



    return figs, data

    


##########################################################


        
