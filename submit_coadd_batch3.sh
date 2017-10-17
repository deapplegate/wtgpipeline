#!/bin/bash -u
#################
# $Id: submit_coadd_batch3.sh,v 1.3 2010-07-20 19:46:21 dapple Exp $
#################
# Submits a cluster to the batch queue
#
# ./submit_coadd_batch.sh cluster "modes" filter1 filter 2 filter3

clustlist=cluster_cat_filters.dat

SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
logdir=${SUBARUDIR}/coaddlogs

cluster=$1
modes=$2

queue=xlong
if [ $# -ge 3 ]; then
    queue=$3
fi

filters=`grep ${cluster} ${clustlist} | awk '{for (i=3;i<=NF;i++) printf "%s ", $i}'`

echo "Cluster: ${cluster}"
echo "Filters: ${filters}"
echo "Modes:   ${modes}"
echo "Queue:   ${queue}"

for filter in ${filters}
do

modestring=`echo ${modes} | sed -e 's/ /./g'`

jobid=${cluster}.${filter}.${modestring}

bsub -q ${queue} -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} ${filter} "${modes}"

done
