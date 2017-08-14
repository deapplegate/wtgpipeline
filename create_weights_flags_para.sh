#!/bin/bash 
. BonnLogger.sh
. log_start
# the script creates weights and flags for 
# for science and photometric standard star frames.
# It assumes the global weight images in the WEIGHT
# directory and the reg files in the sciencedir/reg
# directory.
#
# The current script version is a merging of the 'old'
# 'create_weights_para.sh' and 
# 'create_weights_flags_para.sh' scripts.
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 24.08.04:
# the SExtractor call to produce the cosmic ray mask now
# produces a DUMMY catalog in TEMPDIR (avoiding a lot of
# stdout messages during the processing)
#
# 25.04.2006:
# temporarily created FITS files (cosmic ray masks)
# are removed at the end of the script.
#
# 17.07.2006:
# the temporary file cosmic.cat is renamed to a unique name
# including the process number. It is also removed at the
# end of image processing.
#
# 22.09.2006:
# - I introduced the possibility to use specific cosmic ray mask
#   if necessary. The location of such masks has to be given
#   as (optional) command line argument. If a mask is not
#   provided the standard 'cosmic.ret.sex' mask is used.
# - I made the listing of files more robust if many files
#   are involved (by using 'find' instead of 'ls')
#
# 01.08.2007:
# some cleaning of not needed temporary files added
#
# 03.08.2007:
# I merged the two scripts 'create_weights_para.sh' and
# 'create_weights_flags_para.sh'.

# $1: main directory
# $2: science dir.
# $3: image extension (ext) on ..._iext.fits (i is the chip number)
# $4: WEIGHTS, FLAGS OR WEIGHTS_FLAGS
#     determines whether weights, flags or weights AND flags
#     are produced
# $5: Filter to use for cosmic ray detection (OPTIONAL)
# ${!#}: chips to be processed

. ${INSTRUMENT:?}.ini

# set cosmic ray mask to use:
MASK=${CONF}/cosmic.ret.sex

if [ $# -eq 6 ]; then
   MASK=$5
fi

# what needs to be done?
WEIGHTSPROD=1
FLAGSPROD=0

if [ "$4" = "WEIGHTS" ] || [ "$4" = "WEIGHTS_FLAGS" ]; then
  WEIGHTSPROD=1
fi
if [ "$4" = "FLAGS" ] || [ "$4" = "WEIGHTS_FLAGS" ]; then
  FLAGSPROD=1
fi

if [ "${WEIGHTSPROD}" = 0 ] && [ "${FLAGSPROD}" = 0 ]; then
  echo "Nothing to do!!"
  log_status 1 "Nothing to do!!"
  exit 1;
fi
 
for CHIP in ${!#}
do
  ${P_FIND} /$1/$2/ -maxdepth 1 -name \*_${CHIP}$3.fits \
          -print > ${TEMPDIR}/crw_images_$$

#  ${P_FIND} /$1/$2/ -maxdepth 1 -name \*50756_${CHIP}$3.fits \
#          -print > ${TEMPDIR}/crw_images_$$


  FILE=`${P_GAWK} '(NR==1) {print $0}' ${TEMPDIR}/crw_images_$$`

  if [ -L ${FILE} ]; then
    LINK=`${P_READLINK} ${FILE}`
    RESULTDIR=`dirname ${LINK}`
  else
    RESULTDIR="/$1/WEIGHTS"
  fi
  

  #cat temp |\

  cat ${TEMPDIR}/crw_images_$$ |\
  {
    while read file
    do
      BASE=`basename ${file} $3.fits`

      if [ -r "/$1/$2/reg/${BASE}.reg" ]; then
        INPOLYS="-POLY_NAMES \"/$1/$2/reg/${BASE}.reg\""
      else
        INPOLYS="-POLY_NAMES \"\""	  
      fi

      INFLAGS="-FLAG_NAMES \"\""
      OUTWEIGHTS="-OUTWEIGHT_NAME \"\""
      OUTFLAGS="-OUTFLAG_NAME \"\""
      
      if [ "${WEIGHTSPROD}" = "1" ]; then
        OUTWEIGHTS="-OUTWEIGHT_NAME ${RESULTDIR}/${BASE}$3.weight.fits"
      fi

      if [ "${FLAGSPROD}" = "1" ]; then
        INFLAGS="-FLAG_NAMES ${RESULTDIR}/globalflag_${CHIP}.fits"
        OUTFLAGS="-OUTFLAG_NAME ${RESULTDIR}/${BASE}$3.flag.fits"
      fi

      # first run sextractor to identify cosmic rays:
      ${P_SEX} ${file} -c ${CONF}/cosmic.conf.sex \
                       -CHECKIMAGE_NAME ${TEMPDIR}/cosmic_${CHIP}_$$.fits\
                       -FILTER_NAME ${MASK} \
                       -CATALOG_NAME ${TEMPDIR}/cosmic.cat_$$
      read HEY 
      echo "$HEY"
      # then run weightwatcher
      ${P_WW} -c ${CONF}/weights_flags.ww\
        -WEIGHT_NAMES ${RESULTDIR}/globalweight_${CHIP}.fits,${TEMPDIR}/cosmic_${CHIP}_$$.fits,${file}\
        ${INPOLYS} ${INFLAGS} ${OUTWEIGHTS} ${OUTFLAGS}
      echo ${RESULTDIR}   

      echo "/$1/WEIGHTS"
      if [ "${RESULTDIR}" != "/$1/WEIGHTS" ]; then
        if [ "${WEIGHTSPROD}" = "1" ]; then
          ln -s ${RESULTDIR}/${BASE}$3.weight.fits \
                /$1/WEIGHTS/${BASE}$3.weight.fits
	fi
        if [ "${FLAGSPROD}" = "1" ]; then
          ln -s ${RESULTDIR}/${BASE}$3.flag.fits \
                /$1/WEIGHTS/${BASE}$3.flag.fits
	fi
      fi

      # clean up temporary files:
      test -f ${TEMPDIR}/cosmic_${CHIP}_$$.fits &&\
              rm ${TEMPDIR}/cosmic_${CHIP}_$$.fits
      
      test -f ${TEMPDIR}/cosmic.cat_$$ && rm ${TEMPDIR}/cosmic.cat_$$
    done
  }
  test -f ${TEMPDIR}/crw_images_$$ #&& rm  ${TEMPDIR}/crw_images_$$
done

log_status $?
