#! /bin/bash -xv
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
. progs.ini

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki02/xoc/anja/nobackup/SUBARU/

RAWDATA=/nfs/slac/g/ki/ki11/daveb/rawdata/


#runs="0204 0305 0403 0506 0606 0703 0704 0707 0807 1105 1202 1206"
#runs="0807 1105 1202 1206"
#runs="0403b"
runs="0602"

for run in ${runs}
do

    echo ${run} > tmp.run

    month=`awk 'BEGIN{FS=""}{print $1 $2}' tmp.run`
    year=`awk 'BEGIN{FS=""}{print $3 $4}' tmp.run`

#    myrun=`awk 'BEGIN{printf "20%.2i_%.2i", '${year}', '${month}'}'`

    echo ${run} ${year} ${month} ${myrun}


    find ${RAWDATA}/subaru${month}${year} -maxdepth 1 -name SUPA\*fits\* > cpfiles_$$.txt

    while read FILE
    do
	cp ${FILE} ${SUBARUDIR}
    done < cpfiles_$$.txt
    rm -f cpfiles_$$.txt

    cd ${SUBARUDIR}

    gunzip *.fits.gz

    IMAGE=`find . -maxdepth 1 -name \*.fits | ${P_GAWK} '(NR==1) {print $0}'`
    echo ${IMAGE}
    myrun=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} DATE-OBS |\
	${P_GAWK} '($1!="FILE") {print $2}'`

    echo ${myrun}

    if [ ! -d ${myrun}_RAWDATA ]; then
      mkdir ${myrun}_RAWDATA
    fi

    find . -maxdepth 1 -name SUPA????????\*fits > allfiles_$$.txt
    sed 's/[0-9]\.fits//' allfiles_$$.txt | sort | uniq > uniqfiles_$$.txt

    while read IMAGE
    do
	BASE=`basename ${IMAGE}`
	echo ${BASE}
	mefcreate ${BASE}?.fits -OUTPUT_IMAGE ${BASE}.fits 
	mv ${BASE}?.fits ${myrun}_RAWDATA
    done < uniqfiles_$$.txt

    rm -f allfiles_$$.txt
    rm -f uniqfiles_$$.txt

# sort images by type, filter

    find . -maxdepth 1 -name SUPA???????\*fits > allfiles_mef_$$.txt

    while read IMAGE
    do
	BASE=`basename ${IMAGE}`

	filter=`dfits -x 1 ${BASE} | fitsort FILTER01 | awk '{if($1=="'${BASE}'") print $2}'`

	obstype=`dfits -x 1 ${BASE} | fitsort DATA-TYP | awk '{if($1=="'${BASE}'") print $2}'`

	exptime=`dfits -x 1 ${BASE} | fitsort EXPTIME | awk '{if($1=="'${BASE}'") print $2}'`

	long=`awk 'BEGIN{if('${exptime}'>=30) print 1; else print 0}'`

	if [ "${obstype}" = "OBJECT" ];then
	    if [ ${long} -eq 1 ]; then
		obstype=SCIENCE
	    else
		obstype=STANDARD
	    fi
	fi

	if [ "${obstype}" = "BIAS" ] || [ "${obstype}" = "DARK" ]; then
	    filter=${obstype}
	fi

	if [ ! -d ${myrun}_${filter} ]; then
	    mkdir ${myrun}_${filter}
	fi

	if [ ! -d ${myrun}_${filter}/${obstype} ]; then
	    mkdir ${myrun}_${filter}/${obstype}
	fi

	if [ ! -d ${myrun}_${filter}/${obstype}/ORIGINALS ]; then
	    mkdir ${myrun}_${filter}/${obstype}/ORIGINALS
	fi

	echo ${BASE} ${obstype} ${exptime} ${long}
  
	mv ${BASE} ${myrun}_${filter}/${obstype}/ORIGINALS

    done < allfiles_mef_$$.txt

    rm -f allfiles_mef_$$.txt

done

#adam-BL# log_status $?
