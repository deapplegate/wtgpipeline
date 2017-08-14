#!/usr/bin/env python
####################
# Split a variable at the median point and take one side or another
####################

import numpy as np
import maxlike_controller, maxlike_masses, maxlike_subaru_secure_filehandler as mssf
import maxlike_floatvoigt_shapedistro as mfs


##########################


class SplitModelBuilder(object):

    def __init__(self, modelbuilder):

        self.modelbuilder = modelbuilder

        self.cuts = [self.modelbuilder.modelCut, self.splitVar]

    ###########

    def __getattr__(self, name):

        return getattr(self.__dict__['modelbuilder'], name)

    ##########

    def addCLOps(self, parser):

        self.modelbuilder.addCLOps(parser)

        parser.add_option('--splitcat', dest='splitcat',
                          default = 'lensingcat')
        parser.add_option('--splitvar', dest='splitvar',
                          default = None)
        parser.add_option('--splitvar-high', dest='splitvarTakeHigh',
                          default = False, action='store_true')
        parser.add_option('--splitvar-val', dest='splitvarval',
                          default = None, type='float')


    ######
    
    def createOptions(self, splitcat = 'lensingcat', 
                      splitvar = None, splitvarTakeHigh = False, 
                      splitvarval = None, *args, **keywords):

        options, args = self.modelbuilder.createOptions(*args, **keywords)

        options.splitcat = splitcat
        options.splitvar = splitvar
        options.splitvarTakeHigh = splitvarTakeHigh
        options.splitvarval = splitvarval

        return options, args

    #######

    def splitVar(self, manager):

        options = manager.options

        if options.splitvar is None:
            return np.ones(len(manager.inputcat)) == 1

        cat = getattr(manager, options.splitcat)

        cat = cat.matchById(manager.inputcat)

        if options.splitvarval is None:
            cutpoint = np.median(cat[options.splitvar])
        else:
            cutpoint = options.splitvarval

        if options.splitvarTakeHigh:


            return cat[options.splitvar] > cutpoint

        else:

            return cat[options.splitvar] <= cutpoint




################


makeController = lambda : maxlike_controller.Controller(modelbuilder =  SplitModelBuilder(mfs.FloatVoigtShapedistro()),
                                                        filehandler = mssf.SubaruSecureFilehandler(),
                                                        runmethod = maxlike_masses.SampleModelToFile())


controller = makeController()


###########################


if __name__ == '__main__':

    controller.run_all()

