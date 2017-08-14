#!/usr/bin/env python
###################
# @file datarobot.py
# @author Douglas Applegate
# @date 10/16
#
# @brief Scans directories for Subaru data, updating database as to what is there
####################

from __future__ import with_statement
import sys, os, re, pyfits, datetime, time, inspect, subprocess
from math import *
from optparse import OptionParser
from sqlobject import *

#######################

__cvs_id__="$Id: datarobot.py,v 1.3 2010-08-10 21:29:42 anja Exp $"

######################

rad2deg = pi / 180.
deg2rad = 180./ pi
deg2arcmin = 60.

######################

#DATABASE CONNECTION
sqlhub.processConnection = connectionForURI('mysql://weaklensing:darkmatter@ki-sr01/subaru')

#DATA MODEL

class Run(SQLObject):

    class sqlmeta:
        cacheValues = False

    night = DateCol()
    filter = StringCol()
    instrument = StringCol()
    config = StringCol(default = None)
    exposures = MultipleJoin('Exposure')
    targets = RelatedJoin('Target')

    def _get_nightObj(self):
        return self._SO_get_night()

    def _get_night(self):
        return self._SO_get_night().strftime('%Y-%m-%d')

    def __cmp__(self, other):
        if self.nightObj > other.nightObj:
            return 1
        if self.nightObj < other.nightObj:
            return -1
        if self.filter > other.filter:
            return 1
        if self.filter < other.filter:
            return -1
        return 0
    
    
class Exposure(SQLObject):

    class sqlmeta:
        cacheValues = False
    
    expid = StringCol(unique = True, length=25)
    type = StringCol()
    RA = FloatCol()
    DEC = FloatCol()
    
    airmass = FloatCol(default = None)
    azimuth = FloatCol(default = None)
    altitude = FloatCol(default = None)
    focus = FloatCol(default = None)
    exptime = FloatCol(default = None)
    detid = IntCol(default = None)
    dettemp = FloatCol(default = None)
    gain = FloatCol(default = None)
    seeing = FloatCol(default = None)
    domewind = FloatCol(default = None)
    outwind = FloatCol(default = None)

    run = ForeignKey('Run')
    target = ForeignKey('Target')
    

class Target(SQLObject):

    class sqlmeta:
        cacheValues = False

    name = StringCol(unique = True, length=25)
    RA = FloatCol()
    DEC = FloatCol()
    inSample = BoolCol()
    inSloan = BoolCol(default = None)
    type = StringCol()
    exposures = MultipleJoin('Exposure')
    runs = RelatedJoin('Run')
    aliases = MultipleJoin('TargetAlias')

class TargetAlias(SQLObject):

    class sqlmeta:
        cacheValues = False
        
    alias = StringCol()
    target = ForeignKey('Target')



Run.createTable(ifNotExists = True)
Exposure.createTable(ifNotExists = True)
Target.createTable(ifNotExists = True)
TargetAlias.createTable(ifNotExists = True)

#########################

def cleanDatabase():

    Run.dropTable(ifExists = True)
    Exposure.dropTable(ifExists = True)
    Target.dropTable(ifExists = True)
    TargetAlias.dropTable(ifExists = True)

    Run.createTable(ifNotExists = True)
    Exposure.createTable(ifNotExists = True)
    Target.createTable(ifNotExists = True)
    TargetAlias.createTable(ifNotExists = True)    

#########################

def parseObject(line):

    tokens = line.strip().split()

    name = tokens[0]
    fullname = tokens[1]
    RA = float(tokens[2])
    DEC = float(tokens[3])
    type = tokens[4]
    nicknames = tokens[5:-1]

    curTarget = Target.selectBy(name = name).getOne(None)
    if curTarget is None:
        curTarget = Target(name = name, RA = RA, DEC = DEC, type = type)
    else:
        curTarget.set(name = name, RA = RA, DEC = DEC, type = type)
    
    if TargetAlias.selectBy(alias = name).getOne(None) is None:
        TargetAlias(alias = name, target = curTarget)
    for nickname in nicknames:
        if TargetAlias.selectBy(alias = nickname).getOne(None) is None:
            TargetAlias(alias = nickname, target = curTarget)

#############################

def parseSloan(line):

    tokens = line.strip().split()
    targetalias = tokens[0].strip()
    sloanstat = ' '.join(tokens[1:])

    match = re.match('^(\w*)\.', targetalias)
    if match is not None:
        targetalias = match.group(1)

    if sloanstat == 'no SDSS':
        inSloan = False
    else:
        inSloan = True

        
    alias = TargetAlias.selectBy(alias = targetalias).getOne(None)
    if alias is None:
        print 'Cannot find %s' % targetalias
        return
    
    curTarget = alias.target
    curTarget.inSloan = inSloan

    

###########################

def doesExposureExist(expid):
    return Exposure.selectBy(expid = expid).getOne(None) is not None

##########################

def distOnSphere(ra1, dec1, ra2, dec2):
    return 60.*57.2958*acos(cos(1.5708-(dec1*0.01745))*cos(1.5708-(dec2*0.01745)) + (sin(1.5708-(dec1*0.01745))*sin(1.5708-(dec2*0.01745)))*cos((ra1-ra2)*0.01745));  

###########################

def processExposure(night, filter, instrument, config, targetalias, 
                    expid, type, RA, DEC,  **keywords):

    curRun = Run.selectBy(night = night, 
                          filter = filter, 
                          instrument = instrument).getOne(None)
    if curRun is None:
        curRun = Run(night = night, 
                     filter = filter, 
                     instrument = instrument, 
                     config = config)

    curTarget = None
    try:
        curTarget = TargetAlias.selectBy(alias = targetalias).getOne().target

    except SQLObjectNotFound:
        
        candidates = Target.select(AND(AND(Target.q.RA >= (RA-.1), 
                                           Target.q.RA <= (RA+.1)), 
                                       AND(Target.q.DEC >= (DEC - .1), 
                                           Target.q.DEC <= (DEC + .1))))

        if candidates is not None:
            for candidate in candidates:
                dist = distOnSphere(RA, DEC, candidate.RA, candidate.DEC)
                if dist < 10:
                    curTarget = candidate
                    break
        
        if curTarget is None:
            curTarget = Target(name = targetalias, inSample = False, RA = RA, DEC = DEC,
                               type = 'other')

        TargetAlias(alias = targetalias, target = curTarget)


    
    curExp = Exposure(expid = expid, type = type, RA = RA, DEC = DEC, 
                      run = curRun, target = curTarget,
                      **keywords)
    if curRun not in curTarget.runs:
        curTarget.addRun(curRun)

###########################
##FILE INTERPRETERS
###########################

def getSubaruConfig(mjd):

    nightid = subprocess.Popen("nightid -t 22:00:00 -d 31/12/1998 -m %s" % mjd, 
                               stdout = subprocess.PIPE, shell = True)
    gawk1 = subprocess.Popen("gawk ' ($1 ~ /Days/) {print $6}'", 
                             stdin = nightid.stdout,
                             stdout = subprocess.PIPE, shell = True)
    gawk2 = subprocess.Popen("gawk 'BEGIN{ FS=\".\"} {print $1}'",
                             stdin = gawk1.stdout,
                             stdout = subprocess.PIPE, shell = True)

    gabodsid = float(gawk2.communicate()[0])


    if gabodsid < 575:
        return None
    
    if gabodsid > 575 and gabodsid < 721:
        return '8'

    if gabodsid > 721 and gabodsid < 817:
        return '9'
    
    if gabodsid > 817 and gabodsid < 1309:
        return '10_1'

    if gabodsid > 1309 and gabodsid < 3436:
        return '10_2'
 
    if gabodsid > 3436:
        return None

#######################################

def interpretSubaruRawFile(filename):

    print "Processing %s" % filename

    match = re.search('((SUPA\d+)\d)\.fits(.gz)?', filename)
    if match is None:
        print "Filename doesn't match"
        return False

    expid = match.group(2)

    if doesExposureExist(expid):
        return True

    isZipped = match.group(3) is not None
    if isZipped:
        os.system('gunzip %s' % filename)
        dir = os.path.dirname(filename)
        filename = '%s/%s.fits' % (dir, match.group(1))

    header = pyfits.getheader(filename)

    if header is None:
        return False

    try:

        if header['EXTEND']:
            print "%s:Not Right File Type" % filename
            return False


        keywords = {}
        
        #RUN INFO
        keywords['night'] = datetime.datetime.strptime(header['DATE-OBS'], '%Y-%m-%d')
        keywords['filter'] = header['FILTER01']
        keywords['instrument'] = 'Subaru'
        keywords['config'] = getSubaruConfig(header['MJD'])
        keywords['targetalias'] = header['OBJECT']

        #Required Exposure Info
        keywords['type'] = header['DATA-TYP']
        keywords['RA'] = float(subprocess.Popen(['hmstodecimal', header['RA']], 
                                                stdout=subprocess.PIPE).communicate()[0])
        keywords['DEC'] = float(subprocess.Popen(['dmstodecimal',header['DEC']],
                                                 stdout=subprocess.PIPE).communicate()[0])

    
        #Optional Info
        keywords['airmass']   = header['AIRMASS']
        keywords['azimuth']   = header['AZIMUTH']
        keywords['altitude']  = header['ALTITUDE']
        keywords['focus'] = header['FOC-VAL']
        keywords['exptime'] = header['EXPTIME']
        keywords['detid'] = header['DET-ID']
        keywords['dettemp'] = header['DET-TMP']
        keywords['gain'] = header['GAIN']
        keywords['seeing'] = header['SEEING']
        keywords['domewind'] = header['DOM-WND']
        keywords['outwind'] = header['OUT-WND']

    except KeyError:
        return False


    processExposure(expid = expid, **keywords)

    if isZipped:
        os.system('gzip %s' % filename)

    return True

##############################
##ADD PARSING METHODS HERE
##############################

##############################
#Find all interpret methods
this_mod = __import__(__name__)
fileInterpretors = [getattr(this_mod, name) for name in filter(lambda name: re.match('interpret', name) and inspect.isfunction(getattr(this_mod, name)), dir())]

##############################

def processDirectories(directoryList):

    print directoryList
    
    while directoryList:
        dirname = directoryList.pop()

        print "Processing %s" % dirname

        filetuples = os.walk(dirname)
        
        for (dirpath, dirnames, filenames) in filetuples:
            
            for dir in dirnames:
                fulldir = os.path.join(dirpath, dir)
                if os.path.islink(fulldir):
                    print 'Adding %s to list' % fulldir
                    directoryList.append(fulldir)
                    #because walk doesn't traverse symbolic links, gotta do it by hand
        
            for file in filenames:
                fullfile = os.path.join(dirpath, file)
                try:
                    for curFileInterpretor in fileInterpretors:
                        if curFileInterpretor(fullfile):
                            break
                except IOError, e:
                    print e


################################

if __name__ == '__main__':

    parser = OptionParser(usage='%prog [options] dir1 dir2 ...', description='Will scan each directory listed for exposures')
    
    parser.add_option('-c', '--clean', dest='clean', 
                      help = 'Erase all existing database entries', 
                      action='store_true', default=False)
    parser.add_option('-t', '--targets', dest='targetfile',
                      help = 'Read file to add targets to set',
                      default = None)
    parser.add_option('-s', '--sloan', dest='sloan',
                      help = 'List of clusters with sloan coverage',
                      default = None)
    (options, args) = parser.parse_args()

    
    if options.clean:
        cleanDatabase()

    if options.targetfile is not None:
        with open(options.targetfile) as INPUT:
            for line in INPUT:
                parseObject(line)

    if options.sloan is not None:
        with open(options.sloan) as INPUT:
            for line in INPUT:
                parseSloan(line)

    if len(args) == 0 and not options.clean and not options.targetfile:
        parser.print_help()
        sys.exit(1)
    
    processDirectories(args)
