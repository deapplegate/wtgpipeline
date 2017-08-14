#!/bin/bash

# splits WFI FIts extension images into the
# eight chips. Uses the fitssplit program

# $1: main directory
# $2: science directory

# create image list: we assume that ONLY unsplit
# images are in the directory

. WFI.ini


FILES=`ls $1/$2/*.fits`

cd /$1/$2

mkdir ORIGINALS

for FILE in ${FILES}
do
  i=1
  while [ "${i}" -lt "9" ]
  do
    ${P_FITSSPLIT} -i ${FILE} -x ${i}
    i=$(( $i + 1 ))
  done    
  mv ${FILE} ORIGINALS
done
