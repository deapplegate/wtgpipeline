#!/bin/bash

# $Id: distribute_sets_subaru.sh,v 1.21 2009-06-19 02:10:47 anja Exp $#

#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# the script collects some header keywords of a directory with raw fits
# files into an LDAC catalog with a FILES table. These data are then
# used to distinguish 'sets' of images
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 03.12.2004:
# I substituted the initial 'ls' listing all
# to be looked at by a find command. With 'ls'
# it could happen that we exceed its argument list.
#
# 14.08.2005:
# The call of the UNIX 'find' program is now done
# via a variable 'P_FIND'.
#
# 30.11.2005:
# A ${TEMPDIR} was mssing when creating the initial
# file list.

#adam-example# ./distribute_sets_subaru.sh ${SUBARUDIR} ${run}_${filter}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list WEIGHTS

#$1: main directory
#$2: run/science directory
#$3: image extension (ext) on ..._iext.fits (i is the chip number)
#$4: minimum overlap for counting exposures to the same set
#$5: lookup file: nick full_name ra dec nicknames
#$6: weights directory

. ${INSTRUMENT:?}.ini > /tmp/out.log 2>&1

# configuration parameters:

if [ $6 ];then
    WEIGHTSDIR=$6
else
    WEIGHTSDIR=WEIGHTS
fi

NIGHT=`dirname $2 | awk -F'_' '{print $1}'`
FILTER=`dirname $2 | awk -F'_' '{print $2}'`
RUNDIR=${FILTER}_${NIGHT}

echo "RUNDIR: ${RUNDIR}"

FILTERKEY="FILTER"
OBJECTKEY="OBJECT"
RAKEY="CRVAL1"
DECKEY="CRVAL2"

${P_FIND} $1/$2/ -name \*$3.fits -print > ${TEMPDIR}/images_$$

if [ ! -s ${TEMPDIR}/images_$$ ]; then
    #adam-BL# log_status 2 "No images to work on"
    echo "adam-look | error: No images to work on"
    exit 2
fi

cat ${TEMPDIR}/images_$$ |\
{
  while read IMAGE
  do
    NAME=`basename ${IMAGE}`
    ra=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${RAKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`
    dec=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${DECKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`
    CLUSTER=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${OBJECTKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`
    FILTER=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${FILTERKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`

    nnick=`grep ${CLUSTER} $5 | wc | awk '{print $1}'`

    if [ ${nnick} -eq 1 ]; then
	nick=`grep ${CLUSTER} $5 | awk '{print $1}'`	
    else
	nick=`awk 'function acos(x) { return atan2((1.-x^2)^0.5,x) }
        {
          dist=57.2958*acos(cos(1.5708-('${dec}'*0.01745))*cos(1.5708-($4*0.01745)) + (sin(1.5708-('${dec}'*0.01745))*sin(1.5708-($4*0.01745)))*cos(('${ra}'-$3)*0.01745))
          if( dist<0.5 ) print $1}' $5`
    fi

    if [ -z ${nick} ]; then
	nick=${CLUSTER}
    fi

    echo "CLUSTER: ${CLUSTER} nick: ${nick}"
    nnnick=`echo ${nick} | wc | awk '{print $2}'`

    if [ ${nnnick} -ne 1 ]; then
	echo "More than one cluster match."
	echo "Decrease distance in distribute_sets_subaru.sh ."
	exit 2
    fi

    if [ ! -d "/$1/${nick}" ]; then
      mkdir "/$1/${nick}"
    fi

    if [ ! -d "/$1/${nick}/${RUNDIR}" ]; then
      mkdir "/$1/${nick}/${RUNDIR}"
    fi

    if [ ! -d "/$1/${nick}/${RUNDIR}/SCIENCE" ]; then
      mkdir "/$1/${nick}/${RUNDIR}/SCIENCE"
    fi

    if [ ! -d "/$1/${nick}/${RUNDIR}/SCIENCE/SPLIT_IMAGES" ]; then
      mkdir "/$1/${nick}/${RUNDIR}/SCIENCE/SPLIT_IMAGES"
    fi
    
    ln -s /$1/$2/${NAME} /$1/${nick}/${RUNDIR}/SCIENCE/ 

    split_image=`basename ${NAME} "${3}.fits"`
    ln -s /$1/$2/SPLIT_IMAGES/${split_image}.fits /$1/${nick}/${RUNDIR}/SCIENCE/SPLIT_IMAGES

    if [ ! -d "/$1/${nick}/${RUNDIR}/${WEIGHTSDIR}" ]; then
      mkdir "/$1/${nick}/${RUNDIR}/${WEIGHTSDIR}"
    fi

    if [ ! -f "/$1/${nick}/${RUNDIR}/${WEIGHTSDIR}/globalweight_2.fits" ]; then
	cp /$1/$2/../${WEIGHTSDIR}/globalweight_*.fits /$1/${nick}/${RUNDIR}/${WEIGHTSDIR}
	cp /$1/$2/../${WEIGHTSDIR}/globalflag_*.fits /$1/${nick}/${RUNDIR}/${WEIGHTSDIR}
    elif [ "/$1/$2/../${WEIGHTSDIR}/globalweight_2.fits" -nt "/$1/${nick}/${RUNDIR}/${WEIGHTSDIR}/globalweight_2.fits" ]; then
	cp /$1/$2/../${WEIGHTSDIR}/globalweight_*.fits /$1/${nick}/${RUNDIR}/${WEIGHTSDIR}
	cp /$1/$2/../${WEIGHTSDIR}/globalflag_*.fits /$1/${nick}/${RUNDIR}/${WEIGHTSDIR}
    else
	echo "/$1/${nick}/${RUNDIR}/${WEIGHTSDIR}/globalweight_2.fits already up-to-date"
    fi
      

  done
}

rm -f ${TEMPDIR}/images_$$

#adam-BL# log_status $?
