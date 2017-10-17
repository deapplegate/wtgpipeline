#! /bin/bash -xv
#adam-example# ./parallel_manager.sh add_regionmasks.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS

# $1: main directory
# $2: science dir.
# $3: image extension (ext) on ..._iext.fits (i is the chip number)
# $4: weight directory
# ${!#}: chips to be processed

. ${INSTRUMENT:?}.ini

REDDIR=`pwd`
export WEIGHTSDIR=${1}/${4}

for CHIP in ${!#}
do

  #find SCIENCE/*_#OCF.fits
  ${P_FIND} $1/$2/ -maxdepth 1 -name \*_${CHIP}$3.fits \
            -print > ${TEMPDIR}/crw_images_$$

  FILE=`${P_GAWK} '(NR==1) {print $0}' ${TEMPDIR}/crw_images_$$`

  
  cat ${TEMPDIR}/crw_images_$$ |\
  {
    while read file
    do
      #loop over file=SCIENCE/*_#OCF.fits
      BASE=`basename ${file} $3.fits`

      {
        echo "WEIGHT_NAMES ${WEIGHTSDIR}/${BASE}$3.weight.fits"
	echo "WEIGHT_MIN -1e9"
	echo "WEIGHT_MAX 1e9"
	echo "WEIGHT_OUTFLAGS 0"
	#
        echo "FLAG_NAMES ${WEIGHTSDIR}/${BASE}$3.flag.fits"
        echo 'FLAG_MASKS "255"'
        echo 'FLAG_WMASKS "255"'
        echo 'FLAG_OUTFLAGS "1,2,4,8,16,32,64,128"'
        #
	if [ -s "/$1/$2/reg/${BASE}.reg" ]; then
          echo "POLY_NAMES /$1/$2/reg/${BASE}.reg"
          echo 'POLY_OUTFLAGS "128"'
        else
          echo 'POLY_NAMES ""'
          echo 'POLY_OUTFLAGS ""'
        fi
        echo "OUTWEIGHT_NAME ${WEIGHTSDIR}/${BASE}$3.weight.fits_$$"
	echo "OUTFLAG_NAME ${WEIGHTSDIR}/${BASE}$3.flag.fits_$$"
      } > ${TEMPDIR}/${BASE}.ww_$$

      ${P_WW} -c ${TEMPDIR}/${BASE}.ww_$$ 

      mv ${WEIGHTSDIR}/${BASE}$3.weight.fits_$$ ${WEIGHTSDIR}/${BASE}$3.weight.fits
      mv ${WEIGHTSDIR}/${BASE}$3.flag.fits_$$ ${WEIGHTSDIR}/${BASE}$3.flag.fits

    done
  }

done
