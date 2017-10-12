#!/bin/bash
set -xv
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start

#"$Id: test_run_prep.sh,v 1.5 2009-01-13 17:57:19 dapple Exp $"

#######
# Verifies that all files (BIAS, FLAT, SCIENCE, DARK) are in the directory
# and that the SCIENCE images are properly split.
#######

#$1 run directory
#$2 flat dir
#$3 science dir

. ${INSTRUMENT:?}.ini

for ((chip=1;chip<=${NCHIPS};chip+=1)); do

    if [ ! -r $1/BIAS/BIAS_${chip}.fits ]; then
	echo "Missing Bias Frames: $chip"
	#adam-BL# log_status 1 "Missing Bias Frames: $chip"
	echo "adam-look | error: Missing Bias Frames: $chip"
	exit 1
    fi

    if [ ! -e $1/$2/$2_${chip}.fits ]; then
	echo "Missing Flat Frames: $chip"
	#adam-BL# log_status 1 "Missing Bias Frames: $chip"
	echo "adam-look | error: Missing Bias Frames: $chip"
	exit 2
    fi
done

ls $1/$3/ORIGINALS/*.fits | {

    while read file
    do
	base=`basename $file .fits`
	nfiles=`ls -1 $1/$3/SPLIT_IMAGES/${base}_*.fits | wc | awk '{print $1}'`
	if [ "${NCHIPS}" -ne "${nfiles}" ]; then
	    for ((chip=1;chip<=${NCHIPS};chip+=1)); do
		if [ ! -e $1/$3/SPLIT_IMAGES/${base}_${chip}.fits ]; then
		    echo "Missing ${base}_${chip}.fits"
		fi
	    done
	    echo "Missing SPLIT file: $file"
	    #adam-BL# log_status 1 "Missing SPLIT files: $file"
	    echo "adam-look | error: Missing SPLIT files: $file"
	    exit 3
	fi
    done

}

ls $1/$3/ORIGINALS/*.fits | {

    while read file
    do
	base=`basename $file .fits`
	nfiles=`ls -1 $1/$3/${base}_*OC.fits | wc | awk '{print $1}'`
	if [ $nfiles -eq 0 ]; then
	    nfiles=`ls -1 $1/$3/OC_IMAGES/${base}_*OC.fits | wc | awk '{print $1}'`
	fi
	if [ "${NCHIPS}" -ne "${nfiles}" ]; then
	    for ((chip=1;chip<=${NCHIPS};chip+=1)); do
		if [ ! -e $1/$3/${base}_${chip}OC.fits ] || \
		    [ ! -e $1/$3/OC_IMAGES/${base}_${chip}OC.fits ]; then
		    echo "Missing ${base}_${chip}OC.fits"
		fi
	    done
	    echo "Missing OC files: $file"
	    #adam-BL# log_status 4 "Missing OC files: $file"
	    echo "adam-look | error: Missing OC files: $file"
	    exit 4
	fi
    done

}

#adam-BL# log_status 0
