#!/bin/bash
set -xv
#################
# $Id: submit_coadd_batch2.sh,v 1.6 2010-04-16 23:30:54 dapple Exp $
#################
# Submits a cluster to the batch queue
#
# ./submit_coadd_batch.sh cluster "modes" filter1 filter 2 filter3



SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
logdir=${SUBARUDIR}/coaddlogs

cluster=$1
modes=$2
filter=$3
ending=$4

queue=xlong
if [ $# -ge 5 ]; then
    queue=$5
fi

keep_cats=$6

restrictions=`grep "${cluster}" ${SUBARUDIR}/lensing.bands | grep ${filter} | awk '{print $3}'`


modestring=`echo ${modes} | sed -e 's/ /./g'`


jobid=${cluster}.${filter}.${modestring}

if [ -n "${restrictions}" ]; then
    restriction_file=${jobid}.restrictions
    echo "${restrictions}" > ${restriction_file}
else
    restriction_file=''
fi


bsub -K -q ${queue} -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} ${filter} "${modes}" "${restriction_file}" ${ending}

