#!/bin/bash -u

subaru=/nfs/slac/g/ki/ki05/anja/SUBARU/

cluster=$1
filter=$2
ext=$3

runs=`ls ${subaru}/${cluster} | grep "${filter}" | awk -F'_' '($3 !~ /CALIB/ && NF == 2){print}'`

for run in $runs; do

    for file in ${subaru}/${cluster}/${run}/SCIENCE/*${ext}.fits; do

	base=`basename ${file} ${ext}.fits`
	mv ${subaru}/${cluster}/${filter}/SCIENCE/${base}${ext}R.fits ${subaru}/${cluster}/${run}/SCIENCE/
	mv ${subaru}/${cluster}/${filter}/WEIGHTS/${base}${ext}R.weight.fits ${subaru}/${cluster}/${run}/WEIGHTS/
	mv ${subaru}/${cluster}/${filter}/WEIGHTS/${base}${ext}R.flag.fits ${subaru}/${cluster}/${run}/WEIGHTS/

    done

done