#!/bin/bash -xv
. BonnLogger.sh
. log_start
# the script processes a set of Standard star frames
# the images are overscan corrected, debiased and flatfielded.
# For further processing superflats are NOT created from the
# preprocessed standards but the corresponding files from
# the SCIENCE frames are copied. 
# The script uses the 'preprocess' program to perform the
# reduction. 
# It assumes that all images from ONE chip reside
# in the same physical directory
#

#$1: main directory (filter)
#$2: Bias directory
#$3: Flat directory
#$4: Standard directory
#$5: RESCALE/NORESCALE
#$6: chips to be processed

# preliminary work:
. ${INSTRUMENT:?}.ini

# the resultdir is where the output coadded images
# will go. If ONE image of the corresponding chip
# is a link the image will go to THIS directory

if [ ! -d /$1/$4/SPLIT_IMAGES ]; then
    mkdir /$1/$4/SPLIT_IMAGES
fi

for CHIP in $6
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
      RESULTDIR="$1/$4"
  else
    echo "Chip ${CHIP} will not be processed in $0"  
  fi
done

# perform preprocessing (overscan correction,
# BIAS subtraction, first flatfield pass)
for CHIP in $6
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    FILES=`ls $1/$4/SUPA*_${CHIP}.fits`
    MOVE_SPLIT=1
    if [ ${NOREDO:-0} -eq 0 ] && [ "$FILES" == "" ]; then
	FILES=`ls $1/$4/SPLIT_IMAGES/SUPA*_${CHIP}.fits`
	MOVE_SPLIT=0
    fi
  
    MAXX=$(( ${CUTX[${CHIP}]} + ${SIZEX[${CHIP}]} - 1 ))
    MAXY=$(( ${CUTY[${CHIP}]} + ${SIZEY[${CHIP}]} - 1 ))
  
    # build up list of all flatfields necessary for rescaling
    # when gains between chips are equalised here.
    i=1
    j=1
    FLATSTR=""
    while [ "${i}" -le "${NCHIPS}" ]
    do
      if [ ${NOTUSE[${i}]:=0} -eq 0 ] && [ ${NOTPROCESS[${i}]:=0} -eq 0 ]; then
        if [ "${j}" = "1" ]; then
          FLATSTR="/$1/$3/$3_${i}.fits"
	  j=2
        else
          FLATSTR="${FLATSTR},/$1/$3/$3_${i}.fits"
        fi
      fi    
      i=$(( $i + 1 ))
    done
  
    FLATFLAG=""
    if [ "$5" = "RESCALE" ]; then   
      FLATFLAG="-FLAT_SCALE Y -FLAT_SCALEIMAGE ${FLATSTR}" 
    fi
  
    # overscan correct, bias subtract and flatfield
    # science images:
    ${P_IMRED_ECL:?} ${FILES} \
      -MAXIMAGES ${NFRAMES}\
      -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
      -OVERSCAN Y \
      -OVERSCAN_REGION ${OVSCANX1[${CHIP}]},${OVSCANX2[${CHIP}]} \
      -BIAS Y \
      -BIAS_IMAGE /$1/$2/$2_${CHIP}.fits \
      -FLAT Y \
      -FLAT_IMAGE /$1/$3/$3_${CHIP}.fits \
      -FLAT_THRESHHOLD .1 \
      -COMBINE N \
      -OUTPUT Y \
      -OUTPUT_DIR /$1/$4/ \
      -OUTPUT_SUFFIX OCF.fits \
      -TRIM Y \
      -TRIM_REGION ${CUTX[${CHIP}]},${MAXX},${CUTY[${CHIP}]},${MAXY} ${FLATFLAG}

    exit_code=$?
  
  fi

  if [ "$MOVE_SPLIT" = "1" ]; then
      mv /$1/$4/SUPA*_${CHIP}.fits /$1/$4/SPLIT_IMAGES
  fi

done

log_status $exit_code
