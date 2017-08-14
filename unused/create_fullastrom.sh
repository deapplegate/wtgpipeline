#!/bin/bash -xv

. ${INSTRUMENT:?}.ini

# 30.05.04:
# temporary files go to a TEMPDIR directory

# $1: main dir.
# $2: science dir. (the cat dir is a subdirectory of this)
# $3: extension
# $4: identification (for ldacconv)

k=1

ASSOCCATS=""
ASSOCCATSOUT=""
MAKESSCCATS=""
ASTROMCATS=""
ASTROMCATSOUT=""

# create the command lines (involved catalogs) for a later associate and make_ssc

while [ "${k}" -le "${NCHIPS}" ]
do
  ASSOCCATS="${ASSOCCATS}         /$1/$2/cat/chip_${k}.cat2 /$1/$2/cat/chip_${k}tmp.cat"
  ASSOCCATSOUT="${ASSOCCATSOUT}   /$1/$2/cat/chip_${k}.cat3 /$1/$2/cat/chip_${k}tmp.cat2"
  MAKESSCCATS="${MAKESSCCATS}     /$1/$2/cat/chip_${k}.cat3 /$1/$2/cat/chip_${k}tmp.cat2"
  ASTROMCATS="${ASTROMCATS}       /$1/$2/cat/chip_${k}.cat3"
  ASTROMCATSOUT="${ASTROMCATSOUT} /$1/$2/cat/chip_${k}.cat4"
  k=$(( $k + 1 ))   
done

${P_ASSOCIATE} -i ${ASSOCCATS}   -o ${ASSOCCATSOUT}        -c ${DATACONF}/fullastrom.conf.associate
${P_MAKESSC}   -i ${MAKESSCCATS} -o /$1/$2/cat/chips.pairs -c ${DATACONF}/fullastrom.make_ssc.pairs
${P_ASTROM}    -i ${ASTROMCATS}  -o ${ASTROMCATSOUT}       -c ${DATACONF}/fullastrom.astrom.conf\
               -p /$1/$2/cat/chips.pairs  -r ${TEMPDIR}/residuals

k=1

while [ "${k}" -le "${NCHIPS}" ]
do
  ${P_APLASTROM}   -i /$1/$2/cat/chip_${k}.cat4 -o /$1/$2/cat/chip_${k}.cat5
  ${P_MAKEDISTORT} -i /$1/$2/cat/chip_${k}.cat5 -o /$1/$2/cat/chip_${k}.cat6\
		   -c ${DATACONF}/fullastrom.conf.make_distort
  k=$(( $k + 1 ))
done
