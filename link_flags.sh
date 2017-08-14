#!/bin/bash

subaru=/nfs/slac/g/ki/ki05/anja/SUBARU
cluster=$1
filter=$2

curdir=`pwd`


cd ${subaru}/${cluster}/${filter}/WEIGHTS/

rext=''
use_rext=`ls *R.weight.fits | wc -l`
use_rext2=`ls *RI.weight.fits | wc -l`
if [ "${use_rext}" != "0" ] || [ "${use_rext2}" != "0" ]; then
    rext=R
fi


for file in *.flag.fits; do

    base=`basename ${file} .flag.fits`
    sourcefile=`readlink ${file}`
    sourcedir=`dirname ${sourcefile}`
    ln -s ${sourcedir}/${base}${rext}.flag.fits ${base}${rext}I.flag.fits

done

cd ${curdir}