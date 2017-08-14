#!/bin/bash -xv
. BonnLogger.sh
. log_start
# CVSId: $Id: make_residuals.sh,v 1.3 2008-07-19 00:06:19 dapple Exp $

# $1 : maindir
# $2 : sciendir
# $3 : smoothing radius

. ${INSTRUMENT:?}.ini

# first calculate the modes:
FILES=""
for ((i=1;i<=${NCHIPS};i+=1));
do
    FILES="${FILES} $1/$2/${2}_${i}_illum$3.fits"
done
echo $FILES

${P_IMSTATS} ${FILES} -s \
             ${STATSXMIN} ${STATSXMAX} ${STATSYMIN} ${STATSYMAX} -o \
             ${TEMPDIR}/immode.dat_$$


# create the new directory for the normalized images if
# it does not exist already

if [ ! -d "/$1/$2_norm" ]; then
  mkdir "/$1/$2_norm"
fi


# set the normalization to the highest mode value

NORM=`${P_GAWK} 'BEGIN {max=0} ($1!="#") {if ($2>max) max=$2} END {print max}' \
    ${TEMPDIR}/immode.dat_$$`

# Set the threshold to 20% of the smallest mode value. Note
# that only the chips in the current parallelisation node
# contribute.

THRESH=`${P_GAWK} '($1!="#") {print $2}' ${TEMPDIR}/immode.dat_$$ |\
        ${P_GAWK} 'BEGIN{min=1000000} {if ($1<min) min=$1} END {print 0.2*min}'`


i=1
for ((i=1;i<=10;i+=1));
do

#  if [ -L "/$1/$2/$2_${i}.fits" ]; then
#    LINK=`${P_READLINK} /$1/$2/$2_${i}.fits`
#    RESULTDIR=`dirname ${LINK}`
#    ln -s ${RESULTDIR}/$2_norm_${i}.fits /$1/$2_norm/$2_norm_${i}.fits
#  else
    RESULTDIR=$1/$2_norm/
#  fi

  ${P_IC} '%1 '${NORM}' / '${THRESH}' %1 '${THRESH}' > ?' \
      /$1/$2/$2_${i}_illum$3.fits > ${RESULTDIR}/$2_norm_${i}_illum$3.fits

  ${P_IC} '%1 %2 /' ${RESULTDIR}/$2_norm_${i}.fits \
      ${RESULTDIR}/$2_norm_${i}_illum$3.fits > ${RESULTDIR}/$2_res${3}_${i}.fits


done

rm ${TEMPDIR}/immode.dat_$$
log_status $?
