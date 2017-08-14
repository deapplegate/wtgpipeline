#!/usr/bin/env python
##############################
# Create plots to investigate pdz quality
###############################

import pylab
from numpy import *
import ldac, pdzfile_utils as pdzutils
import nfwmodeltools, nfwutils

###############################

def oldscript():

    bpz = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/simulations/publication/highsn/APER/bpz.cat', 'STDTAB')

    pdzmanager = pdzutils.PDZManager.open('/u/ki/dapple/nfs12/cosmos/simulations/publication/highsn/APER/pdz.cat')


    pdzrange, pdz = pdzmanager.associatePDZ(bpz['SeqNr'])

    delta95Z = zeros(len(pdz))
    for i in range(len(delta95Z)):
        cumpdz = pdz[i].cumsum() / pdz[i].cumsum()[-1]
        delta95Z[i] = pdzrange[cumpdz >= 0.95][0] - pdzrange[cumpdz >= 0.05][0]
    deltaZcut = delta95Z < 2.5

    zcut = logical_and(bpz['BPZ_Z_B'] > 0.5, bpz['BPZ_Z_B'] < 1.25)

    clean = logical_and(zcut, deltaZcut)


    brightPDZ = pdz[logical_and(clean, logical_and(bpz['MAG_APER-SUBARU-10_2-1-W-S-I+'] > 23, bpz['MAG_APER-SUBARU-10_2-1-W-S-I+'] < 23.1))][0]

    faintPDZ = pdz[logical_and(clean, logical_and(bpz['MAG_APER-SUBARU-10_2-1-W-S-I+'] > 24.3, bpz['MAG_APER-SUBARU-10_2-1-W-S-I+'] < 24.5))]
    faintPDZ = faintPDZ[random.randint(0, len(faintPDZ), 1)][0,:]

    wideCandidates = logical_and(zcut, logical_not(deltaZcut))
    widePDZ = pdz[wideCandidates]
    widePDZ = widePDZ[random.randint(0, len(widePDZ), 1)][0,:]



    print brightPDZ.shape, faintPDZ.shape, widePDZ.shape, pdzrange.shape

    pylab.plot(pdzrange, brightPDZ, 'r-', label='Mag 23', linewidth=1.2)
    pylab.plot(pdzrange,faintPDZ, 'b-', label='Mag 24.5', linewidth=1.2)
    pylab.plot(pdzrange, widePDZ, 'k-', label='Wide P(z)', linewidth=1.2)
    pylab.xlabel('Redshift')
    pylab.ylabel('P(z)')
    pylab.legend(loc='upper right')
    pylab.savefig('publication/pdzexample.eps')

#######################################


def pdzbyspec(zspec, pdz, edges):

    nbins = len(edges) - 1

    pdzgrid = zeros((pdz.shape[1], nbins))

    for i in range(nbins):

        inbin = logical_and(zspec >= edges[i], zspec < edges[i+1])

        pdzgrid[:,i] = pdz[inbin].sum(axis=0) / sum(ones(len(zspec))[inbin])
#        pdzgrid[:,i] = pdz[inbin].sum(axis=0)

    


    return pdzgrid

######################################

def cdfbyspec(zspec, pdzrange, pdz, zspecedges, cdfedges):

    cdfvals = ones_like(zspec)

    for i in range(len(zspec)):

        cumpdz = pdz[i].cumsum() / pdz[i].cumsum()[-1]
        
        selector = zspec[i] <= pdzrange
        if not selector.any():
            continue
        cdfvals[i] = cumpdz[selector][0]


    H, xedges, yedges = histogram2d(zspec, cdfvals, bins=[zspecedges, cdfedges])
    xcenters = (xedges[1:] + xedges[:-1])/2.0
    ycenters = (yedges[1:] + yedges[:-1])/2.
    totals = H.sum(axis=-1)
    H = len(xcenters)*H.T/totals
    X,Y = meshgrid(xcenters, ycenters)

    return H, X,Y
    


#######################################


def pdzbyspec_contour(zspec, pdzrange, pdz, edges):

    pdzgrid = pdzbyspec(zspec, pdz, edges)

    pdzcenters = pdzrange + pdzrange[0]/2.
    zspeccenters = (edges[:-1] + edges[1:])/2.

    X,Y = meshgrid(zspeccenters, pdzcenters)

    fig = pylab.figure()
    pylab.contourf(X,Y,pdzgrid, 50)
    pylab.plot([0,4],[0,4], 'r-', linewidth=1.5)

    pylab.colorbar()
    pylab.xlabel('z')
    pylab.ylabel('P(z)')

    return fig
    

#############################################

def deltaShear(zspec, zphot, zcluster = 0.2):

    ginfpredict = nfwmodeltools.NFWShear(ones(1), 4.0, 1., zcluster)

    beta_s_spec = nfwutils.beta_s(zspec, zcluster)
    beta_s_phot = nfwutils.beta_s(zphot, zcluster)

    return (beta_s_spec - beta_s_phot)*ginfpredict

#############################################
