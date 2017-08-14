#!/bin/bash -xv
. BonnLogger.sh
. log_start
#SCRIPT that preps SCIENCE images for experimentation with flatfields

#$Id: prep_science_para.sh,v 1.15 2009-02-10 19:34:42 anja Exp $


#$1: Run directory
#$2: BIAS directory
#$3: SCIENCE directory
#$4: chips to be processed

# preliminary work:
. ${INSTRUMENT:?}.ini

# perform preprocessing (overscan correction,
# BIAS subtraction)

if [ ! -d /$1/$3/SPLIT_IMAGES ]; then
    mkdir /$1/$3/SPLIT_IMAGES
fi

for CHIP in $4
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    FILES=`ls $1/$3/${PREFIX}*_${CHIP}.fits`
    MOVE_SPLIT=1
    if [ "$FILES" = "" ]; then
	#for rerunability
	FILES=`ls $1/$3/SPLIT_IMAGES/${PREFIX}*_${CHIP}.fits`
	MOVE_SPLIT=0
    fi

    if [ "$FILES" = "" ]; then
	log_status 2 "No Files Found"
	exit 2
    fi

    if [ ! -s $1/$2/BIAS_${CHIP}.fits ]; then
	log_status 3 "No Bias Image"
	exit 3
    fi
  
    MAXX=$(( ${CUTX[${CHIP}]} + ${SIZEX[${CHIP}]} - 1 ))
    MAXY=$(( ${CUTY[${CHIP}]} + ${SIZEY[${CHIP}]} - 1 ))
  
    # overscan correct, bias subtract
    # science images:
    ${P_IMRED_ECL:?} ${FILES} \
      -MAXIMAGES ${NFRAMES}\
      -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
      -OVERSCAN Y \
      -OVERSCAN_REGION ${OVSCANX1[${CHIP}]},${OVSCANX2[${CHIP}]} \
      -BIAS Y \
      -BIAS_IMAGE $1/$2/BIAS_${CHIP}.fits \
      -COMBINE N \
      -OUTPUT Y \
      -OUTPUT_DIR $1/$3 \
      -OUTPUT_SUFFIX OC.fits \
      -TRIM Y \
      -TRIM_REGION ${CUTX[${CHIP}]},${MAXX},${CUTY[${CHIP}]},${MAXY} ${FLATFLAG}

    exit_code=$?
  
  fi

  if [ $MOVE_SPLIT -eq 1 ]; then
      mv /$1/$3/*_${CHIP}.fits /$1/$3/SPLIT_IMAGES
  fi


done
log_status $exit_code
