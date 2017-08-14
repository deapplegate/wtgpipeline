#!/bin/bash

# this script creates 8x8-binned mosaics for each image.
# The highly enhanced contrast enables one to easily detect
# satellite tracks and reflections from bright stars outside
# the field.
# Furthermore you can see how well the flat fielding worked.
#
# 15.10.2004:
# - I introduced a new command line argument for
#   the BITPIX value of the result image (can be 16 or -32).
#
# - temporaray files are put into the directory pointed
#   to by TEMPDIR
#
# 25.11.2004:
# I introduced a PREFIX for the images to be mosaiced.
# This allows better to select certain images in 
# a directory.
#
# 11.04.2005:
# I rewrote the script to use the 'album' program for
# image combining instead the FLIPS based immosaic_WFI

# $1: main directory
# $2: science directory
# $3: PREFIX for images to be mosaiced
# $4: extension (e.g. OFCSFF)
# $5: bin size
# $6: BITPIX for output image (16 or -32)

. WFI.ini 

# set default for output BITPIX to 16:
if [ $# -lt 6 ]; then
  BITPIX=16
else
  BITPIX=$6
fi

cd $1/$2

if [ ! -d BINNED ]; then
  mkdir BINNED
fi

if [ -f ${TEMPDIR}/image_list_$$ ]; then
  rm ${TEMPDIR}/image_list_$$
fi

ls $3*$4.fits > ${TEMPDIR}/image_list_$$

cat ${TEMPDIR}/image_list_$$ |\
{
  k=0
  while read file
  do
    k=$(( $k + 1 ))
    if [ "${k}" -eq "1" ]; then
       BASE=`basename ${file} _1$4.fits`
       echo ${BASE}
       ${P_ALBUM} -p ${BITPIX} -b $5 4 2 ${BASE}_8$4.fits ${BASE}_7$4.fits\
                  ${BASE}_6$4.fits ${BASE}_5$4.fits ${BASE}_1$4.fits\
                  ${BASE}_2$4.fits ${BASE}_3$4.fits ${BASE}_4$4.fits >\
                  BINNED/${BASE}_mos.fits
    fi
    if [ "${k}" -eq "${NCHIPS}" ]; then
       k=0
    fi
  done
}

rm ${TEMPDIR}/image_list_$$
