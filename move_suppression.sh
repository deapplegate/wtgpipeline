#!/bin/bash -u

#SUBARUDIR=/nfs/slac/g/ki/ki05/anja/SUBARU/
#SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU/

cluster=$1
filter=$2
ext=$3

runs=`\ls -d ${SUBARUDIR}/${cluster}/*/ | grep "${filter}" | awk -F'_' '($3 !~ /CALIB/ && NF == 2){print}'`

for run in $runs; do

    for file in `\ls ${run}/SCIENCE/*${ext}.fits`; do

	base=`basename ${file} ${ext}.fits`
	cp ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${base}${ext}R.fits ${run}/SCIENCE/
	cp ${SUBARUDIR}/${cluster}/${filter}/WEIGHTS/${base}${ext}R.weight.fits ${run}/WEIGHTS/
	cp ${SUBARUDIR}/${cluster}/${filter}/WEIGHTS/${base}${ext}R.flag.fits ${run}/WEIGHTS/

    done

done
