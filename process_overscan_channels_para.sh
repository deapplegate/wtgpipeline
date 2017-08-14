#!/bin/bash -xv
. BonnLogger.sh
. log_start

# $Id: process_overscan_channels_para.sh,v 1.3 2009-01-29 00:09:09 anja Exp $

## this script does only overscan correction, but takes
## images with several readout channels.
## (at the moment, these are the four channels as read
## by SuprimeCam).

## this script is derived from
## process_bias_eclipse_para.sh

# $1: master directory
# $2: subdirectory with the BIAS/DARK images
# $3: chips to work on
 


# preliminary work:
. ${INSTRUMENT:?}.ini

for CHIP in $3
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then

    FILES=`ls ${1}/${2}/*_${CHIP}.fits`

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
    for file in ${FILES}; do
	basename=`basename $file .fits`
	./horizontal_paste.py -o ${1}/${2}/${basename}OC.fits `ls ${1}/${2}/${basename}OC_CH*.fits`
    done

  fi
done

log_status $?
