#!/bin/bash

. progs.ini
. bash_functions.include

dir=$1
oldext=$2
newext=$3

for file in `ls ${dir}/*${newext}.fits`; do

    base=`basename ${file} ${newext}.fits`
    oldfile=${dir}/${base}${oldext}.fits
    
    if [ ! -e ${oldfile} ]; then
	echo "${oldfile} does not exist!"
	continue
    fi

    badccd=`dfits ${oldfile} | fitsort -d BADCCD | awk '{print $2}'`
    if [ "${badccd}" = "1" ]; then
	value 1
	writekey ${file} BADCCD "${VALUE} / Ignore CCD in processing" REPLACE

    fi

done