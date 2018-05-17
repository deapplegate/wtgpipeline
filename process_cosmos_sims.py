#!/usr/bin/env python
###########################

import sys, glob, numpy as np, os, cPickle
import astropy, astropy.io.fits as pyfits, shearprofile as sp
import ldac, nfwutils, pymc

####################

class MassDist(object):

    def __init__(self, zcluster, rs, m500, mu, sig, chisq):
        self.zcluster = zcluster
        self.rs = rs
        self.m500 = m500
        self.mu = mu
        self.sig = sig
        self.chisq = chisq

class EdgeEffectException(Exception): pass

#######################

def processSummaryFile(resultfile, ext, simdir):

    summary = cPickle.load(open(resultfile, 'rb'))

    dir, filename = os.path.split(resultfile)
    base = filename.split(ext)[0]
    print base
    if simdir is None:
        
        simfile = '%s/%s.cat' % (dir,base)
        if not os.path.exists(simfile):
            simfile = '%s/../%s.cat' % (dir, base)
            if not os.path.exists(simfile):
                simfile = '%s/../../%s.cat' % (dir, base)

    else:
        simfile = '%s/%s.cat' % (simdir, base)

    sim = ldac.openObjectFile(simfile)
    scale_radius = sim.hdu.header['R_S']
    zcluster = sim.hdu.header['Z']
    r500 = nfwutils.rdelta(scale_radius, 4.0, 500)
#    m500 = nfwutils.Mdelta(scale_radius, 4.0, zcluster, 500)
    m500 = nfwutils.massInsideR(scale_radius, 4.0, zcluster, 1.5)


    return MassDist(zcluster, scale_radius, m500, summary['quantiles'][50], 
                    summary['stddev'], None), None


######################

def processSummaryDir(dir, ext='.out.mass.summary.pkl', simdir = None):

    output = sorted(glob.glob('%s/*%s' % (dir, ext)))

    massdists = {}
    for out in output:

        print out

        massdist, masses = processSummaryFile(out, ext, simdir)

        key = (round(massdist.zcluster, 2), round(massdist.m500 / 1e14, 2))
        if key not in massdists:
            massdists[key] = []
        massdists[key].append((massdist, masses))

    return massdists
    


#######################


def processFile(resultfile, nsamples=10000, mass_radius = 1.5):


    print resultfile

    results = ldac.openObjectFile(resultfile)
    
    dir, filename = os.path.split(resultfile)
    filebase, ext = os.path.splitext(filename)
    simfile = '%s/%s.cat' % (dir,filebase)
    if not os.path.exists(simfile):
        simfile = '%s/../%s.cat' % (dir, filebase)
        if not os.path.exists(simfile):
            simfile = '%s/../../%s.cat' % (dir, filebase)

    sim = ldac.openObjectFile(simfile)

    scale_radius = sim.hdu.header['R_S']
    concentration = sim.hdu.header['CONCEN']
    zcluster = sim.hdu.header['Z']


    masses = results['Mass']
    pdf = np.exp(results['prob'] - max(results['prob']))


    cdf = np.cumsum(pdf)
    cdf = cdf / cdf[-1]

    buffered_cdf = np.zeros(len(cdf) + 2)
    buffered_cdf[-1] = 1.
    buffered_cdf[1:-1] = cdf

    mass_samples = []
    for i in range(nsamples):

        cdf_pick = np.random.uniform()
        inbin = np.logical_and(np.roll(buffered_cdf, 1) <= cdf_pick, buffered_cdf > cdf_pick)
        mass_samples.append(masses[inbin[1:-1]][0])

#    rs_samples = [nfwutils.RsMassInsideR(x, concentration, zcluster, mass_radius) \
#                      for x in mass_samples]

    
#    r500 = nfwutils.rdelta(scale_radius, concentration, 500)
#    m500 = nfwutils.Mdelta(scale_radius, concentration, zcluster, 500)
    m500 = nfwutils.massInsideR(scale_radius, concentration, zcluster, 1.5)

#    masses = np.array([nfwutils.massInsideR(x, concentration, zcluster, r500) for x in rs_samples])
    masses = mass_samples

    mu = np.median(masses)
    sig = np.std(masses)
    
    chisq = ((masses - mu)/sig)**2
    
    return MassDist(zcluster, scale_radius, m500, mu, sig, chisq), masses




######


def processDir(dir):

    output = sorted(glob.glob('%s/*.out' % dir))

    massdists = {}
    toredo = []
    for out in output:

        print out

        try:
            massdist = processFile(out)
        except EdgeEffectException:
            toredo.append(out)
            continue

        key = (round(massdist[0].zcluster, 1), round(massdist[0].m500 / 1e14, 2))
        if key not in massdists:
            massdists[key] = []
        massdists[key].append(massdist)

    return massdists, toredo


        
#########

def processPklDir(dir, ext='out'):

    output = sorted(glob.glob('%s/*.%s' % (dir, ext)))

    massdists = {}
    for out in output:

        print ' out=',out

        base, ext = os.path.splitext(out)

        print 'processPklDir file='+'%s.pkl' % base
        input = open('%s.pkl' % base, 'rb')
        massdist = cPickle.load(input)
        input.close()

	#adam-old# resultfile = ldac.openObjectFile(out)
	#adam-old#masses = resultfile['masses']

	resultfile = pyfits.open(out)
	objtab=resultfile['OBJECTS']
	try: masses = objtab.data['masses']
	except: masses = objtab.data['mass'] # In *.out the column is called 'mass'
	resultfile.close()
        # masses is array that goes from 5e13 to 1e16 in steps of 5e12

        key = (round(massdist.zcluster, 1), round(massdist.m500 / 1e14, 2))
        if key not in massdists:
            massdists[key] = []
        massdists[key].append((massdist, masses))

    return massdists
    


#########


def consolidate(massdists):

    results = {}
    for key, clusters in massdists.iteritems():
        zcluster, m500 = key

        rs_true = clusters[0][0].rs

        r500 = nfwutils.rdelta(rs_true, 4.0, 500)
#        truemass = nfwutils.massInsideR(rs_true, 4.0, zcluster, r500)
        truemass = nfwutils.massInsideR(rs_true, 4.0, zcluster, 1.5)
        massests = np.array([x.mu for x,y in clusters])
        diff = massests - truemass
#        ml, (m, p) = sp.ConfidenceRegion(diff, bins=19)
        bias = np.average(diff)
#        bias = ml
        scatter = np.std(diff)
        typsig = np.average(np.array([x.sig for x,y in clusters]))
        cdfs = []
#        for summ, masses in clusters:
#            sorted_masses = np.sort(masses)
#            cdf = float(len(sorted_masses[sorted_masses <= truemass])) / len(sorted_masses)
#            cdfs.append(cdf)
#            

        results[key] = (truemass, diff, bias, scatter, typsig, cdfs)

    return results




###########
