#!/bin/bash 
. BonnLogger.sh
. log_start
#CVSID="$Id: setup_SUBARU.sh,v 1.18 2009-08-07 00:15:25 anja Exp $"
# The script creates a SUBARU.ini file according
# to the date of the run under consideration.
#
# We consider right now setups for the periods:
# 8:    30.06.1999 (GABODSID 180) - 07.08.2000 (GABODSID 585)
# 9:    22.11.2000 (GABODSID 691) - 28.03.2001 (GABODSID 817)
# 10_1: 28.03.2001 (GABODSID 817) - 02.08.2002 (GABODSID 1309)
# 10_2: 02.08.2002 (GABODSID 1309 ) - July 2008 (GABODSID 3470)
# 10_3: July 2008 - now

# The script has to be called in your reduce directory
# and it needs the following files:
# SUBARU.ini.raw, subaru_8.ini, subaru_9.ini, subaru_10_1.ini and
# subaru_10_2.ini.
#
# $1: directory from which to read the first image
#     to obtain the observation date (We use the
#     MJD keyword)
#
. progs.ini

#IMAGE=`ls -1 /$1/*.fits | ${P_GAWK} '(NR==1) {print $0}'`
IMAGE=`find $1/ -maxdepth 1 -name \*.fits | sort -r | ${P_GAWK} '(NR==1) {print $0}'`

EXTEND=`${P_DFITS} ${IMAGE} | ${P_FITSORT} EXTEND |\
        ${P_GAWK} '($1!="FILE") {print $2}'`

if [ "${EXTEND}" == "KEY_N/A" ]; then
    GABODSID=`${P_DFITS} ${IMAGE} | ${P_FITSORT} GABODSID | \
        ${P_GAWK} '($1!="FILE") {print $2}'`
    if [ "${GABODSID}" = "KEY_N/A" ]; then
	echo "no GABODSID"
	log_status 2 "no GABODSID"
	exit 2
    fi
else
    if [ "${EXTEND}" == "F" ]; then
	EXT_FLAG=""
    elif [ "${EXTEND}" == "T" ]; then
	EXT_FLAG='-x 1'
    else
	echo "no EXTEND keyword?!"
	log_status 1 "no EXTEND keyword?!"
	exit 1
    fi
	
    MJD=`${P_DFITS} ${EXT_FLAG} ${IMAGE} | ${P_FITSORT} MJD |\
         ${P_GAWK} '($1!="FILE") {print $2}'`

    GABODSID=`${P_NIGHTID} -t 22:00:00 -d 31/12/1998 -m ${MJD} |\
          ${P_GAWK} ' ($1 ~ /Days/) {print $6}' |\
          ${P_GAWK} 'BEGIN{ FS="."} {print $1}'`
fi


echo "GABODSID:" ${GABODSID} ${MJD} ${IMAGE}

if [ ${GABODSID} -lt 180 ]; then
  echo "no config file provided yet. Exiting !!"
  log_status 1 "no config file provided yet"
  exit 1
fi

#### first delete old global .reg files if any
###i=1
###while [ ${i} -le 12 ]
###do
###  if [ -f CFH12K_${i}.reg ]; then
###      rm CFH12K_${i}.reg 
###  fi
###  i=$(( $i + 1 ))
###done

if [ ${GABODSID} -ge 575 ] && [ ${GABODSID} -lt 691 ]; then
  echo "8 chip configuration"  
  CONFIG="8"
fi

if [ ${GABODSID} -ge 691 ] && [ ${GABODSID} -lt 817 ]; then
  echo "9 chip configuration"  
  CONFIG="9"
fi

if [ ${GABODSID} -ge 817 ] && [ ${GABODSID} -lt 1309 ]; then
  echo "10_1 chip configuration"  
  CONFIG="10_1"
fi

if [ ${GABODSID} -ge 1309 ] && [ ${GABODSID} -lt 3470 ]; then
  echo "10_2 chip configuration"  
  CONFIG="10_2"
fi

if [ ${GABODSID} -ge 3470 ] && [ ${GABODSID} -lt 5000 ]; then
  echo "10_3 chip configuration"  
  CONFIG="10_3"
fi

if [ ${GABODSID} -ge 5000 ]; then
  echo "no config file provided yet. Exiting !!"
  log_status 1 "no config file provided yet"
  exit 1
fi

# create SUBARU.ini file and global regs:
cat SUBARU.ini.raw subaru_${CONFIG}.ini > SUBARU.ini

if [ ! -e SUBARU.ini ]; then
    log_status 2 "No SUBARU.ini produced"
    exit 2
fi

. SUBARU.ini

log_status 0
