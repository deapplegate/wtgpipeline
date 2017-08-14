#!/bin/bash -x

# the script creates hough images for science frames.
# 
# First version : 31/01/2007
# 

# $1: main directory
# $2: science dir.
# $3: image extension (ext) on ..._iext.fits (i is the chip number)
# $4: chips to be processed

. ${INSTRUMENT:?}.ini
. progs.ini

# parameters 
ELL=0.3


WEIGHTDIR="/$1/WEIGHTS"
TEMPDIR=.

# export PWD for progs.ini
PROGS_DIR=$PWD
export PROGS_DIR;
export PIPESOFT;

CHIP=$4
ls -1 /$1/$2/*_${CHIP}$3.fits > ${TEMPDIR}/crw_images_$$

cat ${TEMPDIR}/crw_images_$$ |\
      {
    while read file
        do
# Create the segmentation image
cd /$1/$2
BASE=`basename ${file} $3.fits`
SEG=${BASE}$3_SEG.fits




WEIGHT=${BASE}$3_SEG_hSN.fits


if [ ! -f ${WEIGHT} ]; then
     echo perl ${S_STRACK_HOUGH} -seg ${SEG} -instrum ${INSTRUMENT} -hweight_only -hweight_fin HTweight_${INSTRUMENT}.fits
     perl ${S_STRACK_HOUGH} -seg ${SEG} -instrum ${INSTRUMENT} -hweight_only -hweight_fin HTweight_${INSTRUMENT}.fits
fi
break

    done
    }
  

