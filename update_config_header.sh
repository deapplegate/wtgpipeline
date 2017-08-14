#!/bin/bash

### script to add the CONFIG keyword to images

# $1: main directory
# $2: INSTRUMENT
# $3: OBJECT

INSTRUMENT="'${2}'"

. progs.ini
. bash_functions.include


cd $1

FILES=`find . -maxdepth 1 -name \*.fits`

for IMAGE in ${FILES}
do

    GABODSID=`dfits ${IMAGE} | fitsort -d GABODSID | awk '{print $2}'`
    if [ ${GABODSID} = "KEY_N/A" ]; then
	continue
    fi

    if [ ${GABODSID} -ge 575 ] && [ ${GABODSID} -lt 691 ]; then
      echo "8 chip configuration"  
      CONFIG="'8'"
    fi
    
    if [ ${GABODSID} -ge 691 ] && [ ${GABODSID} -lt 817 ]; then
      echo "9 chip configuration"  
      CONFIG="'9'"
    fi
    
    if [ ${GABODSID} -ge 817 ] && [ ${GABODSID} -lt 1309 ]; then
      echo "10_1 chip configuration"  
      CONFIG="'10_1'"
    fi
    
    if [ ${GABODSID} -ge 1309 ] && [ ${GABODSID} -lt 3470 ]; then
      echo "10_2 chip configuration"  
      CONFIG="'10_2'"
    fi

    if [ ${GABODSID} -ge 3470 ] && [ ${GABODSID} -lt 5000 ]; then
      echo "10_3 chip configuration"  
      CONFIG="'10_3'"
    fi

    if [ ${GABODSID} -ge 5000 ]; then
	echo "no config file provided yet. Exiting !!"
	log_status 1 "no config file provided yet"
	exit 1
    fi

    ic=`awk 'BEGIN{if("'${IMAGE}'"~"I.fits") print 1; else print 0}'`

    if [ ${ic} -eq 1 ]; then
	oldimage=`basename ${IMAGE} I.fits`
	linkimage=`readlink -f ${oldimage}.fits`
    else
	linkimage=`readlink -f ${IMAGE}`
    fi

#    echo ${IMAGE} ${linkimage}
#    IMAGE=`readlink -f $IMAGE`
    imagedir=`dirname ${linkimage}`
    rundir=`dirname $imagedir`
    run=`basename $rundir`
    
    value "'${run}'"
    writekey ${IMAGE} PPRUN "${VALUE} / Preprocess Run" REPLACE


    value "${CONFIG}"
    writekey ${IMAGE} CONFIG "${VALUE} / CCD configuration" REPLACE

    value "${INSTRUMENT}"
    writekey ${IMAGE} INSTRUM "${VALUE} / Instrument" REPLACE

    if [ $# -gt 2 ]; then
	value "'$3'"
	writekey ${IMAGE} OBJNAME "${VALUE} / Official Obj Name" REPLACE
    fi

# fix ROTATION keyword:
# I've only accounted for two rotation angles:
# 0:  N right, E up   (  0  1  1  0 )
# 1:  N up, E left    ( -1  0  0  1 )
# but there are also:
# 2:  N left, E down  (  0 -1 -1  0 )
# 3:  N down, E right (  1  0  0 -1 )
# However, for config 8 and 9 the original keywords are messed up: 
# CD1_1 and CD2_1 (the RA keywords) 
# are negative
# CD1_2 should be correct, though --> thus, if a ROATION 0 images
# has CD1_2 < 0, then the ROTATION needs to be changed to "2"
# likewise, if a ROTATION 1 image has CD2_2 < 0, the ROTATION
# needs to be changed to 3

    ROTATION=`dfits ${IMAGE} | fitsort -d ROTATION | awk '{print $2}'`
    if [ ${ROTATION} -eq 0 ]; then
	newROT=`dfits ${IMAGE} | fitsort CD1_2 | awk '($1!="FILE") {print $2}' | awk '{if($1>0) print 0; else print 2}'`
	value ${newROT}
	writekey ${IMAGE} ROTATION "${VALUE} / Rotation angle" REPLACE
	echo "${IMAGE}: ROTATION ${newROT}"
    elif [ ${ROTATION} -eq 1 ]; then
	newROT=`dfits ${IMAGE} | fitsort -d CD2_2 | awk '{print $2}' | awk '{if($1>0) print 1; else print 3}'`
	value ${newROT}
	writekey ${IMAGE} ROTATION "${VALUE} / Rotation angle" REPLACE
	echo "${IMAGE}: ROTATION ${newROT}"
    fi

done
