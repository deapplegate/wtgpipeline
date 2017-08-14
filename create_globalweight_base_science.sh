#!/bin/bash -xv
. BonnLogger.sh
. log_start

# CVSID: $Id: create_globalweight_base_science.sh,v 1.1 2009-02-05 22:54:31 anja Exp $

# same as create_globalweight_base.sh ; but with the unsmoothed superflat

# $1 : run dir
# $2 : norm flat dir
# $3 : norm illum dir
# $4 : superflat method: SUPER or ILLUM

. ${INSTRUMENT:?}.ini

ILLUMFLAG=""

if [ "$4" != "SUPER" ]; then
    ILLUMFLAG="_illum"
fi

if [ ! -d $1/BASE_WEIGHT ]; then
    mkdir $1/BASE_WEIGHT
fi

for ((i=1;i<=${NCHIPS};i+=1)); do

    ic '%1 %2 *' $1/$2/${2}_${i}.fits $1/$3/${3}_${i}${ILLUMFLAG}.fits > $1/BASE_WEIGHT/BASE_WEIGHT_${i}.fits
    if [ ! -e $1/BASE_WEIGHT/BASE_WEIGHT_${i}.fits ]; then
	echo "Base Weight Not Created!"
	log_status $i
	exit
    fi

done

log_status $?
