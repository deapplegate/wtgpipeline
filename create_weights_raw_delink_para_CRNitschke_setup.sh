#!/bin/bash -xv
#adam-does# this code executes the beginning portions of the CRNitschke cosmic finder on all of the images, but doesn't run the blocked blender!
#adam-call# ./parallel_manager.sh create_weights_raw_delink_para_CRNitschke_NoBB.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS ${filter}
#adam-former-names# create_weights_raw_delink_para_10_3_cr_MAY26th.sh, create_weights_raw_delink_para_10_3_cr_NoBB.sh

. BonnLogger.sh
. log_start
# the script creates weights for science frames.
# It assumes the global weight images in the WEIGHT
# directory and the reg files in the sciencedir/reg
# directory.
#
# $Id: create_weights_raw_delink_para.sh,v 1.9 2010-02-18 02:50:18 dapple Exp $

# $1: main directory
# $2: science dir.
# $3: image extension (ext) on ..._iext.fits (i is the chip number)
#     note that spikefinder images have an additional .sf
# $4: weight directory
# $5: Filter to use for cosmic ray detection (OPTIONAL)
# ${!#}: chips to be processed

. ${INSTRUMENT:?}.ini
REDDIR=`pwd`
export WEIGHTSDIR=${1}/${4}

#adam# this actually does match the value for the 10_3 config
SATLEVEL=${SATURATION:-30000}

#adam# make file if its not there yet
touch CRNitschke_${cluster}_${run}_${filter}.txt

for CHIP in ${!#}
do
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
      out_rms_fwhm_dt_ft=( `/u/ki/awright/thiswork/eyes/CRNitschke/get_sextract_thresholds.py ${file}`)
      out=${out_rms_fwhm_dt_ft[0]}
      rms=${out_rms_fwhm_dt_ft[1]}
      fwhm=${out_rms_fwhm_dt_ft[2]}
      dt=${out_rms_fwhm_dt_ft[3]}
      ft=${out_rms_fwhm_dt_ft[4]}
      echo "${BASE} ${fwhm} ${rms}" >> CRNitschke_${cluster}_${run}_${filter}.txt
    done
  }
  echo ${CHIP}
done

log_status $?
