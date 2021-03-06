#!/bin/bash
set -xv
#applies radial masks to the SCIENCE_weighted/ images
#adam-example# ./parallel_manager.sh ./science_weighted_apply_RADIAL_MASK_para.sh ${SUBARUDIR} /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-J-V/SCIENCE_weighted/ OCFSIR SUPA0127
########################
#$Id: apply_ringmask_para.sh,v 1.5 2009-07-17 02:54:49 anja Exp $
#######################
# Apply ring mask to weight files for coaddition
# Cuts out poorly calibrated outer area of chips.
########################

#$1 : subaru directory
#$2 : coadd directory (full path)
#$3 : extension
#$4 : chip numbers

########################

#adam-BL#. BonnLogger.sh
#adam-BL#. log_start

. progs.ini > /tmp/out.log 2>&1

subarudir=$1
sciencewtdir=$2
ext=$3
filestart=$4
CHIPS=$5

###################
# Loop over chips

for chip in $CHIPS; do

    filebases=`find $sciencewtdir/ -name ${filestart}\*_${chip}${ext}.weighted.fits -exec basename {} .fits \;`

    #adam-BL#if [ -z "${filebases}" ]; then
    #adam-BL#   ./BonnLogger.py comment "apply_ringmask_parap.sh - No Files Found: Chip ${chip}"
    #adam-BL#fi

    config="10_3"
    maskdir=${subarudir}/RADIAL_MASKS/${INSTRUMENT}_${config}
    for base in $filebases; do

	ringmask=${maskdir}/RadialMask_${config}_${chip}.fits

	if [ -f "${ringmask}" ]; then

	    weighted=${sciencewtdir}/${base}.fits

	    ic '%1 %2 *' $weighted $ringmask > ${weighted}.tmp
	    mv ${weighted} ${weighted}.old
	    mv ${weighted}.tmp ${weighted}

	    if [ $? -gt 0 ]; then
		#adam-BL#log_status 2 "Weight watcher failed on $base"
		exit 2
	    fi
	    
	fi
	

    done

done

#adam-BL#log_status 0
