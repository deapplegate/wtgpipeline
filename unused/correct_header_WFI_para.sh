#!/bin/bash -xv

# script to prepare image headers of WFI images
# to prepare for runs through the LDAC
# pipeline.

# 07.05.03:
# introduced imageheader program for header
# update (replacing the replacekey strategy)
#
# 28.05.03:
# - the old images are no longer stored in an
#   UNCORR directory
# - introduced correct treatment of links
# 
# 13.12.03:
# chenaged the name of the temporary file tmp.fits
# to tmp_$$.fits to make it unique (otherwise files
# were deleted if processed on the same disk with
# the multi-processor option)

. WFI.ini

# $1: main dir
# $2: Science dir
# $3: extension before .fits (before the extension we have the chip number _i
# $4: chips to be processed


for CHIP in $4
do
  ls -1 /$1/$2/*_${CHIP}$3.fits > corrheaderimages_$$

  cat corrheaderimages_$$ |\
  {
    while read IMAGE
    do
  	echo "updating ${IMAGE}"
	
	FILT_KEY1=`${P_DFITS} ${IMAGE} | grep "FILT NAME"  | awk '{ print $1,$2,$3,$4,$5}'`
	FILT_KEY2=`${P_DFITS} ${IMAGE} | grep "FILT1 NAME" | awk '{ print $1,$2,$3,$4,$5}'`
	FILT_KEY1_A=${FILT_KEY1}_A
	FILT_KEY2_A=${FILT_KEY2}_A
	if [ "${FILT_KEY1_A}" = "HIERARCH ESO INS FILT NAME_A" ]; then
        {
           FILTNAM=`${P_DFITS} ${IMAGE} | ${P_FITSORT} "HIERARCH ESO INS FILT NAME" | awk '($1!="FILE") {print $2}'`
        }
        fi
	if [ "${FILT_KEY2_A}" = "HIERARCH ESO INS FILT1 NAME_A" ]; then
        {
           FILTNAM=`${P_DFITS} ${IMAGE} | ${P_FITSORT} "HIERARCH ESO INS FILT1 NAME" | awk '($1!="FILE") {print $2}'`
        }
        fi
	FILTNAM="'${FILTNAM}'"
	echo ${FILTNAM}
  	RA=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} RA  | awk '($1!="FILE") {print $2}'`
  	DEC=`${P_DFITS} ${IMAGE} | ${P_FITSORT} DEC | awk '($1!="FILE") {print $2}'`
  	LST=`${P_DFITS} ${IMAGE} | ${P_FITSORT} LST | awk '($1!="FILE") {print $2}'`
        MJD=`${P_DFITS} ${IMAGE} | grep "MJD-OBS" | awk '{print $3}'`
  	EXPTIME=`${P_DFITS} ${IMAGE} | ${P_FITSORT} EXPTIME | awk '($1!="FILE") {print $2}'`
  	AIRMASS=`${P_AIRMASS} -t ${LST} -e ${EXPTIME} -r ${RA} -d ${DEC} -l -29.25694444`
        GABODSID=`${P_NIGHTID} -t 16:00:00 -d 31/12/1998 -m ${MJD} |\
            awk ' ($1 ~ /Days/) {print $6}' | awk 'BEGIN{ FS="."} {print $1}'`

# take into account possible link
	REALIMAGE=${IMAGE}
    	DIR=`dirname ${IMAGE}`

	if [ -L ${IMAGE} ]; then
             REALIMAGE=`${P_READLINK} ${IMAGE}`
             DIR=`dirname ${REALIMAGE}`
	fi
     
        ${P_IMAGEHEADER} -i ${REALIMAGE} -o /${DIR}/tmp_$$.fits\
                         -CRPIX1 ${REFPIXX[${CHIP}]} -CRPIX2 ${REFPIXY[${CHIP}]}\
                         -CRVAL1 ${RA} -CRVAL2 ${DEC}\
                         -CD1_1 ${PIXSCX} -CD2_2 ${PIXSCY}\
                         -CD1_2 0. -CD2_1 0.\
                         -EXPTIME ${EXPTIME} -EQUINOX 2000.0\
                         -GABODSID ${GABODSID} -IMAGEID ${CHIP}\
                         -FILTER ${FILTNAM} -AIRMASS ${AIRMASS}
        mv /${DIR}/tmp_$$.fits ${REALIMAGE}        
    done
  }
done







