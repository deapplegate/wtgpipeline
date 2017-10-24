#!/usr/bin/env python
######################
# Centralized center for photometry db operations
#   or at least thats the eventual end goal
######################

import unittest, datetime, os
import sqlobject, sqlobject.inheritance

######################

__cvs_id__ = "$Id: photometry_db.py,v 1.17 2010-10-05 22:43:59 dapple Exp $"

##################################################
# DATABASE CONNECTION
##################################################


def useTestMode():
    return (('PHOTOMETRY_TEST' in os.environ) and (os.environ['PHOTOMETRY_TEST'] != "0")) or __name__ == '__main__'

testMode = False
__default_connection__ = sqlobject.connectionForURI('mysql://weaklensing:darkmatter@ki-sr01/subaru')

if useTestMode():
    testMode = True
    dbfile = '/u/ki/dapple/nfs/pipeline2/wtgpipeline/phototest.db'
    __default_connection__ = sqlobject.connectionForURI('sqlite://%s' % dbfile)


##################################################
# DATA MODEL
##################################################

class ObservationCalibration(sqlobject.SQLObject):
    
    cluster = sqlobject.StringCol(length=55)
    filter = sqlobject.StringCol(length=55)
    mangledSpecification = sqlobject.StringCol(length=250)
    calibration = sqlobject.ForeignKey('ZeropointEntry')

    ClusterFilterIndex = sqlobject.DatabaseIndex('cluster', 'filter', 'mangledSpecification', unique=True)

    def _get_specification(self):
        return unmangleSpecification(self.mangledSpecification)

    def _set_specification(self, **specification):
        self.mangledSpecification = mangleSpecification(specification)
        

#####

class ZeropointEntry(sqlobject.inheritance.InheritableSQLObject):

    user = sqlobject.StringCol()
    time = sqlobject.DateTimeCol()
    cluster = sqlobject.StringCol()
    filter = sqlobject.StringCol()
    zp = sqlobject.FloatCol()
    mangledSpecification = sqlobject.StringCol()

    def _get_specification(self):
        return unmangleSpecification(self.mangledSpecification)

    def _set_specification(self, **specification):
        self.mangledSpecification = mangleSpecification(specification)



#####

class SlrZP(ZeropointEntry):

    fitFilter = sqlobject.StringCol()
    zperr = sqlobject.FloatCol()

#####

class SpecialFiltersCalibration(ZeropointEntry):
    
    file=sqlobject.StringCol()
    

#######

class LePhareZP(ZeropointEntry):

    constantFilter = sqlobject.StringCol()


#########

class PhotometricCalibration(ZeropointEntry):

    zperr = sqlobject.FloatCol()
    colorterm = sqlobject.FloatCol()
    colorerr = sqlobject.FloatCol(default=0.)
    fixedcolor = sqlobject.BoolCol(default=True)

    table_name = 'photometric_calibration'

##########




zp_subclasses = [ SlrZP, SpecialFiltersCalibration, LePhareZP, PhotometricCalibration]


################################
## Interface
################################

class Photometry_db(object):

    def __init__(self, connection = __default_connection__):

        sqlobject.sqlhub.processConnection = connection

        self.createTables()

    ################################

    def createTables(self, reset = False):

        if reset:
            ObservationCalibration.dropTable(ifExists = True)
            ZeropointEntry.dropTable(ifExists = True)
            for subclass in zp_subclasses:
                subclass.dropTable(ifExists = True)

        ObservationCalibration.createTable(ifNotExists = True)
        ZeropointEntry.createTable(ifNotExists = True)
        for subclass in zp_subclasses:
            subclass.createTable(ifNotExists = True)

    #################################

    def updateCalibration(self, cluster, filter, calibration, **specification):

        mangledSpecification = mangleSpecification(specification)

        observation = ObservationCalibration.selectBy(cluster=cluster, 
                                                      filter=filter, mangledSpecification = mangledSpecification).getOne(default=None)

        if observation is None:
            ObservationCalibration(cluster=cluster,
                                   filter = filter,
                                   mangledSpecification = mangledSpecification,
                                   calibration = calibration)
        else:
            observation.set(calibration = calibration)

    ###################################

    def getZeropoint(self, cluster, filter, **specification):

        mangledSpecification = mangleSpecification(specification)

        observation = ObservationCalibration.selectBy(cluster=cluster, filter=filter, mangledSpecification = mangledSpecification).getOne(default=None) 
        if observation is None:
            return None

        return observation.calibration

    ##############################################

    def releasetag(self, worklist, tagname, **specification):
        #worklist is a list of (cluster, detectfilter, [fullnamed photfilters]) tuples


        for cluster, filter, filters in worklist:

            for pfilter in filters:

                calib = self.getZeropoint(cluster, pfilter, **specification)

                if calib is None:
                    print 'Skipping %s %s %s' % (cluster, filter, pfilter)
                    continue

                self.updateCalibration(cluster = cluster, filter = pfilter, calibration = calib, tag=tagname)




    ##############################################


    def registerLePhareZP(self, cluster, filter, constantFilter,  zp, **specification):

        mangledSpecification = mangleSpecification(specification)

        user = os.environ['USER']
        time = datetime.datetime.now()
        return LePhareZP(cluster = cluster, filter = filter, constantFilter = constantFilter, 
                        user = user, time = time, zp = zp, source = 'lephare', mangledSpecification = mangledSpecification)



    ##############################################

    def registerSlrZP(self, cluster, filter, fitFilter, zp, zperr, **specification):

        mangledSpecification = mangleSpecification(specification)

        user = os.environ['USER']
        time = datetime.datetime.now()
        return SlrZP(cluster = cluster, 
                     filter = filter,
                     user = user, 
                     time = time, 
                     zp = zp,
                     zperr = zperr,
                     fitFilter = fitFilter,
                     mangledSpecification = mangledSpecification)


    ##############################################


    def registerPhotometricCalibration(self, cluster, filter, fitresults, **specification):

        mangledSpecification = mangleSpecification(specification)

        user = os.environ['USER']
        time = datetime.datetime.now()

        return PhotometricCalibration(user = user,
                                      time = time,
                                      cluster = cluster, 
                                      filter = filter,
                                      zp = fitresults.zp,
                                      zperr = fitresults.zperr,
                                      colorterm = fitresults.colorterm,
                                      colorerr = fitresults.colorterm_err,
                                      fixedcolor = fitresults.fixedcolor,
                                      mangledSpecification = mangledSpecification)

    ##############################################

    def registerSpecialFiltersCalibration(self, cluster, filter, file, zp, **specification):

        mangledSpecification = mangleSpecification(specification)

        user = os.environ['USER']
        time = datetime.datetime.now()

        return SpecialFiltersCalibration(user = user,
                                         time = time,
                                         cluster = cluster,
                                         filter = filter, 
                                         zp = zp,
                                         file = file,
                                         mangledSpecification = mangledSpecification)

    ###############################################

    def registerManualCalibration(self, cluster, filter, zp, **specification):

        
        mangledSpecification = mangleSpecification(specification)

        user = os.environ['USER']
        time = datetime.datetime.now()

        return ZeropointEntry(user = user,
                              time = time,
                              cluster = cluster,
                              filter = filter, 
                              zp = zp,
                              mangledSpecification = mangledSpecification)


##############################################
## UTILITIES
##############################################


def mangleSpecification(specification):

    if len(specification) == 0:
        return ''

    keys = specification.keys()
    sorted_keys = sorted(keys)

    mangled = '%s=%s' % (sorted_keys[0], specification[sorted_keys[0]])
    for key in sorted_keys[1:]:
        mangled += ':%s=%s' % (key, specification[key])

    return mangled
    
def unmangleSpecification(specString):

    if specString == '':
        return {}

    unmangled = {}

    pairs = specString.split(':')
    
    for pairString in pairs:
        key, val = pairString.split('=')
        unmangled[key] = val

    return unmangled



##############################################
### TESTING
#############################################


class TestDatabase(unittest.TestCase):

    def setUp(self):

        if os.path.exists(dbfile):
            os.remove(dbfile)

        self.db = Photometry_db()

        self.cluster = 'mytestcluster'
        

    ########

    def tearDown(self):

        if os.path.exists(dbfile):
            os.remove(dbfile)

    #########

    def testStoreAndRetrieve(self):
        
        filter = 'SUBARU-10_2-1-W-J-V'
        file = 'specialfile1'
        zp = 25.3
        mode = 'iso'

        calibration = self.db.registerSpecialFiltersCalibration(cluster = self.cluster, 
                                                                filter = filter,
                                                                file = file,
                                                                zp = zp,
                                                                mode=mode)

        self.db.updateCalibration(cluster = self.cluster,
                                  filter = filter,
                                  calibration = calibration,
                                  mode = mode)

        returnedCali = self.db.getZeropoint(cluster = self.cluster, filter = filter, mode=mode)

        self.assertEquals(calibration, returnedCali)

    #########

    def testMultipleModes(self):

        calibration = self.db.registerSpecialFiltersCalibration(cluster = self.cluster,
                                                                filter= 'SUBARU-10_2-1-W-J-V',
                                                                file = 'specialfile1',
                                                                zp = 25.3,
                                                                mode = 'iso')

        self.db.updateCalibration(cluster = self.cluster, filter = 'SUBARU-10_2-1-W-J-V',
                                  calibration = calibration,
                                  mode = 'iso')
        calibration2 = self.db.registerSpecialFiltersCalibration(cluster = self.cluster,
                                                                filter= 'SUBARU-10_2-1-W-J-V',
                                                                file = 'specialfile1',
                                                                zp = 25.8,
                                                                mode = 'aper')

        self.db.updateCalibration(cluster = self.cluster, filter = 'SUBARU-10_2-1-W-J-V',
                                  calibration = calibration2,
                                  mode = 'aper')

        returnedCali = self.db.getZeropoint(cluster = self.cluster, filter = 'SUBARU-10_2-1-W-J-V',
                                            mode = 'iso')

        self.assertEquals(calibration, returnedCali)

    ########

    def testMultipleSets(self):


        calibration = self.db.registerSpecialFiltersCalibration(cluster = self.cluster,
                                                                filter= 'SUBARU-10_2-1-W-J-V',
                                                                file = 'specialfile1',
                                                                zp = 25.3,
                                                                mode = 'iso')

        self.db.updateCalibration(cluster = self.cluster, filter = 'SUBARU-10_2-1-W-J-V',
                                  calibration = calibration,
                                  mode = 'iso')
        calibration2 = self.db.registerSpecialFiltersCalibration(cluster = self.cluster,
                                                                filter= 'SUBARU-10_2-1-W-J-V',
                                                                file = 'specialfile1',
                                                                zp = 25.8,
                                                                mode = 'iso')

        self.db.updateCalibration(cluster = self.cluster, filter = 'SUBARU-10_2-1-W-J-V',
                                  calibration = calibration2,
                                  mode = 'iso')

        returnedCali = self.db.getZeropoint(cluster = self.cluster, filter = 'SUBARU-10_2-1-W-J-V',
                                            mode = 'iso')

        
        self.assertEquals(calibration2, returnedCali)



########################

def test():

    assert(testMode)

    testcases = [TestDatabase]
    
    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)




##############################################
### COMMAND LINE EXECUTABLE
##############################################

if __name__ == '__main__':

    test()
