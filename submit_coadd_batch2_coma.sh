#!/bin/bash
set -xv
#################
# $Id: submit_coadd_batch2_coma.sh,v 1.2 2010-03-31 19:13:59 anja Exp $
#################
# Submits a cluster to the batch queue
#
# ./submit_coadd_batch.sh cluster "modes" filter1 filter 2 filter3



SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
logdir=${SUBARUDIR}/coaddlogs

cluster=$1
modes=$2
filter=$3
ending=$4

queue=kipac-xocq
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


bsub -K -q ${queue} -J ${jobid} -oo ${logdir}/${jobid}.log -eo ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} ${filter} "${modes}" "${restriction_file}" ${ending}

