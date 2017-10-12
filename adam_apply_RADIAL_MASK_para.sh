#!/bin/bash
set -xv

#pretty sure you don't actually want to use this!
#adam-does# Apply ring mask to weight files for coaddition. Cuts out poorly calibrated outer area of chips.
#adam-use# Use at the end of preprocess-masking stage (before by-hand masking)
#adam-example# ./parallel_manager.sh ./adam_apply_RADIAL_MASK_para.sh ${SUBARUDIR} ${SUBARUDIR}/MACS0416-24/W-S-Z+_2010-11-04/SCIENCE/ ${SUBARUDIR}/MACS0416-24/W-S-Z+_2010-11-04/WEIGHTS/ OCF
#adam-example# ./parallel_manager.sh ./adam_apply_RADIAL_MASK_para.sh ${SUBARUDIR} ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE/ ${SUBARUDIR}/${cluster}/${filter}_${run}/WEIGHTS/ ${ending}
#adam-successor# this replaces apply_RADIAL_MASK_para.sh and apply_ringmask_para.sh
########################
#$Id: apply_ringmask_para.sh,v 1.5 2009-07-17 02:54:49 anja Exp $
#######################
########################

#$1 : subaru directory
#$2 : science directory (full path)
#$3 : weight directory (full path)
#$4 : extension
#$5 : chip numbers

########################

. progs.ini

subarudir=$1
## sciencedir and weightdir are FULL paths!
sciencedir=$2
weightdir=$3
ext=$4
CHIPS=$5

###################
# Loop over chips

for chip in $CHIPS; do

    filebases=`find $sciencedir/ -name \*_${chip}${ext}.fits -exec basename {} .fits \;`

    for base in $filebases; do

	config=`dfits ${sciencedir}/${base}.fits | fitsort -d CONFIG | awk '{print $2}'`

	maskdir=${subarudir}/RADIAL_MASKS/${INSTRUMENT}_${config}
	ringmask=${maskdir}/RadialMask_${config}_${chip}.fits

	if [ -f "${ringmask}" ]; then

	    weight=${weightdir}/${base}.weight.fits
	    if [ -L $weight ];then
		    weight=`readlink -f $weight`
	    fi
	    #flag=${weightdir}/${base}.flag.fits
	    #newflag=${weightdir}/${base}.newflag.fits
	    newweight=${weightdir}/${base}.newweight.fits

	    echo "ringmask=" `ls $ringmask`
	    echo "weight=" `ls $weight`
	    #echo "flag=" `ls $flag`

	    ${P_WW} -c lensconf/poly_flag.ww \
	        -WEIGHT_NAMES $weight,$ringmask \
	        -WEIGHT_MIN -1e12,.5 \
	        -WEIGHT_MAX 1e12,1.5 \
	        -WEIGHT_OUTFLAGS 0,0 \
	        -FLAG_NAMES "" \
	        -OUTWEIGHT_NAME ${newweight} \
	        -OUTFLAG_NAME ""
	    ## I don't know how to fix the flags in addition to the weights, I'll have to change WEIGHT_OUTFLAGS and FLAG_OUTFLAGS, but how?
	    #${P_WW} -c lensconf/poly_flag.ww \
	    #    -WEIGHT_NAMES $weight,$ringmask \
	    #    -WEIGHT_MIN -1e12,.5 \
	    #    -WEIGHT_MAX 1e12,1.5 \
	    #    -WEIGHT_OUTFLAGS 0,0 \
	    #    -FLAG_NAMES $flag \
	    #    -OUTWEIGHT_NAME ${newweight} \
	    #    -OUTFLAG_NAME $newflag

	    if [ $? -gt 0 ]; then
		exit 2
	    fi
	    
	   mv ${newweight} $weight
	   #mv ${newflag} $flag

	    if [ $? -gt 0 ]; then
		exit 3
	    fi
	fi
	

    done

done

