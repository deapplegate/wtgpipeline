#######################
# Plot results of skew surface tests
#######################

import os, re, glob
import numpy as np
import pylab
import scipy.spatial as spatial
import ldac

#######################


def loadCats(cluster, lensfilter, image, filter):

    clusterdir = '/u/ki/dapple/subaru/%s/' % cluster
    photdir = '%s/PHOTOMETRY_%s_aper' % (clusterdir, lensfilter)
    lensingdir = '%s/LENSING_%s_%s_aper/%s' % (clusterdir, lensfilter, lensfilter, image)

    stars = ldac.openObjectFile('%s/coadd_stars.cat' % lensingdir)

    catfiles = glob.glob('%s/%s/unstacked/%s.%s.*.skew' % (photdir, filter, cluster, filter))
    cats = {}
    for catfile in catfiles:
        base = os.path.basename(catfile)
        config = base.split('.')[2]

        cat = ldac.openObjectFile(catfile)
        tree = spatial.KDTree(np.column_stack([cat['Xpos'], cat['Ypos']]))

        dist, index = tree.query(np.column_stack([stars['Xpos'], stars['Ypos']]), distance_upper_bound = 3.)

        starorder = index[np.isfinite(dist)]

        cats[config] = cat.filter(starorder)

    return cats

#################

def matchCat(refcat, othercat):

    tree = spatial.KDTree(np.column_stack([othercat['Xpos'], othercat['Ypos']]))

    dist, index = tree.query(np.column_stack([refcat['Xpos'], refcat['Ypos']]), distance_upper_bound = 3.)

    order = index[np.isfinite(dist)]

    return othercat.filter(order)
    

def loadExpCats(cluster, lensfilter, image, filter, config='SUBARU-10_2'):

    clusterdir = '/u/ki/dapple/subaru/%s/' % cluster
    photdir = '%s/PHOTOMETRY_%s_aper' % (clusterdir, lensfilter)
    lensingdir = '%s/LENSING_%s_%s_aper/%s' % (clusterdir, lensfilter, lensfilter, image)
    unstackeddir = '%s/%s/unstacked' % (photdir, filter)

    stars = ldac.openObjectFile('%s/coadd_stars.cat' % lensingdir)


    stats = ldac.openObjectFile('%s/%s/SCIENCE/cat/chips.cat8' % (clusterdir, filter),
                                        'STATS')

    exposures = [ldac.openObjectFile('%s/%s.filtered.cat.corrected.cat' % (unstackeddir, exp[:11])) for exp in stats['IMAGENAME']]

    mastercat = ldac.openObjectFile('%s/%s.%s.%s.unstacked.cor.cat' % (unstackeddir, cluster, filter, config))
    mastercat = matchCat(stars, mastercat)

    cats = [matchCat(mastercat, expcat) for expcat in exposures]

        
    return mastercat, cats
    


##################


def plotSkewSurface(cat, configchip):

    xpos = cat['Xpos']
    ypos = cat['Ypos']
    skew = cat['FLUX_APER-%s' % configchip][:,1]

    goodskew = np.isfinite(skew)

    fig = pylab.figure()
    pylab.scatter(xpos[goodskew], ypos[goodskew], c=skew[goodskew], vmin=-1.5, vmax = 1.5)
    pylab.colorbar()
    pylab.title('Skew Surface')

    fig2 = pylab.figure()
    pylab.hist(skew[goodskew], bins=30)
    pylab.xlabel('Skew')

    fig3 = pylab.figure()
    negskew = np.logical_and(skew < -1, goodskew)
    pylab.scatter(xpos[negskew], ypos[negskew], c='b')
    posskew = np.logical_and(skew > 1, goodskew)
    pylab.scatter(xpos[posskew], ypos[posskew], c='r')
    

    

    return fig, fig2, fig3
    

###################

def plotSigSurface(cat, configchip):

    xpos = cat['Xpos']
    ypos = cat['Ypos']
    err = cat['FLUXERR_APER-%s' % configchip][:,1]

    gooderr = np.logical_and(err > 0, np.logical_and(err < 90, np.isfinite(err)))

    fig = pylab.figure()
    pylab.scatter(xpos[gooderr], ypos[gooderr], c=err[gooderr])
    pylab.colorbar()
    pylab.title('Sig Ratio Surface')

    fig2 = pylab.figure()
    pylab.hist(err[gooderr], bins=50)
    pylab.xlabel('Sig Ratio')

    return fig, fig2
    


#########################

def plotDeltas(mastercat, expcats, config='SUBARU-10_2-1'):

    figs = []
    for cat in expcats:
        fig = pylab.figure()
        delta = cat['MAG_APER'][:,1] - mastercat['MAG_APER-%s' % config][:,1]
        pylab.scatter(cat['Xpos'], cat['Ypos'], c=delta - np.median(delta), vmin=-0.05, vmax=0.05)
        pylab.colorbar()
        pylab.title(cat.sourcefile)
        figs.append(fig)

    return figs


#########################
