#!/bin/bash
#####################
# Creates a mask file from an imask txt file (from drawRegions.pl)
#
# $1 maindir
# $2 workdir
#
# Assumes files are named workdir_chip.imask
#####################
. BonnLogger.sh
. log_start
#CVSID="$Id: create_badpixel_mask.sh,v 1.9 2008-07-09 18:22:59 dapple Exp $"

REDDIR=`pwd`

. ${INSTRUMENT:?}.ini


MAINDIR=$(cd $1 && pwd)

if [ ! -d ${MAINDIR}/${2}_mask ]; then
    mkdir ${MAINDIR}/${2}_mask
fi

cd ${IRAFDIR}

for ((CHIP=1;CHIP<=10;CHIP+=1));
do

    FILE=${MAINDIR}/${2}/${2}_${CHIP}.imask
    echo $FILE
    
    if [ ! -e ${FILE} ]; then
	ic -c ${SIZEX[${CHIP}]} ${SIZEY[${CHIP}]} 0 \
	    > ${MAINDIR}/${2}_mask/${2}_mask_${CHIP}.fits
	continue
    fi

    if [ -e ${MAINDIR}/${2}_mask/${2}_mask_${CHIP}.fits ]; then
	rm ${MAINDIR}/${2}_mask/${2}_mask_${CHIP}.fits
    fi
    
    {
	echo 'flprc'
	echo "proto"
	sleep 1
	echo "text2mask ${FILE} ${2}_${CHIP}_$$ ${SIZEX[${CHIP}]} ${SIZEY[${CHIP}]}"
	sleep 1
	echo "imcopy ${2}_${CHIP}_$$.pl ${MAINDIR}/${2}_mask/${2}_mask_${CHIP}.fits"
	sleep 1
	echo 'flprc'
	echo "log"
    } | ${P_CL}
    

    rm ${2}_${CHIP}_$$.pl
done

cd ${REDDIR}
log_status $?
