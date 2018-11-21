#!/bin/bash -xv

# the script creates hough images for science frames.
# 
# First version : 31/01/2007
# 

# $1: main directory
# $2: science dir.
# $3: image extension (ext) on ..._iext.fits (i is the chip number)

. ${INSTRUMENT:?}.ini
. progs.ini

PROGS_DIR=$PWD
export PROGS_DIR;
export PIPESOFT;

 #parameters 

i=1
while [ "${i}" -le "${NCHIPS}" ]
do
  CHIPS="${CHIPS} ${i}"
  i=$(( $i + 1 ))
done


WEIGHTDIR="/$1/WEIGHTS"
TEMPDIR=.

ls -1 /$1/$2/*_1$3.fits > ${TEMPDIR}/crw_images_$$
#ls -1 /$1/$2/715230p_1$3.fits > ${TEMPDIR}/crw_images_$$
 
# Loop on the exposures 
cat ${TEMPDIR}/crw_images_$$ |\
      {
      while read file
	do

	# Create the reg files
	BASE=`basename ${file} _1$3.fits`
	
	echo "Working on ${BASE} ... \n"

	cd /$1/$2
	echo perl ${S_STRACK_HOUGH_DETECT} -root ${BASE} -ext ${3} -instrum ${INSTRUMENT} -noim -dthresh 0.8 -norefine
	#exit
	perl ${S_STRACK_HOUGH_DETECT}  -root ${BASE} -ext ${3} -instrum ${INSTRUMENT} -noim -dthresh 0.8 -norefine

	# copy the reg files at the right place
	MASKDIR=/$1/$2/STRACK
	if [ ! -d "${MASKDIR}" ]; then
	    mkdir ${MASKDIR}
	fi
	
	mv /$1/$2/*.reg ${MASKDIR}

      done
  }
  
# Remove epty reg-files
cd ${MASKDIR}
ls -1 ${MASKDIR}/*.reg > ${TEMPDIR}/reg_images_$$
cat ${TEMPDIR}/crw_images_$$ |\
      {
      while read file
	do
	
	TEST=`wc file | ${P_GAWK} '{print $1}'`
	if [ $TEST -le 3 ]; then
	    rm -f file
	fi

      done
}

rm -f ${TEMPDIR}/crw_images_$$ ${TEMPDIR}/reg_images_$$
