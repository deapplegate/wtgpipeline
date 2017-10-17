#!/bin/bash

# $Id: distribute_standards_subaru.sh,v 1.3 2009-02-12 23:55:34 dapple Exp $#

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

#$1: main directory
#$2: run/science directory
#$3: image extension (ext) on ..._iext.fits (i is the chip number)
#$4: minimum overlap for counting exposures to the same set
#$5: lookup file: nick full_name ra dec nicknames
#$6: weights directory

. ${INSTRUMENT:?}.ini

# configuration parameters:

if [ $6 ];then
    WEIGHTSDIR=$6
else
    WEIGHTSDIR=WEIGHTS
fi

NIGHT=`dirname $2 | awk -F'_' '{print $1}'`
FILTER=`dirname $2 | awk -F'_' '{print $2}'`
RUNDIR=${FILTER}_${NIGHT}_CALIB

echo "RUNDIR: ${RUNDIR}"

FILTERKEY="FILTER"
OBJECTKEY="OBJECT"
RAKEY="CRVAL1"
DECKEY="CRVAL2"

rm -f ${TEMPDIR}/*_$$

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
    NAME=`basename ${IMAGE} .fits`
    RA=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${RAKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`
    DEC=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${DECKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`
    OBJECT=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${OBJECTKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`
    FILTER=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${FILTERKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`

    nick=`echo $OBJECT | perl -e 'while(<STDIN>){/^([A-Za-z]+\d+)/; print "$1\n"}'`

    if [ -z ${nick} ]; then
	echo "Skipping ${NAME}"
	continue
    fi

    echo ${NAME} ${OBJECT} ${FILTER} ${RA} ${DEC} >> ${TEMPDIR}/${nick}_$$;
    echo ${nick} >> ${TEMPDIR}/nicknames_tmp.dat_$$
  done
}

cat ${TEMPDIR}/nicknames_tmp.dat_$$ | sort | uniq > ${TEMPDIR}/nicknames.dat_$$

cat ${TEMPDIR}/nicknames.dat_$$ |\
{
    while read NICKNAME
    do

	cat ${TEMPDIR}/${NICKNAME}_$$ |\
        {
	    while read FILE CLUSTER FILTER ra dec
	    do
		nnick=`grep ${CLUSTER} $5 | wc | awk '{print $1}'`

		if [ ${nnick} -eq 1 ]; then
		    nick=`grep ${CLUSTER} $5 | awk '{print $1}'`	
		else
	nick=`awk 'function acos(x) { return atan2((1.-x^2)^0.5,x) }
        {
          dist=57.2958*acos(cos(1.5708-('${dec}'*0.01745))*cos(1.5708-($4*0.01745)) + (sin(1.5708-('${dec}'*0.01745))*sin(1.5708-($4*0.01745)))*cos(('${ra}'-$3)*0.01745))
          if( dist<1.5 ) print $1}' $5`
		fi

		if [ ! -z ${nick} ]; then
		    echo ${nick}
		    break
		fi
	    done
	} > ${TEMPDIR}/nickname_$$

	nick=`cat ${TEMPDIR}/nickname_$$`

	echo "${NICKNAME} ${nick}"

	if [ ! -d "/$1/${nick}" ]; then
	    mkdir "/$1/${nick}"
	fi

	if [ ! -d "/$1/${nick}/${RUNDIR}" ]; then
	    mkdir "/$1/${nick}/${RUNDIR}"
	fi
	
	if [ ! -d "/$1/${nick}/${RUNDIR}/SCIENCE" ]; then
	    mkdir "/$1/${nick}/${RUNDIR}/SCIENCE"
	fi

	if [ ! -d "/$1/${nick}/${RUNDIR}/${WEIGHTSDIR}" ]; then
	    mkdir "/$1/${nick}/${RUNDIR}/${WEIGHTSDIR}"
	fi

	files=`cat ${TEMPDIR}/${NICKNAME}_$$ | awk '{print $1}'`

	echo $files 
	echo $files | wc | awk '{print $2}'
	echo

	for file in $files; do

	    ln -s $1/$2/${file}.fits $1/${nick}/${RUNDIR}/SCIENCE/
	    ln -s $1/$2/../${WEIGHTSDIR}/${file}.*.fits $1/${nick}/${RUNDIR}/${WEIGHTSDIR}/

	done
	
	

  done
}

rm -f ${TEMPDIR}/*_$$

#adam-BL# log_status $?
