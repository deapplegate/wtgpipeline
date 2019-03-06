#!/bin/bash

# The script creates a CFH12K.ini file according
# to the date of the run under consideration.
# The CFH12K camera changed its setup several times
# between 1999 and 2002.
# We assume for the moment that all images in
# the run require the same initialisation.
#
# We consider right now setups for the periods:
# 24/03/1999 (GABODSID 82)  - 02/11/1999 (GABODSID 305)
# 02/11/1999 (GABODSID 305) - 28/05/2000 (GABODSID 514)
# 28/05/2000 (GABODSID 514) - ........
#
# Important dates checked:
# - 480564o.fits (24/03/1999) has march 1999 setup
# - 504141o.fits (01/10/1999) has march 1999 setup
# - 508034o.fits (02/11/1999) has november 1999 setup
# - 532346o.fits (06/05/2000) has november 1999 setup 
# - 532882o.fits (10/05/2000) has november 1999 setup 
# - 534693o.fits (24/05/2000) has november 1999 setup
# - 534850o.fits (25/05/2000) has november 1999 setup
# - 535038o.fits (26/05/2000) has november 1999 setup
# - 535302o.fits (28/05/2000) has 'incorrect' june 2000 setup
#   The CRPIX1 value of the 4th extension has the wrong sign!!
# - 535847o.fits (01/06/2000) has 'incorrect' june 2000 setup
# - 539885o.fits (01/07/2000) has 'correct' june 2000 setup
# - 565625o.fits (01/01/2001) has june 2000 setup
# - 591827o.fits (16/06/2001) has june 2000 setup
# - 623835o.fits (03/02/2002) has june 2000 setup
# 
# Note that the above periods reflect periods
# from data we analysed. They probably do NOT
# mark the dates when setup changes  have been
# actually done. This holds for the transition of
# the 03/1999 to the 11/1999 period. The second change
# is located accurately. 
#
# The script has to be called in your reduce directory
# and it needs the following files:
# CFH12K.ini.raw, cfh12k_03_1999.ini, cfh12k_11_1999.ini and
# cfh12k_06_2000.ini.
#
# $1: directory from which to read the first image
#     to obtain the observation date (We use the
#     MJD-OBS keyword)
#
. progs.ini

IMAGE=`ls -1 /$1/*.fits | ${P_GAWK} '(NR==1) {print $0}'`
MJD=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} MJD-OBS |\
     ${P_GAWK} '($1!="FILE") {print $2}'`
GABODSID=`${P_NIGHTID} -t 22:00:00 -d 31/12/1998 -m ${MJD} |\
          ${P_GAWK} ' ($1 ~ /Days/) {print $6}' |\
          ${P_GAWK} 'BEGIN{ FS="."} {print $1}'`

if [ ${GABODSID} -lt 82 ]; then
  echo "no config file provided yet. Exiting !!"
  exit 1
fi

# first delete old global .reg files if any
i=1
while [ ${i} -le 12 ]
do
  if [ -f CFH12K_${i}.reg ]; then
      rm CFH12K_${i}.reg 
  fi
  i=$(( $i + 1 ))
done

if [ ${GABODSID} -ge 82 ] && [ ${GABODSID} -lt 305 ]; then
  echo "period 03_1999 configuration"  
  PERIOD="03_1999"
fi

if [ ${GABODSID} -ge 305 ] && [ ${GABODSID} -lt 514 ]; then
  echo "period 11_1999 configuration"  
  PERIOD="11_1999"
fi

if [ ${GABODSID} -ge 514 ]; then
  echo "period 06_2000 configuration"  
  PERIOD="06_2000"
fi

# create CFH12K.ini file and global regs:
cat CFH12K.ini.raw cfh12k_${PERIOD}.ini > CFH12K.ini

i=1
while [ ${i} -le 12 ] 
do
  if [ -f CFH12K_${i}_${PERIOD}.reg ]; then
      cp CFH12K_${i}_${PERIOD}.reg CFH12K_${i}.reg 
  fi
  i=$(( $i + 1 ))
done
