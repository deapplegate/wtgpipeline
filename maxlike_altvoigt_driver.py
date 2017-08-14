#!/usr/bin/env python
####################
# Example driver for maxlike sim masses
####################

import maxlike_controller, maxlike_masses, nfwmodel_voigtnorm_shapedistro, maxlike_subaru_secure_filehandler


controller = maxlike_controller.Controller(modelbuilder = maxlike_masses,
                                           shapedistro = nfwmodel_voigtnorm_shapedistro.VoigtnormShapedistro('/nfs/slac/g/ki/ki06/anja/SUBARU/shapedistro/voigt_posterior.enlarged.normapprol.pkl'),
                                           filehandler = maxlike_subaru_secure_filehandler.SubaruSecureFilehandler(),
                                           runmethod = maxlike_masses.SampleModelToFile())



if __name__ == '__main__':

    controller.run_all()

