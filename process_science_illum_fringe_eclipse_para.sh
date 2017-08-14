#!/bin/bash -xv
. BonnLogger.sh
. log_start

#CVSID="$Id: process_science_illum_fringe_eclipse_para.sh,v 1.13 2008-09-08 18:09:13 dapple Exp $"
# the script corrects a set of Science frames
# for illumination pattern and subtracts a fringe
# pattern at the same time by estimating appropriate
# scaling factors for the fringe frame to subtract. 
# The script uses the 'preprocess' program to perform the
# reduction. 
# It assumes that all images from ONE chip reside
# in the same physical directory

# 25.11.2003:
# in the links that are created, the supplementary ending
# of the images was S.fits instead of SF.fits

# 28.07.2004:
# new RESCALE flag; it was introduced so that the user can decide
# whether the gain equalisation is done here with Superflats
# or in the process_science step with skyflats. 

# 02.05.2005:
# The preprocess call now uses the MAXIMAGES parameter.

# 14.08.2005:
# The preprocess calls now explicitely declare the statistics
# region on the command line.

#
# 05.12.2005:
# - Chips whose NOTPROCESS flag is set are not processed at all.
# - Chips whose NOTUSE flag is set are not considered for flat scaling.

# $1: main directory (filter)
# $2: Science directory
# $3: RESCALE/NORESCALE
# $4: smoothing scale
# $5: file directory
# $6: chips to be processed

# preliminary work:
. ${INSTRUMENT:?}.ini
echo $6
for CHIP in $6
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then 
    RESULTDIR[${CHIP}]="$1/$5"
  else
    echo "Chip ${CHIP} will not be processed in $0" 
  fi
done

for CHIP in $6
do
    
    if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then 
	FILES=`ls /$1/$5/*_${CHIP}OCF.fits`
	MOVE_OCF=1
	if [ "$FILES" = "" ]; then
	    FILES=`ls $1/$5/OCF_IMAGES/*_${CHIP}OCF.fits`
	    MOVE_OCF=0
	fi
    fi
    
    for FILE in ${FILES}
    do
	if [ -L ${FILE} ]; then
  	    LINK=`${P_READLINK} ${FILE}`
  	    BASE=`basename ${LINK} .fits`
  	    DIR=`dirname ${LINK}`
  	    ln -s ${DIR}/${BASE}SF.fits $1/$5/${BASE}SF.fits
  	    RESULTDIR[${CHIP}]=`dirname ${LINK}`    
	fi
    done 
    
    i=1
    j=1
    FLATSTR=""
    while [ "${i}" -le "${NCHIPS}" ]
    do
	if [ ${NOTUSE[${i}]:=0} -eq 0 ] && [ ${NOTPROCESS[${i}]:=0} -eq 0 ]; then
            if [ "${j}" = "1" ]; then
		FLATSTR="/$1/$2/$2_${i}_illum${4}.fits"
  		j=2
            else
		FLATSTR="${FLATSTR},/$1/$2/$2_${i}_illum${4}.fits"
            fi    
	fi
	i=$(( $i + 1 ))
    done
   
    RESCALEFLAG=""
    if [ "$3" = "RESCALE" ]; then   
      RESCALEFLAG="-FLAT_SCALE Y -FLAT_SCALEIMAGE ${FLATSTR}"
    fi
    
    ${P_IMRED_ECL:?} ${FILES} \
        -MAXIMAGES ${NFRAMES}\
         -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
        -OVERSCAN N \
        -BIAS N \
        -FLAT Y \
        -FLAT_IMAGE /$1/$2/$2_${CHIP}_illum${4}.fits \
	-FLAT_THRESHHOLD .1 \
        -FRINGE Y \
        -FRINGE_IMAGE /$1/$2/$2_${CHIP}_fringe${4}.fits \
        -FRINGE_REFIMAGE /$1/$2/$2_${CHIP}_illum${4}.fits \
        -COMBINE N \
        -OUTPUT Y \
        -OUTPUT_DIR /$1/$5/ \
        -OUTPUT_SUFFIX SF.fits \
        -TRIM N ${RESCALEFLAG}
    
    exit_status=$?
    
    if [ ! -d /$1/$5/OCF_IMAGES ]; then
	mkdir /$1/$5/OCF_IMAGES
    fi 
    if [ $MOVE_OCF -eq 1 ]; then
	mv /$1/$5/*_${CHIP}OCF.fits /$1/$5/OCF_IMAGES
    fi
    
done






log_status $exit_status
