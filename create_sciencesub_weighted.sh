#!/bin/bash -xv
. BonnLogger.sh
. log_start
##########
# Take Science images and weight them by the weight files
# Save the output for use in masking
#
# ARGS:
# $1: main dir
# $2: science dir
# $3: weight dir
# $4: suffix
# ${!#}: chips to be processed
#########

#CVSID="$Id: create_sciencesub_weighted.sh,v 1.1 2008-11-19 19:39:58 anja Exp $"

. ${INSTRUMENT:?}.ini

for CHIP in ${!#}
do
  ${P_FIND} $1/$2/ -maxdepth 1 -name \*_${CHIP}$4.sub.fits \
            -print > ${TEMPDIR}/crw_images_$$

  FILE=`${P_GAWK} '(NR==1) {print $0}' ${TEMPDIR}/crw_images_$$`

  RESULTDIR="$1/SCIENCE_sub_weighted"
  if [ ! -d ${RESULTDIR} ]; then
      mkdir ${RESULTDIR}
  fi
  
  cat ${TEMPDIR}/crw_images_$$ |\
  {
    while read file
    do

	BASE=`basename ${file} .sub.fits`

	WEIGHT="$1/$3/${BASE}.weight.fits"

	OUTPUT="${RESULTDIR}/${BASE}.sub.weighted.fits"
	
	ic '%1 1 0 %2 0 > ? mult' ${file} ${WEIGHT} > ${OUTPUT}

    done
  }
  test -f ${TEMPDIR}/crw_images_$$ && rm  ${TEMPDIR}/crw_images_$$
done
log_status $?
