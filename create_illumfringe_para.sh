#!/bin/bash
set -xv
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# script that creates an illumination correction and
# fringe image out of a blank sky field (superflat)

# $1: main dir (filter)
# $2: Science directory
# $3: chips to be processed

# preliminary work:
. ${INSTRUMENT:?}.ini

for CHIP in $3
do
  FILE=`ls /$1/$2/$2_${CHIP}.fits`

  if [ -L ${FILE} ]; then
    LINK=`${P_READLINK} ${FILE}`
    BASE=`basename ${LINK} .fits`
    DIR=`dirname ${LINK}`
    ln -s ${DIR}/$2_${CHIP}_illum.fits $1/$2/$2_${CHIP}_illum.fits
    ln -s ${DIR}/$2_${CHIP}_fringe.fits $1/$2/$2_${CHIP}_fringe.fits
    RESULTDIR[${CHIP}]=`dirname ${LINK}`    
  else
    RESULTDIR[${CHIP}]="/$1/$2"
  fi

  ${P_SEX} /$1/$2/$2_${CHIP}.fits -c ${CONF}/illumfringe_back.sex -CHECKIMAGE_NAME ${RESULTDIR[${CHIP}]}/$2_${CHIP}_illum.fits -BACK_SIZE 256
  ${P_SEX} /$1/$2/$2_${CHIP}.fits -c ${CONF}/illumfringe_fringe.sex -CHECKIMAGE_NAME ${RESULTDIR[${CHIP}]}/$2_${CHIP}_fringe.fits -BACK_SIZE 256
done

#adam-BL# log_status $?
