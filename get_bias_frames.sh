#! /bin/bash -xv
###########################
# Get the bias frames and copy them into the BIAS dir.
# 
# CVSID=$Id: get_bias_frames.sh,v 1.10 2009-01-13 17:57:19 dapple Exp $

. BonnLogger.sh
. log_start
. ${INSTRUMENT:?}.ini

SUBARUDIR=$1
run=$2
filter=$3
target=$4

if [ -d ${SUBARUDIR}/${run}_${filter}/BIAS ]; then
    rm -rf  ${SUBARUDIR}/${run}_${filter}/BIAS
fi

mkdir ${SUBARUDIR}/${run}_${filter}/BIAS

find ${SUBARUDIR}/${run}_${filter}/$4/ -maxdepth 1 -name 'SUPA*.fits' > tmpfiles_list

periodWarn=0

#forfile in ``; do
while read FILE
do
    NEWID=`./get_bias_period.sh $FILE`
    if [ ${ID} ]; then
	if [ ${NEWID} -ne ${ID} ]; then
	    periodWarn=1
	    ID=${NEWID}
	fi
    else
	ID=${NEWID}
    fi
done < tmpfiles_list

if [ ${periodWarn} -eq 1 ]; then
    echo WARNING DIFFERENT BIAS PERIODS!!!
    ./BonnLogger.py comment 'Warning: Different bias periods detected'
fi

if [ ${ID} -eq 0 ]; then
	ID=1
fi

ln -s ${SUBARUDIR}/BIAS_Set${NEWID}/BIAS_*.fits ${SUBARUDIR}/${run}_${filter}/BIAS/.

for ((i=1;i<=${NCHIPS};i+=1)); do
    if [ ! -s ${SUBARUDIR}/${run}_${filter}/BIAS/BIAS_$i.fits ]; then
	log_status 2 "Bad Bias Linking: Chip $i"
	exit 2
    fi
done

log_status 0
