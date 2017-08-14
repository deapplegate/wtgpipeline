#!/bin/bash -xv
. BonnLogger.sh
. log_start

# $1 : run dir
# $2 : norm flat dir
# $3 : norm illum dir

. ${INSTRUMENT:?}.ini

if [ ! -d $1/BASE_WEIGHT ]; then
    mkdir $1/BASE_WEIGHT
fi

for ((i=1;i<=${NCHIPS};i+=1)); do
    
    ic '%1 %2 *' $1/$2/${2}_${i}.fits $1/$3/${3}_${i}_illum.fits > $1/BASE_WEIGHT/BASE_WEIGHT_${i}.fits
    if [ ! -e $1/BASE_WEIGHT/BASE_WEIGHT_${i}.fits ]; then
	echo "Base Weight Not Created!"
	log_status $i
	exit
    fi

done

log_status $?
