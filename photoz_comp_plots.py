########################
# Create a 4-panel plot of photo-z quality for Paper 2
########################

import numpy as np, pylab, ldac, os
from dappleutils import readtxtfile

########################


def makeHexbin(specz, photz, xlabel = 'Reference Redshift', ylabel = 'Photo-$z$', gridsize = 100, bins = None):

    fig = pylab.figure()
    ax = fig.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])

    ax.hexbin(specz, photz, gridsize = gridsize, extent=[0, 1.5, 0, 1.5], cmap = pylab.cm.binary, bins=bins)
    ax.plot([0, 1.5], [0, 1.5], 'r-', linewidth=1.25)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    return fig

    


##############################


def cosmos30plot(data = None):

    if data is None:
        data = {}

    if 'bpz' not in data:
        data['bpz'] = ldac.openObjectFile('/u/ki/dapple/subaru/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_BVRIZ/COSMOS_PHOTOZ.APER.1.CWWSB_capak.list.all.bpz.tab', 'STDTAB')

    if 'cosmos' not in data:
        data['cosmos'] = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos.cat')

    if 'galaxies' not in data:
        data['galaxies'] = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/simulations/publication/highsn/BVRIZ/bpz.cat', 'STDTAB')

    bpz = data['bpz']
    cosmos = data['cosmos']
    galaxies = data['galaxies']

    filter = galaxies['BPZ_ODDS'] > 0.5
    
    galaxies = galaxies.filter(filter)


    mbpz = bpz.matchById(galaxies)
    mcosmos = cosmos.matchById(mbpz, 'SeqNr', 'id')

    fig = makeHexbin(mcosmos['zp_best'], mbpz['BPZ_Z_B'], xlabel=r'COSMOS-30 Photo-$z$', ylabel=r'{\it B}$_{\rm J}${\it V}$_{\rm J}${\it r}$^{+}${\it i}$^{+}${\it z}$^{+}$ Photo-$z$',
                     gridsize = 50, bins=None)

#    fig.axes[0].text(1.1, 0.05, '\emph{Log Color Scale}')

    fig.savefig('publication/cosmos30comp.pdf')

    return fig, data


###############################


def zcosmosplot(data = None):

    if data is None:
        data = {}

    if 'bpz' not in data:
        data['bpz'] = ldac.openObjectFile('/u/ki/dapple/subaru/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_BVRIZ/COSMOS_PHOTOZ.APER.1.CWWSB_capak.list.all.bpz.tab', 'STDTAB')

    if 'galaxies' not in data:
        data['galaxies'] = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/simulations/publication/highsn/BVRIZ/bpz.cat', 'STDTAB')

    if 'zcat' not in data:
        data['zcat'] = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/zcosmos.matched.cat')

    if 'refbpz' not in data:
        data['refbpz'] = ldac.openObjectFile('/u/ki/dapple/subaru/COSMOS_PHOTOZ/PHOTOMETRY_W-C-IC_BVRIZ/bpz.zcosmos.matched.cat', 'STDTAB')

        
    bpz = data['bpz']
    galaxies = data['galaxies']
    zcat = data['zcat']
    refbpz = data['refbpz']

    filter = galaxies['BPZ_ODDS'] > 0.5
    
    galaxies = galaxies.filter(filter)

    mbpz = bpz.matchById(galaxies)

    cat1 = mbpz
    cat2 = refbpz
    cat1id = 'SeqNr'
    cat2id = 'SeqNr'


    cat1order = {}
    for i, x in enumerate(cat1[cat1id]):
        cat1order[x] = i
        
    
    cat1KeepOrder = []
    cat2Keep = []
    for x in cat2[cat2id]:
        if x in cat1order:
            cat1KeepOrder.append(cat1order[x])
            cat2Keep.append(True)
        else:
            cat2Keep.append(False)

    cat1keep = np.array(cat1KeepOrder)
    cat2keep = np.array(cat2Keep)
    cat1matched = cat1.filter(cat1keep)
    cat2matched = cat2.filter(cat2keep)


    mbpz = mbpz.filter(cat1keep)
    mzcat = zcat.filter(cat2keep)

    fig = makeHexbin(mzcat['z'], mbpz['BPZ_Z_B'], xlabel=r'Z-COSMOS Spec-$z$', ylabel=r'{\it B}$_{\rm J}${\it V}$_{\rm J}${\it r}$^{+}${\it i}$^{+}${\it z}$^{+}$ Photo-$z$',
                     gridsize = 65, bins='log')

    fig.axes[0].text(1.1, 0.05, '\emph{Log Color Scale}')

    fig.savefig('publication/zcosmoscomp.pdf')

    return fig, data


#####################################################

def hdfnplot(data = None):


    if data is None:
        data = {}

    
    if 'bpz' not in data:
        data['bpz'] = ldac.openObjectFile('/u/ki/dapple/subaru/HDFN/PHOTOMETRY_W-J-V_aper/HDFN.APER1.1.CWWSB_capak.list.all.bpz.tab', 'STDTAB')

    if 'zcat' not in data:
        data['zcat'] = ldac.openObjectFile('/u/ki/dapple/subaru/HDFN/PHOTOMETRY_W-J-V_aper/HDFN.matched.tab', 'STDTAB')

    bpz = data['bpz']
    zcat = data['zcat']

    mbpz, mzcat = ldac.matchCommonSubsets(bpz, zcat, 'SeqNr', 'SeqNr_data')

    
    fig = makeHexbin(mzcat['z_spec'], mbpz['BPZ_Z_B'], xlabel=r'HDFN Spec-$z$', ylabel=r'{\it B}$_{\rm J}${\it V}$_{\rm J}${\it R}$_{\rm C}${\it i}$^{+}${\it z}$^{+}$ Photo-$z$')

    fig.savefig('publication/hdfncomp.pdf')

    return fig, data


########################################################


def clusterplot(data = None):

    if data is None:
        data = {}

    if 'items' not in data:
        data['items'] = readtxtfile('worklist')

    items= data['items']

    if 'clusters' not in data:
        clusters = {}

        for cluster, filter, image in items:

            matchedfile = '/u/ki/dapple/subaru/%s/PHOTOMETRY_%s_aper/%s.matched.tab' % (cluster, filter, cluster)

            if not os.path.exists(matchedfile):
                continue

            bpz = ldac.openObjectFile('/u/ki/dapple/ki06/catalog_backup_2012-05-17/%s.%s.bpz.tab' % (cluster, filter), 'STDTAB')
            zcat = ldac.openObjectFile(matchedfile, 'STDTAB')

            bpz = bpz.matchById(zcat, 'SeqNr_data')

            bpz = bpz.filter(bpz['BPZ_ODDS'] > 0.5)
            zcat = zcat.matchById(bpz, 'SeqNr', 'SeqNr_data')

            clusters[cluster] = np.array([bpz['BPZ_Z_B'], zcat['z_spec']])

        data['clusters'] = clusters

    clusters = data['clusters']

    if 'redshifts' not in data:

        data['redshifts'] = np.column_stack([x for x in clusters.itervalues()])


    redshifts = data['redshifts']

    fig = makeHexbin(redshifts[1,:], redshifts[0,:], xlabel='Cluster Spectroscopic $z$', ylabel='5 Filter Photo-$z$', gridsize = 45, bins='log')

    fig.axes[0].text(1.1, 0.05, '\emph{Log Color Scale}')

    fig.savefig('publication/clustercomp.pdf')

    return fig, data
    

    
