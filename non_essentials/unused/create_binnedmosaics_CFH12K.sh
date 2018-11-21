#!/bin/bash

# this script creates 8x8-binned mosaics for each image.
# The highly enhanced contrast enables one to easily detect
# satellite tracks and reflections from bright stars outside
# the field.
# Furthermore you can see how well the flat fielding worked.
#
# 06.12.2005:
# - temporary files are now deleted at the end of processing.
# - I improved the condition for creating a BINNED subdirectory

# $1: main directory
# $2: science directory
# $3: PREFIX for images to be mosaiced
# $4: extension (e.g. OFCSFF)
# $5: bin size
# $6: BITPIX for output image (16 or -32)

. CFH12K.ini 

# set default for output BITPIX to 16:
if [ $# -lt 6 ]; then
  BITPIX=16
else
  BITPIX=$6
fi

cd $1/$2

if [ -f ${TEMPDIR}/image_list_$$ ]; then
  rm ${TEMPDIR}/image_list_$$
fi

ls $3*_1$4.fits > ${TEMPDIR}/image_list_$$

if [ -s ${TEMPDIR}/image_list_$$ ] && [ ! -d BINNED ]; then
  mkdir BINNED
fi


cat ${TEMPDIR}/image_list_$$ |\
{
  while read file
  do
       BASE=`basename ${file} _1$4.fits`
       echo ${BASE}
       ${P_ALBUM} -p ${BITPIX} -b $5 6 2 ${BASE}_1$4.fits ${BASE}_2$4.fits\
                  ${BASE}_3$4.fits ${BASE}_4$4.fits ${BASE}_5$4.fits\
                  ${BASE}_6$4.fits ${BASE}_7$4.fits ${BASE}_8$4.fits \
                  ${BASE}_9$4.fits ${BASE}_10$4.fits ${BASE}_11$4.fits \
                  ${BASE}_12$4.fits >\
                  BINNED/${BASE}_mos.fits
  done
}

rm ${TEMPDIR}/image_list_$$
