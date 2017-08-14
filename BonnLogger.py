#!/usr/bin/env python
##########################
# Interfaces to Databse for Logging Purposes
##########################


import sys, os, datetime
from sqlobject import *
from sqlobject.inheritance import InheritableSQLObject

__cvs_id__ = "$Id: BonnLogger.py,v 1.9 2010-08-10 21:29:42 anja Exp $"

#####################################

usage = '''
BonnLogger.py

Interface to the Bonn Pipeline Logging System

Commands:
     log cmd [args]          Record that cmd was called with args.
                                Will fail if previous logged command failed.
                                Prints to stdout the id number for the entry.
     
     forceLog cmd [args]     Record that cmd was called with args.
                                Forces the logging of cmd.
     
     update  id status comments  Records exit status of cmd in entry id.
                                    Comments are appended to the record.

     clear                   Resets the fail status of a target

     comment                 Insert a comment into the log

     config KEY=VAR [...]    Records key value pairs             

     state                   Prints to stdout the state of the logging:
                                  Production/Testing : 1/0

     last                    Prints record of last logged cmd

     overview                Prints summary of checkpoints and subsequent coms

     checkpoint              Registers a checkpoint for a target

     help                    Prints this message

Env Vars:
     BONN_TARGET (Req)       Name of current working target
 
     BONN_FILTER (Req)       Name of current working filter

     BONN_TEST               If defined, or set to non-zero,
                                puts logging into test mode

     BONN_LOG                If defined to 0, then logging is turned off
'''

#####################################

class State(object):

    def __init__(self, name, connection):
        self.name = name
        self.connection = connection

    def __str__(self):
        return self.name

    def connect(self):
        sqlhub.processConnection = connectionForURI(self.connection)

class NoneState(object):
    def __str__(self):
        return "nostate"
    def connect(self):
        pass

nostate = NoneState()
production = State('production', 'mysql://weaklensing:darkmatter@ki-sr01/subaru')
testing = State('testing', 'mysql://weaklensing:darkmatter@ki-sr01/test')
#testing = State('testing', 'mysql://weaklensing:darkmatter@ki-sr01/test?debug=t')

def useTestMode():
    return ('BONN_TEST' in os.environ) and (os.environ['BONN_TEST'] != "0")

LogState = nostate
if useTestMode():
    LogState = testing
else:
    LogState = production
LogState.connect()

#########################


class Command(SQLObject):

    class sqlmeta:
        cacheValues = False

    entry = ForeignKey('Entry')
    command = StringCol()
    args = StringCol(default = '')
    status = IntCol(default = None)

    def __str__(self):
        report = 'Command: %s' % self.command
        if self.args != '':
            report += " %s" % ' '.join(self.args)
        if self.status is not None:
            report += ' Status: %d' % self.status
        return report

    def _set_args(self, args):
        val = ' '.join(args)
        self._SO_set_args(val)

    def _get_args(self):
        val = self._SO_get_args()
        return val.split()

class Comment(SQLObject):

    class sqlmeta:
        cacheValues = False

    entry = ForeignKey('Entry')
    comment = StringCol()
    
    def __str__(self):
        return "Comment: %s" % self.comment

class Variable(SQLObject):

    class sqlmeta:
        cacheValues = False

    entry = ForeignKey('Entry')
    var = StringCol()
    val = StringCol()

    def __str__(self):
        return "Var: %s = %s" % (self.var, self.val)

class Checkpoint(SQLObject):

    class sqlmeta:
        cacheValues = False

    entry = ForeignKey('Entry')
    checkpoint = StringCol()

    def __str__(self):
        return "Checkpoint: %s" % self.checkpoint


class Entry(SQLObject):

    class sqlmeta:
        cacheValues = False
    
    user = StringCol()
    target = StringCol()
    filter = StringCol()
    timestamp = DateTimeCol()
    command = SingleJoin('Command')
    comments = MultipleJoin('Comment')
    variables = MultipleJoin('Variable')
    checkpoint = SingleJoin('Checkpoint')

    def __str__(self):
        report = '%d\t%s\t%s\n' % (self.id, str(self.timestamp), self.user)
        if self.command is not None:
            report += '\t\t%s\n' % str(self.command)
        if self.checkpoint is not None:
            report += '\t\t%s\n' % str(self.checkpoint)
        for comment in self.comments:
            report += '\t\t%s\n' % str(comment)
        for var in self.variables:
            report += '\t\t%s\n' % str(var)
        return report



Entry.createTable(ifNotExists = True)
Command.createTable(ifNotExists = True)
Comment.createTable(ifNotExists = True)
Variable.createTable(ifNotExists = True)
Checkpoint.createTable(ifNotExists = True)

########################

class NoTargetError(Exception): pass

class NoFilterError(Exception): pass

#########################

def loggingIsOff():
    
    return 'BONN_LOG' in os.environ and \
        os.environ['BONN_LOG'] == '0'

#########################

def state():
    return LogState

#########################

def reset():

    Entry.dropTable(ifExists = True)
    Command.dropTable(ifExists = True)
    Comment.dropTable(ifExists = True)
    Variable.dropTable(ifExists = True)
    Checkpoint.dropTable(ifExists = True)

    Entry.createTable()
    Command.createTable()
    Comment.createTable()
    Variable.createTable()
    Checkpoint.createTable()
    
#########################

def getTarget():
    try:
        return os.environ['BONN_TARGET']
    except KeyError:
        raise NoTargetError('BONN_TARGET not defined')

########################

def getFilter():
    try:
        return os.environ['BONN_FILTER']
    except KeyError:
        raise NoFilterError('BONN_FILTER not defined')

########################

def targets():
    
    targets = []
    for entry in Entry.select():
        if entry.target not in targets:
            targets.append(entry.target)

    return targets

#######################

def filters(target):
    
    filters = []
    for entry in Entry.selectBy(target = target):
        if entry.filter not in filters:
            filters.append(entry.filter)

    return filters
    

########################

def getUser():

    return os.environ['USER']
    
#########################

def lastEntry(target = None, filter = None):

    entry = getLastEntries(num = 1, 
                    target = target, 
                    filter = filter)
    if len(entry) == 0:
        return None
    else:
        return entry[0]

############################

def getLastStatus():

    isCurTarget = (Command.q.entryID == Entry.q.id) & \
        (Entry.q.target == getTarget()) & \
        (Entry.q.filter == getFilter())

    curStatusId = Command.select(isCurTarget & \
                                     (Command.q.status != None )).max(Command.q.id)

    if curStatusId is None:
        return None
    return Command.get(curStatusId).status

############################

def lastCommand(target = None, filter = None):
    
    if target is None and filter is None:
        maxId = Command.select().max(Command.q.id)
    else:
        isCurTarget = (Command.q.entryID == Entry.q.id) & \
            (Entry.q.target == getTarget()) & \
            (Entry.q.filter == getFilter())
    
        maxId = Command.select(isCurTarget).max(Command.q.id)
    
    if maxId is None:
        return None
    return Command.get(maxId)

    
############################

def getLastEntries(num = 10, target = None, filter = None):

    if target is None and filter is None:
        entries = Entry.select()[-num:]
    else:
        entries = Entry.selectBy(target=target, filter=filter)[-num:]

    return list(entries)

############################

def getEntriesByDate(range = None):

    if range is None:
        return list(Entry.select())

    return list(Entry.select(AND(Entry.q.timestamp >= range[0], 
                              Entry.q.timestamp <= range[1])))

############################

def addEntry():
    return Entry(user = getUser(), 
                     target = getTarget(),
                     filter = getFilter(),
                     timestamp = datetime.datetime.now())


############################

def addCommand(cmd, args = [], status = None, comment = None):

    if loggingIsOff():
        return -1

    entry = addEntry()

    c = Command(entry = entry, 
                command = cmd, 
                args = args,
                status = status)

    if comment is not None:
        Comment(entry = entry, comment = comment)

    return entry.id

############################

def addCheckpoint(target, filter, check, comment = None):

    if loggingIsOff():
        return -1;

    confirm = raw_input("Confirm %s for %s : %s [y/n]?" % (check, target, filter))
    if confirm == 'y' or confirm == 'Y':
        entry = addEntry()
        Checkpoint(entry = entry, checkpoint = check)
        if comment is not None:
            Comment(entry = entry, comment = comment)

############################

def getCheckpoints(target, filter):

    return list(Entry.select(AND(Checkpoint.q.entryID == Entry.q.id,
                            AND(Entry.q.target == target,
                                Entry.q.filter == filter))))



############################

def updateStatus(id, code, comment = None):

    if loggingIsOff():
        return

    entry = Entry.get(id)
    if entry is None or entry.command is None:
        return

    entry.command.status = code
    
    if comment is not None:
        Comment(entry = entry, comment = comment)

############################

def clearStatus():
    addCommand('clearStatus', status = 0)

############################

def report(entries, target, filter):

    report = 'Log for %s : %s\n' % (target, filter)
    
    for entry in entries:

        report += str(entry)
        
    return report

############################
############################


def parseLog(args):

    if loggingIsOff():
        return -1

    curStatus = getLastStatus()

    if curStatus is not None and curStatus > 0:
        sys.stderr.write("BonnLogger: Last Job Failed - Exiting\n")
        sys.exit(1)

    return parseForceLog(args)

############################

def parseForceLog(args):

    command = os.path.basename(args[0])
    
    id = addCommand(command, args[1:])
    print id
    return id

###########################

def parseUpdate(args):

    if loggingIsOff():
        sys.exit(0)

    commandId = args[0]
    exitStatus = int(args[1])
    comment = None
    if len(args) > 2:
        comment = ' '.join(args[2:])

    updateStatus(commandId, exitStatus, comment)

    sys.exit(exitStatus)
    

############################

def parseComment(args):

    entry = addEntry()
    Comment(entry = entry, comment = args[0])

############################

def parseConfig(args):
    
    entry = addEntry()
    for arg in args:
        (var,val) = arg.split('=')
        Variable(entry = entry, var = var, val = val)
        

############################

def parseState(args):

    print "%s : %d" % (state(), int(not loggingIsOff()))

############################

def parseLast(args):

    if len(args) > 0:
        entries = getLastEntries(int(args[0]), getTarget(), getFilter())
    else:
        entries = getLastEntries(1, getTarget(), getFilter())

    print report(entries, getTarget(), getFilter())

############################

def parseOverview(args):

    for target in targets():
        for filter in filters(target):
            entries = getCheckpoints(target, filter)
            lastEntry = getLastEntries(1, target, filter)[0]
            if lastEntry not in entries:
                entries.append(lastEntry)
            print report(entries, target, filter)
            print

#############################

def parseCheckpoint(args):

    if loggingIsOff():
        return -1;

    check = args[0];
    if len(args) > 1:
        comment = args[1];
        addCheckpoint(getTarget(), getFilter(), check, comment)
    else:
        addCheckpoint(getTarget(), getFilter(), check)

############################

def parseCommandLine():

    command = sys.argv[1]
    args = sys.argv[2:]

    try:

        if command == 'log':
            parseLog(args)

        elif command == 'forceLog':
            parseForceLog(args)
            
        elif command == 'update':
            parseUpdate(args)
            
        elif command == 'clear':
            clearStatus()

        elif command == 'config':
            parseConfig(args)
            
        elif command == 'comment':
            parseComment(args)
            
        elif command == 'state':
            parseState(args)
        
        elif command == 'last':
            parseLast(args)

        elif command == 'overview':
            parseOverview(args)

        elif command == 'checkpoint':
            parseCheckpoint(args)

        elif command == 'help':
            print usage

        else:
            print "Error: %s Unrecognized"
            print usage
            sys.exit(1)

    except NoTargetError:
        sys.stderr.write("\nError: BONN_TARGET Not Defined\n")
        if not loggingIsOff():
            sys.exit(1)

    except NoFilterError:
        sys.stderr.write("\nError: BONN_FILTER Not Defined\n")
        if not loggingIsOff():
            sys.exit(1)
    

############################

if __name__ == '__main__':

    parseCommandLine()


    
