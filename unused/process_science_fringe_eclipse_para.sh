#!/bin/bash -xv

# the script corrects a set of Science frames
# for fringe pattern. 
# The script uses the 'preprocess' program to perform the
# reduction.
# It assumes that all images from ONE chip reside
# in the same physical directory

# $1: main directory (filter)
# $2: science directory
# $3: chips to be processed

# 02.05.2005:
# The preprocess call now uses the MAXIMAGES parameter.
#
# 14.08.2005:
# The preprocess calls now explicitely declare the statistics
# region on the command line.
#
# 05.12.2005:
# Chips whote NOTPROCESS flag is set are not processed at all.

# preliminary work:
. ${INSTRUMENT:?}.ini

for CHIP in $3
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    RESULTDIR[${CHIP}]="$1/$2"
  else
    echo "Chip ${CHIP} will not be processed in $0" 
  fi
done

for CHIP in $3
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    FILES=`ls $1/$2/*_${CHIP}OFCS.fits`
  
    for FILE in ${FILES}
    do
      if [ -L ${FILE} ]; then
  	 LINK=`${P_READLINK} ${FILE}`
  	 BASE=`basename ${LINK} .fits`
  	 DIR=`dirname ${LINK}`
  	 ln -s ${DIR}/${BASE}F.fits $1/$2/${BASE}F.fits
  	 RESULTDIR[${CHIP}]=`dirname ${LINK}`  
      fi  
    done 
  
    ${P_IMRED_ECL:?} ${FILES} \
         -MAXIMAGES ${NFRAMES}\
         -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
         -OVERSCAN N \
         -BIAS N \
         -FLAT N \
         -COMBINE N \
         -FRINGE Y \
         -FRINGE_IMAGE /$1/$2/$2_${CHIP}_fringe.fits \
         -FRINGE_REFIMAGE /$1/$2/$2_${CHIP}_illum.fits \
         -OUTPUT Y \
         -OUTPUT_DIR /$1/$2/ \
         -OUTPUT_SUFFIX F.fits \
         -TRIM N
  
    if [ ! -d /$1/$2/OFCS_IMAGES ]; then
       mkdir /$1/$2/OFCS_IMAGES
    fi
    mv /$1/$2/*_${CHIP}OFCS.fits /$1/$2/OFCS_IMAGES
  fi
done




