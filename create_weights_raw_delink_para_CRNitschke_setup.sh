#!/bin/bash
set -xv
#adam-chain#CRN! Starts the CRNitschke cosmic ray masker process off by getting seeing values (chip-median seeing value for each 10CCD total exposure) and writting value to CRNitschke_final_${cluster}_${run}_${filter}.txt
#  which is the final seeing values used by create_weights_raw_delink_para_CRNitschke.sh.
#  run this code like this `./create_weights_raw_delink_para_CRNitschke_setup.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS ${filter}`
#  do not use parallel manager with this code!
#adam-does# this code executes the beginning portions of the CRNitschke cosmic finder on all of the images, but doesn't run the blocked blender!
#adam-call_example# ./create_weights_raw_delink_para_CRNitschke_setup.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS ${filter}

#. BonnLogger.sh
#. log_start
# $Id: create_weights_raw_delink_para.sh,v 1.9 2010-02-18 02:50:18 dapple Exp $

# $1: main directory
# $2: science dir.
# $3: image extension (ext) on ..._iext.fits (i is the chip number)
#     note that spikefinder images have an additional .sf
# $4: weight directory
# $5: Filter to use for cosmic ray detection (OPTIONAL)
# ${!#}: chips to be processed

. ${INSTRUMENT:?}.ini > /tmp/out.log 2>&1
REDDIR=`pwd`
export WEIGHTSDIR=${1}/${4}

#adam# this actually does match the value for the 10_3 config
SATLEVEL=${SATURATION:-30000}

#adam# make file if its not there yet
if [ -e CRNitschke_${cluster}_${run}_${filter}.txt ]
then rm -f CRNitschke_${cluster}_${run}_${filter}.txt
fi

touch CRNitschke_${cluster}_${run}_${filter}.txt

CHIP=3
${P_FIND} $1/$2/ -maxdepth 1 -name \*_${CHIP}$3.fits \
        -print > ${TEMPDIR}/crw_images_$$

FILE=`${P_GAWK} '(NR==1) {print $0}' ${TEMPDIR}/crw_images_$$`

cat ${TEMPDIR}/crw_images_$$ |\
{
  while read file
  do
    echo ${file}
    BASE=`basename ${file} $3.fits`
    #adam# START MY STUFF!
    #adam# get_sextract_thresholds.py to determine the seeing and get the optimal sextractor thresholds
    /u/ki/awright/thiswork/eyes/CRNitschke/get_sextract_thresholds.py ${file} ${TEMPDIR}/crw_gst_$$.txt
    cat CRNitschke_${cluster}_${run}_${filter}.txt ${TEMPDIR}/crw_gst_$$.txt >> CRNitschke_${cluster}_${run}_${filter}.tmp.txt
    mv CRNitschke_${cluster}_${run}_${filter}.tmp.txt CRNitschke_${cluster}_${run}_${filter}.txt
  done
}

sort CRNitschke_${cluster}_${run}_${filter}.txt | uniq | column -t > CRNitschke_final_${cluster}_${run}_${filter}.txt
##rm -f CRNitschke_${cluster}_${run}_${filter}.txt
