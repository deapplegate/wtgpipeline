#!/usr/bin/env python
import sys, os, unittest, manageconfigs as mc
from optparse import OptionParser

##########################################

def eval1(x,y,z): return x*y+z
def eval2(x,y,z): return x+y+z

@mc.manageConfigs
def sampleFunction(x, y, z=5, func=eval1, cat='test.cat'):
    return cat, func(x,y,z)

@mc.manageConfigs
def sampleFunction2(x=5, y=2.45, z=4, func=eval1, cat='test.cat', verbose=True):
    return cat, func(x,y,z)

##############################################

class TestManageConfigsFromPython(unittest.TestCase):
    
    def testProgramaticCall(self):

        cat, num = sampleFunction(1, 2)
        self.assertEquals(cat, 'test.cat')
        self.assertEquals(num, 7)

        cat, num = sampleFunction(5, 6, 7, cat='test1.cat')
        self.assertEquals(cat, 'test1.cat')
        self.assertEquals(num, 37)

        self.assertRaises(TypeError, sampleFunction)


    def testDumpConfig(self):

        results, config = sampleFunction(5, 3, 7, cat='smarts', dumpConfig=True)
        cat, num = results
        self.assertEquals(cat, 'smarts')
        self.assertEquals(num, 22)

        self.assertEquals(config.x, 5)
        self.assertEquals(config.y, 3)
        self.assertEquals(config.z, 7)
        self.assertEquals(config.cat, 'smarts')

    def testExtractKeywords(self):

        defaults = sampleFunction.defaults
        self.assertEquals(defaults.x, None)
        self.assertEquals(defaults.y, None)
        self.assertEquals(defaults.z, 5)
        self.assertEquals(defaults.cat, 'test.cat')

    def testPassConfig(self):

        config = sampleFunction.defaults
        config.x = 2
        config.y = 3
        config.z = 1

        cat, num = sampleFunction(config = config)

        self.assertEquals(cat, 'test.cat')
        self.assertEquals(7, num)

    def testDefaultsImmutable(self):

        default = sampleFunction.defaults
        originalX = default.x
        default.x = 17
        self.assertEquals(originalX, sampleFunction.defaults.x)

    def testPassConfigAndArgs(self):

        config = sampleFunction.defaults
        config.x = 15
        originalY = config.y

        (cat, num), newConfig = sampleFunction(y = 2, config=config, dumpConfig=True)

        self.assertEquals(cat, 'test.cat')
        self.assertEquals(num, 35)
        self.assertEquals(originalY, config.y)

        config.y = 2
        self.assertEquals(config, newConfig)

    def testPassTooMuchConfig(self):

        config = sampleFunction.defaults
        config.x = 2
        config.y = 3
        config.z = 0
        config.extra = 77

        (cat, num), newConfig = sampleFunction(config=config, dumpConfig=True)

        self.assertEquals(cat, 'test.cat')
        self.assertEquals(num, 6)
        self.assertEquals(newConfig, config)

    def testPassDictAsConfig(self):

        myconfig = {}
        myconfig['x'] = 2
        myconfig['y'] = 3
        myconfig['z'] = 4
        myconfig['cat'] = 'mycat'
        myconfig['extra'] = 88
        myconfig['func'] = eval1

        (cat, num), newConfig = sampleFunction(config=myconfig, dumpConfig=True)

        self.assertEquals(cat, 'mycat')
        self.assertEquals(num, 10)
        
        self.assertEquals(type(newConfig), type(sampleFunction.defaults))

        self.assertEquals(newConfig.x, 2)
        self.assertEquals(newConfig.y, 3)
        self.assertEquals(newConfig.z, 4)
        self.assertEquals(newConfig.cat, 'mycat')
        self.assertEquals(newConfig.extra, 88)


class TestManageConfigsWithFiles(unittest.TestCase):

    def setUp(self):
        self.configFile = 'manageconfigs.test.config'
        
        output = open(self.configFile, 'w')
        
        output.write('''# Config File for Testing manageconfigs.py
x=5
y=7
z=1

cat='mytest.cat'

#This is for a different program
extra=99
''')

        self.outputConfig = 'manageconfigs.test2.config'

        

    def tearDown(self):

        if os.path.exists(self.configFile):
            os.remove(self.configFile)

        if os.path.exists(self.outputConfig):
            os.remove(self.outputConfig)
        
        

    def testReadFileConfig(self):

        config = sampleFunction.loadConfig(self.configFile)

        self.assertEquals(config.x, 5)
        self.assertEquals(config.y, 7)
        self.assertEquals(config.z, 1)
        self.assertEquals(config.cat, 'mytest.cat')
        self.assertEquals(config.extra, 99)

    def testWriteConfigToFile(self):

        config=sampleFunction.defaults
        
        config.toFile(self.outputConfig)

        self.assertTrue(os.path.exists(self.outputConfig))

        newconfig = sampleFunction.loadConfig(self.outputConfig)

        self.assertEquals(config, newconfig)

    def testCallWithConfigFile(self):

        cat, num = sampleFunction(x=2, config=self.configFile)

        self.assertEquals(num, 15)
        self.assertEquals(cat, 'mytest.cat')

    def testDumpConfigToFile(self):

        cat, num = sampleFunction(x=2, y=15, dumpConfig=self.outputConfig)

        expectedConfig = sampleFunction.defaults
        expectedConfig.x = 2
        expectedConfig.y = 15

        self.assertEquals(cat, 'test.cat')
        self.assertEquals(num, 35)

        config = sampleFunction.loadConfig(self.outputConfig)

        self.assertEquals(expectedConfig, config)


class TestManageConfigsCommandLine(unittest.TestCase):

    def setUp(self):
        self.configFile = 'manageconfigs.test.config'
        self.dumpFile = 'manageconfigs.dump.config'
        
        output = open(self.configFile, 'w')
        
        output.write('''# Config File for Testing manageconfigs.py
x=5
y=7
z=1

cat='mytest.cat'

#This is for a different program
extra=99
''')

        self.stdout = sys.stdout


    def tearDown(self):

        if os.path.exists(self.configFile):
            os.remove(self.configFile)

        if os.path.exists(self.dumpFile):
            os.remove(self.dumpFile)

        sys.stdout = self.stdout
    
    def testAddConfigManagementToParser(self):

        parser = OptionParser()
        sampleFunction.addConfigToParser(parser)

        self.assertTrue(parser.has_option('-c'))
        self.assertTrue(parser.has_option('--config'))

        parser.parse_args(args=['-c', self.configFile])

        self.assertTrue(isinstance(parser.config, mc.Configuration))


    def testDumpDefault(self):
        parser = OptionParser()
        sampleFunction.addConfigToParser(parser)

        self.assertTrue(parser.has_option('-d'))
        self.assertTrue(parser.has_option('--dump'))

        dumpfile = open(self.dumpFile, 'w')
        sys.stdout = dumpfile
        
        self.assertRaises(SystemExit, parser.parse_args, args=['-d'])

        sys.stdout = self.stdout
        dumpfile.close()

        self.assertEquals(sampleFunction.loadConfig(self.dumpFile), sampleFunction.defaults)
        

        
########################

class TestManageCommandLine(unittest.TestCase):

    def setUp(self):
        self.configFile = 'manageconfigs.test.config'
        
        output = open(self.configFile, 'w')
        
        output.write('''# Config File for Testing manageconfigs.py
x=5
y=7
z=1

cat='mytest.cat'

#This is for a different program
extra=99
''')

        self.outputConfig = 'manageconfigs.test2.config'

        

    def tearDown(self):

        if os.path.exists(self.configFile):
            os.remove(self.configFile)

        if os.path.exists(self.outputConfig):
            os.remove(self.outputConfig)
        
        
    

    def testPopulateParser(self):

        parser = OptionParser()
        sampleFunction2.populateParser(parser)

        self.assertTrue(parser.has_option('-d'))
        self.assertTrue(parser.has_option('--dump'))

        dumpfile = open(self.dumpFile, 'w')
        sys.stdout = dumpfile
        
        self.assertRaises(SystemExit, parser.parse_args, args=['-d'])

        sys.stdout = self.stdout
        dumpfile.close()

        self.assertEquals(sampleFunction.loadConfig(self.dumpFile), sampleFunction.defaults)

        argstring = '-x 3 -y 2.66 --func eval2 --cat mytest.cat --verbose False'
        

        self.assertTrue(parser.has_option('--cat'))
        self.assertTrue(parser.has_option('-v'))
        self.assertTrue(parser.has_option('--verbpse'))

        


        
    

########################

def test():

    testcases = [TestManageConfigsFromPython, TestManageConfigsWithFiles, TestManageConfigsCommandLine, TestManageCommandLine]
    suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                                   testcases))
    unittest.TextTestRunner(verbosity=2).run(suite)


########################

if __name__ == '__main__':
    test()
