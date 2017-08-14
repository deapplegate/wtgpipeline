#!/bin/bash -xv
. BonnLogger.sh
. log_start
# the script changes the BITPIX from input images
# It is used to convert FLOAT data that effectively
# only contain INTEGER or BYTE values to images
# with lower disk space needs.

# $1: main directory
# $2: science directory
# $3: prefix
# $4: extension (including a . before the fits extension)
# $5: new BITPIX value
# $6: chips to be processed

. ${INSTRUMENT:?}.ini

# the chips that are to be processed
for CHIP in ${!#}
do
    ls -1 /$1/$2/${3}*_${CHIP}${4}fits > ${TEMPDIR}/bitpix_change_${CHIP}_$$
  
    cat ${TEMPDIR}/bitpix_change_${CHIP}_$$ |\
    {
        while read file
        do
            if [ -L ${file} ]; then
                LINK=`${P_READLINK} ${file}`
                RESULTDIR[${CHIP}]=`dirname ${LINK}`
            else
	        RESULTDIR[${CHIP}]="/$1/$2"
            fi

            BASE=`basename ${file} ${4}fits`

            ${P_IOFITS} ${RESULTDIR[${CHIP}]}/${BASE}"${4}fits" \
                        ${RESULTDIR[${CHIP}]}/${BASE}"tmp.fits_$$" $5
            mv ${RESULTDIR[${CHIP}]}/${BASE}"tmp.fits_$$" \
               ${RESULTDIR[${CHIP}]}/${BASE}"${4}fits"
        done    
    }
    rm ${TEMPDIR}/bitpix_change_${CHIP}_$$
done


log_status $?
