#!/usr/bin/env python
###########################
# For transfering a fit from one observation to another
###########################

import sys, optparse
import photometry_db

photometry_db = photometry_db.Photometry_db()

#################################

class UnknownObservationException(Exception): pass

#################################

def transferPhotoCalibration(cluster, fromFilter, toFilter, specification):

    from_observation = photometry_db.getZeropoint(cluster=cluster, 
                                                     filter=fromFilter, 
                                                     **specification)

    if from_observation is None:
        raise UnknownObservationException(fromFilter)

    photometry_db.updateCalibration(cluster, filter = toFilter, calibration = from_observation, **specification)

    calibration = photometry_db.getZeropoint(cluster, filter = toFilter, **specification)


    assert(from_observation == calibration)


###################################

def main(argv = sys.argv):

    ###

    def parse_spec(option, opt, value, parser):

        key, val = value.split('=')
        
        if not hasattr(parser.values, 'specification'):
            setattr(parser.values, 'specification', {})
            
        parser.values.specification[key] = val

       
    ###


    parser = optparse.OptionParser()
    parser.add_option('-c', '--cluster',
                      dest='cluster',
                      help = 'Name of cluster')
    parser.add_option('-f', '--from',
                      dest='fromFilter',
                      help = 'Filter to transfer calibration from')
    parser.add_option('--spec', dest='specification',
                      action='callback',
                      type= 'string', 
                      help='key=val set determines the uniqueness of this calibration',
                      default = {},
                      callback = parse_spec)

    options, args = parser.parse_args(argv)

    if options.cluster is None or options.fromFilter is None:
        parser.error('Cluster and originating filter required!!!')

    toFilters = args[1:]

    for toFilter in toFilters:

        print 'Processing %s' % toFilter
        transferPhotoCalibration(options.cluster, options.fromFilter, toFilter, options.specification)


    

###################################

if __name__ == '__main__':

    main()
