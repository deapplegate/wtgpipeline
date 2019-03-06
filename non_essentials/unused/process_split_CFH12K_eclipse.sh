#!/bin/bash -xv

# splits CFH12K Fits extension images into the
# eight chips. Uses the eclipse utilities
# and also updates the image headers
#

# $1: main directory
# $2: science directory

# create image list: we assume that ONLY unsplit
# images are in the directory

. CFH12K.ini


FILES=`ls $1/$2/ORIGINALS/*.fits`

cd /$1/$2/ORIGINALS

for FILE in ${FILES}
do
  FILTNAM=`${P_DFITS}  ${FILE} | ${P_FITSORT} FILTER  | awk '($1!="FILE") {print $2}'`

  RA=`${P_DFITS}  ${FILE} | ${P_FITSORT} RA  | awk '($1!="FILE") {print $2}'`
  RA=`${P_HMSTODECIMAL} ${RA}`
  DEC=`${P_DFITS} ${FILE} | ${P_FITSORT} DEC | awk '($1!="FILE") {print $2}'`
  DEC=`${P_DMSTODECIMAL} ${DEC}`
  LST=`${P_DFITS} ${FILE} | ${P_FITSORT} LST-OBS | awk '($1!="FILE") {print $2}'`
  LST=`echo ${LST} | awk -F: '{print 3600*$1+60*$2+$3}'`
  MJD=`${P_DFITS}  ${FILE} | ${P_FITSORT} MJD-OBS | awk '($1!="FILE") {print $2}'`
  OBJECT=`${P_DFITS} ${FILE} | ${P_FITSORT} OBJECT | awk '($1!="FILE") {print $2}'`
  EXPTIME=`${P_DFITS} ${FILE} | ${P_FITSORT} EXPTIME | awk '($1!="FILE") {print $2}'`
  AIRMASS=`${P_AIRMASS} -t ${LST} -e ${EXPTIME} -r ${RA} -d ${DEC} -l ${OBSLAT}`
  GABODSID=`${P_NIGHTID} -t ${REFERENCETIME} -d 31/12/1998 -m ${MJD} |\
      awk ' ($1 ~ /Days/) {print $6}' | awk 'BEGIN{ FS="."} {print $1}'`

  ${P_FITSSPLIT_ECL} -CRPIX1 \
    "${REFPIXX[1]},${REFPIXX[2]},${REFPIXX[3]},${REFPIXX[4]},${REFPIXX[5]},${REFPIXX[6]},${REFPIXX[7]},${REFPIXX[8]},${REFPIXX[9]},${REFPIXX[10]},${REFPIXX[11]},${REFPIXX[12]}"\
                     -CRPIX2 \
    "${REFPIXY[1]},${REFPIXY[2]},${REFPIXY[3]},${REFPIXY[4]},${REFPIXY[5]},${REFPIXY[6]},${REFPIXY[7]},${REFPIXY[8]},${REFPIXY[9]},${REFPIXY[10]},${REFPIXY[11]},${REFPIXY[12]}"\
                     -CRVAL1 ${RA} -CRVAL2 ${DEC}\
                     -M11 "${M11[1]},${M11[2]},${M11[3]},${M11[4]},${M11[5]},${M11[6]},${M11[7]},${M11[8]},${M11[9]},${M11[10]},${M11[11]},${M11[12]}"\
                     -M22 "${M22[1]},${M22[2]},${M22[3]},${M22[4]},${M22[5]},${M22[6]},${M22[7]},${M22[8]},${M22[9]},${M22[10]},${M22[11]},${M22[12]}"\
                     -M12 "${M12[1]},${M12[2]},${M12[3]},${M12[4]},${M12[5]},${M12[6]},${M12[7]},${M12[8]},${M12[9]},${M12[10]},${M12[11]},${M12[12]}"\
                     -M21 "${M21[1]},${M21[2]},${M21[3]},${M21[4]},${M21[5]},${M21[6]},${M21[7]},${M21[8]},${M21[9]},${M21[10]},${M21[11]},${M21[12]}"\
                     -CD11 "${CD11[1]},${CD11[2]},${CD11[3]},${CD11[4]},${CD11[5]},${CD11[6]},${CD11[7]},${CD11[8]},${CD11[9]},${CD11[10]},${CD11[11]},${CD11[12]}"\
                     -CD22 "${CD22[1]},${CD22[2]},${CD22[3]},${CD22[4]},${CD22[5]},${CD22[6]},${CD22[7]},${CD22[8]},${CD22[9]},${CD22[10]},${CD22[11]},${CD22[12]}"\
                     -CD12 "${CD12[1]},${CD12[2]},${CD12[3]},${CD12[4]},${CD12[5]},${CD12[6]},${CD12[7]},${CD12[8]},${CD12[9]},${CD12[10]},${CD12[11]},${CD12[12]}"\
                     -CD21 "${CD21[1]},${CD21[2]},${CD21[3]},${CD21[4]},${CD21[5]},${CD21[6]},${CD21[7]},${CD21[8]},${CD21[9]},${CD21[10]},${CD21[11]},${CD21[12]}"\
                     -IMAGEID "${IMAGEID[1]},${IMAGEID[2]},${IMAGEID[3]},${IMAGEID[4]},${IMAGEID[5]},${IMAGEID[6]},${IMAGEID[7]},${IMAGEID[8]},${IMAGEID[9]},${IMAGEID[10]},${IMAGEID[11]},${IMAGEID[12]}"\
                     -EXPTIME ${EXPTIME}\
                     -AIRMASS ${AIRMASS}\
                     -GABODSID ${GABODSID}\
                     -FILTER ${FILTNAM}  \
                     -OBJECT ${OBJECT} \
                     -OUTPUT_DIR .. \
                     ${FILE}
done
