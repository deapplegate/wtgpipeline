#!/bin/bash -xv

# this version takes a list of images (usually a subset,
# of images in the set (usually images belonging to the same
# run)) and processes only those).
# Before running this script, images have to go through
# prepare_fullastrom_run_para.sh.

# 22.03.2004:
# corrected a bug in the handling of the run list:
# If the full name including the path is given, we
# have to use the basename for further processing.

. ${INSTRUMENT:?}.ini

# 30.05.04:
# temporary files go to a TEMPDIR directory

# $1: main dir.
# $2: science dir. (the cat dir is a subdirectory of this)
# $3: list of files to be processed (the list has to contain the
#     BASENAMES of the files, i.e. filename=BASENAME_${CHIP}ext.fits;
#     the list has to be given together with the full path

k=1
CATBASE=`basename $3 .txt`

ASSOCCATS=""
ASSOCCATSOUT=""
MAKESSCCATS=""
ASTROMCATS=""
ASTROMCATSOUT=""

# create the command lines (involved catalogs) for a later associate and make_ssc

while [ "${k}" -le "${NCHIPS}" ]
do
  ASSOCCATS="${ASSOCCATS}         /$1/$2/cat/chip_${k}_${CATBASE}.cat2 /$1/$2/cat/chip_${k}_${CATBASE}tmp.cat"
  ASSOCCATSOUT="${ASSOCCATSOUT}   /$1/$2/cat/chip_${k}_${CATBASE}.cat3 /$1/$2/cat/chip_${k}_${CATBASE}tmp.cat2"
  MAKESSCCATS="${MAKESSCCATS}     /$1/$2/cat/chip_${k}_${CATBASE}.cat3 /$1/$2/cat/chip_${k}_${CATBASE}tmp.cat2"
  ASTROMCATS="${ASTROMCATS}       /$1/$2/cat/chip_${k}_${CATBASE}.cat3"
  ASTROMCATSOUT="${ASTROMCATSOUT} /$1/$2/cat/chip_${k}_${CATBASE}.cat4"
  k=$(( $k + 1 ))   
done

${P_ASSOCIATE} -i ${ASSOCCATS}   -o ${ASSOCCATSOUT}        -c ${DATACONF}/fullastrom.conf.associate
${P_MAKESSC}   -i ${MAKESSCCATS} -o /$1/$2/cat/chips.pairs -c ${DATACONF}/fullastrom.make_ssc.pairs
${P_ASTROM}    -i ${ASTROMCATS}  -o ${ASTROMCATSOUT}       -c ${DATACONF}/fullastrom.astrom.conf\
               -p /$1/$2/cat/chips.pairs -r ${TEMPDIR}/residuals

k=1

while [ "${k}" -le "${NCHIPS}" ]
do
  ${P_APLASTROM}   -i /$1/$2/cat/chip_${k}_${CATBASE}.cat4 -o /$1/$2/cat/chip_${k}_${CATBASE}.cat5
  ${P_MAKEDISTORT} -i /$1/$2/cat/chip_${k}_${CATBASE}.cat5 -o /$1/$2/cat/chip_${k}_${CATBASE}.cat6\
		   -c ${DATACONF}/fullastrom.conf.make_distort
  k=$(( $k + 1 ))
done
