#!/usr/bin/env python
#####################
# Testing Code for BonnLogger.py
#####################

__cvs_id__ = "$Id: TestLogger.py,v 1.1 2008-07-09 00:12:23 dapple Exp $"


import unittest, os, sys, datetime, time, re, subprocess


###########################################

os.environ['BONN_TEST'] = '1'
os.environ['BONN_LOG'] = '1'

import BonnLogger as log

###########################################

assert(log.state() == log.testing)

class TestLogSystem(unittest.TestCase):

    def setUp(self):
        os.environ['BONN_LOG'] = '1'
        os.environ['BONN_TEST'] = "1"
        self.assertEquals(log.state(), log.testing)
        log.reset()
        os.environ['BONN_TARGET'] = '2003-09-25'
        os.environ['BONN_FILTER'] = 'W-J-V'
        self.curUser = os.environ['USER']

    def tearDown(self):
        os.environ['USER'] = self.curUser

    def testRunTestCommand(self):
       
        self.assertEquals(os.system('./testcommand.sh'), 0)

    def testAddsEntry(self):

       os.system('./testcommand.sh')
       self.assertEquals(log.lastCommand().command, 'testcommand.sh')

    def testAdds2Entries(self):

        os.system('./testcommand.sh')
        os.system('./testcommand.sh arg1')
        last = log.lastCommand()
        self.assertEquals(last.command, 'testcommand.sh')
        self.assertEquals(last.args, ['arg1'])

    def testAddsEntryWithArg(self):
        os.system('./testcommand.sh arg1')
        last = log.lastCommand()
        self.assertEquals(last.command, 'testcommand.sh')
        self.assertEquals(last.args, ['arg1'])

    def testLogsUser(self):

        os.system('./testcommand.sh')
        command = log.lastEntry()
        self.assertEquals(command.user, os.environ['USER'])

    def testLogsTarget(self):

        os.system('./testcommand.sh')
        command = log.lastEntry()
        self.assertEquals(command.target, '2003-09-25')

    def testLogsFilter(self):
        
        os.system('./testcommand.sh')
        self.assertEquals(log.lastEntry().filter, 'W-J-V')


    def testNoTarget(self):
        del os.environ['BONN_TARGET']
        code = os.system('./testcommand.sh notarget')
        print "Code: %d" % code
        self.assertNotEqual(code, 0)

    def testNoFilter(self):
        del os.environ['BONN_FILTER']
        code = os.system('./testcommand.sh notarget')
        print "Code: %d" % code
        self.assertNotEqual(code, 0)

    def testLogsDate(self):
        
        time1 = datetime.datetime.now()
        os.system('./testcommand.sh g0')
        time.sleep(2)
        os.system('./testcommand.sh g1')
        time.sleep(2)
        os.system('./testcommand.sh g2')
        time.sleep(2)
        time2 = datetime.datetime.now()
        time.sleep(2)
        os.system('./testcommand.sh g3')

        entries = log.getEntriesByDate(range=(time1,time2))
        self.assertEquals(len(entries), 3)
        for i in xrange(3):
            self.assertEquals(entries[i].command.args, ['g%d' % i])

    def testLogsGoodCompletion(self):

        os.system('./testcommand.sh')
        command = log.lastCommand()
        self.assertEquals(command.status, 0)

    def testLogsFailure(self):
        os.system('./testcommand.sh fail 2')
        command = log.lastCommand()
        self.assertEquals(command.status, 2)

    def testFailIfFailure(self):

        log.addCommand('failedCommand', [], status = 1)
        self.assertNotEqual(os.system('./testcommand.sh wantFail'), 0)
        last = log.lastCommand()
        self.assertEquals(last.command, 'failedCommand')

    def testClearFailure(self):

        log.addCommand('failedCommand', [], status = 1)
        os.system('./BonnLogger.py clear')
        self.assertEqual(os.system('./testcommand.sh wantPass'), 0)
        last = log.lastCommand()
        self.assertEquals(last.command, 'testcommand.sh')
        self.assertEquals(last.args, ['wantPass'])

    def testIgnoreFailure(self):

        log.addCommand('failedCommand', [], status = 1)
        os.system('./testcommand.sh forceRun')
        last = log.lastCommand()
        self.assertEquals(last.command, 'testcommand.sh')
        self.assertEquals(last.args, ['forceRun'])

# WEIRDNESS WITH REPORTING FROM SHELL, seems to work
#    def testReportsNoTarget(self):
#        del os.environ['BONN_TARGET']
#        proc = subprocess.Popen('./testcommand.sh notarget', 
#                                shell = True,
#                                stdout = subprocess.PIPE,
#                                stderr = subprocess.STDOUT)
#        code = proc.wait()
#        report = proc.stdout.read()
#        print report
#        self.failUnless(re.search('Error: BONN_TARGET Not Specified', report))
#        self.assertNotEqual(code, 0)

    def testForceStartFailsWithNoTarget(self):
        del os.environ['BONN_TARGET']        
        code = os.system('./testcommand.sh notarget forceRun')
        last = log.lastCommand()
        print last
        self.failUnless(last is None)
        self.assertNotEqual(code, 0)

    def testForceStartFailsWithNoFilter(self):
        del os.environ['BONN_FILTER']        
        code = os.system('./testcommand.sh notarget forceRun')
        last = log.lastCommand()
        print last
        self.failUnless(last is None)
        self.assertNotEqual(code, 0)
    
    def testMultiUsersSameTarget(self):
        os.environ['USER'] = 'dapple'
        os.system('./testcommand.sh args1')
        os.environ['USER'] = 'anja'
        os.system('./testcommand.sh args2')
        commands = log.getEntriesByDate()
        self.assertEquals(commands[0].user, 'dapple')
        self.assertEquals(commands[1].user, 'anja')

    def testMultiUsersDiffTargets(self):
        os.system('./testcommand.sh user1')
        os.environ['USER'] = 'random'
        os.environ['BONN_TARGET'] = 'diff_target'
        os.system('./testcommand.sh notarget fail 1')
        os.environ['USER'] = self.curUser
        os.environ['BONN_TARGET'] = '2003-09-25'

        code = os.system('./testcommand.sh user1good')
        self.assertEquals(code, 0)
        
        last = log.lastCommand()
        self.assertEquals(last.args, ['user1good'])
        
        
    def testMultiUsersSameTargetFail(self):
       os.system('./testcommand.sh fail 1')
       os.environ['USER'] = 'random'
       code = os.system('./testcommand.sh expectFail')
       self.assertNotEqual(code, 0)
       last = log.lastCommand()
       self.assertEquals(last.command, 'testcommand.sh')
       self.assertEquals(last.status, 1)

    def testMultiUsersDiffTargetNoFail(self):
       os.environ['USER'] = 'random'
       os.environ['BONN_TARGET'] = 'other_target'
       log.addCommand('failedCommand', status=1)
       os.environ['USER'] = self.curUser
       self.assertEquals(os.system('./testcommand.sh nofail'), 0)

    def testMultiUsersDiffFilterNoFail(self):
        os.environ['USER'] = 'random'
        os.environ['BONN_FILTER'] = 'other_filter'
        log.addCommand('failedCommand', status=1)
        os.environ['USER'] = self.curUser
        self.assertEquals(os.system('./testcommand.sh nofail'), 0)
 
    def testComment(self):
        os.system('./BonnLogger.py comment "comment1"')
        last = log.lastEntry()
        self.assertEquals(len(last.comments), 1)
        self.assertEquals(last.comments[0].comment, 'comment1')
 
    def testCommentCarryFail(self):
        log.addCommand('failedCommand', status=1)
        os.system('./BonnLogger.py comment "comment1"')
        last = log.lastEntry()
        self.assertEquals(last.comments[0].comment, 'comment1')
        self.assertEquals(log.getLastStatus(), 1)
 
    def testCommentsOnCommands(self):
        self.assertEquals(os.system('./testcommand.sh comment comment1'), 0)
        last = log.lastEntry()
        self.assertEquals(len(last.comments), 1)
        self.assertEquals(last.comments[0].comment, 'comment1')
 
    def testMutliArgs(self):
        os.system('./testcommand.sh args1 args2')
        last = log.lastCommand()
        self.assertEquals(last.args, 'args1 args2'.split())
 
    def testFixesCommandName(self):
        os.system('./BonnLogger.py log ./uglycommand args1')
        last = log.lastCommand()
        self.assertEquals(last.command, 'uglycommand')
 
    def testFixesCommandNameForced(self):
        os.system('./BonnLogger.py forceLog ./uglycommand args1')
        last = log.lastCommand()
        self.assertEquals(last.command, 'uglycommand')
 
    def testReturnsExitCode(self):
        id = log.addCommand('checkRetunCode')
        code = os.system('./BonnLogger.py update %d 1' % id)
        self.assertEquals(code, 256)
 
    def testTestStateVarUnset(self):
        del os.environ['BONN_TEST']
        proc = subprocess.Popen('./BonnLogger.py state', 
                                shell = True,
                                stdout = subprocess.PIPE)
        code = proc.wait()
        report = proc.stdout.read()
        print report
        self.assert_(re.match('production', report))
 
    def testTestStateVarDefined(self):
        os.environ['BONN_TEST'] = ''
        proc = subprocess.Popen('./BonnLogger.py state', 
                                shell = True,
                                stdout = subprocess.PIPE)
        code = proc.wait()
        report = proc.stdout.read()
        print report
        self.assert_(re.match('test', report))
 
    def testTestStateVarSet(self):
        proc = subprocess.Popen('./BonnLogger.py state', 
                                shell = True,
                                stdout = subprocess.PIPE)
        code = proc.wait()
        report = proc.stdout.read()
        print report
        self.assert_(re.match('test', report))
 
    def testTestStateVarSetFalse(self):
        os.environ['BONN_TEST'] = '0'
        proc = subprocess.Popen('./BonnLogger.py state', 
                                shell = True,
                                stdout = subprocess.PIPE)
        code = proc.wait()
        report = proc.stdout.read()
        print report
        self.assert_(re.match('production', report))
 
    def testLast(self):
        os.system('./testcommand.sh arg1')
        os.system('./testcommand.sh arg2')
        proc = subprocess.Popen('./BonnLogger.py last', 
                                shell = True,
                                stdout = subprocess.PIPE)
        code = proc.wait()
        report = proc.stdout.read()
        self.assertTrue(re.search('testcommand.sh', report))
        self.assertTrue(re.search('arg2', report))
        self.assertFalse(re.search('arg1', report))
 
    def testMultiLast(self):
        os.system('./testcommand.sh arg1')
        os.system('./testcommand.sh arg2')
        proc = subprocess.Popen('./BonnLogger.py last 2', 
                                shell = True,
                                stdout = subprocess.PIPE)
        code = proc.wait()
        report = proc.stdout.read()
        print report
        self.assertTrue(re.search('testcommand.sh', report))
        self.assertTrue(re.search('arg1', report))
        self.assertTrue(re.search('arg2', report))
 
 
    def testOffSwitch(self):
        os.environ['BONN_LOG'] = "0"
        os.system('./testcommand.sh nologging')
        last = log.lastCommand()
        if last is not None:
            self.assertNotEquals(last.args, 'nologging')
 
    def testOnSwitch(self):
        os.system('./testcommand.sh logging')
        last = log.lastCommand()
        self.assertEqual(last.args, ['logging'])
 
    def testDefinedOnSwitch(self):
        os.environ['BONN_LOG'] = ''
        os.system('./testcommand.sh logging')
        last = log.lastCommand()
        self.assertEqual(last.args, ['logging'])
 
    def testLogVar(self):
        os.system('./BonnLogger.py config FILTER=W-C-RC FLAT=DOMEFLAT')
        last = log.lastEntry()
        print last.variables
        self.assertEquals(last.variables[0].var, 'FILTER')
        self.assertEquals(last.variables[0].val, 'W-C-RC')
        self.assertEquals(last.variables[1].var, 'FLAT')
        self.assertEquals(last.variables[1].val, 'DOMEFLAT')
       

                   
###########################################

class TestBonnLogging(unittest.TestCase):

    def setUp(self):
        os.environ['BONN_LOG'] = '1'
        log.reset()
        os.environ['BONN_TARGET'] = '2003-09-25'
        os.environ['BONN_FILTER'] = 'W-J-V'

    def testAddEntry(self):

        log.addCommand('testcommand2')
        maxid = log.Command.select().max('id')
        last = log.Command.get(maxid)
        self.assertEquals(last.command, 'testcommand2')

    def testAddEntryReturnsID(self):

        id = log.addCommand('testcommand')
        last = log.lastEntry()
        self.assertEquals(id, last.id)

    def testDefaultStatus(self):

        log.addCommand('testcommand')
        last = log.lastCommand()
        self.assertEquals(last.status, None)

    def testUpdateStatus(self):

        id = log.addCommand('testcommand')
        log.updateStatus(id, 0)
        last = log.lastCommand()
        self.assertEquals(last.status, 0)
        
    def testLastCommand(self):

        log.addCommand('testcommand2')
        self.assertEquals(log.lastCommand().command, 'testcommand2')

    def testLastCommandFromMulti(self):

        log.addCommand('testcommand1')
        log.addCommand('testcommand2')
        log.addCommand('testcommand3')
        self.assertEquals(log.lastCommand().command, 'testcommand3')

    def testAddEntryWArgs(self):

        log.addCommand('testcommand2', ['arg1', 'arg2'])
        last = log.lastCommand()
        self.assertEquals(last.command, 'testcommand2')
        self.assertEquals(last.args, 'arg1 arg2'.split())

    def testAddMultiWArgs(self):

        log.addCommand('testcommand')
        log.addCommand('testcommand', ['arg1'])
        last = log.lastCommand()
        self.assertEquals(last.command, 'testcommand')
        self.assertEquals(last.args, ['arg1'])

    def testGetLastEntriesNoArgs(self):

        for i in xrange(15):
            log.addCommand('test%d' % i)

        entries = log.getLastEntries()
        self.assertEquals(len(entries), 10)
        for i in xrange(10):
            self.assertEquals(entries[i].command.command, 'test%d' % (i+5))

    def testGetLastEntriesNotEnoughPast(self):

        for i in xrange(5):
            log.addCommand('test%d' % i)

        entries = log.getLastEntries(15)
        self.assertEquals(len(entries), 5)
        for i in xrange(5):
            self.assertEquals(entries[i].command.command, 'test%d' % i)

    def testLastNoPast(self):

        last = log.lastCommand()
        self.assertEquals(last, None)

    def testLast(self):

        log.addCommand('test')
        self.assertEquals(log.lastCommand().command, 'test')
        
        
            
###########################################
###########################################

testcases = [ TestBonnLogging, TestLogSystem]
#testcases = [TestBonnLogging]

suite = unittest.TestSuite(map(unittest.TestLoader().loadTestsFromTestCase,
                               testcases))
unittest.TextTestRunner(verbosity=2).run(suite)




