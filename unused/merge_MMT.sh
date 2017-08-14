#!/bin/bash

# MMT Megacam has 36 CCDs which each having two readouts.
# The script merges the two readouts to one file representing
# a Megacam CCD.

#$1: main dir.
#$2: data dir.
#$3: image ending
#$4: new directory containing the merged readouts.

. ${INSTRUMENT:?}.ini
. bash_functions.include

if [ ! -d /$1/$4 ]; then
  mkdir /$1/$4
fi

FILES=`ls /$1/$2/*_1$3.fits`

for file in ${FILES}
do
  BASE=`basename ${file} _1$3.fits`  
  i=1
  id=1  
  while [ "${i}" -le "${NCHIPS}" ]
  do
    j=$(( $i + 1 ))
    #
    # merge readouts to a single Megacam CCD. Note that the first readout of each CCD
    # already contains 'correct' header information (astrometry, photometry) for
    # the resulting CCD.
    ${P_ALBUM} -h 1 2 1 /$1/$2/${BASE}_${i}$3.fits /$1/$2/${BASE}_${j}$3.fits > /$1/$4/${BASE}_${id}$3.fits
    value ${id}
    writekey /$1/$4/${BASE}_${id}$3.fits IMAGEID "${VALUE}" REPLACE
    i=$(( $i + 2 ))
    id=$(( $id + 1 ))
  done 
done
