#!/usr/bin/env python
#########################
#
# Save slr offsets to the photometry database
#
##########################

import unittest, sys, os, optparse, re
import pyfits, numpy as np
sys.path.append('/u/ki/awright/bonnpipeline/')
import photometry_db, ldac, adam_utilities

##########################

__cvs_id__ = "$Id: save_slr.py,v 1.2 2010-09-01 01:38:56 dapple Exp $"

##########################

##################################################
### Photometry Global Database
##################################################

class Phot_db(object):
    '''Provide lazy, proxy access to the photometry database of choice'''
    def __init__(self, db, *args, **keywords):
        self.db = db
        self.instance = None
        self.args = args
        self.keywords = keywords
    def __getattr__(self, name):
        if self.instance is None:
            self.instance = self.db(*self.args, **self.keywords)
        return getattr(self.instance, name)

__default_photometry_db__ = Phot_db(photometry_db.Photometry_db)

####################################################


def main(argv = sys.argv):

    ###
    
    def parse_spec(option, opt, value, parser):

        key, val = value.split('=')
        
        if not hasattr(parser.values, 'specification'):
            setattr(parser.values, 'specification', {})
            
        parser.values.specification[key] = val

       
    ###



    parser = optparse.OptionParser()

    parser.add_option('-c', '--cluster',
                      dest = 'cluster',
                      help = 'Cluster name',
                      default = None)
    parser.add_option('-o', '--offsets',
                      dest = 'offsetfile',
                      help = 'Name of offset file',
                      metavar = 'FILE',
                      default = None)
    parser.add_option('-i', '--input',
                      dest = 'inputfile',
                      help = 'Name of catalog which was calibrated',
                      metavar = 'FILE',
                      default = None)
    parser.add_option('-s', '--spec', dest='specification',
                      action='callback',
                      type= 'string', 
                      help='key=val set determines the uniqueness of this calibration',
                      default = {},
                      metavar = 'key=val',
                      callback = parse_spec)
    parser.add_option('--fluxtype',
                      dest = 'fluxtype',
                      help = 'Flux Type to pull from ZPS table',
                      default = 'APER')
                      

    options, args = parser.parse_args(argv)

    if options.cluster is None:
        parser.error('Please specify cluster name')
    if options.offsetfile is None:
        parser.error('Please specify SLR offset file')
    if options.inputfile is None:
        parser.error('Please specify cat that SLR calibrated')

    zplist = ldac.openObjectFile(options.inputfile, 'ZPS')

    print ' zplist["filter"]=',zplist["filter"]

    
    saveSlrZP(cluster = options.cluster,
              offsetFile = options.offsetfile,
              zplist = zplist,
              fluxtype = options.fluxtype,
              **options.specification)




####################################################
# User Callable Functions
####################################################

def saveSlrZP(cluster, offsetFile, zplist, photometry_db = __default_photometry_db__, fluxtype = 'APER', **specifications):

    offsets = {}
    input = open(offsetFile)
    for line in input.readlines():
        tokens = line.split()
        filter = tokens[1]
        zp = float(tokens[2])
        zperr = float(tokens[3])

        if not re.match('MAG_', filter):
            filter = 'MAG_%s-%s' % (fluxtype, filter)

        offsets[filter] = (zp, zperr)





    filters = {}
    for filter, zp in zip(zplist['filter'], zplist['zeropoints']):
        if not re.match('FLUX_', filter) and not re.match('MAG_', filter):
            filter = 'MAG_%s-%s' % (fluxtype, filter)
        match = re.match('FLUX_(.*)', filter)
        if match:
            filter = 'MAG_%s' % match.group(1)
        filters[filter] = zp




    slr_offsets = {}
    for filterkey in offsets.keys():

        filter = adam_utilities.extractFullFilter(filterkey)

	#adam-SHNT# problem starts here
	try:
		new_zp = filters[filterkey] + offsets[filterkey][0]
	except KeyError:
		print "filterkey=",filterkey
		print "filters.keys()=",filters.keys()
		print "offsets.keys()=",offsets.keys()
		raise
        zperr = offsets[filterkey][1]

        
        
        slrZP = photometry_db.registerSlrZP(cluster, filter = filter, 
                                            zp = float(new_zp), zperr = zperr, 
                                            fitFilter = filter, **specifications)


        instrument, config, chip, stdfilter = adam_utilities.parseFilter(filter)
        slr_offsets[filter] = [instrument, stdfilter, slrZP]


    for filterkey in filters.keys():

        filter = adam_utilities.extractFullFilter(filterkey)
        
        if filter in slr_offsets:

            slr_instrument, slr_stdfilter, slrZP = slr_offsets[filter]
            
            photometry_db.updateCalibration(cluster, filter = filter, calibration = slrZP, **specifications)
            

        else:

            instrument, config, chip, stdfilter = adam_utilities.parseFilter(filter)

            for slr_filterkey, (slr_instrument, slr_stdfilter, slrZP) in slr_offsets.iteritems():

                if slr_instrument == instrument and slr_stdfilter == stdfilter:
                    photometry_db.updateCalibration(cluster, filter = filter, calibration = slrZP, **specifications)
                    break



####################################################
# TESTING
####################################################

class TestingDBEntry(object):

    def __init__(self, id, **fields):
        self.id = id
        self.fields = fields

    def __getattr__(self, name):
        if name in self.fields:
            return self.fields[name]
        raise AttributeError

###

class TestingDatabase(object):

    def __init__(self):

        self.reset()

    ###

    def reset(self):
        self.slr = []
        self.calibrations = []
    
    ###

    def registerSlrZP(self, cluster, fitFilter, zp, zperr, **specification):

        entry = TestingDBEntry(len(self.slr), cluster = cluster,
                                       fitFilter = fitFilter,
                                       zp = zp,
                                       zperr = zperr,
                                       **specification)
        self.slr.append(entry)
        
        return entry

    ###

    def updateCalibration(self, cluster, calibration, **specification):
        self.calibrations.append(TestingDBEntry(len(self.calibrations), cluster = cluster, calibration = calibration, **specification))


###########

class TestSaveOffsets(unittest.TestCase):

    def setUp(self):

        self.db = TestingDatabase()

        raw_slr_offsets = '''V SUBARU-10_2-1-W-J-V 0.039 0.0043
MPu MEGAPRIME-0-1-u 0.195374 0.016295
WHTB WHT-0-1-B 0.516663 0.0217352
'''

        self.filternames = [ line.split()[1] for line in raw_slr_offsets.splitlines() ]
        self.orig_zps = np.random.uniform(-4, 4, size=3) + 27.

        class ZP(object):
            def __init__(self, filter, zp, zperr):
                self.filter = filter
                self.zp = zp
                self.zperr = zperr

        self.slr_zps = {}
        for i, line in enumerate(raw_slr_offsets.splitlines()):
            tokens = line.split()
            filter = tokens[1]
            offset = float(tokens[2])
            zperr = float(tokens[3])
            self.slr_zps[filter] = ZP(filter, self.orig_zps[i] + offset, zperr)

        
        self.offsetFile = 'test_save_slr.offsets'
        output = open(self.offsetFile, 'w')
        output.write(raw_slr_offsets)
        output.close()

    #######

    def tearDown(self):

        if os.path.exists(self.offsetFile):
            os.remove(self.offsetFile)

    #######

    def testSaveOffsetsforSLR(self):

        zplist = ldac.LDACCat(pyfits.new_table(pyfits.ColDefs([pyfits.Column(name = 'filter', format='20A', 
                                                                             array = self.filternames),
                                                               pyfits.Column(name = 'zeropoints', format='E', 
                                                                             array = self.orig_zps)])))

        saveSlrZP(cluster = 'testcluster', offsetFile = self.offsetFile, 
                  zplist = zplist, fluxtype = 'iso', myspec = 'custom',
                  photometry_db = self.db)

        self.assertEquals(len(self.db.slr), 3)

        self.assertEquals(sorted([slr.fitFilter for slr in self.db.slr]), sorted(self.slr_zps.keys()))

        for slr in self.db.slr:

            match = self.slr_zps[slr.fitFilter]
        
            self.assertEquals(slr.cluster, 'testcluster')
            self.assertEquals(slr.fitFilter, match.filter)
            self.assertTrue(np.abs(slr.zp - match.zp) < 0.001)
            self.assertTrue(np.abs(slr.zperr - match.zperr) < 0.001)
            self.assertEquals(slr.fluxtype, 'iso')
            self.assertEquals(slr.myspec, 'custom')


    #######

    def testTransferOffsets(self):

        transferFilters = 'SUBARU-9-2-W-J-V SUBARU-10_1-1-W-J-V MEGAPRIME-0-1-g'.split()
        transfer_orig_zps = [23.4, 25.3, 22.4]
        correspondingFilters = {'SUBARU-9-2-W-J-V' : 'SUBARU-10_2-1-W-J-V',
                                'SUBARU-10_1-1-W-J-V' : 'SUBARU-10_2-1-W-J-V',
                                'MEGAPRIME-0-1-g' : None}
        
        filternames = self.filternames + transferFilters
        orig_zps = self.orig_zps.tolist() + transfer_orig_zps

        zplist = ldac.LDACCat(pyfits.new_table(pyfits.ColDefs([pyfits.Column(name = 'filter', format='20A', 
                                                                             array = filternames),
                                                               pyfits.Column(name = 'zeropoints', format='E', 
                                                                             array = orig_zps)])))

        saveSlrZP(cluster = 'testcluster', offsetFile = self.offsetFile, 
                  zplist = zplist, fluxtype = 'iso', myspec = 'custom',
                  photometry_db = self.db)

        for filter in filternames:

            correspondingFilter = filter
            if filter in correspondingFilters:                
                correspondingFilter = correspondingFilters[filter]

            if correspondingFilter is not None:

                slrmatch = None
                for slr in self.db.slr:
                    if correspondingFilter == slr.fitFilter:
                        slrmatch = slr
                        break
                self.assertTrue(slrmatch is not None)

                calibmatch = None
                for calib in self.db.calibrations:
                    if filter == calib.filter:
                        calibmatch = calib
                        break
                self.assertTrue(calibmatch is not None)

                self.assertEquals(calibmatch.cluster, 'testcluster')
                self.assertEquals(calibmatch.filter, filter)
                self.assertEquals(calibmatch.fluxtype, 'iso')
                self.assertEquals(calibmatch.myspec, 'custom')
                self.assertEquals(calibmatch.calibration, slrmatch)

            
        


#################


def test():

    testcases = [TestSaveOffsets]
    
    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)


                      
                       
################################
### COMMAND LINE EXECUTABLE
################################

if __name__ == '__main__':

    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        test()
    else:
        main()

    
