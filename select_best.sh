#!/bin/bash -xv
. BonnLogger.sh
. log_start
# script to select N 'best' frames.
# Best is defined here as distance from
# the mean of the modes from all images.
# The script is mainly intended to select frames
# if reduction is done with eclipse tools and
# hence disk swapping with too many frames 
# should be avoided.
#
# the NFRAMES variable has to be defined in the
# instrument configuration file !!!!!!
#
# 14.04.2005:
# I rewrote the script to use the imcat based 'imstats'
# instead of the FLIPS-based 'immode' for statistic
# estimation on FITS files.
#
# 14.08.2005:
# - The call of the UNIX 'find' program is now done
#   via a variable 'P_FIND'.
# - The call of the UNIX 'sort' program is now done
#   via a variable 'P_SORT'.
#
# 09.09.2005:
# I corrected a bug in the FIND command. We need to
# test regular files and links, not only regular files.


# $1: master directory
# $2: subdirectory with the images
# $3: image extension (ext) on ..._iext.fits (i is the chip number)

. ${INSTRUMENT:?}.ini

# the selction is done on images from the
# 1st chip!

# check whether something has to be done at all
# This is not the case if the number of exposures
# is smaller or equal to the number of frames that
# can be accepted
NEXPOSURES=`${P_FIND} /$1/$2/ \( -type f -o -type l \) -name \*_1$3.fits -maxdepth 1 | wc | ${P_GAWK} '{print $1}'`

if [ ${NEXPOSURES} -gt ${NFRAMES} ]; then
  ${P_IMSTATS} `${P_FIND} /$1/$2/ \( -type f -o -type l \) -name \*_1$3.fits -maxdepth 1` -s\
               ${STATSXMIN} ${STATSXMAX} ${STATSYMIN} ${STATSYMAX} -o \
               ${TEMPDIR}/immode.dat_$$  
  #
  # get the mean of the modes and do the sorting
  MEAN=`${P_GAWK} 'BEGIN {m=0; n=0} ($1 != "#") {m=m+$2; n=n+1} END {m=m/n; print m}' immode.dat_$$`
  
  ${P_GAWK} '($1 != "#") {print $1, sqrt(($2-'${MEAN}')*($2-'${MEAN}'))}' immode.dat_$$ |\
  ${P_SORT} -g -k 2,2 | ${P_GAWK} '(NR > '${NFRAMES}') {print $1}' > rejectframes_$$.dat

  # move the rejected frames to a REJECTED subdirectory:
  cat rejectframes_$$.dat |\
  {
    while read file
    do
      DIR=`dirname ${file}`
      BASE=`basename ${file} _1$3.fits`
      if [ ! -d "${DIR}/REJECTED" ]; then
          mkdir "${DIR}/REJECTED"
      fi
  
      i=1
      while [ "${i}" -le "${NCHIPS}" ]
      do
        # the following 'if' is necessary as the
        # file(s) may already have been moved
        if [ -f "${DIR}/${BASE}_${i}$3.fits" ]; then
           mv ${DIR}/${BASE}_${i}$3.fits ${DIR}/REJECTED
        fi
        i=$(( $i + 1 ))
      done
    done
  }
fi 

 
log_status $?
