#!/bin/bash -xv
. BonnLogger.sh
. log_start
# this script runs the PHOTOMETRIX tool
# after astrometric calibration by ASTROMETRIX.
# This part only deal with relative photometry,
# not with the absolute one. Images are scales so that
# the mean of relative zeropoints for ALL input
# images is zero. The resulting fluxscale parameters
# are:
# f_i=exp(-0.4 zp[i])/t_i, where t_i is the exposure
# time.
# We assume that ALL chips of an exposure share the same
# photometric zeropoint, i.e. zeropint differences in
# different detectors are not taken into account.

# 14.08.2005:
# The call of the UNIX 'find' program is now done
# via a variable 'P_FIND'.
#
# 28.08.2006:
# more robust file listing by 'find' instead of 'ls'.
# The letter led to 'Argument list too long' errors when
# many images are involved in the processing.
#
# 27.08.2006:
# The SExtractor executable is now called 'sex_theli'
# (command line argument to PHOTOMETRIX).

# CVSId: $Id: create_photometrix.sh,v 1.4 2008-07-09 18:22:59 dapple Exp $

# $1: main dir.
# $2: science dir. (the cat dir is a subdirectory of this)
# $3: extension

. ${INSTRUMENT:?}.ini

DIR=`pwd`

cd /$1/$2/

if [ ! -d "photom" ]; then
  mkdir photom
fi

cd photom

${P_PERL} ${S_PHOTOMETRIX} -mkhead \
 -s hdr_dir=/$1/$2/astrom/astglob -s fits_dir=/$1 -s cats_dir=/$1/$2/astrom\
 -s list=/$1/$2/astrom/$2.list -s outdir_top=./ -s MIN_OVERLAP=30 \
 -s mcats_dir=/$1/$2/astrom/astglob -s observatory=ESO -s ZP0=0. \
 -s SEX=sex_theli

${P_PERL} ${S_PHOTOMETRIX}  -calc

cd ..

# finally copy the photometrix headers to the right place
# and rename them. Here, we overwrite headers previously created
# by ASTROMETRIX. The old headers we copy to a directory
# astrometrix_copy if this directory does not yet already
# exist.

if [ ! -d "headers" ]; then
  mkdir headers
fi

cd ./headers

if [ ! -d "astrometrix_copy" ]; then
  mkdir astrometrix_copy
  ${P_FIND} . -name \*.head -maxdepth 1 -exec mv {} ./astrometrix_copy \;
fi

${P_FIND} ../photom/globphot/ -name \*head -exec cp {} . \;

${P_FIND} . -name \*_1$3.head > files_$$

while read file
do
  i=1
  BASE=`basename ${file} _1$3.head`
  while [ "${i}" -le "${NCHIPS}" ]
  do
    mv ${BASE}_${i}$3.head ${BASE}_${i}.head
    i=$(( $i + 1 )) 
  done
done < files_$$

rm files_$$

cd ${DIR}

log_status $?
