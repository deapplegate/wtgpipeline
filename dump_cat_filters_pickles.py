#!/usr/bin/env python
#########################
# Read a catalog, and dump all filters that match
#      Instrum-config-chipid-filter pattern
#########################

import utilities, sys, ldac, re
from optparse import OptionParser

##########################

__cvs_id__ = "$Id: dump_cat_filters_pickles.py,v 1.1 2010-08-10 21:29:42 anja Exp $"

###########################


filter_pattern = re.compile('^FLUX_APER-(.+)')
def extractFilter(fluxkey):

    match = filter_pattern.match(fluxkey)
    if match is None:
        return None
    return match.group(1)

################################


def _isNotValidFilter(filter):
    if filter is None:
        return True
    try:
        utilities.parseFilter(filter)
        return False
    except utilities.UnrecognizedFilterException:
        return True

###################################

parser = OptionParser(usage='dump_cat_filters.py <-a> cat')
parser.add_option('-a', '--apers',
                  help='Append aperture numbers to filter names',
                  dest='appendAppers',
                  action='store_true',
                  default=False)

options, args = parser.parse_args()

if len(args) != 1:
    parser.error('Specify catalog file!')
catfile = args[0]

cat = ldac.openObjectFile(catfile,"PICKLES")

flux_keys, fluxerr_keys, other_keys = utilities.sortFluxKeys(cat.keys())

for fluxkey in flux_keys:

    filter = extractFilter(fluxkey)

    if _isNotValidFilter(filter):
        continue

    if options.appendAppers:
        nApers = cat[fluxkey].shape[1]
        for i in xrange(nApers):
            print '%s_A%d' % (filter, i)
    else:
        print filter
