#!/bin/bash -xv

. ${INSTRUMENT:?}.ini

# 12.05.03:
# new option to put keywords for SWARP coaddition into
# the headers

# $1: main dir.
# $2: science dir. (the cat dir is a subdirectory of this)
# $3: extension (added by add_image_calibs)
# $4: polynom type (LDAC or SWARP)

# This script can't be parallelised

# ALL new Files are first created in the main directory
# A moving and lnking is only done after all files have
# been created by add_image_calibs.
 
DIR=`pwd`

cd /$1/$2/

if [ "$4" != "SWARP" ]; then
  ${P_ADDIMAGECALIBS} -i ./cat/chips.cat4 -o ".fits" -e "$3.fits" \
                      -c ${DATACONF}/calibheader.conf.add_image_calibs
else
  ${P_ADDIMAGECALIBS} -i ./cat/chips.cat4 -o ".fits" -e "$3.fits" \
                      -c ${DATACONF}/calibheader.conf.add_image_calibs\
                      -MODE WCSSTANDARD
fi

# move files and create links if necessary
${P_LDACTOASC} -i ./cat/chips.cat4 -t FIELDS -k FITSFILE -s -b |\
{
  while read FILE
  do
    if [ -L ${FILE} ]; then
       LINK=`${P_READLINK} ${FILE}`
       DIR=`dirname ${LINK}`
       BASE=`basename ${FILE} .fits`
       mv ${BASE}$3.fits ${DIR}
       ln -s ${DIR}/${BASE}$3.fits /$1/$2/${BASE}$3.fits
    fi
  done
}
cd ${DIR}

