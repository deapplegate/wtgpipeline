#!/bin/bash -xv
. BonnLogger.sh
. log_start
# CVSId: $Id$

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
# $3: file prefix
# $4: file suffix

. ${INSTRUMENT:?}.ini

ls -1 $1/$2/$3*_2${4}.fits | sed s/_2${4}.fits//g > filelist_$$

# create the new directory for the normalized images if
# it does not exist already

if [ ! -d "/$1/$2_norm" ]; then
  mkdir "/$1/$2_norm"
fi

cat filelist_$$ |\
{
while read image
do

  base=`basename ${image}`

  # first calculate the modes:

  FILES=""
  for ((i=1;i<=${NCHIPS};i+=1));
  do
    if [ ! -f $1/$2/${base}_${i}$4.fits ]; then
	mode2=`imstats -s 800 1200 1800 2200 -t 0 22000 $1/$2/${base}_2$4.fits | awk '{if($1!~"#") print $2}'`
	${P_IC} -c ${SIZEX[${i}]} ${SIZEY[${i}]} ${mode2} > $1/$2/${base}_${i}$4.fits
    fi  
    FILES="${FILES} $1/$2/${base}_${i}${4}.fits"
  done
  echo $FILES
  
  ${P_IMSTATS} ${FILES} -s \
               ${STATSXMIN} ${STATSXMAX} ${STATSYMIN} ${STATSYMAX} -o \
               ${TEMPDIR}/immode.dat_$$

  exit_code=$?
  if [ $exit_code -ne 0 ]; then
      log_status $exit_code "IMSTATS failure"
      exit $exit_code
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
  while [ ${i} -le ${NCHIPS} ]
  do
  
  #  if [ -L "/$1/$2/$2_${i}.fits" ]; then
  #    LINK=`${P_READLINK} /$1/$2/$2_${i}.fits`
  #    RESULTDIR=`dirname ${LINK}`
  #    ln -s ${RESULTDIR}/$2_norm_${i}.fits /$1/$2_norm/$2_norm_${i}.fits
  #  else
      RESULTDIR=/$1/$2_norm/
  #  fi

    ${P_IC} '%1 '${NORM}' / '${THRESH}' %1 '${THRESH}' > ?' /$1/$2/${base}_${i}${4}.fits > \
            ${RESULTDIR}/${base}_${i}${4}N.fits
    
    exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_status $exit_code 'IC Failure'
        exit $exit_code
    fi
  
    i=$(( $i + 1 ))
  done
  
  rm ${TEMPDIR}/immode.dat_$$

done
}

log_status $?
