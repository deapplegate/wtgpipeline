#!/usr/bin/env python
####################
# @author Douglas Applegate
# @filename createAutotracker.py
# @date 3/11
#
# Creates a list of chips to exclude for the ldac pipeline
#####################

__cvs_id__ = "$Id: createAutotrackerList.py,v 1.3 2008-07-09 01:22:15 dapple Exp $"

###################

import re, sys

import BonnLogger
__bonn_logger_id__ = BonnLogger.addCommand('createAutotrackerList.py', 
                                           sys.argv[1:])

####################

usage = \
'''createAutotracker.py FILE
     FILE   a txt file with IMAGE    {: sep list, with auto x-x}
'''

if len(sys.argv) != 2:
    print usage
    BonnLogger.updateStatus(__bonn_logger_id__, 1)
    sys.exit(1)

#######################

def parseChipList(chipList):
    
    chips = []
    for entry in filter(lambda x: x != '',
                             map(str.strip, chipList.split(','))):
        match = re.search('(\d+)(\s*-\s*(\d+))?', entry)
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

######################

def parse(noteList):
    
    categories = [x.strip() for x in noteList.split(':')]

    for cat in categories:

        match = re.match('auto\s+(.+)', cat)
        if match is None:
            continue

        chipList = match.group(1)
        
        return parseChipList(chipList)

    return []

#######################

inputFilename = sys.argv[1]

input = open(inputFilename)
output = open('autotracker_mask', 'w')

inputLines = input.readlines()

for line in inputLines:
    match = re.match('(SUPA\d+)\s+(.+)', line)

    if match is None: continue

    exposure = match.group(1)
    noteList = match.group(2)

    maskList = parse(noteList)

    for chip in maskList:
        output.write('%s_%d\n' % (exposure,chip))

    
input.close()
output.close()

BonnLogger.updateStatus(__bonn_logger_id__, 0)
