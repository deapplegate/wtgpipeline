########################
# Compare CC masses fit to independent mass ranges
# Evidence for offsets?
########################

import numpy as np
import intrinsicscatter_grid as isg
import intrinsicscatter_grid_plots as isgp
from readtxtfile import readtxtfile
import compare_masses as cm

########################

subarudir = '/u/ki/dapple/subaru/'

inner_ranges = ['0.75 2.0'.split(), '0.75 2.5'.split(), '0.75 3.0'.split()]
outer_ranges = ['2.0 5.0'.split(), '2.5 5.0'.split(), '3.0 5.0'.split()]


def radialScript(items, curdata = None):

    clusters = [x[0] for x in items]


    if curdata is None:

        curdata = {}

    
    

    

    if 'ir' not in curdata:

        curdata['ir'] = cm.readCCSummary('/u/ki/dapple/ki06/bootstrap_5mpc_2012-02-14/', 
                                         clusters,np.arange(50), '_rm1.5_ri0.75_ro3.0.out')
        

    if 'or' not in curdata:

        curdata['or'] = cm.readCCSummary('/u/ki/dapple/ki06/bootstrap_5mpc_2012-02-14/', 
                                         clusters,np.arange(50), '_rm1.5_ri0.75_ro5.0.out')


    if 'reducedIR' not in curdata or 'reducedOR' not in curdata:

        irMass, irMask = curdata['ir']
        orMass, orMask = curdata['or']

        reducedIR = {}
        reducedOR = {}

        for cluster in clusters:
            totalmask = np.logical_and(irMask[cluster], orMask[cluster])
            reducedIR[cluster] = irMass[cluster][totalmask]
            reducedOR[cluster] = orMass[cluster][totalmask]

            reducedIR[cluster][reducedIR[cluster] == 0.] = 1e13
            reducedOR[cluster][reducedOR[cluster] == 0.] = 1e13
            

        curdata['reducedIR'] = reducedIR
        curdata['reducedOR'] = reducedOR
        


    if 'grid' not in curdata:

        grid, means, scatters = isg.intrinsicScatter(curdata['reducedIR'], curdata['reducedOR'])

        curdata['grid'] = grid
        curdata['means'] = means
        curdata['scatters'] = scatters




    print
    print
    print '-----'
    print 'var\tmode\t68%% +\t-\t95%% +\t-'
    print '-----'


    if 'meandist' not in curdata:

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
        ax.set_title(varname)

        figs.append(fig)
        fig.show()


    return figs, data

        

          
#######################################################

def sizeScript(items, curdata = None):

    clusters = [x[0] for x in items]


    if curdata is None:

        curdata = {}


    if 'norm' not in curdata and 'cut' not in curdata:

        normMass, normMask = cm.readCCSummary('/u/ki/dapple/ki06/bootstrap_2012-02-08/', 
                                              clusters,np.arange(30, 130))
        
        cutMass, cutMask = cm.readCCSummary('/u/ki/dapple/ki06/bootstrap_2012-02-08/', 
                                            clusters, np.arange(30, 130),
                                            '_rh1p2.out')

        
        reducedNorm = {}
        reducedCut = {}
        for cluster in normMass.keys():
            totalmask = np.logical_and(normMask[cluster], cutMask[cluster])
            reducedNorm[cluster] = normMass[cluster][totalmask]
            reducedCut[cluster] = cutMass[cluster][totalmask]

        curdata['norm'] = reducedNorm
        curdata['cut'] = reducedCut
        


    if 'grid' not in curdata:

        grid, means, scatters = isg.intrinsicScatter(curdata['norm'], curdata['cut'])

        curdata['grid'] = grid
        curdata['means'] = means
        curdata['scatters'] = scatters




    print
    print
    print '-----'
    print 'var\tmode\t68%% +\t-\t95%% +\t-'
    print '-----'


    if 'meandist' not in curdata:

        means = curdata['means']
        scatters = curdata['scatters']
        
        mode, (r68, r95) = isg.getdist_1d_hist(means[0], means[1], levels = [0.68, 0.95])
        curdata['meandist'] = (mode, r68, r95)

        mode, (r68, r95) = isg.getdist_1d_hist(scatters[0], scatters[1], levels = [0.68, 0.95])
        curdata['scatterdist'] = (mode, r68, r95)


    figs = []

    for varname in 'mean scatter'.split():

        mode, r68, r95 = curdata['%sdist' % varname]

        print mode, r68, r95

        print '%s\t%2.4f\t+%2.4f\t-%2.4f\t+%2.4f\t-%2.4f' % (varname, mode, 
                                                             r68[0][1] - mode, mode - r68[0][0],
                                                             r95[0][1] - mode, mode - r95[0][0])

        x, prob = curdata['%ss' % varname]
        fig = isgp.plotdist_1d_hist(x, prob, mode, [r68[0], r95[0]])
        ax = fig.axes[0]
        ax.set_title(varname)

        figs.append(fig)
        fig.show()


    return figs, data

        

          
#######################################################



def profileScript(items, curdata = None):

    clusters = [x[0] for x in items]


    if curdata is None:

        curdata = {}


    if 'norm' not in curdata and 'cut' not in curdata:

        normMass, normMask = cm.readCCSummary('/u/ki/dapple/ki06/bootstrap_5mpc_2012-02-14/', 
                                              clusters,np.arange(50),
                                              '_rm1.5_ri0.75_ro3.0.out')
        
        cutMass, cutMask = cm.readCCSummary('/u/ki/dapple/ki06/bootstrap_5mpc_2012-02-14/', 
                                            clusters, np.arange(50),
                                            '_bmo2_t2p0_rm1.5_ri0.75_ro3.0.out')

        
        reducedNorm = {}
        reducedCut = {}
        for cluster in normMass.keys():
            totalmask = np.logical_and(normMask[cluster], cutMask[cluster])
            reducedNorm[cluster] = normMass[cluster][totalmask]
            reducedCut[cluster] = cutMass[cluster][totalmask]

        curdata['norm'] = reducedNorm
        curdata['cut'] = reducedCut
        


    if 'grid' not in curdata:

        grid, means, scatters = isg.intrinsicScatter(curdata['norm'], curdata['cut'], scatters=np.arange(0.005, 0.05, 0.01))

        curdata['grid'] = grid
        curdata['means'] = means
        curdata['scatters'] = scatters




    print
    print
    print '-----'
    print 'var\tmode\t68%% +\t-\t95%% +\t-'
    print '-----'


    if 'meandist' not in curdata or 'scatterdist' not in curdata:

        means = curdata['means']
        scatters = curdata['scatters']
        
        mode, (r68, r95) = isg.getdist_1d_hist(means[0], means[1], levels = [0.68, 0.95])
        curdata['meandist'] = (mode, r68, r95)

        mode, (r68, r95) = isg.getdist_1d_hist(scatters[0], scatters[1], levels = [0.68, 0.95])
        curdata['scatterdist'] = (mode, r68, r95)


    figs = []

    for varname in 'mean scatter'.split():

        mode, r68, r95 = curdata['%sdist' % varname]

        print mode, r68, r95

        print '%s\t%2.4f\t+%2.4f\t-%2.4f\t+%2.4f\t-%2.4f' % (varname, mode, 
                                                             r68[0][1] - mode, mode - r68[0][0],
                                                             r95[0][1] - mode, mode - r95[0][0])

        x, prob = curdata['%ss' % varname]
        fig = isgp.plotdist_1d_hist(x, prob, mode, [r68[0], r95[0]])
        ax = fig.axes[0]
        ax.set_title(varname)

        figs.append(fig)
        fig.show()


    return figs, data

        

          
#######################################################



        

    
