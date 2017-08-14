#!/usr/bin/env python
#####################

# Manually set a zeropoint for a fitid, such as from SLR

#####################

import sys, os, re
import photocalibrate_cat as pcc
import photometry_db, ldac, utilities
photometry_db.initConnection()

######################

def setSlrZP(cluster, cat, zpfile):

    zpf = open(zpfile).readlines()
    zps = {}
    for line in zpf:
        tokens = line.split()
        fitFilter = tokens[1]
        zpoffset = float(tokens[2])
        zperr = float(tokens[3])
        
        zps[fitFilter] = (zpoffset, zperr)



    cat = ldac.openObjectFile(cat,'ZPS')
    if cat is None:
        print 'need to run new version of do_photometry.sh CLUSTER APPLY'
        raise

    filters = {}
    for filter, zp in zip(cat['filters'], cat['zeropoints']):
        filters[filter] = zp


    slr_sets = {}
    for filter in zps.keys():

        new_zp = filters[filter] + zps[filter][0]
        
        slrZP = photometry_db.registerSlrZP(cluster, zp = float(new_zp), zperr = zps[filter][1], fitFilter = filter, filter = filter)

        photometry_db.updateCalibration(cluster, slrZP, filter = filter)

        instrument, config, chip, filter = utilities.parseFilter(filter)
        slr_sets[filter] = [instrument, filter, slrZP]


    

    for filter in filters.keys():
        
        instrument, config, chip, filter = utilities.parseFilter(filter)

        matchFound = False
        for slr_filter, (slr_instrument, slr_filter, slrZP) in slr_sets.iteritems():
            if slr_instrument == instrument and slr_filter == filter:
                photometry_db.updateCalibration(cluster, slrZP, filter = filter)
                break


#######################

def setLePhareZP(cluster, fitID, zpfile):

    zpf = open(zpfile).readlines()
    zps = {}
    for l in zpf:
        import re
        res = re.split('\s+',l[:-1])
        print res
        zps[res[1]] = float(res[2])


    ''' retrieve the slr zeropoint '''

    lephareZP = photometry_db.registerLePhareZP(cluster, fitID, zp)

#######################

def main(argv = sys.argv):

    if len(argv) < 5:
        print 'example: python save_zp.py $photdir MACS2214-13 MACS2214-13.stars.calibrated.cat slr.offsets.list slr'
        print 'python save_zp.py CLUSTER CATALOG OFFSET_FILE (slr or lephare)'

    photdir = argv[1]
    cluster = argv[2]
    cat = argv[3]
    zp_file = argv[4]
    table = argv[5]

    zpfile = '%s/%s' % (photdir,zp_file)

    print table
    if table == 'slr':
        setSlrZP(cluster, '%s/%s' % (photdir, cat), zpfile)
    elif table == 'lephare':
        setLePhareZP(cluster,'%s/%s' % (photdir, cat), zpfile)

    print 'calibrating'

    params = { 'input' : '%s/%s.unstacked.cat' % (photdir, cluster),
               'cluster' : cluster,
               'output' : '%s/%s.%s.cat' % (photdir, cluster, table),
               'table' : table}

    command = './photocalibrate_cat.py -i %(input)s -c %(cluster)s -o %(output)s -t %(table)s' % params
    os.system(command)
    print 'done' 

    

    

#######################

if __name__ == '__main__':

    main()
