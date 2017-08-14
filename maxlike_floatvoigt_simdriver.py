#!/usr/bin/env python
####################
# Example driver for maxlike sim masses
####################

import maxlike_controller, maxlike_masses, maxlike_sim_filehandler, maxlike_floatvoigt_shapedistro as mfs
import numpy as np, pymc

###################################


class SimFloatVoigtShapeDistro(mfs.FloatVoigtShapedistro):


    def calcMC(self, data):

        return 0., 0.


    #########################

    def bin_selectors(self, cat):

        return [np.ones(len(cat)) == 1]

    #########################

            

    ###############


    


###############################


makeController = lambda : maxlike_controller.Controller(modelbuilder = SimFloatVoigtShapeDistro(),
                                                        filehandler = maxlike_sim_filehandler.SimFilehandler(),
                                                        runmethod = maxlike_masses.SampleModelToFile())


###############################

if __name__ == '__main__':

    controller = makeController()

    controller.run_all()




