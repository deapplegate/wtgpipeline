#!/bin/bash

# the script creates links for given chips
# it should be called AFTER images have been
# split and checked for integrity
#
# 30.05.04:
# tempaorary files go to a TEMPDIR directory

# $1: directory with the images
# $2: scratch directory where images
#     should go
# $3: chips that should go to scratch

for CHIP in ${3}
do
  ls -1 /$1/*_${CHIP}.fits > ${TEMPDIR}/linkimages_$$
  
  cat ${TEMPDIR}/linkimages_$$ |\
  {
    while read FILE
    do
      BASE=`basename ${FILE}`
      mv ${FILE} /$2
      ln -s /$2/${BASE} /$1/${BASE} 
    done
  }
done
