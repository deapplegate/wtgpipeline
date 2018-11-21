#!/bin/bash

# 30.05.04:
# tempaorary files go to a TEMPDIR directory 

# the script writes resulting FITS images
# after the coaddition process.
# by a call to IRAF

# Also if we have several processors, the
# IRAF directories are worked thorough here
# one after the other (the win in time
# here is absolutely unimportant)

. ${INSTRUMENT:?}.ini

#$1: name of the cl-script (4 charracters)

DIR=`pwd`

i=1
while [ "${i}" -le "${NPARA}" ]
do
  cd ${IRAFDIR[${i}]}
  
  # first run mcon to get contexts right
  {
    echo "eis"
    #
    echo "flprc"
    echo 'mcon(conims="'$1*context.hhh'", mascon="'$1CONTAB'")'
    echo "flprc"
    echo "logout"
  } | ${P_CL}
  
  # then create FITS images out of the IRAF images
  ls -1 $1*CA??????.hhh > ${TEMPDIR}/coaddresimages
  
  cat ${TEMPDIR}/coaddresimages |\
  {
    while read file
    do
      BASE=`basename ${file} .hhh`
      {
      echo "images"
      echo "wfits ${file} ${BASE}.fits"
      echo "logout"
      } | ${P_CL}
    done
  }
  
  ls -1 $1*CA??????.weight.hhh > ${TEMPDIR}/coaddresimages
  
  cat ${TEMPDIR}/coaddresimages |\
  {
    while read file
    do
      BASE=`basename ${file} .weight.hhh`
      {
      echo "images"
      echo "wfits ${file} ${BASE}.weight.fits"
      echo "logout"
      } | ${P_CL}
    done
  }
  
  ls -1 $1*CA??????.context.hhh > ${TEMPDIR}/coaddresimages
  
  cat ${TEMPDIR}/coaddresimages |\
  {
    while read file
    do
      BASE=`basename ${file} .context.hhh`
      {
      echo "images"
      echo "wfits ${file} ${BASE}.context.fits"
      echo "logout"
      } | ${P_CL}
    done
  }
  i=$(( $i + 1 ))
done  

cd ${DIR}

