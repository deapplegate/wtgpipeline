#!/bin/bash
. BonnLogger.sh
. log_start
# The script writes the keywords ZP[1-3] and COEFF[1-3] to
# images that do not have them. This is to bring headers
# of frames for which no standardstar observations are
# available in accordance with photometrically calibrated
# frames. The script should be called after 
# create_abs_phot_info.sh

# $1: main dir
# $2: science dir (the cat dir is a subdirectory of this)
# $3: extension

. ${INSTRUMENT:?}.ini
. bash_functions.include

ls -1 /$1/$2/*$3.fits > ${TEMPDIR}/images_$$

cat ${TEMPDIR}/images_$$ |\
{
  while read file
  do
    value "0"    
    writekey ${file} ZPCHOICE "${VALUE}" NOREPLACE
    value "-1.0"
    i=1
    while [ ${i} -le 3 ]
    do
      writekey ${file} ZP${i} "${VALUE}" NOREPLACE
      writekey ${file} COEFF${i} "${VALUE}" NOREPLACE
      i=$(( $i + 1 ))
    done
  done
}
log_status $?
