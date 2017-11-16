###################
# Match up objects pre and post coadd
# Determine if the magnitudes are the same
###################

import os, string
import numpy as np
import scipy.spatial as spatial, scipy.misc as misc
import astropy, astropy.io.fits as pyfits
import astropy.wcs as pywcs
import ldac, wcsregionfile
import pylab

import apply_geometric_magcor as agm
import dump_cat_filters as dcf

#####################



def improveRADEC(rawx, rawy, header):

    x0 = rawx - header['CRPIX1']
    y0 = rawy - header['CRPIX2']

    x = x0*header['CD1_1'] + y0*header['CD1_2']
    y = x0*header['CD2_1'] + y0*header['CD2_2']
    
    r = np.sqrt(x**2. + y**2.)

    xi_terms = {'PV1_0':np.ones_like(x),
    'PV1_1':x,
    'PV1_2':y,
    'PV1_3':r,
    'PV1_4':x**2.,
    'PV1_5':x*y,
    'PV1_6':y**2.,
    'PV1_7':x**3.,
    'PV1_8':x**2.*y,
    'PV1_9':x*y**2.,
    'PV1_10':y**3.}
    
    pv1_keys = filter(lambda x: string.find(x,'PV1') != -1, header.keys())

    xi = reduce(lambda x,y: x + y, [xi_terms[k]*header[k] for k in pv1_keys])
    
    eta_terms = {'PV2_0':np.ones_like(x),
    'PV2_1':y,
    'PV2_2':x,
    'PV2_3':r,
    'PV2_4':y**2.,
    'PV2_5':y*x,
    'PV2_6':x**2.,
    'PV2_7':y**3.,
    'PV2_8':y**2.*x,
    'PV2_9':y*x**2.,
    'PV2_10':x**3.}
    
    pv2_keys = filter(lambda x: string.find(x,'PV2') != -1, header.keys())
    eta = reduce(lambda x,y: x + y, [eta_terms[k]*header[k] for k in pv2_keys])

    XI = np.pi* xi / 180.0
    ETA = np.pi *eta / 180.0
    CRVAL1 = np.pi * header['CRVAL1']/180.0
    CRVAL2 = np.pi*header['CRVAL2']/180.0
    p = np.sqrt(XI**2. + ETA**2.) 
    c = np.arctan(p)
                                                                             
    a = CRVAL1 + np.arctan((XI*np.sin(c))/(p*np.cos(CRVAL2)*np.cos(c) - ETA*np.sin(CRVAL2)*np.sin(c)))
    d = np.arcsin(np.cos(c)*np.sin(CRVAL2) + ETA*np.sin(c)*np.cos(CRVAL2)/p)
                                                                                                                                                                                        
    ra = a*180.0/np.pi
    dec = d*180.0/np.pi


    return ra, dec

#####################

def matchCats(ra1, dec1, ra2, dec2, bound = 0.6):
    #bound in arcseconds


    tree = spatial.KDTree(np.column_stack([ra1, dec1]))

    dist, index = tree.query(np.column_stack([ra2, dec2]), distance_upper_bound = bound/3600)
    print dist.shape

    cat2filter = np.isfinite(dist)
    cat1filter = index[cat2filter]

    return cat1filter, cat2filter


#####################

def calcPosRelCenter(cat, header, xkey = 'X_IMAGE', ykey = 'Y_IMAGE'):


    deltaX = cat[xkey] - header['CRPIX1']
    deltaY = cat[ykey] - header['CRPIX2']

    return deltaX, deltaY

    
######################
######################

def compileMatches(dir, cluster, imagebase, headertype = 'SDSS-R6', coaddtype = 'coadd', chips = np.arange(1, 11), iccatdir = 'cat_marmod', iccatext = 'OCFSI'):

    matchedCats = []

    for chipnum in chips:

        if not os.path.exists('%s/%s_%d%s.fits' % (dir, imagebase, chipnum, iccatext)) or \
                not os.path.exists('%s/%s/%s_%d%s.cat' % (dir, iccatdir, imagebase, chipnum, iccatext)):
            print 'skip'
            continue

        iccat = ldac.openObjectFile('%s/%s/%s_%d%s.cat' % (dir, iccatdir, imagebase, chipnum, iccatext), 'LDAC_OBJECTS')

        coadd_starcat = ldac.openObjectFile('%s/%s_%s_%s/coadd_stars.cat' % (dir, coaddtype, cluster, imagebase))
#        coadd_starcat = ldac.openObjectFile('%s/%s_compare.cat' % (dir, imagebase))

        icheaderbuffer = wcsregionfile.FileBuffer('\n'.join(open('%s/headers_scamp_photom_%s/%s_%d.head' % (dir, headertype, imagebase, chipnum)).readlines()))
        icheader = pyfits.Header(txtfile = icheaderbuffer)

        icRA, icDEC = improveRADEC(iccat['X_IMAGE'], iccat['Y_IMAGE'], icheader)


        coaddfilter, icfilter = matchCats(coadd_starcat['RA'], coadd_starcat['DEC'], icRA, icDEC)
#        coaddfilter, icfilter = matchCats(coadd_starcat['ALPHA_J2000'], coadd_starcat['DELTA_J2000'], icRA, icDEC)

        matchedIC = iccat.filter(icfilter)
        matchedCoadd = coadd_starcat.filter(coaddfilter)
        icX, icY = calcPosRelCenter(matchedIC, icheader)

        matchedCats.append((matchedIC, matchedCoadd, icheader, np.column_stack([icX, icY]), np.column_stack([icRA, icDEC])[icfilter]  ))

    
    return matchedCats

    
##################################


def checkPositionMatch(matchedCats, coaddRA = 'RA', coaddDEC = 'DEC'):

    fig = pylab.figure()
    ax = fig.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])

    for iccat, coaddcat, icheader, icPos, icWCS in matchedCats:


        ax.plot(icWCS[:,0] - coaddcat[coaddRA], icWCS[:,1] - coaddcat[coaddDEC], 'b,')

    fig2 = pylab.figure()
    ax = fig2.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])

    for iccat, coaddcat, icheader, icPos, icWCS in matchedCats:

        badmatch = np.sqrt( (icWCS[:,0] - coaddcat[coaddRA])**2 + (icWCS[:,1] - coaddcat[coaddDEC])**2 ) > 5.5e-5


        ax.plot(icPos[:,0][badmatch], icPos[:,1][badmatch], 'b,')

    fig3 = pylab.figure()
    ax = fig3.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])

    for iccat, coaddcat, icheader, icPos, icWCS in matchedCats:


        ax.plot(icWCS[:,0], icWCS[:,1], 'bo')
        ax.plot(coaddcat[coaddRA],  coaddcat[coaddDEC], 'r.')

    
    


    return fig, fig2, fig3
    

####################################


def plotDeltaMagMap(matchedCats, icmag = 'MAG_AUTO', coaddmag = 'MAG_AUTO-new', coaddRA = 'ALPHA_J2000', coaddDelta = 'DELTA_J2000'):



    xpos = []
    ypos = []
    deltamags = []
    coaddmags = []
    icmags = []

    for iccat, coaddcat, icheader, icPos, icWCS in matchedCats:


    
        goodmatch = np.logical_and(np.logical_and(np.sqrt( (icWCS[:,0] - coaddcat[coaddRA])**2 + (icWCS[:,1] - coaddcat[coaddDelta])**2 ) < 4.e-05,
                                                  np.logical_and(iccat['FLAGS'] == 0, coaddcat['Flag'] == 0)),
                                   np.logical_and(iccat['FLUX_MAX'] < 25000,
                                                  iccat['FLUX_AUTO'] / iccat['FLUXERR_AUTO'] > 5))
#                                   np.logical_and(np.logical_and(coaddcat['FLUX_RADIUS'] < 5,

        coaddmags.append((coaddcat[coaddmag])[goodmatch])
        icmags.append((iccat[icmag])[goodmatch])
                        
        deltaMag = iccat[icmag] - coaddcat[coaddmag]


        xpos.append(icPos[:,0][goodmatch])
        ypos.append(icPos[:,1][goodmatch])
        deltamags.append(deltaMag[goodmatch])

    xpos = np.hstack(xpos)
    ypos = np.hstack(ypos)
    coaddmags = np.hstack(coaddmags)
    icmags = np.hstack(icmags)
    deltamags = np.hstack(deltamags)


    goodmatch = np.ones_like(coaddmags) == 1.
 #   goodmatch = np.logical_and(coaddmags > -10, coaddmags < -7)
#    goodmatch = np.logical_and(coaddmags > -5, coaddmags < 0)
#    goodmatch = coaddmags < -9

    residuals = deltamags - np.median(deltamags)



    print np.min(residuals[goodmatch]), np.max(residuals[goodmatch])

    fig = pylab.figure()
#    temp_resids = residuals[goodmatch].copy()
#    temp_resids[temp_resids < -0.05] = -0.051
#    temp_resids[temp_resids > 0.05] = 0.051
    pylab.scatter(xpos[goodmatch], ypos[goodmatch], c = residuals[goodmatch])

    pylab.colorbar()

    fig2 = pylab.figure()
    ax = fig2.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])
    ax.hist(residuals, bins=130)

    fig3 = pylab.figure()
    dist = np.sqrt( (xpos)**2 + (ypos)**2 )
    pylab.hexbin(np.abs(ypos[goodmatch]), residuals[goodmatch], gridsize=50)
    pylab.axhline(0, c='k', linewidth=1.5)
    pylab.xlabel('Ypos')

    fig4 = pylab.figure()
    pylab.hexbin(np.abs(xpos[goodmatch]), residuals[goodmatch], gridsize=50)
    pylab.axhline(0, c='k', linewidth=1.5)
    pylab.xlabel('Xpos')

    fig5 = pylab.figure()
    pylab.hexbin(coaddmags[coaddmags < 30], ((icmags - coaddmags)/coaddmags)[coaddmags < 30], gridsize=(80, 280), bins='log')




    return (fig, fig2, fig3, fig4, fig5), (xpos, ypos, residuals)


#########################################


    
def distortionMagCor(matchCats, defaultpixscale = 0.2):

    corrections = []

    deg2arcsec = 3600.

    for matchedIC, matchedCoadd, header, icpos, icwcs in matchCats:

        rawX = icpos[:,0]
        rawY = icpos[:,1]

        def RA_X(x):
            ra, dec = improveRADEC(x, rawY, header)
            return deg2arcsec*ra
        dRAdX = misc.derivative(RA_X, rawX, order=3)


        def RA_Y(y):
            ra, dec = improveRADEC(rawX,y, header)
            return deg2arcsec*ra
        dRAdY = misc.derivative(RA_Y, rawY, order=3)

        def DEC_X(x):
            ra, dec = improveRADEC(x,rawY, header)
            return deg2arcsec*dec
        dDECdX = misc.derivative(DEC_X, rawX, order=3)

        def DEC_Y(y):
            ra, dec = improveRADEC(rawX,y, header)
            return deg2arcsec*dec
        dDECdY = misc.derivative(DEC_Y, rawY, order=3)

        jacobian = np.abs( (dRAdX * dDECdY) - (dRAdY*dDECdX) )

        corrections.append(-2.5*np.log10(defaultpixscale**2 / jacobian))

    return corrections




#########################################

def plotDistortionCor(matchedCats, fluxcor, icmag = 'MAG_AUTO', coaddmag = 'MAG_AUTO-new', coaddRA = 'ALPHA_J2000', coaddDelta = 'DELTA_J2000'):



    xpos = []
    ypos = []
    coaddmags = []
    deltamags = []
    accumulatedfilter = []

    for iccat, coaddcat, icheader, icPos, icWCS in matchedCats:


        goodmatch = np.logical_and(np.logical_and(np.sqrt( (icWCS[:,0] - coaddcat[coaddRA])**2 + (icWCS[:,1] - coaddcat[coaddDelta])**2 ) < 4.e-05,
                                                  np.logical_and(iccat['FLAGS'] == 0, coaddcat['Flag'] == 0)),
                                   np.logical_and(iccat['FLUX_MAX'] < 25000,
                                                  iccat['FLUX_AUTO'] / iccat['FLUXERR_AUTO'] > 5))
#                                   np.logical_and(np.logical_and(coaddcat['FLUX_RADIUS'] < 5,

        deltaMag = iccat[icmag] - coaddcat[coaddmag]


        coaddmags.append(coaddcat[coaddmag][goodmatch])
        xpos.append(icPos[:,0][goodmatch])
        ypos.append(icPos[:,1][goodmatch])
        deltamags.append(deltaMag[goodmatch])

        accumulatedfilter.append(goodmatch)
    
    xpos = np.hstack(xpos)
    ypos = np.hstack(ypos)
    coaddmags = np.hstack(coaddmags)
    deltamags = np.hstack(deltamags)
    deltamags = deltamags - np.median(deltamags)

    accumulatedfilter = np.hstack(accumulatedfilter)

    print len(accumulatedfilter), len(fluxcor), len(fluxcor[accumulatedfilter]), len(deltamags)

    correction = -2.5*np.log10(fluxcor)[accumulatedfilter]

    magcorresid = deltamags - correction

    goodmatch = np.logical_and((fluxcor != -9999)[accumulatedfilter], coaddmags < 30)
#    goodmatch = (fluxcor != -9999.)[accumulatedfilter]
 

    

    fig = pylab.figure()
    pylab.scatter(xpos[goodmatch], ypos[goodmatch], c = magcorresid[goodmatch])

    pylab.colorbar()


    fig2 = pylab.figure()
    pylab.hexbin(np.abs(xpos[goodmatch]), magcorresid[goodmatch], gridsize=50, extent=[0, 4000, -0.1, 0.1])
    pylab.axhline(0, c='k', linewidth=1.5)
    pylab.xlabel('Xpos')

    fig3 = pylab.figure()
    pylab.hexbin(np.abs(ypos[goodmatch]), magcorresid[goodmatch], gridsize=50, extent=[0, 4000, -0.1, 0.1])
    pylab.axhline(0, c='k', linewidth=1.5)
    pylab.xlabel('Ypos')

    fig4 = pylab.figure()
    pylab.hist(magcorresid, bins=200)

    fig5 = pylab.figure()
    pylab.scatter(xpos[goodmatch], ypos[goodmatch], c=correction[goodmatch])
    pylab.colorbar()
    

    return (fig, fig2, fig3, fig4), (xpos, ypos, magcorresid)

    
###############################################

def truncateString(astr):
    index = astr.find('\x00')
    if index == -1:
        return astr
    return astr[:index]

def iteratePairs(cluster, lensingfilter, image, filter = None):

    clusterdir = '/u/ki/dapple/subaru/%s' % cluster
    photdir = '%s/PHOTOMETRY_%s_aper' % (clusterdir, lensingfilter)

    if filter is None:
        photcat = ldac.openObjectFile('%s/%s.slr.cat' \
                                          % (photdir, cluster))
        filters = dcf.dumpFilters(photcat)
        masterfilters = agm.uniqueMasterFilters(filters)
    else:
        masterfilters = [filter]


    allfigs = []
    for filter in masterfilters:

        try:
            stats = ldac.openObjectFile('%s/%s/SCIENCE/cat/chips.cat8' % (clusterdir, filter),
                                        'STATS')
        except IOError:
            print "Skipping %s" % filter
            continue

        exposures = {0:[], 1:[], -1:[], 2:[]}
        for expid, rot in zip(stats['IMAGENAME'], stats['ROTATION']):
            exposures[rot].append(truncateString(expid))

        
        for exp1, exp2 in zip(exposures[0], exposures[1]):
            figs, cats = plotRotationPair(cluster, lensingfilter, filter, image,
                                          exp1, exp2)
            allfigs.append(figs)

    
    return allfigs


def plotRotationPair(cluster, lensingfilter, filter, image, exp1, exp2):

    clusterdir = '/u/ki/dapple/subaru/%s' % cluster
    unstackeddir = '%s/PHOTOMETRY_%s_aper/%s/unstacked' % (clusterdir, lensingfilter, filter)

    starcat = ldac.openObjectFile('%s/LENSING_%s_%s_aper/%s/coadd_stars.cat' \
                                      % (clusterdir, lensingfilter, lensingfilter, image))

    exp1cat = ldac.openObjectFile('%s/%s.filtered.cat.corrected.cat' % (unstackeddir, exp1))
    exp2cat = ldac.openObjectFile('%s/%s.filtered.cat.corrected.cat' % (unstackeddir, exp2))

    starcatfilter, exp1starfilter = matchCats(starcat['ALPHA_J2000'], starcat['DELTA_J2000'],
                                              exp1cat['ALPHA_J2000'], exp1cat['DELTA_J2000'])

    exp1stars = exp1cat.filter(exp1starfilter)

    exp1filter, exp2filter = matchCats(exp1stars['ALPHA_J2000'], exp1stars['DELTA_J2000'],
                                       exp2cat['ALPHA_J2000'], exp2cat['DELTA_J2000'])

    exp1stars = exp1stars.filter(exp1filter)
    exp2stars = exp2cat.filter(exp2filter)



    rawdeltaMag = exp1stars['MAG_AUTO'] - exp2stars['MAG_AUTO']
    deltaMag = rawdeltaMag - np.median(rawdeltaMag)


    goodmatch = np.logical_and(np.isfinite(deltaMag), np.abs(deltaMag) < 0.1)

    deltaMag = rawdeltaMag - np.median(rawdeltaMag[goodmatch])

    if len(exp1stars.filter(goodmatch)) == 0:
        return None, None
    

    fig2 = pylab.figure()
    pylab.subplot(1,2,1)
    pylab.scatter(exp1stars['ALPHA_J2000'][goodmatch], exp1stars['DELTA_J2000'][goodmatch], c=deltaMag[goodmatch], vmin = -0.05, vmax = 0.05)
    pylab.colorbar()
    pylab.title('%s %s %s' % (filter, exp1, exp2))
    pylab.subplot(1,2,2)
    pylab.hist(deltaMag, bins = 30, range=(-.1, .1))
    pylab.xlabel('Std: %1.5f' % np.std(deltaMag[goodmatch]))
    pylab.savefig('plots_2012-04-11/%s_%s_%s_%s.png' % (cluster, filter, exp1, exp2))

    return fig2, (exp1stars, exp2stars)

                                       

    
    
###############################################################

def oldvsnewMags(filter1, filter2 = None, data = None, cluster=None, lensfilter=None, image=None):

    if data is None:
        data = {}

    if 'oldcat' not in data:

        data['cluster'] = cluster
        data['lensfilter'] = lensfilter
        data['image'] = image

        oldcat = ldac.openObjectFile('/u/ki/dapple/subaru/%s/PHOTOMETRY_%s_aper/%s.unstacked.orig.cat' % \
                                         (cluster, lensfilter, cluster))
        newcat = ldac.openObjectFile('/u/ki/dapple/subaru/%s/PHOTOMETRY_%s_aper/%s.unstacked.geocor.cat' % \
                                         (cluster, lensfilter, cluster))
        starcat = ldac.openObjectFile('/u/ki/dapple/subaru/%s/LENSING_%s_%s_aper/%s/coadd_stars.cat' % \
                                          (cluster, lensfilter, lensfilter, image))

    

        catfilter, starfilter = matchCats(oldcat['Xpos'], oldcat['Ypos'], starcat['Xpos'], starcat['Ypos'], bound = 3600*2)

        oldcat = oldcat.filter(catfilter)
        newcat = newcat.filter(catfilter)

        data['oldcat'] = oldcat
        data['newcat'] = newcat

    else:

        cluster = data['cluster']
        lensfilter = data['lensfilter']
        image = data['image']

        oldcat = data['oldcat']
        newcat = data['newcat']


    if filter2 is None:

        column = 'MAG_APER-%s' % filter1

        deltaMag = oldcat[column][:,1] - newcat[column][:,1]

        goodmatch = np.logical_and(np.logical_and(np.isfinite(deltaMag), deltaMag < 1.), np.abs(oldcat[column][:,1]) < 90)

        vmax = min(0.05, np.max(deltaMag[goodmatch]))
        vmin = max(-0.05, np.min(deltaMag[goodmatch]))


        fig = pylab.figure()
        pylab.scatter(oldcat['Xpos'][goodmatch], oldcat['Ypos'][goodmatch], c = deltaMag[goodmatch], vmin=vmin, vmax = vmax)
        pylab.colorbar()
        pylab.title('%s %s' % (cluster, filter1))
        if vmax != 0.05 or vmin != 0.05:
            pylab.xlabel('Warning: Color Axis Range Stretch')


        return fig, data, deltaMag[goodmatch]

    column1 = 'MAG_APER-%s' % filter1
    column2 = 'MAG_APER-%s' % filter2

    oldcolor = oldcat[column1] - oldcat[column2]
    newcolor = newcat[column1] - newcat[column2]
    deltacolor = (oldcolor - newcolor)[:,1]

    goodmatch = np.logical_and(np.logical_and(np.isfinite(deltacolor), deltacolor < 1), np.abs(oldcat[column1][:,1]) < 90)

    vmax = min(0.05, np.max(deltacolor[goodmatch]))
    vmin = max(-0.05, np.min(deltacolor[goodmatch]))


    fig = pylab.figure()
    pylab.scatter(oldcat['Xpos'][goodmatch], oldcat['Ypos'][goodmatch], c= deltacolor[goodmatch], vmin=vmin, vmax = vmax)
    pylab.colorbar()

    return fig, data, deltacolor[goodmatch]
    
        

##########################################################


def zpChangesByCluster(items):

    
    filters = {}

    for cluster, filter, image in items:

        clusterdelta = {}

        oldcat = ldac.openObjectFile('/u/ki/dapple/subaru/%s/PHOTOMETRY_%s_aper/%s.slr.orig.cat' % (cluster, filter, cluster), 'ZPS')
        newcat = ldac.openObjectFile('/u/ki/dapple/subaru/%s/PHOTOMETRY_%s_aper/%s.slr.cat' % (cluster, filter, cluster), 'ZPS')

        keys_seen = []
        for filter, oldzp, newfilter, newzp in zip(oldcat['filter'], oldcat['zeropoints'], newcat['filter'], newcat['zeropoints']):

            assert(filter == newfilter)

            if filter in keys_seen:
                continue

            if filter not in clusterdelta:
                clusterdelta[filter] = []

            delta = oldzp - newzp
            if np.abs(delta) > 0.1:
                print cluster, filter
            clusterdelta[filter].append(oldzp - newzp)

        filters[cluster] = clusterdelta

    return filters

########
    
def zpChangesByFilter(items):

    
    filters = {}

    for cluster, filter, image in items:

        oldcat = ldac.openObjectFile('/u/ki/dapple/subaru/%s/PHOTOMETRY_%s_aper/%s.slr.orig.cat' % (cluster, filter, cluster), 'ZPS')
        newcat = ldac.openObjectFile('/u/ki/dapple/subaru/%s/PHOTOMETRY_%s_aper/%s.slr.cat' % (cluster, filter, cluster), 'ZPS')

        keys_seen = []
        for filter, oldzp, newfilter, newzp in zip(oldcat['filter'], oldcat['zeropoints'], newcat['filter'], newcat['zeropoints']):

            assert(filter == newfilter)

            if filter in keys_seen:
                continue

            keys_seen.append(filter)

            if filter not in filters:
                filters[filter] = []

            delta = oldzp - newzp
            if np.abs(delta) > 0.1:
                print cluster, filter
            filters[filter].append(oldzp - newzp)



    return filters
    

    

    
