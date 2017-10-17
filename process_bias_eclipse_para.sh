#!/bin/bash
set -xv
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# the script processes a set of BIAS/DARK frames.
# The images are overscan corrected and stacked without
# any rescaling. This script is the parallel version
# and uses the 'preprocess' program to perform the
# reduction. In contrary to the script version based
# on FLIPS, the individual preprocessed images are NOT
# saved to disk but only the final coadded calibration
# frames.
# It assumes that all images from ONE chip reside
# in the same physical directory

# $1: master directory
# $2: subdirectory with the BIAS/DARK images
# $3: chips to work on
 
# The result images are in the $1/$2 directory and have
# the same basic name as the subdirectory, e.g.
# The images are in .../BIAS. Then the stacked 
# images have the names .../BIAS/BIAS_i.fits, where i=1..NCHIPS.

#
# 27.04.2005:
# I rewrote the script to use the MAXIMAGE parameter in preprocess
# and the imcat-based imcombflat for the actual coaddition.
#
# 14.08.2005:
# The preprocess calls now explicitely declare the statistics
# region on the command line.
#
# 05.12.2005:
# - Chips whose NOTPROCESS flag is set are not processed at all.
# - The final co-addition for the master bias now uses the clipped
#   mean algorithm from imcombflat.
#
# 22.12.2005:
# I changed back the final co-addition to median stacking
# (with initial rejection of the highest value at each pixel 
# position).
# The clipped mean turned out to be too affected by outliers.

# preliminary work:
. ${INSTRUMENT:?}.ini

#
# the resultdir is where the output coadded images
# will go. If ONE image of the corresponding chip
# is a link the image will go to THIS directory
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
    FILES=`ls $1/$2/*_${CHIP}.fits`
    
    for FILE in ${FILES}
    do
          if [ -L ${FILE} ]; then
            LINK=`${P_READLINK} ${FILE}`
            BASE=`basename ${LINK} .fits`
            DIR=`dirname ${LINK}`
            ln -s ${DIR}/${BASE}OC.fits $1/$2/${BASE}OC.fits
            RESULTDIR[${CHIP}]=`dirname ${LINK}`
          fi
    done
  
    # check whether the result (a FITS image with the
    # proper name is already there; if yes, do nothing !!
    if [ -f ${RESULTDIR[${CHIP}]}/$2_${CHIP}.fits ]; then
        echo "${RESULTDIR[${CHIP}]}/$2_${CHIP}.fits already present !!! Exiting !!"
	#adam-BL# log_status 1 "${RESULTDIR[${CHIP}]}/$2_${CHIP}.fits already present"
	echo "adam-look | error: ${RESULTDIR[${CHIP}]}/$2_${CHIP}.fits already present"
        exit 1
    fi
  
    MAXX=$(( ${CUTX[${CHIP}]} + ${SIZEX[${CHIP}]} - 1 ))
    MAXY=$(( ${CUTY[${CHIP}]} + ${SIZEY[${CHIP}]} - 1 ))
  
    # overscan correct and trim BIAS frames
    ${P_IMRED_ECL:?} `ls $1/$2/*_${CHIP}.fits` \
        -MAXIMAGES ${NFRAMES}\
        -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
        -OVERSCAN Y \
        -OVERSCAN_REGION ${OVSCANX1[${CHIP}]},${OVSCANX2[${CHIP}]} \
        -OUTPUT Y \
        -OUTPUT_DIR /$1/$2/ \
        -TRIM Y \
        -OUTPUT_SUFFIX OC.fits \
        -TRIM_REGION ${CUTX[${CHIP}]},${MAXX},${CUTY[${CHIP}]},${MAXY}
  
    # and combine them
    ls -1 $1/$2/*_${CHIP}OC.fits > bias_images_$$
    ${P_IMCOMBFLAT_IMCAT} -i  bias_images_$$\
                    -o ${RESULTDIR[${CHIP}]}/$2_${CHIP}.fits \
                    -e 0 1
  
    if [ "${RESULTDIR[${CHIP}]}" != "$1/$2" ]; then
      ln -s ${RESULTDIR[${CHIP}]}/$2_${CHIP}.fits $1/$2/$2_${CHIP}.fits
    fi

    rm -f bias_images_$$
    
  fi
done

#adam-BL# log_status $?
