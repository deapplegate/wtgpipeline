#!/usr/bin/env python
#######################
# script to automate making sims from COSMOS photoz
########################
import ldac, numpy as np, astropy.io.fits as pyfits
from adam_cosmos_options import zchoice_switch, cat_switch, cosmos_idcol

#adam Replaced this with stuff in adam_cosmos_options
######### toggle between the old catalog and the new one by changing `cat_switch` in prep_cosmos_run.py
########cat_switch='newcat_matched' #adam-done# cat_switch='oldcat'
if cat_switch=='oldcat':
	cosmos = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos.cat')
	cosmos30 = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos30.cat')
elif cat_switch=='4cccat':
	cosmos30 = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos30.cat')
	hdulist_4cc = pyfits.open('/u/ki/dapple/nfs12/cosmos/cosmos_4cc.cat')
	cosmos = ldac.LDACCat(hdulist_4cc[1])
elif cat_switch=='newcat_matched':
	cosmos = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos.cat')
	cosmos30 = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos30.cat')
	#adam-SHNT# I'll have to adjust some of the keys used in prepSourceFiles!!!!
	###########cosmos=ldac.openObjectFile("/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat")
	###########cosmos30=ldac.openObjectFile("/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.cat")
	#adam-SHNT# This might actually have to stay as: cosmos30 = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos30.cat')

import os, sys, cPickle, glob
import cosmos_sim as cs
#adam-old# import shearprofile as sp


#######################



def prepSourceFiles(photfilters, outdirbase = '/u/ki/dapple/nfs12/cosmos/simulations/publication', 
                    basedir = '/nfs/slac/g/ki/ki05/anja/SUBARU/COSMOS_PHOTOZ'):

    # transfer in cosmos photo-z's
    # parse PDZ file
    # save everything to simulation directory

    sourcedir = '%s/PHOTOMETRY_W-C-IC_%s' % (basedir, photfilters)
    outputdir = '%s/%s' % (outdirbase, photfilters)

    if not os.path.exists(outdirbase):
        os.mkdir(outdirbase)
    if not os.path.exists(outputdir):
        os.mkdir(outputdir)

    #adam-SHNT# In order to have new BPZ results included here, I'd have to have this sourcedir point to my new cats
    sourceBPZFile = '%s/COSMOS_PHOTOZ.APER.1.CWWSB_capak.list.all.bpz.tab' % sourcedir

    bpz = ldac.openObjectFile(sourceBPZFile, 'STDTAB')
    if len(bpz) > len(cosmos):
	    bpz_shortened=bpz.matchById(cosmos, otherid=cosmos_idcol, selfid='SeqNr')
	    bpz=bpz_shortened
    elif len(bpz) == len(cosmos):
	    pass
    else:
	    raise Exception('len(bpz) < len(cosmos), this is not supposed to happen')
    mcosmos30 = cosmos30.matchById(bpz, selfid='ID')

    
    bpz['BPZ_Z_S'][:] = cosmos['zp_best']
    bpz['zspec'][:] = cosmos['zp_best']
    #adam-SHNT# When I switch over to the newcat, this is going to have to change from selecting 'zp_best' from cosmos = '/u/ki/dapple/nfs12/cosmos/cosmos_4cc.cat' or cosmos = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos.cat')
    #		to using 'zchi' or 'zpdf' or 'zphot' from cosmos=ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat')

    photozcut = np.logical_and(bpz['BPZ_Z_S'] >= 0, bpz['BPZ_Z_S'] < 9)

    sizecut = mcosmos30['i_fwhm'] > 13.8

    magcut = mcosmos30['i_auto'] < 24.5

    if cat_switch!='4cccat':
	    bpz = bpz.filter(np.logical_and(np.logical_and(photozcut, sizecut), magcut))
    else:
	    bpz = bpz.filter(photozcut)

    bpz.saveas('%s/bpz.cat' % outputdir, overwrite=True)

    pdzfilename = '%s/COSMOS_PHOTOZ.APER.1.CWWSB_capak.list.all.probs' % sourcedir
    import pdzfile_utils as pdzfile
    pdzmanager = pdzfile.PDZManager.parsePDZ(pdzfilename)
    pdzmanager.save('%s/pdz.pkl' % outputdir)

########################################

def createMasterFields(workdir, nfields = 100, fieldcenters = None):

    bpz = ldac.openObjectFile('%s/bpz.cat' % workdir, 'STDTAB')

    mcosmos = cosmos.matchById(bpz, selfid = cosmos_idcol)

    size = np.ones(len(bpz))
    snratio = np.ones(len(bpz))

    if fieldcenters is not None:
        for i, center in enumerate(fieldcenters):

            fieldcat = cs.extractField(mcosmos, size, snratio, center = center, id=cosmos_idcol)
        
            fieldcat.saveas('%s/field_%d.cat' % (workdir, i), overwrite=True)
            
    else:

        fieldcenters = []
    
        for i in range(nfields):
            
            fieldcat = cs.extractField(mcosmos, size, snratio,  id=cosmos_idcol)
            
            fieldcenters.append((fieldcat.hdu.header['CENTERX'], fieldcat.hdu.header['CENTERY']))
            
            fieldcat.saveas('%s/field_%d.cat' % (workdir, i), overwrite=True)
        
    return fieldcenters

##########################################

def createBootstrapFields(workdir, nfields = 100):

    bpz = ldac.openObjectFile('%s/bpz.cat' % workdir, 'STDTAB')

    mcosmos = cosmos.matchById(bpz, selfid = cosmos_idcol)

    size = np.ones(len(bpz))
    snratio = np.ones(len(bpz))

    for i in range(nfields):
            
        fieldcat = cs.bootstrapField(mcosmos, size, snratio,id = cosmos_idcol)
            
        fieldcat.saveas('%s/field_%d.cat' % (workdir, i), overwrite=True)
            

##########################################

def createCatalogs(workdir, zs = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7], massrange = [3e14, 7e14, 1.2e15, 1.7e15, 2.5e15]):


    bpz = ldac.openObjectFile('%s/bpz.cat' % workdir, 'STDTAB')
    if bpz is None:
        bpz = ldac.openObjectFile('%s/bpz.cat' % workdir, 'COS30PHOTZ')

    sizes = np.ones(len(bpz))
    snratios = np.ones(len(bpz))

    
    #adam: I think this is right, but I'm not certain, it might be that "master" is right for both old and new cats
    #adam: previously this next line was: fields = [ldac.openObjectFile(x) for x in glob.glob('%s/*master_*.cat' % workdir)]
    fields = [ldac.openObjectFile(x) for x in glob.glob('%s/field_*.cat' % workdir)]
    #if cat_switch=='oldcat':
    #    fields = [ldac.openObjectFile(x) for x in glob.glob('%s/field_*.cat' % workdir)]
    #if cat_switch=='newcat_matched':
    #    fields = [ldac.openObjectFile(x) for x in glob.glob('%s/*master_*.cat' % workdir)]


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

	import nfwutils
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
                         shape_distro_kw_sets = 100*[{'sigma' : 0.18, 'gamma' : 0.016}],
                         idcol = 'SeqNr')


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
                                                      'sigma1' : 0.18, 'gamma1' : 0.016}],
                         idcol = 'SeqNr')


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
    
    
