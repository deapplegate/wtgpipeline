#!/bin/bash -xv
. BonnLogger.sh
. log_start
# splits Subaru Fits extension images into the
# ten chips. Uses the eclipse utilities
# and also updates the image headers
#

# $1: main directory
# $2: science directory

# create image list: we assume that ONLY unsplit
# images are in the directory

. SUBARU.ini

FILES=`ls $1/$2/ORIGINALS/*.fits`

OUTPUTDIR='..'

REDDIR=`pwd`
cd /$1/$2/ORIGINALS

for FILE in ${FILES}
do

  BASE=`basename ${FILE} .fits`

  if [ -e ${OUTPUTDIR}/${BASE}_2.fits ]; then
      continue
  fi

  if [ ${NOREDO:-0} -eq 1 ] && [ -e ${OUTPUTDIR}/${BASE}_2*.fits ]; then
      continue
  fi


  cdmatrix=`${P_DFITS} -x 1 ${FILE} | ${P_FITSORT} CD1_1  | awk '($1!="FILE") {print $2}'`
  pcmatrix=`${P_DFITS} -x 1 ${FILE} | ${P_FITSORT} PC001001  | awk '($1!="FILE") {print $2}'`

  if [ "${cdmatrix}" != "KEY_N/A" ]; then
      i=${NCHIPS}
      while [ $i -ge 1 ]
      do

	  CD11[$i]=`${P_DFITS} -x $i ${FILE} | ${P_FITSORT} CD1_1  | awk '($1!="FILE") {print $2}'`
	  CD12[$i]=`${P_DFITS} -x $i ${FILE} | ${P_FITSORT} CD1_2  | awk '($1!="FILE") {print $2}'`
	  CD21[$i]=`${P_DFITS} -x $i ${FILE} | ${P_FITSORT} CD2_1  | awk '($1!="FILE") {print $2}'`
	  CD22[$i]=`${P_DFITS} -x $i ${FILE} | ${P_FITSORT} CD2_2  | awk '($1!="FILE") {print $2}'`
	  
	  i=$(($i-1))
	  
      done
  elif [ "${pcmatrix}" != "KEY_N/A" ]; then
      i=${NCHIPS}
      while [ $i -ge 1 ]
      do
	  
	  PC11=`${P_DFITS} -x $i ${FILE} | ${P_FITSORT} PC001001  | awk '($1!="FILE") {print $2}'`
	  PC12=`${P_DFITS} -x $i ${FILE} | ${P_FITSORT} PC001002  | awk '($1!="FILE") {print $2}'`
	  PC21=`${P_DFITS} -x $i ${FILE} | ${P_FITSORT} PC002001  | awk '($1!="FILE") {print $2}'`
	  PC22=`${P_DFITS} -x $i ${FILE} | ${P_FITSORT} PC002002  | awk '($1!="FILE") {print $2}'`
	  CDELT1=`${P_DFITS} -x $i ${FILE} | ${P_FITSORT} CDELT1  | awk '($1!="FILE") {print $2}'`
	  CDELT2=`${P_DFITS} -x $i ${FILE} | ${P_FITSORT} CDELT2  | awk '($1!="FILE") {print $2}'`
	  
	  CD11[$i]=`awk 'BEGIN{print '${PC11}'*'${CDELT1}'}'`
	  CD12[$i]=`awk 'BEGIN{print '${PC12}'*'${CDELT1}'}'`
	  CD21[$i]=`awk 'BEGIN{print '${PC21}'*'${CDELT2}'}'`
	  CD22[$i]=`awk 'BEGIN{print '${PC22}'*'${CDELT2}'}'`
	  
	  i=$(($i-1))
	  
      done
      
  fi
  
  FILTNAM=`${P_DFITS} -x 1 ${FILE} | ${P_FITSORT} FILTER01  | awk '($1!="FILE") {print $2}'`
  
  RA=`${P_DFITS} -x 1  ${FILE} | ${P_FITSORT} RA  | awk '($1!="FILE") {print $2}'`
  RA=`${P_HMSTODECIMAL} ${RA}`
  DEC=`${P_DFITS} -x 1 ${FILE} | ${P_FITSORT} DEC | awk '($1!="FILE") {print $2}'`
  DEC=`${P_DMSTODECIMAL} ${DEC}`
  LST=`${P_DFITS} -x 1 ${FILE} | ${P_FITSORT} LST | awk '($1!="FILE") {print $2}'`
  LST=`echo ${LST} | awk -F: '{print 3600*$1+60*$2+$3}'`
  MJD=`${P_DFITS} -x 1 ${FILE} | ${P_FITSORT} MJD | awk '($1!="FILE") {print $2}'`
  OBJECT=`${P_DFITS} -x 1 ${FILE} | ${P_FITSORT} OBJECT | awk '($1!="FILE") {print $2}'`
  EXPTIME=`${P_DFITS} -x 1 ${FILE} | ${P_FITSORT} EXPTIME | awk '($1!="FILE") {print $2}'`
  AIRMASS=`${P_AIRMASS} -t ${LST} -e ${EXPTIME} -r ${RA} -d ${DEC} -l ${OBSLAT}`
  GABODSID=`${P_NIGHTID} -t ${REFERENCETIME} -d 31/12/1998 -m ${MJD} |\
      awk ' ($1 ~ /Days/) {print $6}' | awk 'BEGIN{ FS="."} {print $1}'`
  
  ${P_FITSSPLIT_ECL} -CRPIX1 \
      "${REFPIXX[1]},${REFPIXX[2]},${REFPIXX[3]},${REFPIXX[4]},${REFPIXX[5]},${REFPIXX[6]},${REFPIXX[7]},${REFPIXX[8]},${REFPIXX[9]},${REFPIXX[10]}"\
                     -CRPIX2 \
      "${REFPIXY[1]},${REFPIXY[2]},${REFPIXY[3]},${REFPIXY[4]},${REFPIXY[5]},${REFPIXY[6]},${REFPIXY[7]},${REFPIXY[8]},${REFPIXY[9]},${REFPIXY[10]}"\
                     -CRVAL1 ${RA} -CRVAL2 ${DEC}\
                     -M11 "${M11[1]},${M11[2]},${M11[3]},${M11[4]},${M11[5]},${M11[6]},${M11[7]},${M11[8]},${M11[9]},${M11[10]}"\
                     -M22 "${M22[1]},${M22[2]},${M22[3]},${M22[4]},${M22[5]},${M22[6]},${M22[7]},${M22[8]},${M22[9]},${M22[10]}"\
                     -M12 "${M12[1]},${M12[2]},${M12[3]},${M12[4]},${M12[5]},${M12[6]},${M12[7]},${M12[8]},${M12[9]},${M12[10]}"\
                     -M21 "${M21[1]},${M21[2]},${M21[3]},${M21[4]},${M21[5]},${M21[6]},${M21[7]},${M21[8]},${M21[9]},${M21[10]}"\
                     -CD11 "${CD11[1]},${CD11[2]},${CD11[3]},${CD11[4]},${CD11[5]},${CD11[6]},${CD11[7]},${CD11[8]},${CD11[9]},${CD11[10]}"\
                     -CD22 "${CD22[1]},${CD22[2]},${CD22[3]},${CD22[4]},${CD22[5]},${CD22[6]},${CD22[7]},${CD22[8]},${CD22[9]},${CD22[10]}"\
                     -CD12 "${CD12[1]},${CD12[2]},${CD12[3]},${CD12[4]},${CD12[5]},${CD12[6]},${CD12[7]},${CD12[8]},${CD12[9]},${CD12[10]}"\
                     -CD21 "${CD21[1]},${CD21[2]},${CD21[3]},${CD21[4]},${CD21[5]},${CD21[6]},${CD21[7]},${CD21[8]},${CD21[9]},${CD21[10]}"\
                     -IMAGEID "${IMAGEID[1]},${IMAGEID[2]},${IMAGEID[3]},${IMAGEID[4]},${IMAGEID[5]},${IMAGEID[6]},${IMAGEID[7]},${IMAGEID[8]},${IMAGEID[9]},${IMAGEID[10]}"\
                     -EXPTIME ${EXPTIME}\
                     -AIRMASS ${AIRMASS}\
                     -GABODSID ${GABODSID}\
                     -FILTER ${FILTNAM}  \
      -OBJECT ${OBJECT} \
      -OUTPUT_DIR ${OUTPUTDIR} \
      ${FILE}
  
# check for rotation - if yes, then ROT=1
  ROTATION=`awk 'BEGIN{if('${CD12[1]}'==0 && '${CD21[1]}'==0) print 1; else print 0}'`
  
  
  i=${NCHIPS}
  while [ $i -ge 1 ]
  do
      
      ${P_REPLACEKEY} /$1/$2/${BASE}_$i.fits "ROTATION= ${ROTATION}" "DUMMY1  "
      ${P_REPLACEKEY} /$1/$2/${BASE}_$i.fits "CONFIG  = ${config}  " "DUMMY2  "
      
      i=$(($i-1))
      
  done
  
done
cd $REDDIR
log_status $?
