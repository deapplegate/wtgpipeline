#!/bin/bash -u
#################
# $Id: submit_coadd_batch.sh,v 1.10 2010-07-20 19:46:21 dapple Exp $
#################
# Submits a cluster to the batch queue
#
# ./submit_coadd_batch.sh cluster "modes" filter1 filter 2 filter3



SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
logdir=${SUBARUDIR}/coaddlogs

queue=$1
cluster=$2
modes=$3

modestring=`echo ${modes} | sed -e 's/ /./g'`

i=4
nfilters=$#
while [ $i -le $nfilters ]; do
    
    filter=${!i}
    echo $filter
    


    jobid=${cluster}.${filter}.${modestring}
    
    bsub -q ${queue} -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} ${filter} "${modes}"


    i=$(($i+1))
    
done