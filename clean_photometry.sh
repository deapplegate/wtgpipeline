#!/bin/bash
set -xv


for job in photoqueue/submitted.*.extract; do 
    cluster=`echo $job | awk -F'.' '{print $3}'` 
    filter=`echo $job | awk -F'.' '{print $4}'` 
    mode=`echo $job | awk -F'.' '{print $5}'` 
    stat=`./check_extract_stat.sh $cluster $filter $mode` 
    if [ "$stat" == "OK" ]; then 
	pushd ~/subaru/$cluster/PHOTOMETRY_${filter}_${mode} 
	rm -f */unstacked/*.fits 
	popd 
    fi 
done