#!/bin/bash
set -xv
#. BonnLogger.sh
#. log_start

# $Id: process_bias_4channels_eclipse_para.sh,v 1.1 2009-01-29 00:09:09 anja Exp $

## this script is derived from
##  process_bias_eclipse_para.sh
## but takes images with several readout channels
## (currently four for SuprimeCam)

# $1: master directory
# $2: subdirectory with the BIAS/DARK images
# $3: chips to work on
 


# preliminary work:
. ${INSTRUMENT:?}.ini > /tmp/instrum.out 2>&1

for CHIP in $3
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then

    #adam-added# I added this so that I don't keep getting this trying to process BIAS_#.fits
    \ls -1 $1/$4/*_${CHIP}.fits > files_${CHIP}_$$
    FILES=`grep -v "BIAS_${CHIP}.fits" files_${CHIP}_$$`
    rm -f files_${CHIP}_$$
    if [ -z "${FILES}" ]; then
	    continue
    fi


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
	  -OUTPUT_DIR /$1/$2/ \
	  -TRIM Y \
	  -OUTPUT_SUFFIX OC_CH${CHANNEL}.fits \
	  -TRIM_REGION ${CUTX[${NCHIP}]},${MAXX},${CUTY[${CHIP}]},${MAXY}
  
    CHANNEL=$(( ${CHANNEL} + 1 ))
    done

#---> paste four fits files
    for file in ${FILES}
    do
	basename=`basename $file .fits`
	./horizontal_paste.py -o ${1}/${2}/${basename}OC.fits `ls ${1}/${2}/${basename}OC_CH*.fits`
    done

    # and combine them
    ls -1 $1/$2/*_${CHIP}OC.fits > bias_images_$$
    ${P_IMCOMBFLAT_IMCAT} -i  bias_images_$$\
                    -o ${1}/${2}/$2_${CHIP}.fits \
                    -e 0 1

    rm -f bias_images_$$

  fi
done

#log_status $?
