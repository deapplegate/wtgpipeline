#adam: this is an older version of the script from ~/wtgpipeline, which probably won't be needed anymore, but should be saved anyway (just in case)
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

def plotCompactSummary(consols, datarange, label, plotkey=(1,2,1)):

    pylab.subplot(*plotkey)
    pylab.plot(datarange, [consol[2]/consol[0] for consol in consols], label = label, marker='None')
    pylab.grid()
    pylab.axis([min(datarange), max(datarange), -.1, +.1])
    
    nextplotkey = (plotkey[0], plotkey[1], plotkey[2] + 1)

    pylab.subplot(*nextplotkey)
    pylab.plot(datarange, [consol[3]/consol[0] for consol in consols], marker='None', linestyle='-', label = label)
    pylab.plot(datarange, [consol[4]/consol[0] for consol in consols], marker='None', linestyle='--', label = label)
    pylab.axis([min(datarange), max(datarange), 0.0, 0.4])
    
#    pylab.legend(loc='upper left')
    pylab.grid()

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
        line = pylab.errorbar(zs + offset, medians, errs, label = r'%d $M_{\odot}^{14}$' % cur_mass, marker='o', linewidth=0.2, color = mass_colors[cur_mass] )

#    for cur_mass, offset in zip(mass_s, np.arange(offsetStart, offsetStart + nlines*deltaOffset, deltaOffset)):
#
#        zs = sorted([ x[0] for x in keys_to_use[cur_mass] ])
#
#        min_z = min(min_z, min(zs))
#        max_z = max(max_z, max(zs))
#
#        cur_consols = [ contamconsols[(cur_z, cur_mass)] for cur_z in zs ]
#
#        medians = []
#        hpds = []
#        for cur_consol in cur_consols:
#            cur_median, cur_hpd = bootstrapMedian(cur_consol[1]/cur_consol[0])
#            medians.append(cur_median)
#            hpds.append(cur_hpd)
#
#        medians = np.array(medians)
#        hpds = np.array(hpds)
#        
#        errs = np.zeros((2, len(zs)))
#        errs[0,:] = hpds[:,1] - medians
#        errs[1,:] = medians - hpds[:,0]
#        line = pylab.plot(zs + offset, medians, '%s-.' % mass_colors[cur_mass], marker='None', linewidth=0.5)
#
#    
#    pylab.grid()
    pylab.axis([min_z-0.05, max_z + 0.05, -.1001, +.1001])
    pylab.xlabel(r'Z')
    pylab.ylabel(r'$\Delta M_{500} / M_{500}^{true}$')
    if doLegend:
        pylab.legend(loc='upper left', ncol=2, numpoints = 1, scatterpoints = 1)
    pylab.axhline(0, c='k', linewidth=0.4)

    
    


########################



def plotZCompact(consols, plotkey=(1,2,1), plotfunc = plotCompactSummary):

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
        
        plotfunc(cur_consols, zs, 'Mass = %1.2f' % cur_mass, plotkey = plotkey)


################################


