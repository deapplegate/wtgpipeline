if 'np' not in dir():
    import numpy as np

if 'pdb' not in dir() or 'db' not in dir():
    import photometry_db as pdb

    db = pdb.Photometry_db()

#################################

def calcPatDeltas(filter):

    zps = pdb.SlrZP.selectBy(user='pkelly', filter=filter)

    bycluster = {}
    for zp in zps:                            
        if zp.cluster not in bycluster:
            bycluster[zp.cluster] = []
        bycluster[zp.cluster].append(zp)

    multipleCalibs = {}
    for cluster, zps in bycluster.iteritems():
        if len(zps) > 1:
            multipleCalibs[cluster] = zps

    deltas = []
    for cluster, zps in multipleCalibs.iteritems():
        oldest = min(zps)
        if oldest.time > datetime.datetime(2011, 04, 01):
            continue
        old = max([zp for zp in zps if zp.time < datetime.datetime(2011, 04, 01)])
        young = max(zps)
        deltas.append(young.zp - old.zp)

    return deltas

####################################

def calcWillPatDeltas(filter):



    def findMaxZps(zps):
        bycluster = {}
        for zp in zps:                            
            if zp.cluster not in bycluster:
                bycluster[zp.cluster] = zp
            else:
                bycluster[zp.cluster] = max(zp, bycluster[zp.cluster])
        return bycluster

    pat_zps = findMaxZps(pdb.SlrZP.selectBy(user='pkelly', filter=filter))

    will_zps = findMaxZps(pdb.SlrZP.selectBy(user='dapple', filter=filter))

    deltas = []
    for cluster in pat_zps.keys():
        if cluster not in will_zps:
            continue
        deltas.append(pat_zps[cluster].zp - will_zps[cluster].zp)

    return deltas
        
    
    

#####################################


def detContents(**conditions):

    clusters = {}
    filters = {}
    for x in pdb.SlrZP.selectBy(**conditions):
        if x.filter not in filters:
            filters[x.filter] = None
        if x.cluster not in clusters:
            clusters[x.cluster] = None
    return filters.keys(), clusters.keys()

if 'filters' not in dir() or 'clusters' not in dir():
    filters, clusters = detContents()

########################################

def findSignificantOffset(cluster):


    filters, clusters = detContents(cluster=cluster)
    
    deltas = {}
    for filter in filters:

        zps = pdb.SlrZP.selectBy(cluster = cluster, filter=filter)

        young = max(zps)
        old_zps = [zp for zp in zps if zp.time < datetime.datetime(2011, 04, 15)]
        if len(old_zps) == 0:
            print 'No Old Calib for %s %s' % (cluster, filter)
            continue
        old = max(old_zps)
        delta = young.zp - old.zp
        deltas[filter] = delta
    

    if (np.abs(np.array([deltas[x] for x in deltas.keys()])) > 0.01).any():
        return deltas
    else:
        return None

    
    
