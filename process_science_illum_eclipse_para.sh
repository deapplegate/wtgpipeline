#!/bin/bash -xv
. BonnLogger.sh
. log_start


#CVSID="$Id: process_science_illum_eclipse_para.sh,v 1.13 2008-09-08 18:09:13 dapple Exp $"
# the script corrects a set of Science frames
# for illumination pattern. This is an effective
# second flat-fielding. 
# The script uses the 'preprocess' program to perform the
# reduction.
# It assumes that all images from ONE chip reside
# in the same physical directory
#
# 28.07.2004:
# new RESCALE flag; it was introduced so that the user can decide
# whether the gain equalisation is done here with Superflats
# or in the process_science step with skyflats. 
#
# 14.08.2005:
# The preprocess calls now explicitely declare the statistics
# region on the command line.
#
# 02.05.2005:
# The preprocess call now uses the MAXIMAGES parameter.
#
# 05.12.2005:
# - Chips whose NOTPROCESS flag is set are not processed at
#   all
# - Chips whose NOTUSE flag is set are not considered in the
#   Flatscale images.
# - New command line argument: The 4th command line argument now
#   determined whether images are superflatted with the original
#   (parameter value SUPER),
#   unsmoothed superflat or the illumination correction image
#   (parameter value ILLUM).
# - I corrected a bug in the indexing of NOTPROCESS arrays.

# $1: main directory (filter)
# $2: Science directory
# $3: RESCALE/NORESCALE
# $4: ILLUM/SUPER (Is the illumination correction done with
#     the 'illumination correction image' or with the unsmoothed
#     superflat?)
# $5: smooth scale
# $6: directory to find files
# $7: chips to be processed


# preliminary work:
. ${INSTRUMENT:?}.ini

ILLUMFLAG=""

if [ "$4" != "SUPER" ]; then
    ILLUMFLAG="_illum${5}"
fi

for CHIP in $7
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    RESULTDIR[${CHIP}]="$1/$6"
  else
    echo "Chip ${CHIP} will not be processed in $0"  
  fi
done

for CHIP in $7
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    FILES=`ls $1/$6/*_${CHIP}OCF.fits`
    MOVE_OCF=1
    if [ "$FILES" = "" ]; then
	FILES=`ls $1/$6/OCF_IMAGES/*_${CHIP}OCF.fits`
	MOVE_OCF=0
    fi

    for FILE in ${FILES}
    do
      if [ -L ${FILE} ]; then
	   LINK=`${P_READLINK} ${FILE}`
	   BASE=`basename ${LINK} .fits`
	   DIR=`dirname ${LINK}`
	   ln -s ${DIR}/${BASE}S.fits $1/$6/${BASE}S.fits
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
          FLATSTR="/$1/$2/$2_${i}${ILLUMFLAG}.fits"
          j=2
        else
          FLATSTR="${FLATSTR},/$1/$2/$2_${i}${ILLUMFLAG}.fits"
        fi   
      fi 
      i=$(( $i + 1 ))
    done
 

    RESCALEFLAG=""
    if [ "$3" = "RESCALE" ]; then   
      RESCALEFLAG="-FLAT_SCALE Y -FLAT_SCALEIMAGE ${FLATSTR}"
    fi

    ${P_IMRED_ECL:?} ${FILES} \
	-MAXIMAGES ${NFRAMES} \
	-STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
	-OVERSCAN N \
	-BIAS N \
	-FLAT Y \
	-FLAT_IMAGE /$1/$2/$2_${CHIP}${ILLUMFLAG}.fits \
	-FLAT_THRESHHOLD .1 \
	-COMBINE N \
	-OUTPUT Y \
	-OUTPUT_DIR /$1/$6/ \
	-OUTPUT_SUFFIX S.fits \
	-TRIM N ${RESCALEFLAG}

    exit_status=$?
    
    if [ ! -d /$1/$6/OCF_IMAGES ]; then
       mkdir /$1/$6/OCF_IMAGES
    fi
    if [ $MOVE_OCF -eq 1 ]; then
	mv $1/$6/*_${CHIP}OCF.fits /$1/$6/OCF_IMAGES
    fi

  fi
done






log_status $exit_status
