#!/usr/bin/env python
########################
# For testing a z_split for simulated clusters
########################

import maxlike_split_driver, maxlike_sim_filehandler, nfwmodel_normshapedistro, maxlike_masses
import maxlike_controller

makeController = lambda : maxlike_controller.Controller(modelbuilder = maxlike_split_driver.SplitModelBuilder(nfwmodel_normshapedistro.NormShapedistro()),
                                                        filehandler = maxlike_sim_filehandler.SimFilehandler(),
                                                        runmethod = maxlike_masses.ScanModelToFile())

if __name__ == '__main__':

    controller = makeController()
    controller.run_all()
