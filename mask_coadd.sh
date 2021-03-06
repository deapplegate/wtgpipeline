#!/bin/bash
set -uxv
#adam-use# use to make the coadd.stars.reg file (without input mask file) or to apply a coadd mask/reg file to the coadd flags file
#adam-example# ./mask_coadd.sh ${cluster} W-C-RC coadd.stars.reg 'gabodsid1554' 2>&1 | tee -a OUT-mask_coadd.stars.${cluster}.log
#adam-example# ./mask_coadd.sh ${cluster} W-C-RC coadd.asteroids.reg 'gabodsid1554' 2>&1 | tee -a OUT-mask_coadd.asteroids.${cluster}.log
#adam-example# ./mask_coadd.sh ${cluster} W-C-RC coadd.final_combination.reg 'gabodsid1554' 2>&1 | tee -a OUT-mask_coadd.final.${cluster}.log

#adam-example# ./mask_coadd.sh MACS1226+21 W-C-RC coadd.stars.reg 2>&1 | tee -a OUT-mask_coadd.stars.log
#adam-example# ./mask_coadd.sh MACS1226+21 W-C-RC coadd.asteroids.reg 2>&1 | tee -a OUT-mask_coadd.asteroids.log

#adam-old# subarudir=$1
#adam-old# cluster=$2
#adam-old# filter=$3
subarudir=${SUBARUDIR}
cluster=$1
filter=$2

flagFile=''
if [ $# -gt 2 ]; then
    flagFile=$3
fi
lenstype='good'
if [ $# -gt 3 ]; then
    lenstype=$4
fi

. progs.ini > /tmp/progs.out 2>&1

workdir=${subarudir}/${cluster}/masks

if [ ! -d $workdir ]; then
    mkdir $workdir
fi

coadd_dir=${subarudir}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${lenstype}

#if no region file given, then make the coadd.stars.reg file
if [ -z "$flagFile" ]; then

    ./maskstars.sh -i ${coadd_dir}/coadd.fits \
    -o ${workdir}/coadd.stars.reg \
    -a USNOB1 \
    -s ${AUTOMASKCONF}/SUBARU_V_15.reg \
    -p 14.0 -m 0.2 -l 18.5

fi


#if you give an input region file given, then apply it to the coadd
if [ ! -z "$flagFile" ]; then

    base=`basename $flagFile .reg`
    
    sed 's/polygon/POLYGON/g' ${workdir}/${flagFile} > ${workdir}/${base}.ww.reg

    ${P_WW} -c lensconf/poly_flag.ww \
        -WEIGHT_NAMES ${coadd_dir}/coadd.weight.fits \
	-WEIGHT_MIN 1e-6 \
        -WEIGHT_MAX 1e9 \
	-POLY_NAMES ${workdir}/${base}.ww.reg \
	-POLY_OUTWEIGHTS "0" \
	-OUTWEIGHT_NAME ${coadd_dir}/coadd.weight.masked_poly.fits
    ic -p 8 '16 1 %1 1e-6 < ?' ${coadd_dir}/coadd.weight.masked_poly.fits > ${coadd_dir}/coadd.flag.masked_poly.fits
    mv ${coadd_dir}/coadd.flag.fits ${coadd_dir}/coadd.flag.swarp.fits
    mv ${coadd_dir}/coadd.weight.fits ${coadd_dir}/coadd.weight.swarp.fits
    mv ${coadd_dir}/coadd.flag.masked_poly.fits ${coadd_dir}/coadd.flag.fits
    mv ${coadd_dir}/coadd.weight.masked_poly.fits ${coadd_dir}/coadd.weight.fits
    #adam-tmp# #ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale ${coadd_dir}/coadd.weight.masked_poly.fits ${coadd_dir}/coadd.weight.fits &
    #adam-tmp# ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale ${coadd_dir}/coadd.flag.masked_poly.fits  ${coadd_dir}/coadd.weight.masked_poly.fits &

    ## ORIGINAL ##
    ########${P_WW} -c lensconf/poly_flag.ww \
    ########    -FLAG_NAMES ${coadd_dir}/coadd.flag.fits \
    ########    -FLAG_MASKS "0xfff" \
    ########    -FLAG_WMASKS "0x0" \
    ########    -FLAG_OUTFLAGS "1,2,4,8,16,32,64,128,256,512,1024,2048" \
    ########    -POLY_NAMES ${workdir}/${base}.ww.reg \
    ########    -POLY_OUTFLAGS "4096" \
    ########    -OUTFLAG_NAME ${coadd_dir}/coadd.flag.masked.fits

    ## ATTEMPT THAT FAILED ##
    ########${P_WW} -c lensconf/poly_flag.ww \
    ########    -FLAG_NAMES ${coadd_dir}/coadd.flag.fits \
    ########    -WEIGHT_NAMES ${coadd_dir}/coadd.weight.fits \
    ########    -WEIGHT_MIN 1e-6 \
    ########    -WEIGHT_MAX 1e9 \
    ########    -WEIGHT_OUTFLAGS "0" \
    ########    -FLAG_WMASKS "16" \
    ########    -FLAG_MASKS "1,16" \
    ########    -FLAG_OUTFLAGS "1,16" \
    ########    -POLY_NAMES ${workdir}/${base}.ww.reg \
    ########    -POLY_OUTFLAGS "4" \
    ########    -POLY_OUTWEIGHTS "0" \
    ########    -OUTWEIGHT_NAME ${coadd_dir}/coadd.weight.masked.fits \
    ########    -OUTFLAG_NAME ${coadd_dir}/coadd.flag.masked.fits
    ########

    #adam-tmp# mv ${coadd_dir}/coadd.flag.fits ${coadd_dir}/coadd.flag.swarp.fits
    #adam-tmp# mv ${coadd_dir}/coadd.flag.masked.fits ${coadd_dir}/coadd.flag.fits
    #ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale ${coadd_dir}/coadd.flag.masked16.fits ${coadd_dir}/coadd.flag.masked.fits ${coadd_dir}/coadd.flag.fits ${coadd_dir}/coadd.weight.masked.fits ${coadd_dir}/coadd.weight.fits &

fi
