#!/bin/bash -xv
#. BonnLogger.sh
#. log_start
##########
# Take Science images and weight them by the weight files
# Save the output for use in masking
#
# ARGS:
# $1: main dir
# $2: science dir
# $3: weight dir
# $4: suffix
# $5: file
#########

#CVSID="$Id: create_science_weighted.sh,v 1.5 2008-09-12 16:33:49 dapple Exp $"

. ${INSTRUMENT:?}.ini

RESULTDIR="$1/SCIENCE_weighted"
if [ ! -d ${RESULTDIR} ]; then
    mkdir ${RESULTDIR}
fi

file=$5
BASE=`basename ${file} .fits`

WEIGHT="$1/$3/${BASE}.weight.fits"

OUTPUT="${RESULTDIR}/${BASE}.weighted.fits"

ic '%1 1 0 %2 0 > ? mult' ${file} ${WEIGHT} > ${OUTPUT}
