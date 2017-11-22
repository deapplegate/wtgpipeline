#####################
# Measure bounds on bias from independent splits of data
#####################

import numpy as np, pylab
import pymc
from readtxtfile import readtxtfile
import intrinsicscatter_grid as isg, intrinsicscatter_grid_plots as isgp
import compare_masses as cm

#####################


def loadData(splitxdir, splitydir, items, burn = 5000):

    xclusters = {}
    yclusters = {}

    for cluster, filter, image in items:

        def loadDB(dir, cluster, filter, item):
            db = pymc.database.pickle.load('%s/%s.%s.%s.out' % (dir, cluster, filter, image))
            return db.trace('mass_15mpc', -1)[burn:]

        key = (cluster, filter, image)
        xclusters[key] = loadDB(splitxdir, cluster, filter, image)
        yclusters[key] = loadDB(splitydir, cluster, filter, image)

    return [xclusters, yclusters]

#####################

trialsdir = '/u/ki/dapple/subaru/doug/publication/trials_2012-05-17'

#####################

filename_conv = {'Imag' : 'publication/imag_split.eps',
                 'redshift' : 'publication/zsplit.eps',
                 'size' : 'publication/rh_split.eps',
                 'snratio' : 'publication/sn_split.eps'}

label_conv = {'Imag' : ('Faint $\mathrm{I_{mag}}$', 'Bright $\mathrm{I_{mag}}$'),
              'redshift' : ('Low Redshift', 'High Redshift'),
              'size' : ('Small Galaxies', 'Large Galaxies'),
              'snratio' : ('Low S/N', 'High S/N')}

def magSplit_script(category, data = None):

    figs = []

    if data is None:

        data = {}

    if 'items' not in data:

        data['items'] = readtxtfile('worklist')

#    try:

    loc1 = '%s/%s/low' % (trialsdir, category)
    loc2 = '%s/%s/high' % (trialsdir, category)

    if category not in data:

        
        masses = loadData(loc1, loc2,
                           data['items'])

        data[category] = {}
        data[category]['masses'] = masses

    curdata = data[category]


    if 'grid' not in curdata:

        grid, means, scatters = isg.intrinsicScatter(curdata['masses'][0], curdata['masses'][1], means = np.arange(0.6, 1.4, 0.002), scatters = np.arange(0.02, 0.2, 0.01))

        curdata['grid'] = grid
        curdata['means'] = means
        curdata['scatters'] = scatters

    else:

        grid = curdata['grid']
        means = curdata['means']
        scatters = curdata['scatters']

    print
    print
    print category
    print '-----'
    print 'var\tmode\t68%% +\t-\t95%% +\t-'
    print '-----'


    if 'meandist' not in curdata:

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

    xlabel, ylabel = label_conv[category]
    fig, xmasses, ymasses = cm.publicationPlotMassMass(loc1, loc2, xlabel, ylabel)
    ax = fig.axes[0]

    mode, r68, r95 = curdata['meandist']

#    ax.axhline(mode, c='r', ls='--', linewidth=1.5)

    ax.fill_between([0.16, 0.72], r95[0][0], r95[0][1], facecolor=(1, 0.642, 0.610), zorder=-1)
    ax.fill_between([0.16, 0.72], r68[0][0], r68[0][1], facecolor='#CC0000', zorder=-1)
    ax.set_xlim(0.16, 0.72)
    ax.set_ylim(0.1, 10)

    fig.show()
    fig.savefig(filename_conv[category])
    figs.append(fig)
    

#    finally:
    
    return figs, data
    

