#!/bin/bash

subaru=/gpfs/slac/kipac/fs1/u/awright/SUBARU
logdir=${subaru}/iclog
cluster=$1
filter=$2
queue=$3


export subdir=${subaru}/
export bonn=`pwd`/

runs=`ls ${subaru}/${cluster} | grep "${filter}" | awk -F'_' '($3 !~ /CALIB/ && NF == 2){print}'`

for run in ${runs}; do

    echo $run

    rext=''
    use_rext=`ls ${subaru}/${cluster}/${run}/SCIENCE/*R.fits | wc -l`
    
    if [ "${use_rext}" != "0" ]; then
	rext=yes
    fi

    filter=`echo $run | awk -F'_' '{print $1}'`
    night=`echo $run | awk -F'_' '{print $2}'`
    pprun=${night}_${filter}

    jobid=${cluster}.${pprun}.ic
    echo $jobid

    bsub -K -q ${queue} -J ${jobid} -oo ${logdir}/${jobid}.log -eo ${logdir}/${jobid}.err ./ic_wrapper.py $cluster $filter $pprun ${rext}

    if [ "$?" -gt 0 ]; then
	echo "Failure with ic_wrapper.py"
	exit 1
    fi

done


./link_flags.sh ${cluster} ${filter}


