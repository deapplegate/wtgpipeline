#!/bin/bash -xv
. BonnLogger.sh
. log_start

# $1 clusterdir
# $2 filter
# $3 extension
# $3 astrocat [NOMAD-1, SDSS-DR6, etc]

clusterdir=$1
filter=$2
ext=$3
#astrocat=
#if [ $# -gt 3 ]; then
    astrocat=$4
#
astromadd=$5


#first, compile list of input runs


    find ${clusterdir}/${filter}/SCIENCE  -maxdepth 1 -name \*${ext}.fits -print >> file.list_$$



###

if [ ! -s file.list_$$ ]; then
    echo "Cannot find any files"
    log_status 8 "Cannot find any files"
    exit 8
fi


###verify all input files are present and are of consistant size

function testExists {
    # $1 filename
    
    base=`basename $1 .fits`

    if [ ! -f ${clusterdir}/${filter}/SCIENCE/${base}.fits ]; then
	echo "File does not exist: ${1}"
	log_status 1 "File does not exist: ${1}"
	exit 1
    fi

    if [ ! -f ${clusterdir}/${filter}/WEIGHTS/${base}.weight.fits ]; then
	echo "Weight file does not exist: ${base}.weight.fits"
	log_status 2 "Weight file does not exist: ${base}.weight.fits"
	exit $?
    fi

    instrument=`dfits ${clusterdir}/${filter}/SCIENCE/${base}.fits | fitsort -d INSTRUM | awk '{print $2}'`

    if [ "${instrument}" == "SUBARU" ]; then

	if [ ! -f ${clusterdir}/${filter}/WEIGHTS/${base}.flag.fits ]; then
	    echo "Flag file does not exist: ${base}.flag.fits"
	    log_status 3 "Flag file does not exist: ${base}.flag.fits"
	    exit 3
	fi
    fi

    if [ ! -z "$astrocat" ]; then

	headerbase=`basename $1 ${ext}.fits`

	if [ ! -f ${clusterdir}/${filter}/SCIENCE/headers${astromadd}/${headerbase}.head ]; then
	    echo "Header file does not exist: ${headerbase}.head"
	    log_status 4 "Header file does not exist: ${headerbase}.head"
	    exit 4
	fi
    fi

}

#################

function testMinSize {
    size1=$1
    size2=$2

    isGreater=`echo "(${size1} > ${size2});" | bc`

    return $isGreater
}


for file in `cat file.list_$$`; do
    echo $file

    BADCCD=`dfits $file | fitsort -d BADCCD | awk '{print $2}'`
    if [ "$BADCCD" = "1" ]; then
	echo "Continuing past"
	continue
    fi

    testExists $file
    exitcode=$?
    if [ $exitcode -gt 0 ]; then
	exit $exitcode
    fi

    base=`basename $file .fits`
    
    scienceActual=`readlink -f $file`
    weightActual=`readlink -f ${clusterdir}/${filter}/WEIGHTS/${base}.weight.fits`
    flagActual=`readlink -f ${clusterdir}/${filter}/WEIGHTS/${base}.flag.fits`
    
    scienceSize=`stat -c%s ${scienceActual}`
    weightSize=`stat -c%s ${weightActual}`
    flagSize=`stat -c%s ${flagActual}`


    testMinSize ${scienceSize} 1000000
    if [ $? -eq 0 ]; then
	echo "Science file size mismatch: ${reffile} ${file}"
	log_status 5 "Science file size mismatch: ${reffile} ${file}"
	exit $?
    fi
    
    testMinSize ${weightSize} 1000000
    if [ $? -eq 0 ]; then
	echo "Weight file size mismatch: ${reffile} ${file}"
	log_status 6 "Weight file size mismatch: ${reffile} ${file}"
	exit $?
    fi
    
    instrument=`dfits ${clusterdir}/${filter}/SCIENCE/${base}.fits | fitsort -d INSTRUM | awk '{print $2}'`

    if [ "${instrument}" == "SUBARU" ]; then
	testMinSize ${flagSize} 1000000
	if [ $? -eq 0 ]; then
	    echo "Flag file size mismatch: ${reffile} ${file}"
	    log_status 7 "Flag file size mismatch: ${reffile} ${file}"
	    exit $?
	fi
    fi
    


    
done

rm file.list_$$




log_status 0
