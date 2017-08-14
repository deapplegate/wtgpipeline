#!/usr/bin/env python
####################
# Split a variable at the median point and take one side or another
####################

import numpy as np
import maxlike_controller, maxlike_masses, maxlike_subaru_secure_filehandler as mssf
import maxlike_bentstep_voigt as mbv, maxlike_split_driver as msd


##########################


makeController = lambda : maxlike_controller.Controller(modelbuilder =  msd.SplitModelBuilder(mbv.BentVoigt3Shapedistro()),
                                                        filehandler = mssf.SubaruSecureFilehandler(),
                                                        runmethod = maxlike_masses.SampleModelToFile())


controller = makeController()


###########################


if __name__ == '__main__':

    controller.run_all()

