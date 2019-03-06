#!/bin/bash
set -xv
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
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

# set cosmic ray mask to use:
MASK=${CONF}/cosmic.ret.sex

export WEIGHTSDIR=${1}/${4}

#adam# this actually does match the value for the 10_3 config
SATLEVEL=${SATURATION:-30000}

if [ $# -eq 6 ]; then
   MASK=$5
fi

for CHIP in ${!#}
do
  ${P_FIND} $1/$2/ -maxdepth 1 -name \*_${CHIP}$3.fits \
            -print > ${TEMPDIR}/crw_images_$$

  FILE=`${P_GAWK} '(NR==1) {print $0}' ${TEMPDIR}/crw_images_$$`


#  fi
  
  cat ${TEMPDIR}/crw_images_$$ |\
  {
    while read file
    do
      BASE=`basename ${file} $3.fits`

      # first run sextractor to determine the seeing:

      rms_fwhm_dt_ft=( `grep $BASE CRNitschke_final_Zw2089_2007-02-13_W-S-I+.txt | awk '{print $2, $3, $4, $5}'`)
      rms=${rms_fwhm_dt_ft[0]}
      fwhm=${rms_fwhm_dt_ft[1]}
      dt=${rms_fwhm_dt_ft[2]}
      ft=${rms_fwhm_dt_ft[3]}
      undersampl=`${P_GAWK} 'BEGIN{if('${fwhm}'<0.5) print 1; else print 0}'`

      if [ ${undersampl} -eq 1 ]; then
	  conffile="${CONF}/cosmic.conf.sex -DETECT_THRESH 10"
      else
	  conffile=${REDDIR}/cosmic.conf.sex
      fi

      #adam-SHNT# I believe this is where EyE should go
      # first run sextractor to identify cosmic rays:

      ${P_SEX} ${file} -c ${conffile} -CHECKIMAGE_NAME \
                          ${TEMPDIR}/cosmic_${CHIP}_$$.fits \
                          -FILTER_NAME ${MASK} \
                          -CATALOG_NAME ${TEMPDIR}/cosmic.cat_$$ \
                          -SEEING_FWHM ${fwhm}


      # Expand the cosmc ray making:
      #adam# expand_cosmics_mask only extends by one pixel (not good enough), this doesn't help the fact that we're actually missing some things entirely
      sfdir/expand_cosmics_mask ${TEMPDIR}/cosmic_${CHIP}_$$.fits  ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits
      mv ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits /u/ki/awright/my_data/SUBARU/Zw2089/W-S-I+_2007-02-13/SCIENCE/cosmics_10_2/${BASE}_cosmics.fits
      # create ww config file on the fly

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
done


#adam-BL# log_status $?
