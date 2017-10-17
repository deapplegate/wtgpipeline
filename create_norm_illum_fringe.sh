#!/bin/bash
set -xv
# CVSId: $Id: create_norm_illum_fringe.sh,v 1.3 2008-09-03 18:49:40 dapple Exp $

#02.09.2008 (DA): special modification to keep scaling between illum and fringe images constant

# 30.06.2008 (AvdL):
# normalizes images by the highest mode value of the
# individual chips

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
# $3: file suffix

. ${INSTRUMENT:?}.ini > /tmp/out.log 2>&1

# first calculate the modes:
FILES=""
for ((i=1;i<=${NCHIPS};i+=1));
do
    FILES="${FILES} $1/$2/${2}_${i}_illum${3}.fits"
done
echo $FILES

${P_IMSTATS} ${FILES} -s \
             ${STATSXMIN} ${STATSXMAX} ${STATSYMIN} ${STATSYMAX} -o \
             ${TEMPDIR}/immode.dat_$$

exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "adam-look | error: IMSTATS failure"
    exit $exit_code
fi

# create the new directory for the normalized images if
# it does not exist already

if [ ! -d "/$1/$2_norm" ]; then
  mkdir "/$1/$2_norm"
fi



# set the normalization to the highest mode value

NORM=`${P_GAWK} 'BEGIN {max=0} ($1!="#") {if ($2>max) max=$2} END {print max}' \
    ${TEMPDIR}/immode.dat_$$`

i=1
while [ ${i} -le ${NCHIPS} ]
do

    RESULTDIR=/$1/$2_norm/

    if [ -f /$1/$2/$2_${i}_fringe${3}.fits ]; then
	    ${P_IC} '%1 '${NORM}' / ' /$1/$2/$2_${i}_fringe${3}.fits > \
		${RESULTDIR}/$2_norm_${i}_fringe${3}.fits
    fi
    ${P_IC} '%1 '${NORM}' / ' /$1/$2/$2_${i}_illum${3}.fits > \
        ${RESULTDIR}/$2_norm_${i}_illum${3}.fits
    
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo "adam-look | error: IC failure"
	exit $exit_code
    fi
    
    i=$(( $i + 1 ))
done

rm -f ${TEMPDIR}/immode.dat_$$
