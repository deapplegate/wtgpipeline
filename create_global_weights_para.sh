#!/bin/bash
set -xv
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# the script creates normaliced images.
# It puts the result into new directories ..._norm.
# The script assumes a threshhold. Pixels under
# this threshhold will be assigned a value of threshhold
# in the resulting images.

# 23.12.:
#  introduced the possibility to give a reg file
#  (The regfiles have the names ${INSTRUMENT}_CIPNR.reg
#   where CHIPNR is the number of the chip) 
#
# 09.09.03:
# the creation of the WEIGHTS directory has to be shifted
# to the very start of the script. Otherwise it may be that
# the script tries to create links into a not yet existing
# directory.
#
# 30.05.04:
# tempaorary files go to a TEMPDIR directory 
#
# 03.02.05:
# I resolved the hardcoding as the 11th argument
# being the last argument. The last argument can
# directly be accessed via ${!#}.

# $1: main directory
# $2....: directories from which the weights have to be
#         created. The first dir is also the input weight.
#         Every sequence has three arguments: The dir.,
#         the low and high thressholds
# last argument: chips to be processed

#CVSID="$Id: create_global_weights_para.sh,v 1.5 2008-07-09 18:22:59 dapple Exp $"

. ${INSTRUMENT:?}.ini

if [ ! -d $1/WEIGHTS ]; then
  mkdir $1/WEIGHTS
fi
  
for CHIP in ${!#}
do
  j=2
  l=3
  m=4
  i=1
  WNAMES=""
  WMIN=""
  WMAX=""
  WFLAG=""
  ACTUFLAG=2

  maxarg=$(( $# - 1 ))

  while [ "$j" -le "${maxarg}" ]
  do
    DIR=`echo $* | ${P_GAWK} '{print $'${j}'}'`
    MIN=`echo $* | ${P_GAWK} '{print $'${l}'}'`
    MAX=`echo $* | ${P_GAWK} '{print $'${m}'}'`

    if [ "${i}" -eq "1" ]; then
      WNAMES="/$1/${DIR}/${DIR}_${CHIP}.fits"
      WMIN="${MIN}"
      WMAX="${MAX}"
      WFLAG="${ACTUFLAG}"
    else
      WNAMES="${WNAMES},/$1/${DIR}/${DIR}_${CHIP}.fits"
      WMIN="${WMIN},${MIN}"
      WMAX="${WMAX},${MAX}"      
      WFLAG="${WFLAG},${ACTUFLAG}"      
    fi

    # create link if necessary:
    if [ -L "/$1/${DIR}/${DIR}_${CHIP}.fits" ]; then
      LINK=`${P_READLINK} /$1/${DIR}/${DIR}_${CHIP}.fits`
      RESULTDIR=`dirname ${LINK}`
      ln -s ${RESULTDIR}/globalweight_${CHIP}.fits \
            /$1/WEIGHTS/globalweight_${CHIP}.fits
    else
      RESULTDIR="/$1/WEIGHTS/"
    fi   

    ACTUFLAG=$(( ${ACTUFLAG} * 2 ))
    j=$(( $j + 3 ))
    l=$(( $l + 3 ))
    m=$(( $m + 3 ))
    i=$(( $i + 3 ))

    #write config file for ww
    echo "WEIGHT_NAMES ${WNAMES}"   >  ${TEMPDIR}/${CHIP}.ww_$$
    echo "WEIGHT_MIN ${WMIN}"       >> ${TEMPDIR}/${CHIP}.ww_$$
    echo "WEIGHT_MAX ${WMAX}"       >> ${TEMPDIR}/${CHIP}.ww_$$
    echo "WEIGHT_OUTFLAGS ${WFLAG}" >> ${TEMPDIR}/${CHIP}.ww_$$
    #
    echo 'FLAG_NAMES ""'            >> ${TEMPDIR}/${CHIP}.ww_$$
    echo 'FLAG_MASKS ""'            >> ${TEMPDIR}/${CHIP}.ww_$$
    echo 'FLAG_WMASKS ""'           >> ${TEMPDIR}/${CHIP}.ww_$$
    echo 'FLAG_OUTFLAGS ""'         >> ${TEMPDIR}/${CHIP}.ww_$$
    #
    if [ -f "$1/reg/${INSTRUMENT}_${CHIP}.reg" ]; then
      echo "POLY_NAMES $1/reg/${INSTRUMENT}_${CHIP}.reg" >> ${TEMPDIR}/${CHIP}.ww_$$
      echo "POLY_OUTFLAGS 1"                      >> ${TEMPDIR}/${CHIP}.ww_$$
    else
      echo 'POLY_NAMES ""'                        >> ${TEMPDIR}/${CHIP}.ww_$$
      echo 'POLY_OUTFLAGS ""'                     >> ${TEMPDIR}/${CHIP}.ww_$$
    fi
    #
    echo "OUTWEIGHT_NAME ${RESULTDIR}/globalweight_${CHIP}.fits" >> ${TEMPDIR}/${CHIP}.ww_$$
    echo 'OUTFLAG_NAME ""'                                      >> ${TEMPDIR}/${CHIP}.ww_$$
  done

  ${P_WW} -c ${TEMPDIR}/${CHIP}.ww_$$
  
  rm -f ${TEMPDIR}/${CHIP}.ww_$$
done




#adam-BL# log_status $?
