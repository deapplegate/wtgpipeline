#!/bin/bash -xv

# 30.05.04:
# temporary files go to a TEMPDIR directory 

. ${INSTRUMENT:?}.ini

# $1: main dir.
# $2: science dir. (the cat dir is a subdirectory of this)
# $3: extension
# $4: identification (for ldacconv)
# $5: chips to be processed

for CHIP in $5
do
  RAWCATS=`ls /$1/$2/cat/*_${CHIP}$3.cat`
  ${P_LDACCONV} -b ${CHIP} -c $4 -i ${RAWCATS} -o /$1/$2/cat/chip_${CHIP}.cat0

  # now preastrom
  ${P_PREASTROM} -i /$1/$2/cat/chip_${CHIP}.cat0   -o /$1/$2/cat/chip_${CHIP}.cat1 \
	         -p /$1/$2/cat/chip_${CHIP}tmp.cat -a ${STANDARDSTARSCAT} \
                 -d ${TEMPDIR}/distances.cat \
	         -c ${DATACONF}/fullastrom.preastrom.conf
  
  ${P_APLASTROM} -i /$1/$2/cat/chip_${CHIP}.cat1 -o /$1/$2/cat/chip_${CHIP}.cat2
done
