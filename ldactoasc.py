#!/usr/bin/env python
######################

import ldac, sys, re
from optparse import OptionParser

parser = OptionParser(usage='''ldactoasc.py -i catfile <-t table> key1 key2 ...
                                      specify vectors with key1:vecpos.
                                      Remember, its 0 indexed!''')

parser.add_option('-i', '--input',
                  help = 'input cat file',
                  dest='infile')
parser.add_option('-t', '--table',
                  help = 'table name',
                  dest='table',
                  default='OBJECTS')

options, keys = parser.parse_args()

if options.infile is None:
    error('Must Specify Input Catalog!')

if len(keys) == 0:
    sys.exit(0)

class ExtractScalarKey():
    def __init__(self, key):
        self.key = key
    def __call__(self, cat, index):
        return cat[self.key][index]
class ExtractVectorKey():
    def __init__(self, key, pos):
        self.key = key
        self.pos = pos
    def __call__(self, cat, index):
        return cat[self.key][index, self.pos]

extractKeys = []
positionArgCheck = re.compile('(.+?):(\d+)')
for key in keys:
    match = positionArgCheck.match(key)
    if match is None:
        extractKeys.append(ExtractScalarKey(key))
    else:
        actualkey = match.group(1)
        pos = int(match.group(2))
        extractKeys.append(ExtractVectorKey(actualkey, pos))


cat = ldac.openObjectFile(options.infile, options.table)

for index in xrange(len(cat)):

    output = [ '%f' % key(cat, index) for key in extractKeys ]
    print ' '.join(output)
