#!/bin/bash
set -xv
#!/bin/bash -u

#adam-BL##adam-BL#. BonnLogger.sh
##adam-BL##adam-BL#. log_start

#CVSID="$Id: setup_general.sh,v 1.11 2010-10-05 02:29:02 anja Exp $"

# The script calls setup_SUBARU.sh or setup_CFH12K.sh 

# $1: directory from which to read the first image
#     to obtain the observation date (We use the
#     MJD keyword)
# $2 file to write results to
. progs.ini > /tmp/progs.out 2>&1

IMAGE=`find $1/ -maxdepth 1 -name \*.fits | sort -r | ${P_GAWK} '(NR==1) {print $0}'`

INSTRUM=`${P_DFITS} ${IMAGE} | ${P_FITSORT} -d INSTRUM |\
        ${P_GAWK} '($1!="FILE") {print $2}'`
DETECTOR=`${P_DFITS} -x 1 ${IMAGE} | ${P_FITSORT} -d DETECTOR |\
        ${P_GAWK} '($1!="FILE") {print $2}'`
INSTRUME=`${P_DFITS} -x 1 ${IMAGE} | ${P_FITSORT} -d INSTRUME |\
        ${P_GAWK} '($1!="FILE") {print $2}'`
ORIGIN=`${P_DFITS} ${IMAGE} | ${P_FITSORT} -d ORIGIN |\
        ${P_GAWK} '($1!="FILE") {print $2}'`

INSTRUMENT=UNKNOWN
COMMENT=
if [ "${INSTRUM}" != "KEY_N/A" ]; then
    if [ "${INSTRUM}" == "SUBARU" ] || [ "${INSTRUM}" == "CFH12K" ]; then
	export INSTRUMENT=${INSTRUM}
	./setup_${INSTRUM}.sh $1
    elif [ "${INSTRUM}" == "MEGAPRIME" ]; then
	export INSTRUMENT=MEGAPRIME
    elif [ "${INSTRUM}" == "WHT" ]; then
        export INSTRUMENT=WHT
    elif [ "${INSTRUM}" == "ACS" ]; then
	export INSTRUMENT=ACS
    elif [ "${INSTRUM}" == "WFPC2" ]; then
	export INSTRUMENT=WFPC2
    elif [ "${INSTRUM}" == "CFH12Kmos" ]; then
	export INSTRUMENT=CFH12Kmos
    elif [ "${INSTRUM}" == "WIRCAM" ]; then
	export INSTRUMENT=WIRCAM
    elif [ "${INSTRUM}" == "SDSS" ]; then
	export INSTRUMENT=SDSS
    else
	echo "Instrument ${INSTRUM} not known!" >&2
	#adam-BL##adam-BL#log_status 1 "Instrument ${INSTRUM} not known!"	
	exit 2
    fi
elif [ "${DETECTOR}" == "CFH12K" ]; then
    export INSTRUMENT=CFH12K
    ./setup_CFH12K.sh $1
elif [ "${INSTRUME}" == "SuprimeCam" ]; then
    export INSTRUMENT=SUBARU
    ./setup_SUBARU.sh $1
elif [ "${INSTRUME}" == "WFPC2" ]; then
    export INSTRUMENT=WFPC2
elif [ "${ORIGIN}" == "SDSS" ]; then
    export INSTRUMENT=SDSS
else
    echo "Cannot determine instrument of ${IMAGE}." >&2
    #adam-BL#log_status 2 "Can not determine instrument of ${IMAGE}."
fi

echo ${INSTRUMENT} > $2

##adam-BL##adam-BL#log_status 0
