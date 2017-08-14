#########################
# Find photometry database offsets between current ZPs and ZPS matching
# a prior date range
########################

from __future__ import with_statement
import datetime, os, utilities, re, numpy as np
import photometry_db as pdb, ldac, utilities
import pylab

#######################

subarudir='/nfs/slac/g/ki/ki05/anja/SUBARU'


db = pdb.Photometry_db()

def getRun():

    pairs = []
    with open('%s/lensing.bands' % subarudir) as input:
        for line in input.readlines():

            tokens = line.split()
            cluster = tokens[0]
            if re.match('#', cluster):
                continue

            filter = tokens[1]
            pair = (cluster, filter)
            if pair not in pairs:
                pairs.append(pair)

    return pairs

def report(pair):
    
    cluster, filter = pair

    print cluster

    offsets = runCluster(*pair)

    print
    print

    return offsets

def runCluster(cluster, stdfilter):

    cat = ldac.openObjectFile('%s/%s/PHOTOMETRY_%s_aper/%s.slr.cat' % (subarudir, cluster, 
                                                                       stdfilter, cluster))

    filters = []
    for key in cat.keys():

        match = re.match('MAG_APER1-(.+)', key)
        if match is None:
            continue
        filter = match.group(1)
        filters.append(filter)

    offsets = {}
    for filter in filters:
        instr, config, chip, std = utilities.parseFilter(filter)
        if config == 'COADD':
            continue

        cur_calib = db.getZeropoint(cluster, filter, mode = 'APER1')

        if cur_calib is None:
            continue


        if cur_calib.filter != filter:
            continue

        delta = findOffsets(cluster, filter)
        if delta is None:
            continue
        offsets[filter] = delta

    return offsets


def findOffsets(cluster, filter):


    cur_calib = db.getZeropoint(cluster, filter, mode = 'APER1')

    patcals = [ x for x in pdb.ZeropointEntry.selectBy(cluster = cluster, filter = filter,
                                             mangledSpecification = pdb.mangleSpecification({'mode' : 'APER1'}))]


    dougcals = [ x for x in pdb.ZeropointEntry.selectBy(cluster = cluster, filter = filter,
                                                        mangledSpecification = pdb.mangleSpecification({'mode' : 'aper'}))]

    if len(patcals) == 0:
        print cluster, filter, 'No Pat Entry Found'
        return None

    patnew = patcals[-1]
    
    patrefs = [x for x in patcals if x.time < datetime.datetime(2011, 06, 15)]
    if len(patrefs) == 0:
        print cluster, filter, 'No Pat Ref'
        patref = patnew
        patdelta = None
    else:
        patref = patrefs[-1]
        patdelta = patnew.zp - patref.zp

    
        
    if len(dougcals) == 0:
        print cluster, filter, 'No Doug Entry Found'
        dougdelta = None
    else:
        douglast = dougcals[-1]
        dougdelta = patref.zp - douglast.zp





    



#    print cluster, filter
#    print cur_calib.time, cur_calib.zp, '   ', patnew.time, patnew.zp, '   ', patref.time, patref.zp, '   ', douglast.time, douglast.zp
#    print patnew.zp - patref.zp, patref.zp - douglast.zp
#    print
#
    return patdelta, dougdelta



def offsetReport(allfilters, offsets):

    clusters = []

    for filter in allfilters:
        pylab.figure()
        print filter
        poffsets = []
        doffsets = []
        for key, items in offsets.iteritems():
            if filter in items:
                patoffset, dougoffset = items[filter]
                flag = False
                if patoffset is not None:
                    poffsets.append(patoffset)
                    if patoffset > 0.02:
                        if key[0] not in clusters:
                            clusters.append(key[0])
                if dougoffset is not None:
                    doffsets.append(dougoffset)
                    if patoffset is not None and patoffset - dougoffset > 0.02:
                        if key[0] not in clusters:
                            clusters.append(key[0])

        pylab.subplot(1,2,1)
        pylab.hist(poffsets, bins=51)
        pylab.subplot(1,2,2)
        pylab.hist(doffsets, bins=51)
        pylab.title(filter)

    return clusters
