#!/bin/bash
set -xv

### script to add the CONFIG keyword to Olli's CFHT image

# $1: main directory
# $2: INSTRUMENT
# $3: filter
# $4: date of observation  dy/mo/year

. progs.ini
. bash_functions.include


cd $1


IMAGE=`find $1/ -maxdepth 1 -name \*.fits | ${P_GAWK} '(NR==1) {print $0}'`

DATEOBS="1/1/2000"
if [ $# -eq 4 ]; then
    DATEOBS=$4
fi
DATE=`${P_DFITS} ${IMAGE} | ${P_FITSORT} -d DATE-OBS | ${P_GAWK} '{print $2}' | sed 's/\-/\//g'`
if [ ${DATE} != "KEY_N/A" ]; then
    DATEOBS=${DATE}
fi

MJD=`${P_MJD} -t 22:00:00 -d ${DATEOBS} | awk '{print $7}'`

GABODSID=`${P_NIGHTID} -t 22:00:00 -d 31/12/1998 -m ${MJD} |\
          ${P_GAWK} ' ($1 ~ /Days/) {print $6}' |\
          ${P_GAWK} 'BEGIN{ FS="."} {print $1}'`

ROTATION=0
CONFIG=0

FILES=`${P_FIND} . -maxdepth 1 -name \*.fits`

for IMAGE in ${FILES}
do

  fthedit ${IMAGE} GABODSID add ${GABODSID}
  fthedit ${IMAGE} ROTATION add ${ROTATION}
  fthedit ${IMAGE} CONFIG add ${CONFIG}
  fthedit ${IMAGE} INSTRUM add $2
  fthedit ${IMAGE} FILTER add $3

done
