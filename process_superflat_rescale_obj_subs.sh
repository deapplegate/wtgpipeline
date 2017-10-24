#!/bin/bash
set -xv

. ~/wtgpipeline/progs.ini > /tmp/progs.out 2>&1
. ~/wtgpipeline/SUBARU.ini > /tmp/SUBARU.out 2>&1

################
# Takes sub images, and creates superflats
#$1 Run directory
#$2 SCIENCE directory

if [ ! -d $1/$2/SUB_IMAGES ]; then
    exit 1;
fi
SUBDIR=$1/$2/SUB_IMAGES

files=`\ls ${SUBDIR}/SUPA*_10OCF_sub.fits`
for fl in $files
do
	fname=`basename ${fl} _10OCF_sub.fits`
	imstats -d 4 ${SUBDIR}/${fname}_{1,2,3,4,5,6,7,8,9,10}OCF_sub.fits > SUBDIR_$$
	sed -i.old '/^#/d'  SUBDIR_$$

	NORM=`${P_GAWK} 'BEGIN {max=0} ($1!="#") {if ($2>max) max=$2} END {print max}' SUBDIR_$$`
	for CHIP in 1 2 3 4 5 6 7 8 9 10
	do
		mv ${SUBDIR}/${fname}_${CHIP}OCF_sub.fits ${SUBDIR}/${fname}_${CHIP}OCF_sub1.fits

		ic '%1 '${NORM}' /' ${SUBDIR}/${fname}_${CHIP}OCF_sub1.fits > ${SUBDIR}/${fname}_${CHIP}OCF_sub.fits
	done
done
