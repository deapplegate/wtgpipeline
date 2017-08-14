#!/bin/bash -xv
. BonnLogger.sh
. log_start
# the script creates weights for science frames.
# It assumes the global weight images in the WEIGHT
# directory and the reg files in the sciencedir/reg
# directory.
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 24.08.04:
# the SExtractor call to produce the cosmic ray mask now
# produces a DUMMY catalog in TEMPDIR (avoiding a lot of
# stdout messages during the processing)
#
# 15.10.05:
# a line break (in the argument images of ww) 
# in the case where a reg file is present
# led to problems on aibn202. Hence, I removed it.
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
# 10.04.2008:  AvdL
# edited so that 'spikefinder' masks can be used
#
# 01.07.2008: (AvdL)
# removed link structure

# $Id: create_weights_delink_para.sh,v 1.3 2008-07-09 18:22:59 dapple Exp $

# $1: main directory
# $2: science dir.
# $3: image extension (ext) on ..._iext.fits (i is the chip number)
#     note that spikefinder images have an additional .sf
# $4: Filter to use for cosmic ray detection (OPTIONAL)
# ${!#}: chips to be processed

. ${INSTRUMENT:?}.ini

# set cosmic ray mask to use:
MASK=${CONF}/cosmic.ret.sex

if [ $# -eq 5 ]; then
   MASK=$4
fi

for CHIP in ${!#}
do
  ${P_FIND} /$1/$2/ -maxdepth 1 -name \*_${CHIP}$3.fits \
            -print > ${TEMPDIR}/crw_images_$$

  FILE=`${P_GAWK} '(NR==1) {print $0}' ${TEMPDIR}/crw_images_$$`

#  if [ -L ${FILE} ]; then
#    LINK=`${P_READLINK} ${FILE}`
#    RESULTDIR=`dirname ${LINK}`
#  else
    RESULTDIR="/$1/WEIGHTS"
#  fi
  
  cat ${TEMPDIR}/crw_images_$$ |\
  {
    while read file
    do
      BASE=`basename ${file} $3.fits`

      # first run sextractor to identify cosmic rays:
      ${P_SEX} ${file} -c ${CONF}/cosmic.conf.sex -CHECKIMAGE_NAME \
                          ${TEMPDIR}/cosmic_${CHIP}_$$.fits \
                          -FILTER_NAME ${MASK} \
                          -CATALOG_NAME ${TEMPDIR}/cosmic.cat_$$

      # create ww config file on the fly

      if [ -r "$1/$2/diffmask/${BASE}$3.sf.fits" ]; then
	  echo "WEIGHT_NAMES ${RESULTDIR}/globalweight_${CHIP}.fits,${TEMPDIR}/cosmic_${CHIP}_$$.fits,${file},/$1/$2/diffmask/${BASE}$3.sf.fits"                               >  ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_MIN -1e9,-1e9,0,0.1"       >> ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_MAX 1e9,0.1,30000,1"       >> ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_OUTFLAGS 0,16,32,64"       >> ${TEMPDIR}/${BASE}.ww_$$
      else
	  echo "WEIGHT_NAMES ${RESULTDIR}/globalweight_${CHIP}.fits,${TEMPDIR}/cosmic_${CHIP}_$$.fits,${file}" \
	                                          >  ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_MIN -1e9,-1e9,0"           >> ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_MAX 1e9,0.1,30000"         >> ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_OUTFLAGS 0,16,32"          >> ${TEMPDIR}/${BASE}.ww_$$
      fi
      #
      echo 'FLAG_NAMES ""'                        >> ${TEMPDIR}/${BASE}.ww_$$
      echo 'FLAG_MASKS ""'                        >> ${TEMPDIR}/${BASE}.ww_$$
      echo 'FLAG_WMASKS ""'                       >> ${TEMPDIR}/${BASE}.ww_$$
      echo 'FLAG_OUTFLAGS ""'                     >> ${TEMPDIR}/${BASE}.ww_$$
      #
      if [ -f "/$1/$2/reg/${BASE}.reg" ]; then
        echo "POLY_NAMES /$1/$2/reg/${BASE}.reg"  >> ${TEMPDIR}/${BASE}.ww_$$
        echo "POLY_OUTFLAGS 1"                    >> ${TEMPDIR}/${BASE}.ww_$$
      else
        echo 'POLY_NAMES ""'                      >> ${TEMPDIR}/${BASE}.ww_$$
        echo 'POLY_OUTFLAGS ""'                   >> ${TEMPDIR}/${BASE}.ww_$$
      fi
      #
      echo "OUTWEIGHT_NAME ${RESULTDIR}/${BASE}$3.weight.fits"  >> ${TEMPDIR}/${BASE}.ww_$$
      echo 'OUTFLAG_NAME ""'                                    >> ${TEMPDIR}/${BASE}.ww_$$
      
      # then run weightwatcher

      ${P_WW} -c ${TEMPDIR}/${BASE}.ww_$$
      rm ${TEMPDIR}/${BASE}.ww_$$

      if [ "${RESULTDIR}" != "/$1/WEIGHTS" ]; then
        ln -s ${RESULTDIR}/${BASE}$3.weight.fits /$1/WEIGHTS/${BASE}$3.weight.fits
      fi

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
