#!/usr/bin/env python
#########################

# convert all FLUX_APER, MAG_APER, and associated errors, from 2D ldac columns to vector columns

import sys, unittest, re
import astropy, astropy.io.fits as pyfits, numpy
import ldac

#############################

__cvs_id__ = "$Id: convert_aper.py,v 1.1 2010-04-16 23:30:54 dapple Exp $"

#############################

############################################
# USER FUNCTIONS
############################################


containsAper_regex = re.compile('APER')

def convertAperColumns(cat):


    cols = []
    for key in cat.keys():

        if len(cat[key].shape) == 2 and containsAper_regex.search(key):

            cols.extend(convert2DAperColumn(key, cat[key]))

        else:

            cols.append(cat.extractColumn(key))

    newcat = ldac.LDACCat(pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols)))
    newcat.sourcefile = cat.sourcefile

    return newcat

###############################

def convertAper(hdulist):

    newhdus = [pyfits.PrimaryHDU()]
    for hdu in hdulist:

        if 'EXTNAME' in hdu.header:

            if hdu.header['EXTNAME'] == 'OBJECTS' or hdu.header['EXTNAME'] == 'LDAC_OBJECTS':
                
                newhdu = convertAperColumns(ldac.LDACCat(hdu)).hdu
                newhdu.header.update('EXTNAME', hdu.header['EXTNAME'])
                newhdus.append(newhdu)

                

            else:

                newhdus.append(hdu)

    return pyfits.HDUList(newhdus)

################################################
# MAIN
################################################

def main(argv = sys.argv):

    if len(argv) != 3:
        sys.stderr.write('Usage:  convert_aper.py inputcat outputcat\n')
        sys.exit(1)

    input = argv[1]
    output = argv[2]

    hdulist = pyfits.open(input)
    newhdulist = convertAper(hdulist)

    newhdulist.writeto(output, clobber=True)


#########################################################
# Utility Functions
#########################################################

class ConfusionException(Exception): pass

aper_keys = 'FLUX_APER FLUXERR_APER MAG_APER MAGERR_APER'.split()
aper_regexs = [ re.compile('^%s(.+)?' % key) for key in aper_keys ]

def convert2DAperColumn(key, data):

    cols = []

    for aper_key, aper_regex in zip(aper_keys, aper_regexs):
        match = aper_regex.match(key)
        if match is not None:
            break

    if match is None:
        raise ConfusionException('Unrecognized Column Name: %s' % key)

    napers = data.shape[1]

    for i in xrange(napers):
        if match.group(1) is None:
            newcolname = '%s%d' % (aper_key, i)
        else:
            newcolname = '%s%d%s' % (aper_key, i, match.group(1))

        cols.append(pyfits.Column(name=newcolname,
                                  format='E',
                                  array=data[:,i]))

    return cols


########################################################
## TESTING
##############################

class TestConvert2DAperColumn(unittest.TestCase):

    def setUp(self):

        self.napers = 5
        self.data = numpy.ones((30, self.napers))
        for i in xrange(self.napers):
            self.data[:,i] = i+1

    def testTypes(self):

        colList = convert2DAperColumn('FLUX_APER', self.data)

        for col in colList:
            self.assertTrue(isinstance(col, pyfits.Column))

    def testTransform(self):

        colList = convert2DAperColumn('FLUX_APER', self.data)

        self.assertEquals(len(colList), self.napers)

        for i in xrange(self.napers):
            
            self.assertEqual(colList[i].name, '%s%d' % ('FLUX_APER', i))

            self.assertTrue((colList[i].array == i+1).all())

    def testConfusion(self):

        self.assertRaises(ConfusionException, convert2DAperColumn, 'FAKE_NAME', numpy.zeros((30,4)))

    def testFancyFilterNames(self):

        colList = convert2DAperColumn('MAG_APER-SUBARU-10_2-1-W-J-B', self.data)

        self.assertEquals(len(colList), self.napers)
        
        for i in xrange(self.napers):

            self.assertEqual(colList[i].name, 'MAG_APER%d-SUBARU-10_2-1-W-J-B' % i)
            
            self.assertTrue((colList[i].array == i+1).all())

##########################################


def tablesEqual(table1, table2):

    cat1 = ldac.LDACCat(table1)
    cat2 = ldac.LDACCat(table2)

    if not len(cat1) == len(cat2):
        return False

    if not len(cat1.keys()) == len(cat2.keys()):
        return False

    for key in cat1.keys():

        if not (cat1[key] == cat2[key]).all():
            return False

    return True

################

class TestConvertAper(unittest.TestCase):

    def setUp(self):

        cols = [pyfits.Column(name='SeqNr',
                              format='E',
                              array=numpy.arange(100))]

        self.vector_one_cols = 'MAG_ISO MAGERR_ISO FLUX_ISO FLUXERR_ISO FLUX_RADIUS FLUX_APER7 FLUXERR_APER7 MAG_APER7 MAGERR_APER7'.split()

        for col in self.vector_one_cols:
            cols.append(pyfits.Column(name=col,
                                      format='E',
                                      array=numpy.ones(100)))

        self.block_one_cols_basic = 'FLUX_APER FLUXERR_APER MAG_APER MAGERR_APER'.split()

        self.block_one_cols_fancy = ['%s-MEGAPRIME-0-1-u' % x for x in self.block_one_cols_basic]

        self.block_one_cols = self.block_one_cols_basic + self.block_one_cols_fancy

        self.napers = 5        
        for col in self.block_one_cols:
            data = numpy.ones((100,self.napers))
            for i in xrange(self.napers):
                data[:,i] = i + 1
            cols.append(pyfits.Column(name=col,
                                      format='%dE' % self.napers,
                                      array = data))
        

        self.objectshdu = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
        self.objectshdu.header.update('EXTNAME', 'OBJECTS')

        cols=[pyfits.Column(name='Seeing',
                            format='E',
                            array=numpy.array([1.0])),
              pyfits.Column(name='Background',
                            format='E',
                            array=numpy.array([3.0]))]
        self.fieldhdu = pyfits.BinTableHDU.from_columns(pyfits.ColDefs(cols))
        self.fieldhdu.header.update('EXTNAME', 'FIELDS')
        self.hdulist = [pyfits.PrimaryHDU(), self.objectshdu, self.fieldhdu]

    ##############

    def testConvertColumns_ReturnsHDU(self):

        newcat = convertAperColumns(ldac.LDACCat(self.objectshdu))

        self.assertTrue(isinstance(newcat, ldac.LDACCat))
        
    ###################

    def testConvertColumns_KeepOthers(self):

        newcat = convertAperColumns(ldac.LDACCat(self.objectshdu))

        headerkeys = newcat.keys()
        for key in self.vector_one_cols:
            self.assertTrue(key in headerkeys)
        self.assertTrue('SeqNr' in headerkeys)
        
        self.assertTrue((newcat['SeqNr'] == numpy.arange(100)).all())

    ###################

    def testConvertColumns_SplitAper(self):

        newcat = convertAperColumns(ldac.LDACCat(self.objectshdu))

        headerkeys = newcat.keys()

        for col in self.block_one_cols:

            root, sep, filter = col.partition('-')

            for i in xrange(self.napers):

                if filter == '':
                    colname = '%s%d' % (root, i)
                else:
                    colname = '%s%d-%s' % (root, i, filter)

                self.assertTrue(colname in headerkeys)

                self.assertEquals(len(newcat[colname].shape), 1)

                self.assertTrue((newcat[colname] == i+1).all())



    #######################

    def testConvertAper(self):


        newhdulist = convertAper(self.hdulist)

        self.assertTrue(isinstance(newhdulist, pyfits.HDUList))

        self.assertEquals(len(newhdulist), 3)

        seenObjects = False
        seenFields = False
        for hdu in newhdulist:

            if 'EXTNAME' in hdu.header.keys():
                
                tablename = hdu.header['EXTNAME']

                if tablename == 'OBJECTS':
                    seenObjects = True
                    self.assertTrue(tablesEqual(hdu, convertAperColumns(ldac.LDACCat(self.objectshdu)).hdu))

                elif tablename == 'FIELDS':
                    seenFields = True
                    self.assertTrue(tablesEqual(hdu, self.fieldhdu))

                else:

                    self.asssertFail('Unexpected Table')

        self.assertTrue(seenObjects)
        self.assertTrue(seenFields)

    ###################

    def testLDACObject(self):

        self.objectshdu.header.update('EXTNAME', 'LDAC_OBJECTS')

        newhdulist = convertAper(self.hdulist)

        seenObjects = False
        for hdu in newhdulist:

            if 'EXTNAME' in hdu.header.keys() and hdu.header['EXTNAME'] == 'LDAC_OBJECTS':
                seenObjects = True
                self.assertTrue(tablesEqual(hdu, convertAperColumns(ldac.LDACCat(self.objectshdu)).hdu))

        self.assertTrue(seenObjects)



        



                            
            
                           

##############################

def test():

    testcases = [TestConvertAper, TestConvert2DAperColumn]
    
    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)



##############################
# COMMANDLINE EXECUTABLE
##############################

if __name__ == '__main__':
    
    if len(sys.argv) == 2 and sys.argv[1] == 'test':
        test()
    else:
        main()
