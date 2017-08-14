#!/bin/bash -uxv

subarudir=$1
cluster=$2
filter=$3

flagFile=
if [ $# -gt 3 ]; then
    flagFile=$4
fi

. progs.ini

workdir=${subarudir}/${cluster}/masks

if [ ! -d $workdir ]; then
    mkdir $workdir
fi

coadd_dir=${subarudir}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_good

if [ -z "$flagFile" ]; then

./maskstars.sh -i ${coadd_dir}/coadd.fits \
    -o ${workdir}/coadd.stars.reg \
    -a USNOB1 \
    -s ${AUTOMASKCONF}/SUBARU_V_15.reg \
    -p 14.0 -m 0.2 -l 18.5

fi


if [ ! -z "$flagFile" ]; then

    base=`basename $flagFile .reg`
    
    sed 's/polygon/ POLYGON/g' ${workdir}/${flagFile} > ${workdir}/${base}.ww.reg

    ${P_WW} -c lensconf/poly_flag.ww \
        -FLAG_NAMES ${coadd_dir}/coadd.flag.fits \
        -FLAG_MASKS "0xfff" \
        -FLAG_WMASKS "0x0" \
        -FLAG_OUTFLAGS "1,2,4,8,16,32,64,128,256,512,1024,2048" \
	-POLY_NAMES ${workdir}/${base}.ww.reg \
	-POLY_OUTFLAGS "4096" \
	-OUTFLAG_NAME ${coadd_dir}/coadd.flag.masked.fits

    mv ${coadd_dir}/coadd.flag.fits ${coadd_dir}/coadd.flag.swarp.fits
    mv ${coadd_dir}/coadd.flag.masked.fits ${coadd_dir}/coadd.flag.fits

fi




