#!/usr/bin/env python
####################
# Example driver for maxlike sim masses
####################

import maxlike_controller, maxlike_masses, nfwmodel_normshapedistro, maxlike_sim_filehandler


makeController = lambda : maxlike_controller.Controller(modelbuilder = nfwmodel_normshapedistro.NormShapedistro(),
                                           filehandler = maxlike_sim_filehandler.SimFilehandler(),
                                           runmethod = maxlike_masses.ScanModelToFile())


if __name__ == '__main__':

    controller = makeController()

    controller.run_all()




