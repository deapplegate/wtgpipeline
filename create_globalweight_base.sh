#!/bin/bash
set -xv

# $1 : run dir
# $2 : norm flat dir
# $3 : norm illum dir

. ${INSTRUMENT:?}.ini > /tmp/inst.out 2>&1

if [ ! -d $1/BASE_WEIGHT ]; then
    mkdir $1/BASE_WEIGHT
fi

for ((i=1;i<=${NCHIPS};i+=1)); do
    
    ic '%1 %2 *' $1/$2/${2}_${i}.fits $1/$3/${3}_${i}_illum.fits > $1/BASE_WEIGHT/BASE_WEIGHT_${i}.fits
    if [ ! -e $1/BASE_WEIGHT/BASE_WEIGHT_${i}.fits ]; then
	echo "adam-look | error: Base Weight Not Created!"
	exit 1;
    fi

done
