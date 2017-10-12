#!/usr/bin/env python
####################
# @author Douglas Applegate
# @filename createExclusion.py
# @date 2/13
#
# Creates a list of chips to exclude for the ldac pipeline
#####################

__cvs_id__ = "$Id: createExclusion.py,v 1.8 2008-11-04 18:24:11 anja Exp $"

###################

import re, sys, bashreader, os

#import BonnLogger
#__bonn_logger_id__ = BonnLogger.addCommand('createExclusion.py', 
#                                           sys.argv[1:])
####################

usage = \
'''createExclusion.py FILE
     FILE   a txt file with IMAGE    1,2,5,7-9
'''

if len(sys.argv) != 2:
    print usage
#    BonnLogger.updateStatus(__bonn_logger_id__, 1)
    sys.exit(1)

if 'INSTRUMENT' not in os.environ:
    print "INSTRUMENT not set!"
    sys.exit(1)


config = bashreader.parseFile('%s.ini' % os.environ['INSTRUMENT'])
if config is None:
    print "Cannot read %s.ini!" % os.environ['INSTRUMENT']
    sys.exit(1)


filePrefix = config.prefix
print "filePrefix = ",filePrefix
nchips = int(config.nchips)


####################

def parseChipList(chipList):
    
    chips = []
    for entry in filter(lambda x: x != '',
                             map(str.strip, chipList.split(','))):
        match = re.search('(\d+)(\s*-\s*(\d+))?(\s+[\(\w]+)?', entry)
        if match is None:
            print "Error! Should be able to read: %s" % entry
            continue

        startChip = int(match.group(1))
        endChip = match.group(3)
        if endChip is None:
            chips.append(startChip)
        else:
            endChip = int(endChip)
            chips.extend(range(startChip, endChip + 1))

    return chips


####################

def parseForRejection(chipList):

    if re.match('^all', chipList):
        return range(1,nchips + 1)

    if re.match('^none', chipList):
        return []

    return parseChipList(chipList)


###################

def parseForAcceptance(chipList):

    if chipList == 'all':
        return []

    if chipList == 'none': 
        return range(1,nchips + 1)

    allChips = range(1,nchips + 1)

    chipsToKeep = parseChipList(chipList)

    for chip in chipsToKeep:
        try:
            allChips.remove(chip)
        except ValueError: continue

    return allChips

###################

#Pass your input file as the first command line argument

#PARSE ARGUMENTS
if len(sys.argv) > 1:
    inputFilename = sys.argv[1]
else:
    inputFilename = './raw_superflat_exclusion'

#OPEN FILES
input = open(inputFilename)
if input is None:
    print "Cannot open %s" % inputFilename
    sys.exit(1)
dir = os.path.dirname(inputFilename)
output = open('%s/superflat_exclusion' % dir, 'w')


#init'ing counter of how many chips we reject
rejectRate = {}
for i in xrange(1,nchips + 1):
    rejectRate[i] = 0

#READ FILE
inputLines = input.readlines()

parse = parseForRejection
if re.match('#ACCEPT', inputLines[0]):
    print "Using Acceptance Parser"
    parse = parseForAcceptance

for line in inputLines:

    if re.match('^#', line):
        continue

    match = re.match('(%s.+?)\s+(.+)' % filePrefix, line)

    if match is None:
        print line
        continue
    

    exposure = match.group(1)
    groups = match.group(2)
    chipList = groups.split(':')[0].strip()

    rejectList = parse(chipList)

    for chip in rejectList:
        rejectRate[chip] += 1
        output.write('%s_%d\n' % (exposure,chip))

    
    #modify this line for your particular notetaking style (Regex format)
    
input.close()
output.close()


print "Reject Rate:"
print rejectRate


#BonnLogger.updateStatus(__bonn_logger_id__, 0)
