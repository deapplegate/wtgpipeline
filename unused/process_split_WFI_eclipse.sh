#!/bin/bash -xv

# splits WFI FIts extension images into the
# eight chips. Uses the eclipse utilities
# and also updates the image headers
#
# 16.02.2005:
# I now transfer also the OBJECTS keyword from the
# original files.
#
# 30.01.2006:
# The raw images now have to be already in a
# ORIGINALS subdirectory (from /$1/$2). They
# are no longer moved after extraction of 
# individual chips.
#
# 20.07.2007:
# I added the IMAGEID command line option to the
# mefsplit call. It is necessary due to a new 
# numbering scheme for WFI chips.

# $1: main directory
# $2: science directory

# create image list: we assume that ONLY unsplit
# images are in the directory

. WFI.ini


FILES=`ls $1/$2/ORIGINALS/*.fits`

cd /$1/$2/ORIGINALS

for FILE in ${FILES}
do
  FILT_KEY1=`${P_DFITS} ${FILE} | grep "FILT NAME"  | awk '{ print $1,$2,$3,$4,$5}'`
  FILT_KEY2=`${P_DFITS} ${FILE} | grep "FILT1 NAME" | awk '{ print $1,$2,$3,$4,$5}'`
  FILT_KEY1_A=${FILT_KEY1}_A
  FILT_KEY2_A=${FILT_KEY2}_A
  if [ "${FILT_KEY1_A}" = "HIERARCH ESO INS FILT NAME_A" ]; then
  {
     FILTNAM=`${P_DFITS} ${FILE} | ${P_FITSORT} "HIERARCH ESO INS FILT NAME" | awk '($1!="FILE") {print $2}'`
  }
  fi
  if [ "${FILT_KEY2_A}" = "HIERARCH ESO INS FILT1 NAME_A" ]; then
  {
     FILTNAM=`${P_DFITS} ${FILE} | ${P_FITSORT} "HIERARCH ESO INS FILT1 NAME" | awk '($1!="FILE") {print $2}'`
  }
  fi
  FILTNAM="'${FILTNAM}'"

  RA=`${P_DFITS}  ${FILE} | ${P_FITSORT} RA  | awk '($1!="FILE") {print $2}'`
  DEC=`${P_DFITS} ${FILE} | ${P_FITSORT} DEC | awk '($1!="FILE") {print $2}'`
  LST=`${P_DFITS} ${FILE} | ${P_FITSORT} LST | awk '($1!="FILE") {print $2}'`
  MJD=`${P_DFITS} ${FILE} | grep "MJD-OBS" | awk '{print $3}'`
  OBJECT=`${P_DFITS} ${FILE} | ${P_FITSORT} OBJECT | awk '($1!="FILE") {print $2}'`
  EXPTIME=`${P_DFITS} ${FILE} | ${P_FITSORT} EXPTIME | awk '($1!="FILE") {print $2}'`
  AIRMASS=`${P_AIRMASS} -t ${LST} -e ${EXPTIME} -r ${RA} -d ${DEC} -l -29.25694444`
  GABODSID=`${P_NIGHTID} -t 16:00:00 -d 31/12/1998 -m ${MJD} |\
      awk ' ($1 ~ /Days/) {print $6}' | awk 'BEGIN{ FS="."} {print $1}'`


  ${P_FITSSPLIT_ECL} -CRPIX1 \
    "${REFPIXX[1]},${REFPIXX[2]},${REFPIXX[3]},${REFPIXX[4]},${REFPIXX[5]},${REFPIXX[6]},${REFPIXX[7]},${REFPIXX[8]}"\
                     -CRPIX2 \
    "${REFPIXY[1]},${REFPIXY[2]},${REFPIXY[3]},${REFPIXY[4]},${REFPIXY[5]},${REFPIXY[6]},${REFPIXY[7]},${REFPIXY[8]}"\
                     -IMAGEID \
    "${IMAGEID[1]},${IMAGEID[2]},${IMAGEID[3]},${IMAGEID[4]},${IMAGEID[5]},${IMAGEID[6]},${IMAGEID[7]},${IMAGEID[8]}"\
                     -CRVAL1 ${RA} -CRVAL2 ${DEC}\
                     -EXPTIME ${EXPTIME}\
                     -AIRMASS ${AIRMASS}\
                     -GABODSID ${GABODSID}\
                     -FILTER ${FILTNAM}  \
                     -OBJECT ${OBJECT} \
                     -OUTPUT_DIR .. \
                     ${FILE}
done
