#!/bin/bash -xv

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

for CHIP in $4
do
  ls -1 /$1/$2/*_${CHIP}$3.fits > ${TEMPDIR}/crw_images_$$
  
  cat ${TEMPDIR}/crw_images_$$ |\
      {
      while read file
	do
	
	# Create the segmentation image
	cd /$1/$2
	BASE=`basename ${file} $3.fits`
	WEIGHT=${WEIGHTDIR}/${BASE}$3.weight.fits
	IMAGE=${file}
	SEG=${BASE}$3_SEG.fits
	

	if [ ! -f ${SEG} ]; then
	
	    cd /$1/$2
	    echo perl ${S_STRACK_SEG} -image ${IMAGE} -weight ${WEIGHT} -ell ${ELL} -seeing -instrum ${INSTRUMENT} 
	    perl ${S_STRACK_SEG} -image ${IMAGE} -weight ${WEIGHT} -ell ${ELL} -seeing -instrum ${INSTRUMENT} 
	fi
	
	
	HSN=${BASE}$3_SEG_hSN.fits
	# create the hough image
	#SEG=${BASE}$3_SEG.fits
	
	if [ ! -f ${HSN} ]; then
	    echo perl ${S_STRACK_HOUGH} -seg ${SEG} -instrum ${INSTRUMENT} -hweight  -hweight_fin HTweight_${INSTRUMENT}.fits
	    perl ${S_STRACK_HOUGH} -seg ${SEG} -instrum ${INSTRUMENT} -hweight -check 0.8 -hweight_fin HTweight_${INSTRUMENT}.fits
	fi
      done
  }
  
done
