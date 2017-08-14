##########################
#Calculate average PSF seeing and ellipticity from stars in the FOV
##########################

import numpy as np, cPickle
import pylab
import ldac, nfwutils
from maxlike_subaru_filehandler import readClusterCenters

##########################

subarudir='/nfs/slac/g/ki/ki05/anja/SUBARU'

def calcPSF(cluster, filter, image, redshift, pixscale = 0.2):

    cat = ldac.openObjectFile('%s/%s/LENSING_%s_%s_aper/%s/coadd_stars.cat' % (subarudir, cluster, filter, filter, image))

    center = readClusterCenters(cluster, basedir=subarudir)

    dR = pixscale*np.sqrt( (cat['Xpos'] - center[0])**2 + (cat['Ypos'] - center[1])**2  )  #arcsec

    dR_mpc = dR * (1./3600.) * (np.pi / 180. ) * nfwutils.angulardist(redshift)


    accept = np.logical_and(0.75 < dR_mpc, dR_mpc < 3.)

    stars = cat.filter(accept)

    seeing = np.median(stars['rh'])

    ellip = np.median(np.sqrt( stars['e1']**2 + stars['e2']**2))

    return seeing, ellip



###############################


def createDataList(items, outfile, redshifts):


    output = open(outfile, 'w')

    seeinglist = {}
    elliplist = {}

    for cluster, filter, image in items:

        seeing, ellip = calcPSF(cluster, filter, image, redshifts[cluster])

        seeinglist[(cluster, filter, image)] = seeing
        elliplist[(cluster, filter, image)] = ellip

        output.write('%s %s %s %f %f\n' % (cluster, filter, image, seeing, ellip))
        

    output.close()

    cPickle.dump((seeinglist, elliplist), open('%s.pkl' % outfile, 'wb'), -1)

    return seeinglist, elliplist


################################

STEP_seeing = {'A' : 1.526,
               'C' : 1.871,
               'D' : 1.774}

STEP_ellip = {'A' : 0.01107,
              'C' : 0.01136,
              'D' : 0.08915}


def publicationSeeingPlot(items, seeinglist, pixscale = 0.2):

    fig = pylab.figure()

    ax = fig.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])

    seeings = np.array([seeinglist[tuple(item)] for item in items])
    
    ax.hist(2*pixscale*seeings, bins = 25)

    ax.axvline(2*pixscale*STEP_seeing['A'], c='r', linestyle='-',  linewidth = 1.5, label='STEP2 PSF A')
    ax.axvline(2*pixscale*STEP_seeing['C'], c='k', linestyle='--', linewidth = 1.5, label='STEP2 PSF C')
    ax.axvline(2*pixscale*STEP_seeing['D'], c='m', linestyle='-.', linewidth = 1.5, label='STEP2 PSF D')

    ax.legend(loc='upper right')

    ax.set_xlabel('Seeing FWHM (")')
    ax.set_ylabel('\# of Cluster Fields')

    fig.show()
    fig.savefig('publication/psfSize.eps')

    return fig

####################



def publicationEllipPlot(items, elliplist):

    fig = pylab.figure()

    ax = fig.add_axes([0.12, 0.12, 0.95 - 0.12, 0.95 - 0.12])

    ellips = np.array([elliplist[tuple(item)] for item in items])
    
    ax.hist(ellips, bins = 25)

    ax.axvline(STEP_ellip['A'], c='r', linestyle='-',  linewidth = 1.5, label='STEP2 PSF A')
    ax.axvline(STEP_ellip['C'], c='k', linestyle='--', linewidth = 1.5, label='STEP2 PSF C')
    ax.axvline(STEP_ellip['D'], c='m', linestyle='-.', linewidth = 1.5, label='STEP2 PSF D')

    ax.set_xlim(0.0, 0.10)

    ax.legend(loc='upper right')

    ax.set_xlabel('PSF Ellipticity $|e|$')
    ax.set_ylabel('\# of Cluster Fields')

    fig.show()
    fig.savefig('publication/psfmag_distro.eps')

    return fig

####################






    

                              
