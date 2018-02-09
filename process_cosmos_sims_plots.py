import pylab, numpy as np, pymc

#######################

def plotSummary(consol):
    c = 1
    for i in range(2,8):
        for j in range(4,7):
            key = (i,j)
            pylab.subplot(6,3,c)
            pylab.hist(consol[key][-1], bins = 15)
            c += 1
            print key
            pylab.xlabel('%1.3f %1.3f %1.3f' % (consol[key][2]/consol[key][0], consol[key][3]/consol[key][0], consol[key][4]/consol[key][0]))


########################

def plotCompactSummary(consols, datarange, label, plotkey=(1,2,1),title=None):

    pylab.subplot(*plotkey)
    pylab.plot(datarange, [consol[2]/consol[0] for consol in consols], label = label, marker='None')
    pylab.grid()
    pylab.axis([min(datarange), max(datarange), -.1, +.1])
    
    nextplotkey = (plotkey[0], plotkey[1], plotkey[2] + 1)

    pylab.subplot(*nextplotkey)
    pylab.plot(datarange, [consol[3]/consol[0] for consol in consols], marker='None', linestyle='-', label = label)
    #pylab.plot(datarange, [consol[4]/consol[0] for consol in consols], marker='None', linestyle='--', label = label)
    pylab.axis([min(datarange), max(datarange), 0.0, 0.4])
    
    pylab.legend(loc='upper left')
    pylab.grid()
    if not title==None:
	    pylab.suptitle(title)

########################

def bootstrapMedian(set, nboot=1000):

    medians = []
    for i in range(nboot):
        boot = np.random.randint(0, len(set), len(set))
        bootset = set[boot]
        medians.append(np.median(bootset))

    medians = np.array(medians)
    mu = np.mean(medians)
    hpd = pymc.utils.hpd(medians, 0.32)

    return mu, hpd

###

default_masscolors = {25 : 'b',
                      17 : 'g',
                      12 : 'r',
                      7 : 'm',
                      3 : 'c'}
massbins=np.sort(default_masscolors.keys())
def find_nearest(array,value):
    idx = (np.abs(array-value)).argmin()
    return array[idx]


###

def publicationBias(consols, contamconsols, mass_colors = default_masscolors, doLegend = True):

    keys_to_use = {}
    for key in consols.keys():
        curz, cur_mass = key
        if cur_mass not in keys_to_use:
            keys_to_use[cur_mass] = []

        keys_to_use[cur_mass].append(key)

    mass_s = sorted(keys_to_use.keys())
    min_z = 99
    max_z = -1
    xmarg = 0.14
    ymarg = 0.13
    pylab.figure(figsize=(11,11))
    pylab.axes([xmarg, ymarg, 0.95-xmarg, 0.95-ymarg])

    nlines = len(mass_s)
    deltaOffset = 0.005
    offsetStart = -deltaOffset*nlines/2.
    for cur_mass, offset in zip(mass_s, np.arange(offsetStart, offsetStart + nlines*deltaOffset, deltaOffset)):

        zs = sorted([ x[0] for x in keys_to_use[cur_mass] ])

        min_z = min(min_z, min(zs))
        max_z = max(max_z, max(zs))

        cur_consols = [ consols[(cur_z, cur_mass)] for cur_z in zs ]

        medians = []
        hpds = []
        for cur_consol in cur_consols:
            cur_median, cur_hpd = bootstrapMedian(cur_consol[1]/cur_consol[0])
            medians.append(cur_median)
            hpds.append(cur_hpd)

        medians = np.array(medians)
        hpds = np.array(hpds)
        
        errs = np.zeros((2, len(zs)))
        errs[0,:] = hpds[:,1] - medians
        errs[1,:] = medians - hpds[:,0]
	if cur_mass in mass_colors.keys():
		masslinecolor=mass_colors[cur_mass]
	else:
		usemass=find_nearest(massbins,cur_mass)
		masslinecolor=mass_colors[ usemass]
	line = pylab.errorbar(zs + offset, medians, errs, label = r'%d $M_{\odot}^{14}$' % cur_mass, marker='o', linewidth=0.2, color = masslinecolor )

    if contamconsols!=None:
	    for cur_mass, offset in zip(mass_s, np.arange(offsetStart, offsetStart + nlines*deltaOffset, deltaOffset)):

		zs = sorted([ x[0] for x in keys_to_use[cur_mass] ])

		min_z = min(min_z, min(zs))
		max_z = max(max_z, max(zs))

		cur_consols = [ contamconsols[(cur_z, cur_mass)] for cur_z in zs ]

		medians = []
		hpds = []
		for cur_consol in cur_consols:
		    cur_median, cur_hpd = bootstrapMedian(cur_consol[1]/cur_consol[0])
		    medians.append(cur_median)
		    hpds.append(cur_hpd)

		medians = np.array(medians)
		hpds = np.array(hpds)
		
		errs = np.zeros((2, len(zs)))
		errs[0,:] = hpds[:,1] - medians
		errs[1,:] = medians - hpds[:,0]
		line = pylab.plot(zs + offset, medians, '%s-.' % mass_colors[cur_mass], marker='None', linewidth=0.5)

    pylab.grid()
    pylab.axis([min_z-0.05, max_z + 0.05, -.1001, +.1001])
    pylab.xlabel(r'Z')
    pylab.ylabel(r'$\Delta M_{500} / M_{500}^{true}$')
    if doLegend:
        pylab.legend(loc='upper left', ncol=2, numpoints = 1, scatterpoints = 1)
    pylab.axhline(0, c='k', linewidth=0.4)
    from adam_cosmos_options import zchoice_switch, cat_switch, cosmos_idcol, dirtag, filterset
    titlestr='| %s = %s | %s = %s | %s = %s |' % ('cat',cat_switch,'filterset',filterset, 'dirtag',dirtag)
    pylab.suptitle(titlestr)

########################

def plotZCompact(consols, plotkey=(1,2,1), plotfunc = plotCompactSummary, label=None):

    from adam_cosmos_options import zchoice_switch, cat_switch, cosmos_idcol, dirtag, filterset
    titlestr='| %s = %s | %s = %s | %s = %s |' % ('cat',cat_switch,'filterset',filterset, 'dirtag',dirtag)
    istitled=False
    label0=label
    keys_to_use = {}
    
    for key in consols.keys():

        curz, cur_mass = key

        if cur_mass not in keys_to_use:
            keys_to_use[cur_mass] = []
        
        keys_to_use[cur_mass].append(key)


    mass_s = sorted(keys_to_use.keys())

    for cur_mass in mass_s:

        zs = sorted([ x[0] for x in keys_to_use[cur_mass] ])

        cur_consols = [ consols[(cur_z, cur_mass)] for cur_z in zs ]

        if label0 is None:
            label = 'Mass = %1.2f' % cur_mass
        if istitled==False:
        	plotfunc(cur_consols, zs, label, plotkey = plotkey, title=titlestr)
		istitled=True
	else:
        	plotfunc(cur_consols, zs, label, plotkey = plotkey)

################################


#adam-SHNT# this is the plot in Weighing the Giants - III figure 8
#copied and modified from scatter_sims_plots.py
import readtxtfile
def PointEstPzScript():

    worklist = readtxtfile('simclusterlist')
    clusters = [x[0] for x in worklist]
    redshifts = cm.readClusterRedshifts()
    properredshifts = np.array([redshifts[x] for x in clusters])

    subdirs = ['nocontam/maxlike']

    MLfracbias = ss.processFracBiasData('/u/ki/awright/simcl/simcl_CATnewcat_matched-Zpoint/UGRIZ/',
                                        subdirs, clusters, redshifts)[0]

    Bpointmass, Bpointgrid, scale_radii = ss.readPointMasses( '/u/ki/awright/simcl/simcl_CATnewcat_matched-Zpoint/UGRIZ/',subdirs[0], clusters)

    truemasses = [nfwutils.massInsideR(scale_radii[x], 4., redshifts[x], 1.5) for x in clusters]


    Bpointfracbias = ss.calcFracBias(Bpointgrid, truemasses)

    fig = pylab.figure()

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
    ax.legend(loc='upper left', numpoints = 1, ncol=1)
    return fig
