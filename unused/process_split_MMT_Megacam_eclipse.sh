#!/bin/bash -xv

# Splits MMT Megacam Fits extension images into the
# 72 chips. Uses the eclipse utilities
# and also updates the image headers.
# Assumes that ONLY unsplit images are in the directory.
# Adapted for MMT Megacam: reiprich 2004-12-01

# $1: main directory
# $2: science directory

. MMT_Megacam.ini

# Create image list: we assume that ONLY unsplit
# images are in the directory.

FILES=`ls $1/$2/ORIGINALS/*.fits`

cd /$1/$2/ORIGINALS

for FILE in ${FILES}
do
  FILTNAM=`${P_DFITS} -x 1 ${FILE} | ${P_FITSORT} BFILTID  | awk '($1!="FILE") {print $2}'`
  OBJECT=`${P_DFITS} -x 1  ${FILE} | ${P_FITSORT} OBJECT  | awk '($1!="FILE") {print $2}'`
  RATMP=`${P_DFITS} -x 1  ${FILE} | ${P_FITSORT} RA  | awk '($1!="FILE") {print $2}'`
  DECTMP=`${P_DFITS} -x 1 ${FILE} | ${P_FITSORT} DEC | awk '($1!="FILE") {print $2}'`

  # for several calibration files such as some BIAS, DARKS, image headers
  # contain no useful RA and DEC information.
  if [ "${RATMP}" != "KEY_N/A" ]; then
      RA=`hmstodecimal ${RATMP}`
  else
      RA=0.00
  fi
  if [ "${DECTMP}" != "KEY_N/A" ]; then
      DEC=`dmstodecimal ${DECTMP}`
  else
      DEC=0.0
  fi
  LST=`${P_DFITS} -x 1 ${FILE} | ${P_FITSORT} ST | awk '($1!="FILE") {print $2}' | awk -F: '{print $1*3600+$2*60+$3}'`
  MJD=`${P_DFITS} -x 1 ${FILE} | ${P_FITSORT} MJD  | awk '($1!="FILE") {print $2}'`
  EXPTIME=`${P_DFITS} -x 1 ${FILE} | ${P_FITSORT} DARKTIME | awk '($1!="FILE") {print $2}'`
  AIRMASS=`${P_AIRMASS} -t ${LST} -e ${EXPTIME} -r ${RA} -d ${DEC} -l ${OBSLAT}`

  # for several calibration files such as some BIAS, DARKS, image headers
  # contain no MJD keyword.
  if [ "${MJD}" != "KEY_N/A" ]; then
      GABODSID=`${P_NIGHTID} -t ${REFERENCETIME} -d 31/12/1998 -m ${MJD} |\
      awk ' ($1 ~ /Days/) {print $6}' | awk 'BEGIN{ FS="."} {print $1}'`
  else
      GABODSID=0
  fi
  

 ${P_FITSSPLIT_ECL} -CRPIX1 \
 "${REFPIXX[1]},${REFPIXX[2]},${REFPIXX[3]},${REFPIXX[4]},${REFPIXX[5]},${REFPIXX[6]},${REFPIXX[7]},${REFPIXX[8]},${REFPIXX[9]},${REFPIXX[10]},${REFPIXX[11]},${REFPIXX[12]},${REFPIXX[13]},${REFPIXX[14]},${REFPIXX[15]},${REFPIXX[16]},${REFPIXX[17]},${REFPIXX[18]},${REFPIXX[19]},${REFPIXX[20]},${REFPIXX[21]},${REFPIXX[22]},${REFPIXX[23]},${REFPIXX[24]},${REFPIXX[25]},${REFPIXX[26]},${REFPIXX[27]},${REFPIXX[28]},${REFPIXX[29]},${REFPIXX[30]},${REFPIXX[31]},${REFPIXX[32]},${REFPIXX[33]},${REFPIXX[34]},${REFPIXX[35]},${REFPIXX[36]},${REFPIXX[37]},${REFPIXX[38]},${REFPIXX[39]},${REFPIXX[40]},${REFPIXX[41]},${REFPIXX[42]},${REFPIXX[43]},${REFPIXX[44]},${REFPIXX[45]},${REFPIXX[46]},${REFPIXX[47]},${REFPIXX[48]},${REFPIXX[49]},${REFPIXX[50]},${REFPIXX[51]},${REFPIXX[52]},${REFPIXX[53]},${REFPIXX[54]},${REFPIXX[55]},${REFPIXX[56]},${REFPIXX[57]},${REFPIXX[58]},${REFPIXX[59]},${REFPIXX[60]},${REFPIXX[61]},${REFPIXX[62]},${REFPIXX[63]},${REFPIXX[64]},${REFPIXX[65]},${REFPIXX[66]},${REFPIXX[67]},${REFPIXX[68]},${REFPIXX[69]},${REFPIXX[70]},${REFPIXX[71]},${REFPIXX[72]}"\
                    -CRPIX2 \
 "${REFPIXY[1]},${REFPIXY[2]},${REFPIXY[3]},${REFPIXY[4]},${REFPIXY[5]},${REFPIXY[6]},${REFPIXY[7]},${REFPIXY[8]},${REFPIXY[9]},${REFPIXY[10]},${REFPIXY[11]},${REFPIXY[12]},${REFPIXY[13]},${REFPIXY[14]},${REFPIXY[15]},${REFPIXY[16]},${REFPIXY[17]},${REFPIXY[18]},${REFPIXY[19]},${REFPIXY[20]},${REFPIXY[21]},${REFPIXY[22]},${REFPIXY[23]},${REFPIXY[24]},${REFPIXY[25]},${REFPIXY[26]},${REFPIXY[27]},${REFPIXY[28]},${REFPIXY[29]},${REFPIXY[30]},${REFPIXY[31]},${REFPIXY[32]},${REFPIXY[33]},${REFPIXY[34]},${REFPIXY[35]},${REFPIXY[36]},${REFPIXY[37]},${REFPIXY[38]},${REFPIXY[39]},${REFPIXY[40]},${REFPIXY[41]},${REFPIXY[42]},${REFPIXY[43]},${REFPIXY[44]},${REFPIXY[45]},${REFPIXY[46]},${REFPIXY[47]},${REFPIXY[48]},${REFPIXY[49]},${REFPIXY[50]},${REFPIXY[51]},${REFPIXY[52]},${REFPIXY[53]},${REFPIXY[54]},${REFPIXY[55]},${REFPIXY[56]},${REFPIXY[57]},${REFPIXY[58]},${REFPIXY[59]},${REFPIXY[60]},${REFPIXY[61]},${REFPIXY[62]},${REFPIXY[63]},${REFPIXY[64]},${REFPIXY[65]},${REFPIXY[66]},${REFPIXY[67]},${REFPIXY[68]},${REFPIXY[69]},${REFPIXY[70]},${REFPIXY[71]},${REFPIXY[72]}"\
                    -CD11 \
 "${CD11[1]},${CD11[2]},${CD11[3]},${CD11[4]},${CD11[5]},${CD11[6]},${CD11[7]},${CD11[8]},${CD11[9]},${CD11[10]},${CD11[11]},${CD11[12]},${CD11[13]},${CD11[14]},${CD11[15]},${CD11[16]},${CD11[17]},${CD11[18]},${CD11[19]},${CD11[20]},${CD11[21]},${CD11[22]},${CD11[23]},${CD11[24]},${CD11[25]},${CD11[26]},${CD11[27]},${CD11[28]},${CD11[29]},${CD11[30]},${CD11[31]},${CD11[32]},${CD11[33]},${CD11[34]},${CD11[35]},${CD11[36]},${CD11[37]},${CD11[38]},${CD11[39]},${CD11[40]},${CD11[41]},${CD11[42]},${CD11[43]},${CD11[44]},${CD11[45]},${CD11[46]},${CD11[47]},${CD11[48]},${CD11[49]},${CD11[50]},${CD11[51]},${CD11[52]},${CD11[53]},${CD11[54]},${CD11[55]},${CD11[56]},${CD11[57]},${CD11[58]},${CD11[59]},${CD11[60]},${CD11[61]},${CD11[62]},${CD11[63]},${CD11[64]},${CD11[65]},${CD11[66]},${CD11[67]},${CD11[68]},${CD11[69]},${CD11[70]},${CD11[71]},${CD11[72]}"\
                    -CD22 \
 "${CD22[1]},${CD22[2]},${CD22[3]},${CD22[4]},${CD22[5]},${CD22[6]},${CD22[7]},${CD22[8]},${CD22[9]},${CD22[10]},${CD22[11]},${CD22[12]},${CD22[13]},${CD22[14]},${CD22[15]},${CD22[16]},${CD22[17]},${CD22[18]},${CD22[19]},${CD22[20]},${CD22[21]},${CD22[22]},${CD22[23]},${CD22[24]},${CD22[25]},${CD22[26]},${CD22[27]},${CD22[28]},${CD22[29]},${CD22[30]},${CD22[31]},${CD22[32]},${CD22[33]},${CD22[34]},${CD22[35]},${CD22[36]},${CD22[37]},${CD22[38]},${CD22[39]},${CD22[40]},${CD22[41]},${CD22[42]},${CD22[43]},${CD22[44]},${CD22[45]},${CD22[46]},${CD22[47]},${CD22[48]},${CD22[49]},${CD22[50]},${CD22[51]},${CD22[52]},${CD22[53]},${CD22[54]},${CD22[55]},${CD22[56]},${CD22[57]},${CD22[58]},${CD22[59]},${CD22[60]},${CD22[61]},${CD22[62]},${CD22[63]},${CD22[64]},${CD22[65]},${CD22[66]},${CD22[67]},${CD22[68]},${CD22[69]},${CD22[70]},${CD22[71]},${CD22[72]}"\
                    -CD12 \
 "${CD12[1]},${CD12[2]},${CD12[3]},${CD12[4]},${CD12[5]},${CD12[6]},${CD12[7]},${CD12[8]},${CD12[9]},${CD12[10]},${CD12[11]},${CD12[12]},${CD12[13]},${CD12[14]},${CD12[15]},${CD12[16]},${CD12[17]},${CD12[18]},${CD12[19]},${CD12[20]},${CD12[21]},${CD12[22]},${CD12[23]},${CD12[24]},${CD12[25]},${CD12[26]},${CD12[27]},${CD12[28]},${CD12[29]},${CD12[30]},${CD12[31]},${CD12[32]},${CD12[33]},${CD12[34]},${CD12[35]},${CD12[36]},${CD12[37]},${CD12[38]},${CD12[39]},${CD12[40]},${CD12[41]},${CD12[42]},${CD12[43]},${CD12[44]},${CD12[45]},${CD12[46]},${CD12[47]},${CD12[48]},${CD12[49]},${CD12[50]},${CD12[51]},${CD12[52]},${CD12[53]},${CD12[54]},${CD12[55]},${CD12[56]},${CD12[57]},${CD12[58]},${CD12[59]},${CD12[60]},${CD12[61]},${CD12[62]},${CD12[63]},${CD12[64]},${CD12[65]},${CD12[66]},${CD12[67]},${CD12[68]},${CD12[69]},${CD12[70]},${CD12[71]},${CD12[72]}"\
                    -CD21 \
 "${CD21[1]},${CD21[2]},${CD21[3]},${CD21[4]},${CD21[5]},${CD21[6]},${CD21[7]},${CD21[8]},${CD21[9]},${CD21[10]},${CD21[11]},${CD21[12]},${CD21[13]},${CD21[14]},${CD21[15]},${CD21[16]},${CD21[17]},${CD21[18]},${CD21[19]},${CD21[20]},${CD21[21]},${CD21[22]},${CD21[23]},${CD21[24]},${CD21[25]},${CD21[26]},${CD21[27]},${CD21[28]},${CD21[29]},${CD21[30]},${CD21[31]},${CD21[32]},${CD21[33]},${CD21[34]},${CD21[35]},${CD21[36]},${CD21[37]},${CD21[38]},${CD21[39]},${CD21[40]},${CD21[41]},${CD21[42]},${CD21[43]},${CD21[44]},${CD21[45]},${CD21[46]},${CD21[47]},${CD21[48]},${CD21[49]},${CD21[50]},${CD21[51]},${CD21[52]},${CD21[53]},${CD21[54]},${CD21[55]},${CD21[56]},${CD21[57]},${CD21[58]},${CD21[59]},${CD21[60]},${CD21[61]},${CD21[62]},${CD21[63]},${CD21[64]},${CD21[65]},${CD21[66]},${CD21[67]},${CD21[68]},${CD21[69]},${CD21[70]},${CD21[71]},${CD21[72]}"\
                     -M11 \
    "1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1"\
                     -M22 \
    "1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1"\
                     -M12 \
    "0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0"\
                     -M21 \
    "0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0"\
                     -CRVAL1 ${RA} -CRVAL2 ${DEC}\
                     -EXPTIME ${EXPTIME}\
                     -AIRMASS ${AIRMASS}\
                     -GABODSID ${GABODSID}\
                     -FILTER ${FILTNAM}  \
                     -OBJECT ${OBJECT}  \
                     -OUTPUT_DIR ../ \
                     ${FILE}
done
