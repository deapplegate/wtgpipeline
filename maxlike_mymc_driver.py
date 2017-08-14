#!/usr/bin/env python
####################
# Example driver for maxlike sim masses
####################

import maxlike_controller, maxlike_bentstep_voigt as mbv
import  maxlike_subaru_secure_filehandler as mssf, pymc_mymcmc_adapter as pma
from mpi4py import MPI

#######################

class MPIController(maxlike_controller.Controller):

    def load(self, options = None, args = None):

        if options is None:
            options = self.options

        options.outputFile = '%s.chain%d' % (options.outputFile, MPI.COMM_WORLD.Get_rank())

        maxlike_controller.Controller.load(self, options, args)



#######################

makeController = lambda : MPIController(modelbuilder =  mbv.BentVoigt3Shapedistro(),
                                        filehandler = mssf.SubaruSecureFilehandler(),
                                        runmethod = pma.MyMCRunner())


controller = makeController()



if __name__ == '__main__':

    controller.run_all()

