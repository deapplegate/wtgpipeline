#!/bin/bash -xv

# this script runs the fullastrometric calibration
# on the single chips. It has to be used instead of
# the usual fullastrom script if the number of overlap
# objects between different chips is very small

. ${INSTRUMENT:?}.ini

# $1: main dir.
# $2: science dir. (the cat dir is a subdirectory of this)

k=1

while [ "${k}" -le "${NCHIPS}" ]
do
  ASSOCCATS="      /$1/$2/cat/chip_${k}.cat2 /$1/$2/cat/chip_${k}tmp.cat"
  ASSOCCATSOUT="   /$1/$2/cat/chip_${k}.cat3 /$1/$2/cat/chip_${k}tmp.cat2"
  MAKESSCCATS="    /$1/$2/cat/chip_${k}.cat3 /$1/$2/cat/chip_${k}tmp.cat2"
  ASTROMCATS="     /$1/$2/cat/chip_${k}.cat3"
  ASTROMCATSOUT="  /$1/$2/cat/chip_${k}.cat4"

  ${P_ASSOCIATE} -i ${ASSOCCATS}   -o ${ASSOCCATSOUT}             \
                 -c ${DATACONF}/fullastrom.conf.associate
  ${P_MAKESSC}   -i ${MAKESSCCATS} -o /$1/$2/cat/chips_${k}.pairs \
                 -c ${DATACONF}/fullastrom.make_ssc.pairs
  ${P_ASTROM}    -i ${ASTROMCATS}  -o ${ASTROMCATSOUT}            \
                 -c ${DATACONF}/fullastrom.chip.astrom.conf            \
                 -p /$1/$2/cat/chips_${k}.pairs 

  k=$(( $k + 1 ))   
done

k=1

while [ "${k}" -le "${NCHIPS}" ]
do
  ${P_APLASTROM}   -i /$1/$2/cat/chip_${k}.cat4 -o /$1/$2/cat/chip_${k}.cat5
  ${P_MAKEDISTORT} -i /$1/$2/cat/chip_${k}.cat5 -o /$1/$2/cat/chip_${k}.cat6\
		   -c ${DATACONF}/fullastrom.conf.make_distort
  k=$(( $k + 1 ))
done






