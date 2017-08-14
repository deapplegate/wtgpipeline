#!/bin/bash -u

subaru=/nfs/slac/g/ki/ki05/anja/SUBARU

cluster=$1
filter=$2
queue=$3

logdir=${subaru}/coaddlogs
jobid=${cluster}.${filter}.regen

runs=`ls ${subaru}/${cluster} | grep "${filter}" | awk -F'_' '($3 !~ /CALIB/ && NF == 2){print}'`

for run in $runs; do

    bsub -K -oo ${logdir}/${jobid}.gunzip.log -eo ${logdir}/${jobid}.gunzip.err -q ${queue} gunzip ${subaru}/${cluster}/${run}/SCIENCE/diffmask/*.fits.gz 

    bsub -K -oo ${logdir}/${jobid}.log -eo ${logdir}/${jobid}.err -q ${queue} ./do_masking.sh ${cluster} ${run}

    if [ $? -ne 0 ]; then
	exit 2
    fi
    
    bsub -oo ${logdir}/${jobid}.gzip.log -eo ${logdir}/${jobid}.gzip.err -q ${queue} gzip ${subaru}/${cluster}/${run}/SCIENCE/diffmask/*.fits


done