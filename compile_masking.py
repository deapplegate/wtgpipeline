#!/usr/bin/env python
########################
# Script to run weight watcher & compile masking and depth info
########################

import sys, unittest, os, re, tempfile, shutil, subprocess
import numpy as np, astropy, astropy.io.fits as pyfits
import regionfile, utilities

########################

__cvs_id__ = "$Id: compile_masking.py,v 1.2 2011-03-11 18:56:54 dapple Exp $"

#######################
# EXCEPTIONS
#######################

class MissingFileException(Exception): pass

#######################
# USER CALLABLE
#######################

def compileMasking(weightfile        , 
                   flagfile          , 
                   edgemaskfile      , 
                   polygonfile       , 
                   ringfile          , 
                   outputflagfile,
                   relWeightThreshold = 0.5):

    for file in [weightfile, flagfile, edgemaskfile, polygonfile, ringfile]:
        if not os.path.exists(file):
            raise MissingFileException(file)

    weightimage = pyfits.open(weightfile)[0].data
    maxWeight = np.amax(weightimage)
    weightThreshold = relWeightThreshold * maxWeight

    configfile = utilities.getTempFile()

    print '!!!!!!!!!!', configfile

    writeWWConfig(weightfile        =   weightfile       ,
                  flagfile          =   flagfile         ,
                  edgemaskfile      =   edgemaskfile     ,
                  polygonfile       =   polygonfile      ,
                  ringfile          =   ringfile         ,
                  weightThreshold   =   weightThreshold  ,
                  outputflagfile    =   outputflagfile   ,
                  outputconfigfile  =   configfile)
    
    assert(os.path.exists(configfile), 'WeightWatcher Configuration File Not Produced!')
    
    subprocess.check_call(('ww_theli -c %s' % configfile).split())
    
    assert(os.path.exists(outputflagfile), 'Final Flag Image Not Produced!')



    if os.path.exists(configfile):
        os.remove(configfile)

    
#######################

def combineRings(ringfiles, outputfile):

    result = None
    for ringfile in ringfiles:
    
        image = pyfits.open(ringfile)[0].data
        if result is None:
            result = np.zeros_like(image).astype(np.int16)
        result[np.logical_and(np.right_shift(image, 5) == 1, np.logical_not(np.bitwise_and(image, 16) == 16))] = 1

    hdu = pyfits.PrimaryHDU(result)
    hdu.writeto(outputfile, clobber=True)



#######################
# UTILITIES
#######################

wwConfigTemplate = '''
# Image par image Configuration file for WeightWatcher V1.0
# EB 12/08/97
#--------------------------------- Weights ------------------------------------

WEIGHT_NAMES	%(weightfile)s,%(edgemaskfile)s
WEIGHT_MIN	%(weightThreshold)5.2f,-0.5
WEIGHT_MAX	9e9,0.5
WEIGHT_OUTFLAGS	1,8


#---------------------------------- Flags -------------------------------------

FLAG_NAMES	%(flagfile)s,%(ringfile)s

FLAG_WMASKS	0,0
FLAG_MASKS	16,1
FLAG_OUTFLAGS	16,2

#---------------------------------- Polygons -------------------------------------
POLY_NAMES	%(polygonfile)s
POLY_OUTFLAGS	4


#---------------------------------- Output ------------------------------------

OUTWEIGHT_NAME  ""
OUTFLAG_NAME	%(outputflagfile)s
'''

def writeWWConfig(weightfile        , 
                  flagfile          , 
                  edgemaskfile      , 
                  polygonfile       , 
                  ringfile          , 
                  weightThreshold   , 
                  outputflagfile    , 
                  outputconfigfile):  

    weightfile      = os.path.abspath(weightfile     )
    flagfile        = os.path.abspath(flagfile       )
    edgemaskfile    = os.path.abspath(edgemaskfile   )
    polygonfile     = os.path.abspath(polygonfile    )
    ringfile        = os.path.abspath(ringfile       )
    outputflagfile  = os.path.abspath(outputflagfile )

    wwConfig = wwConfigTemplate % locals()
    output = open(outputconfigfile, 'w')
    output.write(wwConfig)
    output.close()



#########################

comment_re = re.compile('^#')

def parseConfigFile(configfile):

    config = {}
    input = open(configfile)
    for line in input.readlines():
        
        if comment_re.match(line):
            continue

        if line.strip() == '':
            continue

        tokens = line.split()
        keyword = tokens[0]
        rawvalue = tokens[1:]

        value = []
        for entry in rawvalue:
            if comment_re.match(entry):
                break
            value.extend(entry.split(','))

        value = filter(lambda x: x != '', value)


        if len(value) == 1:
            value = value[0]
        config[keyword] = value

    return config
        

########################
# TESTING
########################

class TestConfigGenerator(unittest.TestCase):
    
    def setUp(self):



        self.weight =   'weight.fits'
        self.flagfile = 'coadd.flag.fits'
        self.edgemask = 'edgemask.fits'                      
        self.polygons = 'polygons.reg'                       
        self.ringmask = 'ringfile.fits'                      
        self.outputflag = 'output.flag.fits'
        self.outputconfig =   'test_compile_masking_config.tmp.ww' 


        self.weightThreshold = 123.5

        if os.path.exists(self.outputconfig):
            os.remove(self.outputconfig)


        
        
    #######

    def tearDown(self):
        
        if os.path.exists(self.outputconfig):
            os.remove(self.outputconfig)


    #######

    def checkConfig(self, configfile, weightfile, flagfile, edgemaskfile, polygonfile, ringfile, outputflagfile, weightThreshold):


        weightfile       = os.path.abspath(weightfile     )
        flagfile         = os.path.abspath(flagfile       )           
        edgemaskfile     = os.path.abspath(edgemaskfile   )           
        polygonfile      = os.path.abspath(polygonfile    )           
        ringfile         = os.path.abspath(ringfile       )           
        outputflagfile   = os.path.abspath(outputflagfile )           


        config = parseConfigFile(configfile)

        print config.keys()

        expectedKeywords = 'WEIGHT_NAMES WEIGHT_MIN WEIGHT_MAX WEIGHT_OUTFLAGS FLAG_NAMES FLAG_WMASKS FLAG_MASKS FLAG_OUTFLAGS POLY_NAMES POLY_OUTFLAGS OUTWEIGHT_NAME OUTFLAG_NAME'.split()

        self.assertEquals(len(expectedKeywords), len(config.keys()))

        self.assertEquals(config['WEIGHT_NAMES'], [weightfile, edgemaskfile])
        self.assertEquals(map(float, config['WEIGHT_MIN']), [weightThreshold, -0.5])
        self.assertEquals(map(float, config['WEIGHT_MAX']), [9e9, 0.5])
        self.assertEquals(config['WEIGHT_OUTFLAGS'], '1 8'.split())

        self.assertEquals(config['FLAG_NAMES'], [flagfile, ringfile])
        self.assertEquals(config['FLAG_WMASKS'], '0 0'.split())
        self.assertEquals(config['FLAG_MASKS'], '16 1'.split())
        self.assertEquals(config['FLAG_OUTFLAGS'], '16 2'.split())

        self.assertEquals(config['POLY_NAMES'], polygonfile)
        self.assertEquals(config['POLY_OUTFLAGS'], '4')
        
        self.assertEquals(config['OUTWEIGHT_NAME'], '""')
        self.assertEquals(config['OUTFLAG_NAME'], outputflagfile)
        
        


    #######

    def testBasic(self):

        writeWWConfig(weightfile = self.weight, 
                      flagfile = self.flagfile,
                      edgemaskfile = self.edgemask, 
                      polygonfile = self.polygons, 
                      ringfile = self.ringmask,
                      weightThreshold = self.weightThreshold,
                      outputflagfile = self.outputflag,
                      outputconfigfile = self.outputconfig)

        self.assertTrue(os.path.exists(self.outputconfig))
        
        self.checkConfig(configfile = self.outputconfig,
                         weightfile = self.weight,
                         flagfile = self.flagfile,
                         edgemaskfile = self.edgemask, 
                         polygonfile = self.polygons, 
                         ringfile = self.ringmask,
                         weightThreshold = self.weightThreshold,
                         outputflagfile = self.outputflag)
                                         

##################

class TestParseConfig(unittest.TestCase):

    def setUp(self):

        self.sampleConfigfile = 'test_compile_masking_sampleconfig.tmp.ww'
        self.sampleConfig = '''
# Image par image Configuration file for WeightWatcher V1.0
# EB 12/08/97
# M.N. added 32 to POLY_OUTFLAGS
#--------------------------------- Weights ------------------------------------

WEIGHT_NAMES\t"" # filename(s) of the input WEIGHT map(s)
WEIGHT_MIN\t-9e9               
WEIGHT_MAX      9e9                
WEIGHT_OUTFLAGS 0                  
                                   
                                   
#---------------------------------- Flags -------------------------------------
                                   
FLAG_NAMES      flag.fits,flag1.fits,flag3.fits       # filename(s) of the input FLAG map(s)
                                   
FLAG_WMASKS     0x0,0x1,0x2             # bits which will nullify the WEIGHT-map pixels
FLAG_MASKS      0x10,0x11,0x100            # bits which will be converted as output FLAGs
FLAG_OUTFLAGS   0x1,0x11, 0x100             # translation of the INPUT_MASKS bits
                                   
#---------------------------------- Polygons -------------------------------------
POLY_NAMES      poly.reg                # filename of the regions
POLY_OUTFLAGS   0x2                
                                   
                                   
#---------------------------------- Output ------------------------------------
                                   
OUTWEIGHT_NAME  ""                 
OUTFLAG_NAME    flag.masked.fits        # output FLAG-map filename
'''
        
        if os.path.exists(self.sampleConfigfile):
            os.remove(self.sampleConfigfile)
        output = open(self.sampleConfigfile, 'w')
        output.write(self.sampleConfig)
        output.close()

    #################

    def tearDown(self):
        
        if os.path.exists(self.sampleConfigfile):
            os.remove(self.sampleConfigfile)

    ################

    def testParseConfigFile(self):

        config = parseConfigFile(self.sampleConfigfile)

        expectedKeys = 'WEIGHT_NAMES WEIGHT_MIN WEIGHT_MAX WEIGHT_OUTFLAGS FLAG_NAMES FLAG_WMASKS FLAG_MASKS FLAG_OUTFLAGS POLY_NAMES POLY_OUTFLAGS OUTWEIGHT_NAME OUTFLAG_NAME'.split()

        self.assertEquals(len(expectedKeys), len(config.keys()))

        for key in config.keys():
            self.assertTrue(key in expectedKeys, '%s not found' % key)


            
        self.assertEquals(config['WEIGHT_NAMES'],  '""'                     )
        self.assertEquals(config['WEIGHT_MIN'],  '-9e9')
        self.assertEquals(config['WEIGHT_MAX'],  '9e9')
        self.assertEquals(config['WEIGHT_OUTFLAGS'],  '0')
        self.assertEquals(config['FLAG_NAMES'],  'flag.fits flag1.fits flag3.fits'.split() )
        self.assertEquals(config['FLAG_WMASKS'],  '0x0 0x1 0x2'.split() )
        self.assertEquals(config['FLAG_MASKS'],  '0x10 0x11 0x100'.split() )
        self.assertEquals(config['FLAG_OUTFLAGS'],  '0x1 0x11  0x100'.split() )
        self.assertEquals(config['POLY_NAMES'],  'poly.reg' )
        self.assertEquals(config['POLY_OUTFLAGS'],  '0x2' )
        self.assertEquals(config['OUTWEIGHT_NAME'],  '""')
        self.assertEquals(config['OUTFLAG_NAME'],  'flag.masked.fits' )


############################

class TestAllExistsOps(unittest.TestCase):

    def setUp(self):

        self.workdir = tempfile.mkdtemp(dir='./')   #explicitely relative, to test for conversion to abs path
        print 'Workdir: %s' % self.workdir

        self.weight =       '%s/weight.fits'                         % self.workdir
        self.flagfile =     '%s/coadd.flag.fits'                     % self.workdir
        self.edgemask =     '%s/edgemask.fits'                       % self.workdir
        self.polygons =     '%s/polygons.reg'                        % self.workdir
        self.ringmask =     '%s/ringfile.fits'                       % self.workdir
        self.outputflag =   '%s/output.flag.fits'                    % self.workdir


        self.maxWeight = 275.
        self.relWeightThreshold = 0.5

        X,Y = np.meshgrid(np.arange(-500,500), np.arange(-500,500))
        R = np.sqrt(X**2 + Y**2)
        weightimage = self.maxWeight - (175./500)*R
        hdu = pyfits.PrimaryHDU(weightimage)
        hdu.writeto(self.weight)

        flag = np.zeros_like(weightimage).astype(np.int16)
        flag[:5,:] = 16
        flag[-5:,:] = 16
        flag[:,:5] = 16
        flag[:,-5] = 16
        flag[:,888:891] = 16
        hdu = pyfits.PrimaryHDU(flag)
        hdu.writeto(self.flagfile)

        edgeimage = np.zeros_like(weightimage)
        edgeimage[:15,:] = 1
        edgeimage[-15:,:] = 1
        edgeimage[:,:15] = 1
        edgeimage[:,-15] = 1
        edgeimage[634:643,350:355] = 1
        assert((edgeimage == 1).any())
        hdu = pyfits.PrimaryHDU(edgeimage)
        hdu.writeto(self.edgemask)

        regions = [ x.toPolygon() for x in [ regionfile.Box((250,137),(26,36), 0), regionfile.Box((750,750),(36,26),0) ] ]
        regionfile.writeRegionFile(self.polygons, regions)
        regionMask = np.zeros_like(weightimage).astype(np.int16)
        regionMask[137-18:137+18  ,250-13 - 1 :250+13  - 1] = 1
        regionMask[750-13:750+13  ,750-18 - 1 :750+18  - 1] = 1

        rings = np.zeros_like(weightimage).astype(np.int16)
        center = np.array([650,120])
        X,Y = np.meshgrid(np.arange(1000), np.arange(1000))
        R = np.sqrt((X - center[0])**2 + (Y - center[1])**2)
        rings[np.logical_and(R > 100, R < 120)] = 1
        rings[np.logical_and(R > 150, R < 170)] = 1
        hdu = pyfits.PrimaryHDU(rings)
        hdu.writeto(self.ringmask)

    
        self.answer = np.zeros_like(weightimage).astype(np.int16)
        self.answer[weightimage < self.relWeightThreshold*self.maxWeight] += 1
        self.answer[flag == 16] += 16
        self.answer[edgeimage > 0.5] += 8
        self.answer[regionMask == 1] += 4
        self.answer[rings == 1] += 2
        

    #######

    def tearDown(self):

        if os.path.exists(self.workdir):
            shutil.rmtree(self.workdir)


    #######

    def testAllExists(self):

        compileMasking(weightfile = self.weight, 
                       flagfile = self.flagfile,
                       edgemaskfile = self.edgemask, 
                       polygonfile = self.polygons, 
                       ringfile = self.ringmask,
                       outputflagfile = self.outputflag,
                       relWeightThreshold = self.relWeightThreshold)

        self.assertTrue(os.path.exists(self.outputflag))
        
        output = pyfits.open(self.outputflag)[0].data

        self.assertTrue((output == self.answer).all())

    #######

    def testMissingCritical(self):

        self.assertRaises(MissingFileException, compileMasking, weightfile = 'fake', 
                          flagfile = self.flagfile,
                          edgemaskfile = self.edgemask, 
                          polygonfile = self.polygons, 
                          ringfile = self.ringmask,
                          outputflagfile = self.outputflag,
                          relWeightThreshold = self.relWeightThreshold)


    ########

class TestCombineRings(unittest.TestCase):

    def setUp(self):

        self.workdir = tempfile.mkdtemp(dir='./')   #explicitely relative, to test for conversion to abs path
        print 'Workdir: %s' % self.workdir

        

        flag1 = np.ones((1000,1000), dtype=np.int16)
        goodpix1 = np.zeros_like(flag1)
        
        X,Y = np.meshgrid(np.arange(1000),np.arange(1000))
        center = (450,550)
        dR = np.sqrt((X - center[1])**2 + (Y - center[0])**2)
        flag1[450:550,550:580] = 2
        flag1[dR < 50] += 48
        
        flag1[np.logical_and(dR > 100, dR < 120)] += 32
        goodpix1[np.logical_and(dR > 100, dR < 120)] = 1
        
        flag1[np.logical_and(dR > 250, dR < 270)] += 32
        goodpix1[np.logical_and(dR > 250, dR < 270)] = 1
        
        flag1[:450, :] += 16
        goodpix1[:450, :] = 0
        
        flag1[230:890, 770:775] += (128 + 16 + 32)
        goodpix1[230:890, 770:775] = 0
        
        flag1[:50,:] = 16
        goodpix1[:50,:] = 0
        
        flag1[-50:,:] =  16
        goodpix1[-50:,:] = 0
        
        flag1[:,:50] = 16
        goodpix1[:,:50] = 0
        
        flag1[:,-50:] = 16
        goodpix1[:,-50:] = 0
        
        hdu = pyfits.PrimaryHDU(flag1)
        hdu.writeto('%s/flag1.fits' % self.workdir)



        flag2 = np.ones((1000,1000), dtype=np.int16)
        goodpix2 = np.zeros_like(flag2)
        
        flag2[400:450,500:550] = 2
        flag2[dR < 50] += 48
        
        flag2[np.logical_and(dR > 100, dR < 120)] += 32
        goodpix2[np.logical_and(dR > 100, dR < 120)] = 1
        
        flag2[np.logical_and(dR > 250, dR < 270)] += 32
        goodpix2[np.logical_and(dR > 250, dR < 270)] = 1

        flag2[:, 550:] += 16
        goodpix2[:, 550:] = 0

        flag2[8760:990, 550:645] += 128 + 16 + 32
        goodpix2[8760:990, 550:645] = 0
        
        flag2[:50,:] = 16
        goodpix2[:50,:] = 0

        flag2[-50:,:] = 16
        goodpix2[-50:,:]  = 0

        flag2[:,:50] = 16
        goodpix2[:,:50] = 0

        flag2[:,-50:] = 16
        goodpix2[:,-50:] = 0


        hdu = pyfits.PrimaryHDU(flag2)
        hdu.writeto('%s/flag2.fits' % self.workdir)





        flag3 = np.ones((1000,1000), dtype=np.int16)
        center = (750,150)
        dR = np.sqrt((X - center[1])**2 + (Y - center[0])**2)
        flag3[dR < 50] = 49
        flag3[np.logical_and(dR > 100, dR < 120)] = 33
        flag3[:50,:] = 16
        flag3[-50:,:] = 16
        flag3[:,:50] = 16
        flag3[:,-50:] = 16
        hdu = pyfits.PrimaryHDU(flag3)
        hdu.writeto('%s/flag3.fits' % self.workdir)
        goodpix3 = np.zeros_like(flag3)
        goodpix3[flag3 == 33] = 1

        
        self.ringfiles = [ '%s/flag%d.fits' % (self.workdir, i) for i in range(1,4) ]

        self.outputfile = '%s/output.fits' % self.workdir

        self.answer = np.zeros_like(flag1)
        for goodpix in [goodpix1, goodpix2, goodpix3]:
            self.answer[goodpix == 1] = 1
            

    #####

    def tearDown(self):

        if os.path.exists(self.workdir):
            shutil.rmtree(self.workdir)


    ######

    def testCombineRings(self):

        
        combineRings(ringfiles = self.ringfiles, outputfile = self.outputfile)

        self.assertTrue(os.path.exists(self.outputfile))
        
        output = pyfits.open(self.outputfile)[0].data
        self.assertTrue(isinstance(output[0,0], np.int16) or isinstance(output[0,0], np.int16))

        self.assertTrue((output == self.answer).all())

        
        
        

    

########################

def test():

    testcases = [TestConfigGenerator, TestParseConfig, TestAllExistsOps, TestCombineRings]
    
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
