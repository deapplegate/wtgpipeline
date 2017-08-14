#!/bin/bash -u

subaru=/nfs/slac/g/ki/ki05/anja/SUBARU

cluster=$1
filter=$2

logdir=${subaru}/coaddlogs
jobid=${cluster}.${filter}.regen

runs=`ls ${subaru}/${cluster} | grep "${filter}" | awk -F'_' '($3 !~ /CALIB/ && NF == 2){print}'`
echo ${runs}

for run in $runs; do
    echo ${run}

    bsub -K -o ${logdir}/${jobid}.gunzip.log -e ${logdir}/${jobid}.gunzip.err -q kipac-xocq gunzip ${subaru}/${cluster}/${run}/SCIENCE/diffmask/*.fits.gz

    bsub -K -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err -q kipac-xocq ./do_masking.sh ${cluster} ${run}
    if [ $? -ne 0 ]; then
	exit 2
    fi
    

    bsub -K -oo ${logdir}/${jobid}.gzip.log -eo ${logdir}/${jobid}.gzip.err -q kipac-xocq gzip ${subaru}/${cluster}/${run}/SCIENCE/diffmask/*.fits

    echo "${run} is finished"


done