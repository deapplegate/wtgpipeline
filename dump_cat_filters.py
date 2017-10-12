#!/usr/bin/env python
#########################
# Read a catalog, and dump all filters that match
#      Instrum-config-chipid-filter pattern
#########################

import utilities, sys, ldac, re
from optparse import OptionParser

##########################

__cvs_id__ = "$Id: dump_cat_filters.py,v 1.6 2010-10-05 22:34:57 dapple Exp $"

###########################


filter_patterns = [re.compile('^FLUX_ISO\d?-(.+)'), re.compile('^FLUX_APER\d?-(.+)'), re.compile('^MAG_APER\d?-(.+)')]
def extractFilter(fluxkey):

    for filter_pattern in filter_patterns:
        match = filter_pattern.match(fluxkey)
        if match is not None:
            return match.group(1)

    return None

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

#adam-tmp# START
def adam_dumpFilters(cat, appendAppers = False):

    filters = []

    for fluxkey in cat.keys():

        filter = extractFilter(fluxkey)

        if _isNotValidFilter(filter):
            print "_isNotValidFilter"
            continue

        print "filter=",filter," fluxkey=",fluxkey
        if appendAppers:
            nApers = cat[fluxkey].shape[1]
            for i in xrange(nApers):
                filter = '%s_A%d' % (filter, i)
                if filter not in filters:
                    filters.append(filter)
        elif filter not in filters:
            filters.append(filter)

    return filters
#cat1 = ldac.openObjectFile(fl1)
#cat2 = ldac.openObjectFile(fl2)
#adam-tmp# END

###################################

def dumpFilters(cat, appendAppers = False):

    filters = []

    for fluxkey in cat.keys():

        filter = extractFilter(fluxkey)

        if _isNotValidFilter(filter):
            continue

        if appendAppers:
            nApers = cat[fluxkey].shape[1]
            for i in xrange(nApers):
                filter = '%s_A%d' % (filter, i)
                if filter not in filters:
                    filters.append(filter)
        elif filter not in filters:
            filters.append(filter)

    return filters


###################################

ns=globals() #adam-tmp
def main(argv):

    parser = OptionParser(usage='dump_cat_filters.py <-a> cat')
    parser.add_option('-a', '--apers',
                      help='Append aperture numbers to filter names',
                      dest='appendAppers',
                      action='store_true',
                      default=False)

    options, args = parser.parse_args(argv)

    if len(args) != 1:
        parser.error('Specify catalog file!')
    catfile = args[0]

    cat = ldac.openObjectFile(catfile)

    filters = dumpFilters(cat, options.appendAppers)

    ns.update(locals()) #adam-tmp

    for filter in filters:
        print filter


###################################

if __name__ == '__main__':
    #print "sys.argv=",sys.argv
    from adam_quicktools_ArgCleaner import ArgCleaner
    argv=ArgCleaner()
    #print "argv=",argv
    main(argv[1:])

