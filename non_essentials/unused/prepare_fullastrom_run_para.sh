#!/bin/bash -xv

# this version takes a list of images (usually a subset,
# of images in the set (usually images belonging to the same
# run)) and processes only those).

# 22.03.2004:
# corrected a bug in the handling of the run list:
# If the full name including the path is given, we
# have to use the basename for further processing.

. ${INSTRUMENT:?}.ini

# $1: main dir.
# $2: science dir. (the cat dir is a subdirectory of this)
# $3: extension
# $4: identification (for ldacconv)
# $5: list of files to be processed (the list has to contain the
#     BASENAMES of the files, i.e. filename=BASENAME_${CHIP}$3.fits;
#     the list has to be given together with the full path
# $6: chips to be processed

RAWCATS=""
CATBASE=`basename $5 .txt`

for CHIP in $6
do
  while read file
  do
    RAWCATS="${RAWCATS} /$1/$2/cat/${file}_${CHIP}$3.cat"
  done < $5

  ${P_LDACCONV} -b ${CHIP} -c $4 -i ${RAWCATS} -o /$1/$2/cat/chip_${CHIP}_${CATBASE}.cat0
  
  # now preastrom
  ${P_PREASTROM} -i /$1/$2/cat/chip_${CHIP}_${CATBASE}.cat0   -o /$1/$2/cat/chip_${CHIP}_${CATBASE}.cat1 \
  	         -p /$1/$2/cat/chip_${CHIP}_${CATBASE}tmp.cat -a ${STANDARDSTARSCAT} \
  	         -c ${DATACONF}/fullastrom.preastrom.conf
    
  ${P_APLASTROM} -i /$1/$2/cat/chip_${CHIP}_${CATBASE}.cat1 -o /$1/$2/cat/chip_${CHIP}_${CATBASE}.cat2
  RAWCATS=""
done
