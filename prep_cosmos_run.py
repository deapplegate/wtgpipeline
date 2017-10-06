#!/usr/bin/env python
#######################
# script to automate making sims from COSMOS photoz
########################

import os, sys, cPickle, glob
import ldac, numpy as np
import pdzfile_utils as pdzfile
import cosmos_sim as cs, shearprofile as sp
import nfwutils


#######################

cosmos = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos.cat')
cosmos30 = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos30.cat')


def prepSourceFiles(photfilters, outdirbase = '/u/ki/dapple/nfs12/cosmos/simulations/publication', 
                    basedir = '/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ'):

    # transfer in cosmos photo-z's
    # parse PDZ file
    # save everything to simulation directory

    sourcedir = '%s/PHOTOMETRY_W-C-IC_%s' % (basedir, photfilters)
    outputdir = '%s/%s' % (outdirbase, photfilters)

    if not os.path.exists(outputdir):
        os.mkdir(outputdir)

    sourceBPZFile = '%s/COSMOS_PHOTOZ.APER.1.CWWSB_capak.list.all.bpz.tab' % sourcedir

    bpz = ldac.openObjectFile(sourceBPZFile, 'STDTAB')

    mcosmos30 = cosmos30.matchById(bpz, selfid='ID')

    bpz['BPZ_Z_S'][:] = cosmos['zp_best']
    bpz['zspec'][:] = cosmos['zp_best']

    photozcut = np.logical_and(bpz['BPZ_Z_S'] >= 0, bpz['BPZ_Z_S'] < 9)

    sizecut = mcosmos30['i_fwhm'] > 13.8

    magcut = mcosmos30['i_auto'] < 24.5

    bpz = bpz.filter(np.logical_and(np.logical_and(photozcut, sizecut),
                                    magcut))

    bpz.saveas('%s/bpz.cat' % outputdir, overwrite=True)
    

    pdzfilename = '%s/COSMOS_PHOTOZ.APER.1.CWWSB_capak.list.all.probs' % sourcedir

    pdzmanager = pdzfile.PDZManager.parsePDZ(pdzfilename)

    pdzmanager.save('%s/pdz.pkl' % outputdir)
    
    
########################################

def createMasterFields(workdir, nfields = 100, fieldcenters = None):

    bpz = ldac.openObjectFile('%s/bpz.cat' % workdir, 'STDTAB')

    mcosmos = cosmos.matchById(bpz, selfid = 'id')

    size = np.ones(len(bpz))
    snratio = np.ones(len(bpz))

    if fieldcenters is not None:
        for i, center in enumerate(fieldcenters):

            fieldcat = cs.extractField(mcosmos, size, snratio, center = center)
        
            fieldcat.saveas('%s/field_%d.cat' % (workdir, i), overwrite=True)
            
    else:

        fieldcenters = []
    
        for i in range(nfields):
            
            fieldcat = cs.extractField(mcosmos, size, snratio)
            
            fieldcenters.append((fieldcat.hdu.header['CENTERX'], fieldcat.hdu.header['CENTERY']))
            
            fieldcat.saveas('%s/field_%d.cat' % (workdir, i), overwrite=True)
        
    return fieldcenters

##########################################

def createBootstrapFields(workdir, nfields = 100):

    bpz = ldac.openObjectFile('%s/bpz.cat' % workdir, 'STDTAB')

    mcosmos = cosmos.matchById(bpz, selfid = 'id')

    size = np.ones(len(bpz))
    snratio = np.ones(len(bpz))

    for i in range(nfields):
            
        fieldcat = cs.bootstrapField(mcosmos, size, snratio)
            
        fieldcat.saveas('%s/field_%d.cat' % (workdir, i), overwrite=True)
            

##########################################

def createCatalogs(workdir, zs = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7], massrange = [3e14, 7e14, 1.2e15, 1.7e15, 2.5e15]):


    bpz = ldac.openObjectFile('%s/bpz.cat' % workdir, 'STDTAB')
    if bpz is None:
        bpz = ldac.openObjectFile('%s/bpz.cat' % workdir, 'COS30PHOTZ')

    sizes = np.ones(len(bpz))
    snratios = np.ones(len(bpz))

    
    fields = [ldac.openObjectFile(x) for x in glob.glob('%s/field_*.cat' % workdir)]

    
    cs.createCutoutSuite(zs = zs, massrange = massrange, 
                         goodbpz = bpz, 
                         sizes = sizes, 
                         snratios = snratios, 
                         outputdir = workdir,
                         simcats = fields,
                         idcol = 'SeqNr')


############################################

def createContamCatalogs(bpzfile, workdir, outdir, f500):

    bpz = ldac.openObjectFile(bpzfile, 'STDTAB')
    if bpz is None:
        bpz = ldac.openObjectFile(bpzfile, 'COS30PHOTZ')


    snratio = np.ones(len(bpz))
    size = np.ones(len(bpz))

    for catfile in glob.glob('%s/cutout*.cat' % workdir):

        catbase = os.path.basename(catfile)

        simcat = ldac.openObjectFile(catfile)

        zcluster = simcat.hdu.header['z']

        r_s = simcat.hdu.header['r_s']

        concentration = simcat.hdu.header['concen']

        r500 = nfwutils.rdelta(r_s, concentration, 500)

        contamcat = cs.addContamination(sourcebpz = bpz,
                                        source_snratio = snratio, 
                                        source_size = size, 
                                        simcat = simcat, 
                                        simpdz = None, 
                                        r500 = r500,
                                        zcluster = zcluster,
                                        f500 = f500,
                                        shape_distro_kw = {'sigma' : 0.25})

        contamcat.saveas('%s/%s' % (outdir, catbase), overwrite=True)



###########################################

def createVoigtCatalogs(workdir, zs = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7], massrange = [3e14, 7e14, 1.2e15, 1.7e15, 2.5e15]):

    bpz = ldac.openObjectFile('%s/bpz.cat' % workdir, 'STDTAB')

    sizes = np.ones(len(bpz))
    snratios = np.ones(len(bpz))

    
    fields = [ldac.openObjectFile(x) for x in glob.glob('%s/field_*.cat' % workdir)]

    
    cs.createCutoutSuite(zs = zs, massrange = massrange, 
                         goodbpz = bpz, 
                         sizes = sizes, 
                         snratios = snratios, 
                         outputdir = workdir,
                         simcats = fields,
                         shape_distro = cs.voigtdistro,
                         shape_distro_kw_sets = 100*[{'sigma' : 0.18, 'gamma' : 0.016}])


#########################################

def createDoubleVoigtCatalogs(workdir, zs = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7], massrange = [3e14, 7e14, 1.2e15, 1.7e15, 2.5e15]):

    bpz = ldac.openObjectFile('%s/bpz.cat' % workdir, 'STDTAB')

    sizes = np.ones(len(bpz))
    snratios = np.ones(len(bpz))

    
    fields = [ldac.openObjectFile(x) for x in glob.glob('%s/field_*.cat' % workdir)]

    
    cs.createCutoutSuite(zs = zs, massrange = massrange, 
                         goodbpz = bpz, 
                         sizes = sizes, 
                         snratios = snratios, 
                         outputdir = workdir,
                         simcats = fields,
                         shape_distro = cs.voigtDistro2,
                         shape_distro_kw_sets = 100*[{'alpha' : 0.2, 
                                                      'sigma2' : 0.23, 
                                                      'gamma2' : 0.025, 
                                                      'sigma1' : 0.18, 'gamma1' : 0.016}])

                         
    

##########################################

if __name__ == '__main__':

    workdir = sys.argv[1]
    contam = False
    if len(sys.argv) > 2:
        f500 = float(sys.argv[2])
        outdir = sys.argv[3]
        createContamCatalogs('%s/bpz.cat' % workdir, workdir, outdir, f500)

    else:
        createCatalogs(workdir)
    
    
