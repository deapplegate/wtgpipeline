#!/bin/bash

# this script creates binned mosaics for each Megacam image.
# It works with images split into the 72 Megacam readouts as
# well as for 36 CCDs, where the two readouts of each CCD have
# been merged again.

# The highly enhanced contrast enables one to easily detect
# satellite tracks and reflections from bright stars outside
# the field.
# Furthermore you can see how well the flat fielding worked.
#

# $1: main directory
# $2: science directory
# $3: PREFIX for images to be mosaiced
# $4: extension (e.g. OFCSFF)
# $5: bin size
# $6: MERGED/NOTMERGED (the NOTMERGED mode works images split into
#     the 72 Megacam readouts) 
# $7: BITPIX for output image (16 or -32)

. MMT_Megacam.ini 

# set default for output BITPIX to 16:
if [ $# -lt 7 ]; then
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

ls $3*_1$4.fits > ${TEMPDIR}/image_list_$$

cat ${TEMPDIR}/image_list_$$ |\
{
  while read file
  do
       BASE=`basename ${file} _1$4.fits`
       echo ${BASE}

       if [ "$5" == "MERGED" ]; then
         ${P_ALBUM} -p ${BITPIX} -b $5 9 4 \
                  ${BASE}_1$4.fits ${BASE}_2$4.fits\
                  ${BASE}_3$4.fits ${BASE}_4$4.fits ${BASE}_5$4.fits\
                  ${BASE}_6$4.fits ${BASE}_7$4.fits ${BASE}_8$4.fits ${BASE}_9$4.fits \
                  ${BASE}_10$4.fits ${BASE}_11$4.fits\
                  ${BASE}_12$4.fits ${BASE}_13$4.fits ${BASE}_14$4.fits\
                  ${BASE}_15$4.fits ${BASE}_16$4.fits ${BASE}_17$4.fits ${BASE}_18$4.fits \
                  ${BASE}_19$4.fits ${BASE}_20$4.fits\
                  ${BASE}_21$4.fits ${BASE}_22$4.fits ${BASE}_23$4.fits\
                  ${BASE}_24$4.fits ${BASE}_25$4.fits ${BASE}_26$4.fits ${BASE}_27$4.fits \
                  ${BASE}_28$4.fits ${BASE}_29$4.fits\
                  ${BASE}_30$4.fits ${BASE}_31$4.fits ${BASE}_32$4.fits\
                  ${BASE}_33$4.fits ${BASE}_34$4.fits ${BASE}_35$4.fits ${BASE}_36$4.fits >\
                  BINNED/${BASE}_mos.fits
       else
         ${P_ALBUM} -l -p ${BITPIX} -b $5 18 4 \
                  ${BASE}_1$4.fits ${BASE}_2$4.fits\
                  ${BASE}_3$4.fits ${BASE}_4$4.fits ${BASE}_5$4.fits\
                  ${BASE}_6$4.fits ${BASE}_7$4.fits ${BASE}_8$4.fits ${BASE}_9$4.fits \
                  ${BASE}_10$4.fits ${BASE}_11$4.fits\
                  ${BASE}_12$4.fits ${BASE}_13$4.fits ${BASE}_14$4.fits\
                  ${BASE}_15$4.fits ${BASE}_16$4.fits ${BASE}_17$4.fits ${BASE}_18$4.fits \
                  ${BASE}_19$4.fits ${BASE}_20$4.fits\
                  ${BASE}_21$4.fits ${BASE}_22$4.fits ${BASE}_23$4.fits\
                  ${BASE}_24$4.fits ${BASE}_25$4.fits ${BASE}_26$4.fits ${BASE}_27$4.fits \
                  ${BASE}_28$4.fits ${BASE}_29$4.fits\
                  ${BASE}_30$4.fits ${BASE}_31$4.fits ${BASE}_32$4.fits\
                  ${BASE}_33$4.fits ${BASE}_34$4.fits ${BASE}_35$4.fits ${BASE}_36$4.fits \
                  ${BASE}_37$4.fits ${BASE}_38$4.fits\
                  ${BASE}_39$4.fits ${BASE}_40$4.fits ${BASE}_41$4.fits\
                  ${BASE}_42$4.fits ${BASE}_43$4.fits ${BASE}_44$4.fits ${BASE}_45$4.fits \
                  ${BASE}_46$4.fits ${BASE}_47$4.fits\
                  ${BASE}_48$4.fits ${BASE}_49$4.fits ${BASE}_50$4.fits\
                  ${BASE}_51$4.fits ${BASE}_52$4.fits ${BASE}_53$4.fits ${BASE}_54$4.fits \
                  ${BASE}_55$4.fits ${BASE}_56$4.fits\
                  ${BASE}_57$4.fits ${BASE}_58$4.fits ${BASE}_59$4.fits\
                  ${BASE}_60$4.fits ${BASE}_61$4.fits ${BASE}_62$4.fits ${BASE}_63$4.fits \
                  ${BASE}_64$4.fits ${BASE}_65$4.fits\
                  ${BASE}_66$4.fits ${BASE}_67$4.fits ${BASE}_68$4.fits\
                  ${BASE}_69$4.fits ${BASE}_70$4.fits ${BASE}_71$4.fits ${BASE}_72$4.fits >\
                  BINNED/${BASE}_mos.fits
	   
       fi
  done
}

rm ${TEMPDIR}/image_list_$$
