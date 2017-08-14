#!/usr/bin/env python
#############################
# Handles loading files for a simulation run
#############################

import ldac, cPickle, numpy as np
import pdzfile_utils, nfwutils, maxlike_subaru_filehandler as msf, maxlike_controller, maxlike_masses
import nfwmodel_voigtnorm_shapedistro

############################

subarudir = '/nfs/slac/g/ki/ki05/anja/SUBARU'

default_workdir = '/nfs/slac/g/ki/ki06/anja/SUBARU/catalog_backup_2010-07-27'

#############################

class CovarFilehandler(object):

    def addCLOps(self, parser):

        parser.add_option('-i', '--inputcat', dest='inputCatFile', 
                          help='Simulation format cat containing shape info')
        parser.add_option('-c', '--cluster', dest='cluster',
                          help='Cluster name')
        parser.add_option('-f', '--filter', dest='filter',
                          help='Detection and lensing filter')
        parser.add_option('-v', '--image', dest='image',
                          help='Lensing image, (eg. good, gabodsid3088)')
        parser.add_option('--workdir', dest='workdir',
                          help='location to read/write all files', 
                          default=default_workdir)



    #############################


    def readData(self, manager):

        options = manager.options
        args = manager.args

        manager.open('inputcat', options.inputCatFile, ldac.openObjectFile)

        manager.concentration = 4.0
        manager.zcluster = msf.parseZCluster(options.cluster)
        manager.r500 = msf.readR500(options.cluster)


        clusterdir = '%s/%s' % (subarudir, options.cluster)
        photdir = '%s/PHOTOMETRY_%s_aper' % (clusterdir, options.filter)
        lensingdir = '%s/LENSING_%s_%s_aper/%s' % (clusterdir, options.filter, options.filter, options.image)



        manager.inputPDZ = '%s/%s.%s.pdz.cat' % (options.workdir, options.cluster,
                                                 options.filter)



        manager.open('pdzmanager', manager.inputPDZ, pdzfile_utils.PDZManager.open)
        manager.store('pdzrange pdz'.split(), manager.pdzmanager.associatePDZ(manager.inputcat['SeqNr']))
        
        manager.replace('pdzmanager', None)
    


##############################################


controller = maxlike_controller.Controller(modelbuilder = maxlike_masses,
                                           shapedistro = nfwmodel_voigtnorm_shapedistro.VoigtnormShapedistro(),
                                           filehandler = CovarFilehandler(),
                                           runmethod = maxlike_masses.SampleModelToFile())


#################

if __name__ == '__main__':

    controller.run_all()
