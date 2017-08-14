#!/usr/bin/env python
####################
# Example driver for maxlike sim masses
####################

import maxlike_controller, maxlike_nfw2param as m2p
import  maxlike_subaru_secure_filehandler as mssf


#######################

makeController = lambda : maxlike_controller.Controller(modelbuilder =  m2p.NFW2Param(),
                                    filehandler = mssf.SubaruSecureFilehandler(),
                                    runmethod = m2p.SampleModelToFile())


controller = makeController()



if __name__ == '__main__':

    controller.run_all()

