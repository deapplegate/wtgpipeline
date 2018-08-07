#!/bin/bash
set -xv
##########
# Take Science Flats and weight them by the global weight files
# Save the output for use in masking global regions
#
# ARGS:
# $1: main dir
# $2: science dir
# $3: weight dir
# $4: SUPA
# $5: ending
#########


#CVSID = "$Id: create_global_science_weighted.sh,v 1.5 2008-11-04 18:24:11 anja Exp $"

. ${INSTRUMENT:?}.ini > /tmp/out.log 2>&1

for ((CHIP=1;CHIP<=${NCHIPS};CHIP+=1));
do

  FILE=${1}/${2}/${4}_${CHIP}${5}.fits

  RESULTDIR="$1/${2}_weighted"
  if [ ! -d ${RESULTDIR} ]; then
      mkdir ${RESULTDIR}
  fi
  
  

  BASE=`basename ${FILE} .fits`

  WEIGHT=$1/$3/globalweight_${CHIP}.fits

  OUTPUT=${RESULTDIR}/${BASE}.weighted.fits

	
  ic '%1 1 0 %2 0 > ? mult' ${FILE} ${WEIGHT} > ${OUTPUT}

done
