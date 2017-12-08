#!/usr/bin/env python
####################
# Example driver for maxlike sim masses
####################

import maxlike_controller, maxlike_masses, nfwmodel_voigtnorm_shapedistro, maxlike_subaru_filehandler


#controller = maxlike_controller.Controller(modelbuilder = maxlike_masses,
#                                           shapedistro = nfwmodel_voigtnorm_shapedistro.VoigtnormShapedistro(),
#                                           filehandler = maxlike_subaru_filehandler.SubaruFilehandler(),
#                                           runmethod = maxlike_masses.SampleModelToFile())

makeController = lambda : maxlike_controller.Controller(modelbuilder = maxlike_masses,
                                           filehandler = maxlike_subaru_filehandler.SubaruFilehandler(),
                                           runmethod = maxlike_masses.SampleModelToFile())
#####################
if __name__ == '__main__':
    controller = makeController()
    controller.run_all()
