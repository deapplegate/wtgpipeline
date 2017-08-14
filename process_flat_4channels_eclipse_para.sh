#!/bin/bash -xv
#. BonnLogger.sh
#. log_start
# CVSId: $Id: process_flat_4channels_eclipse_para.sh,v 1.1 2009-01-29 00:09:09 anja Exp $

# the script processes a set of FLAT frames
# the images are overscan corrected, debiased and stacked with
# mode rescaling.
# The script uses the 'preprocess' program to perform the
# reduction. In contrary to the script version based
# on FLIPS, the individual preprocessed images are NOT
# saved to disk but only the final coadded calibration
# frames.

#$1: main directory (filter)
#$2: Bias directory
#$3: Flat directory
#$4: chips to process

# 02.05.2005:
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
for CHIP in $4
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    RESULTDIR[${CHIP}]="$1/$3"
  else
    echo "Chip ${CHIP} will not be processed in $0"  
  fi
done

# Correction overscan; create config file on the fly
# we do not assume that the overscan is the same for all chips

for CHIP in $4
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    FILES=`ls $1/$3/*_${CHIP}.fits`

    CHANNEL=1
    while [ "${CHANNEL}" -le "${NCHANNELS}" ]
    do

      NCHIP=$(( ${NCHIPS}*( ${CHANNEL} -1 ) + ${CHIP}))

      MAXX=$(( ${CUTX[${NCHIP}]} + ${SIZEX[${NCHIP}]} - 1 ))
      MAXY=$(( ${CUTY[${CHIP}]} + ${SIZEY[${CHIP}]} - 1 ))
  
    # overscan correct and trim BIAS frames
      ${P_IMRED_ECL:?} ${FILES} \
	  -MAXIMAGES ${NFRAMES}\
	  -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
	  -OVERSCAN Y \
	  -OVERSCAN_REGION ${OVSCANX1[${NCHIP}]},${OVSCANX2[${NCHIP}]} \
	  -OUTPUT Y \
	  -OUTPUT_DIR /$1/$3/ \
	  -TRIM Y \
	  -OUTPUT_SUFFIX OC_CH${CHANNEL}.fits \
	  -TRIM_REGION ${CUTX[${NCHIP}]},${MAXX},${CUTY[${CHIP}]},${MAXY}
  
    CHANNEL=$(( ${CHANNEL} + 1 ))
    done

#---> paste four fits files
    for file in ${FILES}; do
	basename=`basename $file .fits`
	./horizontal_paste.py -o ${1}/${3}/${basename}OC_CHall.fits `ls ${1}/${3}/${basename}OC_CH?.fits`
    done

    # bias correct FLAT frames
    ${P_IMRED_ECL:?} `ls /$1/$3/*_${CHIP}OC_CHall.fits` \
        -MAXIMAGES ${NFRAMES} \
        -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
        -BIAS Y \
        -BIAS_IMAGE /$1/$2/$2_${CHIP}.fits \
        -OUTPUT Y \
        -OUTPUT_DIR /$1/$3/ \
        -OUTPUT_SUFFIX OC.fits       

    ${P_RENAME} 's/OC_CHallOC/OC/g' /$1/$3/*${CHIP}OC_CHallOC.fits
  
    # and combine them
    ${P_IMSTATS} `ls /$1/$3/*_${CHIP}OC.fits`\
                 -s ${STATSXMIN} ${STATSXMAX} ${STATSYMIN} ${STATSYMAX}\
                 -o flat_images_$$
    ${P_IMCOMBFLAT_IMCAT} -i  flat_images_$$\
                    -o ${RESULTDIR[${CHIP}]}/$3_${CHIP}.fits \
                    -s 1 -e 0 1
  
    if [ "${RESULTDIR[${CHIP}]}" != "$1/$3" ]; then
      ln -s ${RESULTDIR[${CHIP}]}/$3_${CHIP}.fits $1/$3/$3_${CHIP}.fits
    fi  

    rm /$1/$3/*_${CHIP}OC_CH?.fits /$1/$3/*_${CHIP}OC_CHall.fits
    rm flat_images_$$
  fi
done

#log_status $?
