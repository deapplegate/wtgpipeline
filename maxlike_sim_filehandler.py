#############################
# Handles loading files for a simulation run
#############################

import ldac, cPickle, numpy as np
import astropy.io.fits as pyfits
import pdzfile_utils, nfwutils, varcontainer

#############################

__cvs_id__ = "$Id$"

#############################

class SimFilehandler(object):


    ###############

    def addCLOps(self, parser):

        parser.add_option('-i', '--inputcat', dest='inputCatFile', 
                          help='Simulation format cat containing shape info')
        parser.add_option('-b', '--bpz', dest='inputBPZ',
                          help='BPZ file objects were drawn from')
        parser.add_option('-p', '--pdzfile', dest='inputPDZ', 
                          help='Simulation PDZ file')

    #############################

    def createOptions(self, inputCatFile, inputBPZ, inputPDZ, options = None, args = None):
        
        if options is None:
            options = varcontainer.VarContainer()

        options.inputCatFile = inputCatFile
        options.inputBPZ = inputBPZ
        options.inputPDZ = inputPDZ

        return options, args
        

    #############################

    def readData(self, manager):

        options = manager.options

        manager.open('inputcat', options.inputCatFile, ldac.openObjectFile)

        manager.concentration = manager.inputcat.hdu.header['CONCEN']
        manager.zcluster = manager.inputcat.hdu.header['Z']
        manager.store('r500', nfwutils.rdelta, manager.inputcat.hdu.header['R_S'],
                      manager.concentration, 500)
        
        bpz = ldac.openObjectFile(options.inputBPZ, 'STDTAB')
        if bpz is None:
            bpz = ldac.openObjectFile(options.inputBPZ, 'COS30PHOTZ')
            

        manager.matchedBPZ = bpz.matchById(manager.inputcat, 'z_id')
        bpz = manager.matchedBPZ
        newcols = [pyfits.Column(name = 'z_b', format = 'E', array = bpz['BPZ_Z_B']),
                   pyfits.Column(name='odds', format = 'E', array = bpz['BPZ_ODDS']),
                   pyfits.Column(name='z_t', format = 'E', array = bpz['BPZ_T_B'])]
        inputcat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(newcols) + manager.inputcat.hdu.columns))
        manager.replace('inputcat', inputcat)

        manager.open('pdzmanager', options.inputPDZ, pdzfile_utils.PDZManager.open)
        pdzrange, associatedPDZs = manager.pdzmanager.associatePDZ(manager.inputcat['z_id'])


        pdzrange = pdzrange.astype(np.float64)
        associatedPDZs = associatedPDZs.astype(np.float64)

        manager.pdzrange = pdzrange
        manager.pdz = associatedPDZs

        manager.replace('pdzmanager', None)


