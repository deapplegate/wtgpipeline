#! /bin/bash -xv

### script which sorts a subdir with downloaded files according
### to data and type

# CVSId: $Id: sort_aux_data.sh,v 1.2 2009-01-29 00:09:09 anja Exp $

. progs.ini

REDDIR=`pwd`

MAINDIR=$1
AUXDATA=$2

# sort images by type, filter

cd ${MAINDIR}/${AUXDATA}

find . -maxdepth 1 -name SUPA???????\*fits > allfiles_mef_$$.txt

while read IMAGE
do
    BASE=`basename ${IMAGE}`

    date=`dfits ${BASE} | fitsort DATE-OBS | awk '{if($1=="'${BASE}'") print $2}'`

    filter=`dfits ${BASE} | fitsort FILTER01 | awk '{if($1=="'${BASE}'") print $2}'`

    obstype=`dfits ${BASE} | fitsort DATA-TYP | awk '{if($1=="'${BASE}'") print $2}'`

    exptime=`dfits ${BASE} | fitsort EXPTIME | awk '{if($1=="'${BASE}'") print $2}'`

    long=`awk 'BEGIN{if('${exptime}'>=30) print 1; else print 0}'`

    RUNDIR="${date}_${filter}"

    if [ "${obstype}" = "OBJECT" ];then
	if [ ${long} -eq 1 ]; then
      	   obstype=SCIENCE
	else
	   obstype=STANDARD
	fi
    fi

    if [ "${obstype}" = "BIAS" ] || [ "${obstype}" = "DARK" ]; then
	filter=${obstype}
	RUNDIR="${date}_${obstype}"
    fi

    if [ ! -d ${MAINDIR}/${RUNDIR} ]; then
	mkdir ${MAINDIR}/${RUNDIR}
    fi

    if [ ! -d ${MAINDIR}/${RUNDIR}/${obstype} ]; then
	mkdir ${MAINDIR}/${RUNDIR}/${obstype}
    fi

    if [ ! -d ${MAINDIR}/${RUNDIR}/${obstype}/ORIGINALS ]; then
	mkdir ${MAINDIR}/${RUNDIR}/${obstype}/ORIGINALS
    fi

    echo ${BASE} ${obstype} ${exptime} ${long} ${MAINDIR}/${RUNDIR}/${obstype}/ORIGINALS

    cp ${BASE} ${MAINDIR}/${RUNDIR}/${obstype}

done < allfiles_mef_$$.txt

rm allfiles_mef_$$.txt
