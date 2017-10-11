#!/usr/bin/env python
#######################
# Test Suite for maxlike_datamanager.py
#######################

import datamanager as md

import os, unittest, tempfile, shutil, datetime, time, pwd, inspect, getpass
import astropy, astropy.io.fits as pyfits, numpy as np
import ldac, pdzfile_utils as pdzutils

##########################


class TestInterface(unittest.TestCase):

    def setUp(self):
        
        self.workdir = tempfile.mkdtemp()
        
        self.cat1file= '%s/cat1.cat' % self.workdir
        self.cat2file = '%s/cat2.cat' % self.workdir
        
        self.cat1 = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([pyfits.Column(name = 'SeqNr', format='K', array = np.arange(15))])))
        self.cat1.saveas(self.cat1file)
        
        self.cat2 = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([pyfits.Column(name = 'SeqNr', format='K', array = np.arange(15))])))
        self.cat2.hdu.header['EXTNAME']= 'STDTAB'
        self.cat2.saveas(self.cat2file)

        self.pdzfile = '%s/pdz.cat' % self.workdir
        pdzcat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([pyfits.Column(name = 'SeqNr',
                                                                             format = 'K',
                                                                             array = np.arange(15)),
                                               pyfits.Column(name = 'pdz',
                                                             format = '25E',
                                                             array = np.ones((15, 25)))])))
        pdzcat.hdu.header['MINPDZ'  ]= 0 
        pdzcat.hdu.header['MAXPDZ'  ]= 25
        pdzcat.hdu.header['PDZSTEP' ]= 1 

        pdzcat.saveas(self.pdzfile)

    ###############
        
    def tearDown(self):

        shutil.rmtree(self.workdir)

    ################
        

    def testOpenCatalog(self):

        manager = md.DataManager()

        manager.open(name = 'cat1', file = self.cat1file, open = ldac.openObjectFile)

        self.assertTrue('cat1' in manager)
        self.assertTrue(hasattr(manager, 'cat1'))
        self.assertTrue((manager.cat1['SeqNr'] == self.cat1['SeqNr']).all())

        manager.open('cat2', self.cat2file, ldac.openObjectFile, 'STDTAB')
        
        self.assertTrue('cat2' in manager)
        self.assertTrue((manager.cat2['SeqNr'] == self.cat2['SeqNr']).all())
        
    #################

    def testOpenPDZFile(self):

        pdzmanager = pdzutils.PDZManager.open(self.pdzfile)

        manager = md.DataManager()

        manager.open(name = 'pdzmanager', file = self.pdzfile, open = pdzutils.PDZManager.open)

        self.assertTrue('pdzmanager' in manager)
        self.assertEquals(pdzmanager, manager.pdzmanager)


    ##################
        
    def testImmutibility(self):

        manager = md.DataManager()

        manager.sizecol = 'rh'

        self.assertRaises(md.ManagedDataException, setattr, manager, 'sizecol', 32)
        self.assertRaises(md.ManagedDataException, manager.__setitem__, 'sizecol', 42)

    ####################

    def testStore(self):

        manager = md.DataManager()

        thing0 = np.zeros(5)
        manager.store('thing0', thing0)

        thing1 = np.zeros(15) + 1
        thing2 = np.zeros(25) + 2
        
        manager.store('thing1 thing2'.split(), (thing1, thing2))

        self.assertTrue((manager.thing1 == thing1).all())
        self.assertTrue((manager.thing2 == thing2).all())

        self.assertRaises(md.ManagedDataException, manager.store, 'thing0', thing1)

    ####################

    def testStoreFuncResult(self):

        manager = md.DataManager()

        def makeThing(theamount):
            return np.arange(theamount)

        manager.store('thing1', makeThing, 5)

        expected = makeThing(5)


        self.assertTrue((manager.thing1 == expected).all())



        def makeTwoThings(theamount):
            return np.zeros(theamount), np.arange(theamount)
        
        manager.store('thing2 thing3'.split(), makeTwoThings, theamount = 5)

        expected2, expected3 = makeTwoThings(5)

        self.assertTrue((manager.thing2 == expected2).all())
        self.assertTrue((manager.thing3 == expected3).all())
        

    
    #####################

    def testImmutableInPlace(self):
        
        #need to prevent an object, or an object's objects from changing once managed.
        # How?

        pass

    #####################

    def testFilter(self):

        manager = md.DataManager()

        manager.thing0 = np.zeros(15)

        manager.open(name = 'cat1', file = self.cat1file, open = ldac.openObjectFile)

        manager.open(name = 'pdzmanager', file = self.pdzfile, open = pdzutils.PDZManager.open)

        manager.store('pdzrange pdz'.split(), manager.pdzmanager.associatePDZ(manager.cat1['SeqNr']))

        def filterFunction(manager):
            return np.arange(len(manager.cat1))[manager.cat1['SeqNr'] % 2 == 0]

        theFilter = filterFunction(manager)
        expectedSeq = manager.cat1.filter(theFilter)['SeqNr']
        

        manager.update(filterFunction, {'cat1' : 'filter', 'pdz' : '__getitem__'})

        self.assertEquals(len(manager.thing0), 15)
        self.assertEquals(len(manager.pdzrange), 25)

        self.assertTrue((manager.cat1['SeqNr'] == expectedSeq).all())
        self.assertEquals(manager.pdz.shape, (len(expectedSeq), 25))

    ######################

    def testFilterWithArgs(self):

        manager = md.DataManager()

        manager.open(name = 'cat1', file = self.cat1file, open = ldac.openObjectFile)

        def filterFunction(seqnr, mod):
            return seqnr % mod == 0

        expected = manager.cat1.filter(filterFunction(manager.cat1['SeqNr'], 3))

        manager.update(filterFunction, {'cat1' : 'filter'}, manager.cat1['SeqNr'], mod = 3)


        self.assertTrue((expected['SeqNr'] == manager.cat1['SeqNr']).all())

    #######################

    def testReplace(self):

        manager = md.DataManager()

        manager.thing0 = np.zeros(15)

        manager.replace('thing0', None)

        self.assertTrue(manager.thing0 is None)

        history = manager.history[-1]

        self.assertEquals(history.name, 'thing0')
        self.assertEquals(history.action, 'REPLACE')


    #######################

    def testInitHistory(self):

        preTime = datetime.datetime.now()
        manager = md.DataManager()
        postTime = datetime.datetime.now()

        historyitem = manager.history[-1]
        
        self.assertTrue(preTime <= historyitem.time <= postTime)
        self.assertEquals(historyitem.action, 'INIT')

        printedhistory = str(historyitem)
        print printedhistory

        self.assertTrue('INIT' in printedhistory)
        self.assertTrue(time.asctime(historyitem.time.timetuple()) in printedhistory)
        self.assertTrue(getpass.getuser() in printedhistory)

        

    #######################

    def testOpenHistory(self):

        filestat = os.stat(self.cat2file)

        manager = md.DataManager()

        preTime = datetime.datetime.now()
        manager.open('cat2', self.cat2file, ldac.openObjectFile, 'STDTAB')
        postTime = datetime.datetime.now()

        history = manager.history[-1]

        self.assertTrue(preTime <= history.time <= postTime)
        self.assertEquals(history.action, 'OPEN')
        self.assertEquals(history.name, 'cat2')
        self.assertEquals(history.file, self.cat2file)
        self.assertEquals(history.filestat, filestat)
        self.assertEquals(history.method, ldac.openObjectFile)
        self.assertEquals(history.methodargs, ('STDTAB',))
        self.assertEquals(history.methodkeywords, {})

        printedhistory = str(history)
        print printedhistory

        self.assertTrue(time.asctime(history.time.timetuple()) in printedhistory)

        self.assertTrue('cat2' in printedhistory)

        self.assertTrue(os.path.abspath(self.cat2file) in printedhistory)

        userid = pwd.getpwuid(filestat.st_uid)[0]
        self.assertTrue(userid in printedhistory)

        modtime = time.asctime(time.localtime(filestat.st_mtime))
        self.assertTrue(modtime in printedhistory)

        methodname = ldac.openObjectFile.__name__
        self.assertTrue(methodname in printedhistory)

        self.assertTrue(str(ldac.openObjectFile) not in printedhistory)

        self.assertTrue(str(history.methodargs) in printedhistory)
        self.assertTrue(str(history.methodkeywords) in printedhistory)

        sourcefile = inspect.getfile(ldac.openObjectFile)
        self.assertTrue(sourcefile in printedhistory)

        sourcefile_moddate = time.asctime(time.localtime(filestat.st_mtime))
        self.assertTrue(sourcefile_moddate in printedhistory)

    ########################

    def testStoreHistory(self):

        manager = md.DataManager()

        manager.thing0 = np.zeros(5)

        historyitem = manager.history[-1]

        self.assertEquals(historyitem.name, 'thing0')
        self.assertEquals(historyitem.action, 'STORE')

        printedhistory = historyitem.log()
        print printedhistory

        self.assertTrue(time.asctime(historyitem.time.timetuple()) in printedhistory)
        self.assertTrue(historyitem.name in printedhistory)
        self.assertTrue('STORE' in printedhistory)

    #######################

    def testMultiStoreHistory(self):

        manager = md.DataManager()

        manager.store('thing1 thing2'.split(), (np.zeros(5), np.ones(5)))

        historyitem = manager.history[-1]

        self.assertEquals(historyitem.name, ['thing1', 'thing2'])
        self.assertEquals(historyitem.action, 'STORE')

        printedhistory = historyitem.log()

        self.assertTrue(time.asctime(historyitem.time.timetuple()) in printedhistory)
        self.assertTrue('thing1' in printedhistory)
        self.assertTrue('thing2' in printedhistory)
        self.assertTrue(str('thing1 thing2'.split()) not in printedhistory)
        self.assertTrue('STORE' in printedhistory)
        

    ########################

    def testFunctionStoreHistory(self):

        manager = md.DataManager()

        def makeThing(theamount):
            return np.arange(theamount)

        manager.store('thing1', makeThing, 5)

        history = manager.history[-1]

        self.assertEquals(history.name, 'thing1')
        self.assertEquals(history.action, 'STORE')
        self.assertEquals(history.method, makeThing)
        self.assertEquals(history.methodargs, (5,))
        self.assertEquals(history.methodkeywords, {})

        printedhistory = str(history)
        print printedhistory

        self.assertTrue('thing1' in printedhistory)
        self.assertTrue('STORE' in printedhistory)
        self.assertTrue(time.asctime(history.time.timetuple()) in printedhistory)
        
        methodname = makeThing.__name__
        self.assertTrue(methodname in printedhistory)
        self.assertTrue(str(makeThing) not in printedhistory)

        sourcefile = inspect.getfile(makeThing)
        self.assertTrue(sourcefile in printedhistory)

        sourcefile_moddate = time.asctime(time.localtime(os.stat(sourcefile).st_mtime))
        self.assertTrue(sourcefile_moddate in printedhistory)

        sourcecode = inspect.getsource(makeThing)
        self.assertTrue(sourcecode in printedhistory)

        self.assertTrue('args = %s' % str(history.methodargs) in printedhistory)
        self.assertTrue('keywords = %s' % str(history.methodkeywords))

    
    #######################

    def testFunctionMultiStore(self):

        manager = md.DataManager()

        def makeThings(theamount):
            return np.zeros(theamount), np.arange(theamount)

        manager.store('thing1 thing2'.split(), makeThings, 5)

        history = manager.history[-1]

        printedhistory = str(history)
        print printedhistory

        self.assertTrue('thing1' in printedhistory)
        self.assertTrue('thing2' in printedhistory)
        self.assertTrue(str('thing1 thing2'.split()) not in printedhistory)

        
    ########################

    def testFilterHistory(self):

        manager = md.DataManager()

        manager.open(name = 'cat1', file = self.cat1file, open = ldac.openObjectFile)

        manager.open(name = 'pdzmanager', file = self.pdzfile, open = pdzutils.PDZManager.open)

        manager.store('pdzrange pdz'.split(), manager.pdzmanager.associatePDZ(manager.cat1['SeqNr']))

        def filterFunction(manager):
            return np.arange(len(manager.cat1))[manager.cat1['SeqNr'] % 2 == 0]

        preTime = datetime.datetime.now()
        manager.update(filterFunction, {'cat1' : 'filter', 'pdz' : '__getitem__'})
        postTime = datetime.datetime.now()

        history = manager.history[-1]

        self.assertTrue(preTime <= history.time <= postTime)
        self.assertEquals(history.action, 'UPDATE')
        self.assertEquals(history.name, ['cat1', 'pdz'])
        self.assertEquals(history.method, filterFunction)
        self.assertEquals(history.methodargs, ())
        self.assertEquals(history.methodkeywords, {})

        printedhistory = str(history)
        print printedhistory

        self.assertTrue(time.asctime(history.time.timetuple()) in printedhistory)

        self.assertTrue('UPDATE' in printedhistory)

        self.assertTrue('cat1' in printedhistory)
        self.assertTrue('pdz' in printedhistory)

        methodname = filterFunction.__name__
        self.assertTrue(methodname in printedhistory)
        self.assertTrue(str(filterFunction) not in printedhistory)

        sourcefile = inspect.getfile(filterFunction)
        self.assertTrue(sourcefile in printedhistory)

        sourcefile_moddate = time.asctime(time.localtime(os.stat(sourcefile).st_mtime))
        self.assertTrue(sourcefile_moddate in printedhistory)

        sourcecode = inspect.getsource(filterFunction)
        self.assertTrue(sourcecode in printedhistory)

        self.assertTrue(str(history.methodargs) in printedhistory)
        self.assertTrue(str(history.methodkeywords) in printedhistory)

        
    #####################

    
    def testLogStatement(self):

        manager = md.DataManager()

        manager.open(name = 'cat1', file = self.cat1file, open = ldac.openObjectFile)

        manager.open(name = 'pdzmanager', file = self.pdzfile, open = pdzutils.PDZManager.open)

        manager.store('pdzrange pdz'.split(), manager.pdzmanager.associatePDZ(manager.cat1['SeqNr']))

        def filterFunction(manager):
            return np.arange(len(manager.cat1))[manager.cat1['SeqNr'] % 2 == 0]

        manager.update(filterFunction, {'cat1' : 'filter', 'pdz' : '__getitem__'})

        
        self.assertEquals(len(manager.history), 5)

        log = manager.history.log()
        print log

        for historyitem in manager.history:
            self.assertTrue(historyitem.log() in log)


    #########################

    def testComments(self):

        manager = md.DataManager()

        options = {'arg1' : 5, 'arg2' : 'agb'}

        comment = 'Maxlike called with %s' % str(options)

        manager.history.comment(comment)

        history = manager.history[-1]

        self.assertEquals(history.action, 'COMMENT')
        self.assertEquals(history.comment, comment)

        printedhistory = history.log()
        print printedhistory

        self.assertTrue(time.asctime(history.time.timetuple()) in printedhistory)
        self.assertTrue('COMMENT' in printedhistory)
        self.assertTrue(comment in printedhistory)
        


##########################

def test():

    testcases = [TestInterface]
    
    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)





################################
###############################

if __name__ == '__main__':

    test()
