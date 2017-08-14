#!/bin/bash

### script to add the INSTRUM, CONFIG, and ROTATION keyword

# $1: main directory
# $2: INSTRUMENT

INSTRUMENT="'${2}'"

. progs.ini
. bash_functions.include


cd $1

ROTATION=0
CONFIG=0

FILES=`${P_FIND} . -maxdepth 1 -name \*.fits`

for IMAGE in ${FILES}
do

  echo ${IMAGE}
  value ${INSTRUMENT}
  writekey ${IMAGE} INSTRUM "${VALUE} / Instrument" REPLACE

  value ${ROTATION}
  writekey ${IMAGE} ROTATION "${VALUE} / Rotation" REPLACE

  value ${CONFIG}
  writekey ${IMAGE} CONFIG "${VALUE} / Configuration" REPLACE

done
