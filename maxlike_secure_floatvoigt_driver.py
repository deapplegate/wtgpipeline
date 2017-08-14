#!/usr/bin/env python
####################
# Example driver for maxlike sim masses
####################

import maxlike_controller, maxlike_floatvoigt_shapedistro as mfs
import  maxlike_subaru_secure_filehandler as mssf, maxlike_masses


#######################

makeController = lambda : maxlike_controller.Controller(modelbuilder =  mfs.FloatVoigtShapedistro(),
                                    filehandler = mssf.SubaruSecureFilehandler(),
                                    runmethod = maxlike_masses.SampleModelToFile())


controller = makeController()



if __name__ == '__main__':

    controller.run_all()

