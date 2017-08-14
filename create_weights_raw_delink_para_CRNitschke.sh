#!/bin/bash -xv
#adam-does# this code executes the CRNitschke cosmic finder on all of the images!
#adam-call# ./parallel_manager.sh create_weights_raw_delink_para_CRNitschke.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS ${filter}
#adam-former-names# create_weights_raw_delink_para_10_3_cr.sh
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

#adam# this is needed for the 10_2 config
#if [ $# -eq 6 ]; then
#   MASK=$5
#fi

#you MUST run create_weights_raw_delink_para_CRNitschke_setup.sh FIRST!!!

for CHIP in ${!#}
do
  ${P_FIND} $1/$2/ -maxdepth 1 -name \*_${CHIP}$3.fits \
            -print > ${TEMPDIR}/crw_images_$$

  FILE=`${P_GAWK} '(NR==1) {print $0}' ${TEMPDIR}/crw_images_$$`
  
  cat ${TEMPDIR}/crw_images_$$ |\
  {
    while read file
    do
      BASE=`basename ${file} $3.fits`
      #adam# START MY STUFF!
      #adam# determine the seeing and get the optimal sextractor thresholds
      rms_fwhm_ft_dt=( `grep $BASE CRNitschke_final_${cluster}_${run}_${filter}.txt | awk '{print $3, $4, $5, $6}'`)
      rms=${rms_fwhm_ft_dt[0]}
      fwhm=${rms_fwhm_ft_dt[1]}
      ft=${rms_fwhm_ft_dt[2]}
      dt=${rms_fwhm_ft_dt[3]}
      #adam# run sextractor to get the cosmics
      ${P_SEX} ${file}   -c /u/ki/awright/thiswork/eyes/CRNitschke/config-sex.10_3_cr \
			 -SEEING_FWHM ${fwhm} \
			 -FILTER_NAME /u/ki/awright/thiswork/eyes/CRNitschke/retina-eye.10_3_cr.ret \
			 -FILTER_THRESH ${ft} \
			 -DETECT_THRESH ${dt} \
			 -ANALYSIS_THRESH ${dt} \
			 -DETECT_MINAREA 1 \
			 -CHECKIMAGE_TYPE SEGMENTATION,FILTERED \
			 -CHECKIMAGE_NAME /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/data_filter_results/results_2.2/data_SCIENCE_cosmics/SEGMENTATION_CRNitschke.${BASE}.fits,/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/data_filter_results/results_2.2/data_SCIENCE_cosmics/FILTERED_CRNitschke.${BASE}.fits \
			-CATALOG_NAME /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/data_filter_results/results_2.2/data_SCIENCE_cosmics/CATALOG_CRNitschke.${BASE}.cat
      #adam# now put in the FT400 stuff in order to pick up extra cosmics
      ft400=$(echo "400.0 / $rms" |bc -l)
      #adam# run sextractor to get the cosmics
      ${P_SEX} ${file}   -c /u/ki/awright/thiswork/eyes/CRNitschke/config-sex.10_3_cr \
                         -SEEING_FWHM ${fwhm} \
                         -FILTER_NAME /u/ki/awright/thiswork/eyes/CRNitschke/retina-eye.10_3_cr.ret \
                         -FILTER_THRESH ${ft400} \
                         -DETECT_THRESH ${dt} \
                         -ANALYSIS_THRESH ${dt} \
                         -DETECT_MINAREA 1 \
                         -CHECKIMAGE_TYPE SEGMENTATION,FILTERED \
                         -CHECKIMAGE_NAME /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/data_filter_results/results_2.2/data_SCIENCE_cosmics/SEGMENTATION_FT400_CRNitschke.${BASE}.fits,/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/data_filter_results/results_2.2/data_SCIENCE_cosmics/FILTERED_FT400_CRNitschke.${BASE}.fits \
                        -CATALOG_NAME /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/data_filter_results/results_2.2/data_SCIENCE_cosmics/CATALOG_FT400_CRNitschke.${BASE}.cat
      #adam# put keywords in the headers of these files:
      /u/ki/awright/InstallingSoftware/pythons/header_key_add.py /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/data_filter_results/results_2.2/data_SCIENCE_cosmics/FILTERED_FT400_CRNitschke.${BASE}.fits CRN_FT=${ft400} CRN_DT=${dt} CRN_DMA=1 MYSEEING=${fwhm} MYRMS=${rms}
      /u/ki/awright/InstallingSoftware/pythons/header_key_add.py /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/data_filter_results/results_2.2/data_SCIENCE_cosmics/SEGMENTATION_FT400_CRNitschke.${BASE}.fits CRN_FT=${ft400} CRN_DT=${dt} CRN_DMA=1 MYSEEING=${fwhm} MYRMS=${rms}
      /u/ki/awright/InstallingSoftware/pythons/header_key_add.py /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/data_filter_results/results_2.2/data_SCIENCE_cosmics/FILTERED_CRNitschke.${BASE}.fits CRN_FT=${ft} CRN_DT=${dt} CRN_DMA=1 MYSEEING=${fwhm} MYRMS=${rms}
      /u/ki/awright/InstallingSoftware/pythons/header_key_add.py /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/data_filter_results/results_2.2/data_SCIENCE_cosmics/SEGMENTATION_CRNitschke.${BASE}.fits CRN_FT=${ft} CRN_DT=${dt} CRN_DMA=1 MYSEEING=${fwhm} MYRMS=${rms}
      /u/ki/awright/InstallingSoftware/pythons/header_key_add.py ${file} MYSEEING=${fwhm}
      #adam#now get the stars:this will make /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/data_filter_results/results_2.2/data_SCIENCE_stars/SEGMENTATION_stars_${BASE}OCF.fits and /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/data_filter_results/results_2.2/data_SCIENCE_stars/CATALOG_stars_${BASE}OCF.cat
      /u/ki/awright/thiswork/eyes/CRNitschke/stars2block.py ${file}
      #adam# now run the blocked_blender!
      /u/ki/awright/thiswork/eyes/CRNitschke/blocked_blender_withplots.2.2.py ${file}
      #adam# END MY STUFF!
      # Expand the cosmic ray masking:
      cp /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/data_filter_results/results_2.2/data_SCIENCE_cosmics/SEGMENTATION_BB_CRNitschke.${BASE}.fits ${TEMPDIR}/cosmic_${CHIP}_$$.fits
      sfdir/expand_cosmics_mask ${TEMPDIR}/cosmic_${CHIP}_$$.fits  ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits
      mv ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits  ${TEMPDIR}/cosmic_${CHIP}_$$.fits 
      # create ww config file on the fly
      #SHNT:check and make sure cosmic flags (#1) are in the right spots by checking the ${WEIGHTSDIR}/${BASE}$3.flag.fits file
      if [ -r "$1/$2/diffmask/${BASE}$3.sf.fits" ]; then
	  echo "WEIGHT_NAMES ${WEIGHTSDIR}/globalweight_${CHIP}.fits,${TEMPDIR}/cosmic_${CHIP}_$$.fits,${file},/$1/$2/diffmask/${BASE}$3.sf.fits" > ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_MIN -1e9,-1e9,-${SATLEVEL},0.1"       >> ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_MAX 1e9,0.1,${SATLEVEL},1"       >> ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_OUTFLAGS 0,1,2,4"       >> ${TEMPDIR}/${BASE}.ww_$$
      else
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
      rm ${TEMPDIR}/${BASE}.ww_$$

      # clean up temporary files
      if [ -f ${TEMPDIR}/cosmic_${CHIP}_$$.fits ]; then
          rm ${TEMPDIR}/cosmic_${CHIP}_$$.fits
      fi
      
      if [ -f ${TEMPDIR}/cosmic.cat_$$ ]; then
          rm ${TEMPDIR}/cosmic.cat_$$
      fi

    done
  }
  test -f ${TEMPDIR}/crw_images_$$ && rm  ${TEMPDIR}/crw_images_$$
done


log_status $?
