#!/bin/bash

#adam-does# give it a pprun and it sees if there are a consistent number of files there
#adam-example# ./count_for_consistency.sh 2010-11-04_W-S-Z+

pprun=$1
SUBARUDIR="/nfs/slac/g/ki/ki18/anja/SUBARU/"
dir=${SUBARUDIR}/${pprun}/
echo ""
echo "######## ${pprun} ########"

for chip in 1 2 3 4 5 6 7 8 9 10
do
	splitNum=`ls -1 ${dir}/SCIENCE/SUPA*_${chip}.fits | wc -l`
	OCFNum=`ls -1 ${dir}/SCIENCE/SUPA*_${chip}OCF.fits | wc -l`
	OCFNNum=`ls -1 ${dir}/SCIENCE_norm/SUPA*_${chip}OCFN.fits | wc -l`
	echo "chip=${chip} (none OCF OCFN): $splitNum $OCFNum $OCFNNum"
done

echo "total number consistent too if these are the same:"
ls -1 ${dir}/SCIENCE/ORIGINALS/SUPA*.fits | wc -l
ls -1 ${dir}/SCIENCE_norm/BINNED/SUPA*.fits | wc -l
