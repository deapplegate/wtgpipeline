#!/bin/bash -u

#subaru=/nfs/slac/g/ki/ki05/anja/SUBARU/
subaru=/nfs/slac/g/ki/ki18/anja/SUBARU/

cluster=$1
filter=$2
ext=$3

runs=`\ls -d ${subaru}/${cluster}/*/ | grep "${filter}" | awk -F'_' '($3 !~ /CALIB/ && NF == 2){print}'`

for run in $runs; do

    for file in `\ls ${run}/SCIENCE/*${ext}.fits`; do

	base=`basename ${file} ${ext}.fits`
	cp ${subaru}/${cluster}/${filter}/SCIENCE/${base}${ext}R.fits ${run}/SCIENCE/
	cp ${subaru}/${cluster}/${filter}/WEIGHTS/${base}${ext}R.weight.fits ${run}/WEIGHTS/
	cp ${subaru}/${cluster}/${filter}/WEIGHTS/${base}${ext}R.flag.fits ${run}/WEIGHTS/

    done

done
