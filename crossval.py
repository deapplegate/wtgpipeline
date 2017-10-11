#!/usr/bin/env python
######################
# Create Cross validation catalogs for shape distribution tests
#######################

import sys, os, unittest
import numpy as np, astropy, astropy.io.fits as pyfits
import ldac

#######################

__cvs_id__ = "$Id: crossval.py,v 1.1 2011/01/11 19:55:35 dapple Exp $"

#######################




#######################



def makeCrossValCats(cat,  nsets):

    if isinstance(cat, ldac.LDACCat):

        nentries = len(cat)
    else:
        nentries = len(cat[cat.keys()[0]])

    indices = np.random.permutation(nentries)

    slicepoints = np.linspace(0, nentries, nsets + 1)

    cat_sets = []

    for cur_set_index in range(nsets):

        raw_testing_cat = {}
        raw_training_cat = {}

        for key in cat.keys():
        
            for i in range(nsets):

                if i == cur_set_index:
                    raw_testing_cat[key] = cat[key][indices[slicepoints[i]:slicepoints[i+1]]]

                else:
                    if key not in raw_training_cat:
                        raw_training_cat[key] = []
                    raw_training_cat[key].append(cat[key][indices[slicepoints[i]:slicepoints[i+1]]])


        testing_cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([pyfits.Column(name = key, format = 'E', array = vals) \
                                                                        for key, vals in raw_testing_cat.iteritems()])))
        testing_cat.hdu.header['EXTNAME']= 'OBJECTS'

        
        training_cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([pyfits.Column(name = key, format = 'E', array = np.hstack(vals)) \
                                                                         for key, vals in raw_training_cat.iteritems()])))
        training_cat.hdu.header['EXTNAME']= 'OBJECTS'



        cat_sets.append((training_cat, testing_cat))

        
                                            
    return cat_sets


######################


def createBins(cat, selectors):

    if selectors == [] or None:

        return {'' : cat}

    bins = {}

    ndim = len(selectors)
    dimsize = [len(x) for x in selectors]

    index_counters = np.mgrid[[slice(x) for x in dimsize]]

    for curindex in zip(*[x.flatten() for x in index_counters]):

        print curindex
    
        inbin = reduce(np.logical_and, [selectors[i][curindex[i]](cat) \
                                            for i in range(ndim)] )

        bins[curindex] = cat.filter(inbin)

        

    return bins



#######################
# TESTING
#######################

class TestCrossVal(unittest.TestCase):

    #######################

    def setUp(self):

        self.nentries = 50
        self.nsets = 5

        self.catalog = {'a' : np.ones(self.nentries),
                        'SeqNr' : np.arange(self.nentries),
                        'c' : np.zeros(self.nentries)}

        self.catalog['a'][:self.nentries/2] = 0
        
        even_entries = self.catalog['SeqNr'] % 2 == 0
        self.catalog['c'][even_entries] = 1

        

    #######################

    def testOneBin(self):


    
        cat_sets = makeCrossValCats(cat = self.catalog, nsets = self.nsets)

        for i in range(len(cat_sets)):

            training, testing = cat_sets[i]

            self.assertTrue(isinstance(training, ldac.LDACCat))
            self.assertTrue(isinstance(testing, ldac.LDACCat))

            for key in self.catalog.keys():
                self.assertTrue(key in training.keys())
                self.assertTrue(key in testing.keys())

            for id in self.catalog['SeqNr']:
                self.assertTrue(id in training['SeqNr'] or id in testing['SeqNr'])

            for id in testing['SeqNr']:
                self.assertTrue(id not in training['SeqNr'])

            for id in training['SeqNr']:
                self.assertTrue(id not in testing['SeqNr'])

            for j in range(len(cat_sets)):
                if j != i:
                    other_training, other_testing = cat_sets[j]
                    for id in testing['SeqNr']:
                        self.assertTrue(id not in other_testing['SeqNr'])


    ############################

    def testCreateBins(self):


        cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([pyfits.Column(name = key, format = 'E', array = vals) \
                                                                        for key, vals in self.catalog.iteritems()])))
        cat.hdu.header['EXTNAME']= 'OBJECTS'

        
        bins = createBins(cat, [[lambda x: x['a'] == 0, lambda x: x['a'] == 1], [lambda x: x['c'] == 1, lambda x: x['c'] == 0]])

        self.assertTrue(len(bins), 4)

        self.assertTrue((0,0) in bins.keys())
        self.assertTrue(np.logical_and(bins[(0,0)]['a'] == 0, bins[(0,0)]['c'] == 1).all())

        self.assertTrue((1,0) in bins.keys())
        self.assertTrue(np.logical_and(bins[(1,0)]['a'] == 1, bins[(1,0)]['c'] == 1).all())

        self.assertTrue((0,1) in bins.keys())
        self.assertTrue(np.logical_and(bins[(0,1)]['a'] == 0, bins[(0,1)]['c'] == 0).all())

        self.assertTrue((1,1) in bins.keys())
        self.assertTrue(np.logical_and(bins[(1,1)]['a'] == 1, bins[(1,1)]['c'] == 0).all())



    ###########################

    def testCreateBins_onebin(self):

        
        cat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs([pyfits.Column(name = key, format = 'E', array = vals) \
                                                                        for key, vals in self.catalog.iteritems()])))
        cat.hdu.header['EXTNAME']= 'OBJECTS'

        
        bins = createBins(cat, [])

        self.assertEquals(bins.keys(), [('')])

        bincat = bins[('')]

        self.assertEquals(len(cat), len(bincat))

        self.assertEquals(cat.keys(), bincat.keys())


        


        
        

                

    

##############################

def test():

    testcases = [TestCrossVal]
    
    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                  testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)



##############################
# COMMANDLINE EXECUTABLE
##############################

if __name__ == '__main__':
    
    test()
