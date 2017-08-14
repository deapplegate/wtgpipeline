#!/bin/bash -xv
. BonnLogger.sh
. log_start
. ${INSTRUMENT:?}.ini

# 25.11.03:
# script creation:
# this is the parallel version of create_calibheader.sh
# it is based on modifications of add_image_calibs allowing
# to give the chip number that is to be updated

# $1: main dir.
# $2: science dir. (the cat dir is a subdirectory of this)
# $3: image extension (ext)
# $4: extension (added by add_image_calibs)
# $5: polynom type (LDAC or SWARP)

DIRCUR=`pwd`

for CHIP in $6
do
   FILES=`ls $1/$2/*_${CHIP}$3.fits`
 
   for FILE in ${FILES}
   do
     if [ -L ${FILE} ]; then
 	LINK=`${P_READLINK} ${FILE}`
 	BASE=`basename ${LINK} .fits`
 	DIR=`dirname ${LINK}`
 	ln -s ${DIR}/${BASE}$4.fits $1/$2/${BASE}$4.fits
 	RESULTDIR[${CHIP}]=`dirname ${LINK}`    
     else
 	RESULTDIR[${CHIP}]=/$1/$2    
     fi
   done 

done

for CHIP in $6
do
  cd ${RESULTDIR[${CHIP}]}

  if [ "$5" != "SWARP" ]; then
    ${P_ADDIMAGECALIBS} -i /$1/$2/cat/chips.cat4 -o ".fits" -e "$4.fits" \
                        -c ${DATACONF}/calibheader.conf.add_image_calibs \
                        -USE_IMAGEID YES -IMAGEIDVALUE ${CHIP}
  else
    ${P_ADDIMAGECALIBS} -i /$1/$2/cat/chips.cat4 -o ".fits" -e "$4.fits" \
                        -c ${DATACONF}/calibheader.conf.add_image_calibs\
                        -MODE WCSSTANDARD -USE_IMAGEID YES -IMAGEIDVALUE ${CHIP}
fi
done

cd ${DIRCUR}

log_status $?
