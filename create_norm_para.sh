#!/bin/bash -xv
. BonnLogger.sh
. log_start
# the script creates normaliced images.
# It puts the result into new directories ..._norm.
# The script assumes a threshhold. Pixels under
# this threshhold will be assigned a value of threshhold
# in the resulting images.
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 12.04.2005:
# - I rewrote the script so that it works with the
#   'imstats' program instead with the FLIPS based
#   'immode'.
# - I substituted XMIN etc. by STATSXMIN etc. that are
#   now defined in the in the instrument initialisation
#   files.
#
# 13.09.2005:
# If a camera has more than 10 chips, results were not correct.

# $1: main directory
# $2: directory from which normaliced images should be created 
# $3: chips to be processed

. ${INSTRUMENT:?}.ini

# first calculate the modes:
FILES=""
for CHIP in $3
do
  FILES="${FILES} `ls /$1/$2/$2*_${CHIP}.fits`"
done

${P_IMSTATS} ${FILES} -s \
             ${STATSXMIN} ${STATSXMAX} ${STATSYMIN} ${STATSYMAX} -o \
             ${TEMPDIR}/immode.dat_$$


# create the new directory for the normalized images if
# it does not exist already

if [ ! -d "/$1/$2_norm" ]; then
  mkdir "/$1/$2_norm"
fi

MODES=`${P_GAWK} '($1!="#") {printf ("%f ", $2)}' ${TEMPDIR}/immode.dat_$$`

# Set the threshold to 20% of the smallest mode value. Note
# that only the chips in the current parallelisation node
# contribute.

THRESH=`${P_GAWK} '($1!="#") {print $2}' ${TEMPDIR}/immode.dat_$$ |\
        ${P_GAWK} 'BEGIN{min=1000000} {if ($1<min) min=$1} END {print 0.2*min}'`

i=1
for CHIP in $3
do
  ACTUMODE=`echo ${MODES} | ${P_GAWK} '{print $'${i}'}'`

  if [ -L "/$1/$2/$2_${CHIP}.fits" ]; then
    LINK=`${P_READLINK} /$1/$2/$2_${CHIP}.fits`
    RESULTDIR=`dirname ${LINK}`
    ln -s ${RESULTDIR}/$2_norm_${CHIP}.fits /$1/$2_norm/$2_norm_${CHIP}.fits
  else
    RESULTDIR=/$1/$2_norm/
  fi

  ${P_IC} '%1 '${ACTUMODE}' / '${THRESH}' %1 '${THRESH}' > ?' /$1/$2/$2_${CHIP}.fits > \
          ${RESULTDIR}/$2_norm_${CHIP}.fits

  i=$(( $i + 1 ))
done

rm ${TEMPDIR}/immode.dat_$$

log_status $?
