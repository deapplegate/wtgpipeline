#!/bin/bash
set -xv
#adam-call_example# ./parallel_manager.sh create_weights_raw_delink_para_CRNitschke_3sec_and_30sec.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B_2015-12-15/ SCIENCE OCF WEIGHTS
#adam-chain#CRN! Runs the CRNitschke cosmic ray masker. first run create_weights_raw_delink_para_CRNitschke_setup.sh, then run this code like this `./parallel_manager.sh create_weights_raw_delink_para_CRNitschke.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS ${filter}`
#adam-does# this code executes the CRNitschke cosmic finder on all of the images!
#adam-call_example# ./parallel_manager.sh create_weights_raw_delink_para_CRNitschke.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS ${filter}
#adam-predecessor# create_weights_raw_delink_para_10_3_cr.sh

#. BonnLogger.sh
#. log_start

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

INSTRUMENT=SUBARU
. ${INSTRUMENT:?}.ini > /tmp/subaru_ini_output.log 2>&1
REDDIR=`pwd`
export WEIGHTSDIR=${1}/${4}

#adam# this actually does match the value for the 10_3 config
SATLEVEL=${SATURATION:-30000}

#adam# this is needed for the 10_2 config
#if [ $# -eq 6 ]; then
#   MASK=$5
#fi

#you MUST run create_weights_raw_delink_para_CRNitschke_setup.sh FIRST!!!

echo "START: create_weights_raw_delink_para_CRNitschke.sh $1 $2 $3 $4 $5 ${!#}"
for CHIP in ${!#}
do
  cat ${1}/3sec.log | grep "_${CHIP}$3.fits" > ${TEMPDIR}/crw_images_$$
  cp ${1}/3sec.log ${1}/3sec.done

  FILE=`${P_GAWK} '(NR==1) {print $0}' ${TEMPDIR}/crw_images_$$`
  
  cat ${TEMPDIR}/crw_images_$$ |\
  {
    while read file
    do
      BASE=`basename ${file} $3.fits`
      if [ -f "${WEIGHTSDIR}/${BASE}$3.weight.fits" ] ;then
              #echo "#adam-look# SKIPPING ${WEIGHTSDIR}/${BASE}$3.weight.fits"
              #ls -lrth ${WEIGHTSDIR}/${BASE}$3.weight.fits
              #echo "#adam-look# because it's already there!"
	      #continue
	      rm ${WEIGHTSDIR}/${BASE}$3.weight.fits
      fi
      #adam# START MY STUFF!
      ft=15
      dt=130
      fwhm=.7
      #adam# determine the seeing and get the optimal sextractor thresholds
      ${P_SEX} ${file}  -c /u/ki/awright/CRNitschke/config-sex.10_3_cr \
			-SEEING_FWHM ${fwhm} \
			-FILTER_NAME /u/ki/awright/CRNitschke/retina-eye.10_3_cr.ret \
			-FILTER_THRESH ${ft} \
			-DETECT_THRESH ${dt} \
			-ANALYSIS_THRESH ${dt} \
			-DETECT_MINAREA 1 \
			-CHECKIMAGE_TYPE SEGMENTATION \
			-CHECKIMAGE_NAME ${TEMPDIR}/cosmic_${CHIP}_$$.${BASE}.fits
      exit_stat=$? 
      if [ "${exit_stat}" -gt "0" ]; then
          echo "adam-look: create_weights_raw_delink_para_CRNitschke.sh failed for file=${file}"
	  continue
      fi 
      #adam# now put in the FT400 stuff in order to pick up extra cosmics
      sfdir/expand_cosmics_mask ${TEMPDIR}/cosmic_${CHIP}_$$.${BASE}.fits  ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits
      exit_stat=$? 
      if [ "${exit_stat}" -gt "0" ]; then
          echo "adam-look: create_weights_raw_delink_para_CRNitschke.sh failed for file=${file}"
	  continue
      fi 
      mv ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits  ${TEMPDIR}/cosmic_${CHIP}_$$.fits 
      # create ww config file on the fly

      #CRN-files#
      #       17.)${SUBARUDIR}/${cluster}/${filter}_${run}/WEIGHTS/${BASE}${ending}.flag.fits
      #       check with: ls -lrth ${SUBARUDIR}/${cluster}/${filter}_${run}/WEIGHTS/*${ending}.flag.fits > CRN-weights_last_run.log #not necessary
      if [ -r "$1/$2/diffmask/${BASE}$3.sf.fits" ]; then
	  echo "WEIGHT_NAMES ${WEIGHTSDIR}/globalweight_${CHIP}.fits,${TEMPDIR}/cosmic_${CHIP}_$$.fits,${file},/$1/$2/diffmask/${BASE}$3.sf.fits" > ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_MIN -1e9,-1e9,-${SATLEVEL},0.1"       >> ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_MAX 1e9,0.1,${SATLEVEL},1"       >> ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_OUTFLAGS 0,1,2,4"       >> ${TEMPDIR}/${BASE}.ww_$$
      else
	  echo "adam-look: no sf.fits file: $1/$2/diffmask/${BASE}$3.sf.fits"
	  continue
	  echo "WEIGHT_NAMES ${WEIGHTSDIR}/globalweight_${CHIP}.fits,${TEMPDIR}/cosmic_${CHIP}_$$.fits,${file}" > ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_MIN -1e9,-1e9,-${SATLEVEL}"           >> ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_MAX 1e9,0.1,${SATLEVEL}"         >> ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_OUTFLAGS 0,1,2"          >> ${TEMPDIR}/${BASE}.ww_$$
      fi
      #
      echo "FLAG_NAMES ${WEIGHTSDIR}/globalflag_${CHIP}.fits"                        >> ${TEMPDIR}/${BASE}.ww_$$
      echo 'FLAG_MASKS "0x42"'                        >> ${TEMPDIR}/${BASE}.ww_$$
      echo 'FLAG_WMASKS "0x42"'                       >> ${TEMPDIR}/${BASE}.ww_$$
      echo 'FLAG_OUTFLAGS "32,64"'                     >> ${TEMPDIR}/${BASE}.ww_$$
      #
      if [ -s "/$1/$2/reg/${BASE}.reg" ]; then
        echo "POLY_NAMES /$1/$2/reg/${BASE}.reg"  >> ${TEMPDIR}/${BASE}.ww_$$
        echo "POLY_OUTFLAGS 256"                    >> ${TEMPDIR}/${BASE}.ww_$$
      else
        echo 'POLY_NAMES ""'                      >> ${TEMPDIR}/${BASE}.ww_$$
        echo 'POLY_OUTFLAGS ""'                   >> ${TEMPDIR}/${BASE}.ww_$$
      fi
      #
      echo "OUTWEIGHT_NAME ${WEIGHTSDIR}/${BASE}$3.weight.fits"  >> ${TEMPDIR}/${BASE}.ww_$$
      echo "OUTFLAG_NAME ${WEIGHTSDIR}/${BASE}$3.flag.fits"  >> ${TEMPDIR}/${BASE}.ww_$$
      
      # then run weightwatcher
      ${P_WW} -c ${TEMPDIR}/${BASE}.ww_$$
      exit_stat=$? 
      if [ "${exit_stat}" -gt "0" ]; then
          echo "adam-look: create_weights_raw_delink_para_CRNitschke.sh failed for file=${file}"
	  continue
      fi 
      rm -f ${TEMPDIR}/${BASE}.ww_$$

      # clean up temporary files
      if [ -f ${TEMPDIR}/cosmic_${CHIP}_$$.fits ]; then
          rm -f ${TEMPDIR}/cosmic_${CHIP}_$$.fits
      fi
      
      if [ -f ${TEMPDIR}/cosmic.cat_$$ ]; then
          rm -f ${TEMPDIR}/cosmic.cat_$$
      fi

    done
  }
  test -f ${TEMPDIR}/crw_images_$$ && rm -f  ${TEMPDIR}/crw_images_$$
  echo "adam-look: ds9e ${file} ${TEMPDIR}/cosmic_${CHIP}_$$.${BASE}.fits "
done


#log_status $?
