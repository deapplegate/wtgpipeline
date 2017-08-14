###########################
# Create simulations matched to cluster catalogs to check ccmass v P(z) mass scatter
###########################

import os, glob
import numpy as np
import ldac, cosmos_sim as cs
from dappleutils import readtxtfile
import process_cosmos_sims as pcs
import nfwutils, shearprofile as sp
import compare_masses as cm


###########################


def createSimFiles(cluster, filter, image, mass, redshift, bpzfile, outdir, nfields = 25):

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    clusterdir = '/u/ki/dapple/subaru/%s/LENSING_%s_%s_aper/%s' % (cluster, filter, filter, image)

    lensing = ldac.openObjectFile('%s/cut_lensing.cat' % clusterdir)

    bpz = ldac.openObjectFile(bpzfile, 'COS30PHOTZ')


    ngals = len(lensing)
    maxradii = np.max(np.sqrt((lensing['Xpos'] - 5000)**2 + (lensing['Ypos'] - 5000)**2))

    fields = []

    for i in range(nfields):

        field = cs.bootstrapField(bpz, np.ones(len(bpz)), np.ones(len(bpz)), galdensity = galdensity,
                                  maxradii = maxradii, id = 'SeqNr', ngals = ngals)

        field.saveas('%s/%s.%s.%s.master_%d.cat' % (outdir, cluster, filter, image, i), clobber=True)

        fields.append(field)


    cs.createCutoutSuite([redshift], [mass], bpz, None, None, outdir, simcats = fields, shape_distro_kw_sets = nfields*[{'sigma' : 0.25}])


#####################################

def createPrecutSimFiles(cluster, filter, image, mass, redshift, bpzfile, reconfile, outdir, nfields = 50):

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    clusterdir = '/u/ki/dapple/subaru/%s/LENSING_%s_%s_aper/%s' % (cluster, filter, filter, image)

    lensing = ldac.openObjectFile('%s/cut_lensing.cat' % clusterdir)

    bpz = ldac.openObjectFile(bpzfile)
    recon = ldac.openObjectFile(reconfile, 'COS30PHOTZ')
    bpz = bpz.matchById(recon, selfid='ID')
    recon = recon.matchById(bpz, otherid='ID')

    assert(len(bpz) == len(recon))


    bpz = bpz.filter(np.logical_and(recon['zp_best'] > redshift + 0.1, recon['zp_best'] < 1.25))



    maxradii = np.max(np.sqrt((lensing['Xpos'] - 5000)**2 + (lensing['Ypos'] - 5000)**2))

    fields = []

    for i in range(nfields):

        field = cs.bootstrapField(bpz, np.ones(len(bpz)), np.ones(len(bpz)), galdensity = None,
                                  maxradii = maxradii, id = 'ID', ngals = 10000)

        field.saveas('%s/%s.%s.%s.master_%d.cat' % (outdir, cluster, filter, image, i), clobber=True)

        fields.append(field)


    cs.createCutoutSuite([redshift], [mass], bpz, None, None, outdir, simcats = fields, shape_distro_kw_sets = nfields*[{'sigma' : 0.25}])

##################

def createPrecutNoOutlierSimFiles(cluster, filter, image, mass, redshift, bpzfile, reconfile, outdir, nfields = 50):

    if not os.path.exists(outdir):
        os.mkdir(outdir)

    clusterdir = '/u/ki/dapple/subaru/%s/LENSING_%s_%s_aper/%s' % (cluster, filter, filter, image)

    lensing = ldac.openObjectFile('%s/cut_lensing.cat' % clusterdir)

    bpz = ldac.openObjectFile(bpzfile, 'COS30PHOTZ')
    recon = ldac.openObjectFile(reconfile, 'STDTAB')
    recon = recon.matchById(bpz)


    bpz = bpz.filter(np.logical_and(np.logical_and(recon['BPZ_Z_B'] > redshift + 0.1, recon['BPZ_Z_B'] < 1.25),
                                    np.abs(recon['BPZ_Z_B'] - bpz['zp_best']) < 0.3))



    ngals = len(lensing)
    maxradii = np.max(np.sqrt((lensing['Xpos'] - 5000)**2 + (lensing['Ypos'] - 5000)**2))

    fields = []

    for i in range(nfields):

        field = cs.bootstrapField(bpz, np.ones(len(bpz)), np.ones(len(bpz)), galdensity = None,
                                  maxradii = maxradii, id = 'SeqNr', ngals = 10000)

        field.saveas('%s/%s.%s.%s.master_%d.cat' % (outdir, cluster, filter, image, i), clobber=True)

        fields.append(field)


    cs.createCutoutSuite([redshift], [mass], bpz, None, None, outdir, simcats = fields, shape_distro_kw_sets = nfields*[{'sigma' : 0.25}])

    
    
#####################################

    
    
#####################################

def createTxtCats(cluster, filter, image, outdir):

    output = open('%s/info.txt' % outdir, 'w')
    output.write('%s %s %s\n' % (cluster, filter, image))
    output.close()


    for catfile in glob.glob('%s/cutout_*.cat' % outdir):

        root, ext = os.path.splitext(catfile)

        cat = ldac.openObjectFile(catfile)
        
        output = open('%s.dat' % root, 'w')

        for id, r_pix, ghat in zip(cat['SeqNr'], cat['r_pix'], cat['ghats']):

            xpos = r_pix
            ypos = 0.0
            
            gs1 = -ghat
            gs2 = 0.0
            sigma = 0.25

            output.write('%d %f %f %f %f %f\n' % (id, xpos, ypos, gs1, gs2, sigma))

        output.close()

############################################

def outputBeta(simdir, cluster):

    for catfile in glob.glob('%s/%s//cutout_*.cat' % (simdir, cluster)):

        root, ext = os.path.splitext(catfile)

        cat = ldac.openObjectFile(catfile)

        zcluster = cat.hdu.header['Z']
        
        output = open('%s.beta' % root, 'w')

        betas = nfwutils.beta_s(cat['z'], zcluster)

        aveBeta = np.mean(betas)
        aveBeta2 = np.mean(betas**2)

        
        output.write('%f %f\n' % (aveBeta, aveBeta2))

        output.close()
    
                     
    
############################################


def readCCSummary(outdir, clusters):

    masses = {}
    
    for cluster in clusters:

        masses[cluster] = np.hstack(readtxtfile('%s/%s.anja.mass.dat' % (outdir, cluster)))

        print cluster, len(masses[cluster])
        
            

    return masses, np.array([masses[x] for x in clusters])

##############################################

def readMLMasses(workdir, subdir, clusters):

    
    masses = {}
    errs = {}
    scale_radii = {}

    for cluster in clusters:

        print cluster

        outdir = '%s/%s/%s' % (workdir, cluster, subdir)

        print outdir

        massdists = list(pcs.processSummaryDir(outdir, '.out.mass15mpc.mass.summary.pkl').itervalues())[0]

        masses[cluster] = np.array([x[0].mu for x in massdists])
        errs[cluster] = np.array([x[0].sig for x in massdists])
        scale_radii[cluster] = float(massdists[0][0].rs)

    return masses, errs, np.row_stack([masses[x] for x in clusters]), scale_radii

################################################

def readPointMasses(workdir, subdir, clusters):

    
    masses = {}
    scale_radii = {}

    for cluster in clusters:

        print cluster

        outdir = '%s/%s/%s' % (workdir, cluster, subdir)

        print outdir

        rawmassdists = pcs.processPklDir(outdir)
        massdists = list(rawmassdists.itervalues())[0]

        masses[cluster] = np.array([x[0].mu for x in massdists])
        scale_radii[cluster] = massdists[0][0].rs

    return masses, np.row_stack([masses[x] for x in clusters]), scale_radii


################################################

def bootstrapMean(fracbias):

    nclusters = fracbias.shape[1]
    nsamples = fracbias.shape[0]

    means = np.zeros(nclusters)
    errs = np.zeros((2, nclusters))

    for i in range(nclusters):

        curset = fracbias[:,i]
        
        bootstraps = np.array([np.mean(curset[np.random.randint(0, nsamples, nsamples)]) for j in range(100000)])

        ave, err = sp.ConfidenceRegion(bootstraps)


        means[i] = ave
        errs[:,i] = err

    return means, errs
            
    


#################################################

def biasLevel(fracbias):

    nsamples, nclusters = fracbias.shape

    bias_samples = np.zeros(10000)
    for i in range(10000):
        includeClusters = np.random.randint(0, nclusters, nclusters)
        sampleGrid = fracbias.T[includeClusters]
        samplePick = np.random.randint(0, nsamples, nclusters)
        
        bias_samples[i] = np.mean([sampleGrid[j,k] for j,k in enumerate(samplePick)])

    return bias_samples
        

##################################################

def calcMasses(clusters, scale_radii, concentration = 4.0, mradius = 1.5):

    redshifts = cm.readClusterRedshifts()
    redshifts = [redshifts[x] for x in clusters]



    return masses

####################################################

def calcFracBias(measuredgrid, truemasses):

    return (measuredgrid.T - truemasses) / truemasses

####################################################

def processFracBiasData(workdir, subdirs, clusters, redshifts, concentration = 4., mradius = 1.5):

    fracbiases = []

    for subdir in subdirs:

        masses, errs, massgrid, scale_radii = readMLMasses(workdir, subdir, clusters)

        truemasses = [nfwutils.massInsideR(scale_radii[x], concentration, redshifts[x], mradius) for x in clusters]

        fracbias = calcFracBias(massgrid, truemasses)

        fracbiases.append(fracbias)


    return fracbiases


#########################################################

