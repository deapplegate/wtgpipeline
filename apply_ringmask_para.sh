#!/bin/bash
set -xv
#adam-does# Apply ring mask to weight files for coaddition. Cuts out poorly calibrated outer area of chips.
#adam-use# Use at the end of preprocess-masking stage (before by-hand masking)
#adam-example# ./parallel_manager.sh ./adam_apply_RADIAL_MASK_para.sh ${SUBARUDIR} ${SUBARUDIR}/MACS0416-24/W-S-Z+_2010-11-04/SCIENCE/ ${SUBARUDIR}/MACS0416-24/W-S-Z+_2010-11-04/WEIGHTS/ OCF
########################
#$Id: apply_ringmask_para.sh,v 1.5 2009-07-17 02:54:49 anja Exp $
#######################
#
########################

#$1 : subaru directory
#$2 : coadd directory (full path)
#$3 : extension
#$4 : chip numbers

########################

#adam-BL#. BonnLogger.sh
#adam-BL#. log_start

. progs.ini > /tmp/progs.out 2>&1 

subarudir=$1
coadddir=$2
ext=$3
CHIPS=$4

###################
# Loop over chips

for chip in $CHIPS; do

    filebases=`find $coadddir/ -name \*_${chip}${ext}.fits -exec basename {} .fits \;`

    #adam-BL#if [ -z "${filebases}" ]; then
    #adam-BL#   ./BonnLogger.py comment "apply_ringmask_parap.sh - No Files Found: Chip ${chip}"
    #adam-BL#fi

    for base in $filebases; do

	config=`dfits ${coadddir}/${base}.fits | fitsort -d CONFIG | awk '{print $2}'`

	maskdir=${subarudir}/RADIAL_MASKS/${INSTRUMENT}_${config}
	ringmask=${maskdir}/RadialMask_${config}_${chip}.fits

	if [ -f "${ringmask}" ]; then

	    weight=${coadddir}/${base}.weight.fits
	    flag=${coadddir}/${base}.flag.fits
	    newweight=${coadddir}/${base}.newweight.fits

	    ${P_WW} -c lensconf/poly_flag.ww \
		-WEIGHT_NAMES $weight,$ringmask \
		-WEIGHT_MIN -1e12,.5 \
		-WEIGHT_MAX 1e12,1.5 \
		-WEIGHT_OUTFLAGS 0,0 \
		-FLAG_NAMES "" \
		-OUTWEIGHT_NAME ${newweight} \
		-OUTFLAG_NAME ""

	    if [ $? -gt 0 ]; then
		#adam-BL#log_status 2 "Weight watcher failed on $base"
		exit 2
	    fi
	    
	    mv ${newweight} $weight

	    if [ $? -gt 0 ]; then
		#adam-BL#log_status 3 "Can't move weight file $base"
		exit 3
	    fi
	fi
	

    done

done

#adam-BL#log_status 0
