#!/bin/bash -u

subaru=/nfs/slac/g/ki/ki05/anja/SUBARU
logdir=${subaru}/iclog
cluster=$1
filter=$2


runs=`ls ${subaru}/${cluster} | grep "${filter}" | awk -F'_' '($3 !~ /CALIB/ && NF == 2){print}'`

for run in ${runs}; do

    rm ${subaru}/${cluster}/${run}/SCIENCE/*R.fits
    rm ${subaru}/${cluster}/${run}/WEIGHTS/*R.weight.fits
    

done