#!/bin/bash

subaru=/nfs/slac/g/ki/ki05/anja/SUBARU/

cluster=$1

runs=`ls ${subaru}/${cluster} | awk -F'_' '($3 !~ /CALIB/ && NF == 2){print}'`

for run in ${runs}; do

    filter=`echo ${run} | awk -F'_' '{print $1}'`
    if [ "${filter}" = "W-J-B" ] || [ "${filter}" = "W-J-V" ] || [ "${filter}" = "W-C-RC" ]; then
	ending=OCFS
    elif [ "${filter}" = "W-C-IC" ] || [ "${filter}" = "W-S-I+" ] || [ "${filter}" = "W-S-Z+" ]; then
	ending=OCFSF
    else
	continue
    fi

    rm ${subaru}/${cluster}/${run}/WEIGHTS/*${ending}.weight.fits


done