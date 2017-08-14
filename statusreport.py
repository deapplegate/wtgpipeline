#!/usr/bin/env python

import datetime
import BonnLogger as bl
import datarobot as dr
import re

clusters = dr.Target.select()
clusters_inSample = dr.Target.selectBy(inSample = True)

runs = dr.Run.select().orderBy('night')
runs_inSample = []
for cluster in clusters_inSample:

    for run in cluster.runs:
        if run not in runs_inSample:
            runs_inSample.append(run)
runs_inSample.sort()

print "Number of Sample Runs: %d" % len(runs_inSample)


run_checks = ['Preprocess']
cluster_checks = ['Masking']

def bufferCheckpoints(checks, checkpoints, buffer):
    for check in checks:
        if check in [x.checkpoint.checkpoint \
                         for x in checkpoints]:
            buffer += "\tY"
        else:
            buffer += "\t-"
    return buffer

def bufferLastEntry(lastEntry, target_checkpoints, buffer):
    if lastEntry is None:
        buffer += '\tN/A'
    elif len(lastEntry) > 0:
        lastEntry  = lastEntry[0]
        if lastEntry not in target_checkpoints:
            if lastEntry.command is not None:
                buffer += '\t%s' % str(lastEntry.command.command)
    else:
        buffer += '\t?'
    return buffer

def getAllRunCheckpoints(run):
    checkpoints = bl.getCheckpoints(run.night, run.filter)
    checkpoints.extend(bl.getCheckpoints((run.nightObj - datetime.timedelta(1)).strftime('%Y-%m-%d'), run.filter))
    checkpoints.extend(bl.getCheckpoints((run.nightObj + datetime.timedelta(1)).strftime('%Y-%m-%d'), run.filter))
    return checkpoints

    

def reportRuns(title, targets, checks):

    print "Status Report for %s" % title
    print
    header = "Night\tFilter\t#Exp"
    for check in checks:
        header += "\t%s" % check
    header += "\tLast Cmd"
    print header
    print
    for run in targets:
        exposures = filter(lambda x: x.type == 'OBJECT', run.exposures)
        buffer = "%s\t%s\t%d" % (run.night, run.filter, len(exposures))

        target_checkpoints = getAllRunCheckpoints(run)
        buffer = bufferCheckpoints(checks, target_checkpoints, buffer)
        
        lastEntry = bl.getLastEntries(1, run.night, run.filter)
        buffer = bufferLastEntry(lastEntry, target_checkpoints, buffer)

        print buffer

        for cluster in run.targets:
            cluster_exposures = filter(lambda x: x.target == cluster, run.exposures)
            print "\t%s\t%d\t%d" % (cluster.name, len(cluster_exposures), 
                                    cluster_exposures[0].exptime)
                                    
        buffer = "\t"

def reportClusters(title, clusters, runchecks, clusterchecks):

    print "Status Report for %s" % title
    print
    header =  "Cluster\tNight\tFilter\t#Exp\tExptime"
    for check in runchecks:
        header += "\t%s" % check
    for check in clusterchecks:
        header += "\t%s" % check

    header += "\tLast Cmd"
    print header
    print
    for cluster in clusters:
        print "%s\t%s" % (cluster.name, cluster.type)
        buffer = "\t"
        runs = cluster.runs
        runs.sort()
        for run in runs:
            exposures = filter(lambda x: x.run == run, cluster.exposures)
            buffer += "%s\t%s\t%d\t%s\t" % (run.night, run.filter, len(exposures), exposures[0].exptime)

            run_checkpoints = getAllRunCheckpoints(run)

            buffer = bufferCheckpoints(runchecks, run_checkpoints, buffer)

            cluster_checkpoints = []
            for alias in cluster.aliases:
                cluster_checkpoints.extend(bl.getCheckpoints(alias.alias, run.filter))
            buffer = bufferCheckpoints(clusterchecks, cluster_checkpoints, buffer)

            print buffer
            buffer = "\t"
                
            
    

reportRuns('Runs In Sample', runs_inSample, run_checks)
#print
#print
#reportRuns('All Runs', runs, run_checks)
#print
#print
reportClusters('Clusters in Sample', clusters_inSample, run_checks, cluster_checks)
print
print
#reportClusters('All Clusters', clusters, run_checks, cluster_checks)
