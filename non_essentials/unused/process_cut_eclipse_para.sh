#!/bin/bash -xv

# the script trims a set of frames.
# It is for instance useful to substitutes the 
# SCIENCE processing in the case of Elixir
# preprocessed images (at CFHT) where only
# useless border regions need to be trimmed.

# 07.03.2007:
# - I included the possibility to give the BITPIX
#   of the trimmed output images on the command line
# - 'ls' commands are replaced by more robust 'find' 
#   constructs.

#$1: main directory (filter)
#$2: Science directory
#$3: BITPIX of output images (OPTIONAL; default is -32)
#${!#}: chips to be processed

# preliminary work:
. ${INSTRUMENT:?}.ini

# set BITPIX to use for output images:
BITPIX=-32

if [ $# -eq 4 ]; then
    BITPIX=$3
fi

# the resultdir is where the output coadded images
# will go. If ONE image of the corresponding chip
# is a link the image will go to THIS directory
for CHIP in ${!#}
do
    RESULTDIR[${CHIP}]="$1/$2"
done

# perform cutting
for CHIP in ${!#}
do
    FILES=`${P_FIND} /$1/$2/ -maxdepth 1 -name \*_${CHIP}.fits`

    for FILE in ${FILES}
    do
        if [ -L ${FILE} ]; then
            LINK=`${P_READLINK} ${FILE}`
            BASE=`basename ${LINK} .fits`
            DIR=`dirname ${LINK}`
            ln -s ${DIR}/${BASE}C.fits $1/$4/${BASE}C.fits
            RESULTDIR[${CHIP}]=`dirname ${LINK}`    
        fi
    done 

    MAXX=$(( ${CUTX[${CHIP}]} + ${SIZEX[${CHIP}]} - 1 ))
    MAXY=$(( ${CUTY[${CHIP}]} + ${SIZEY[${CHIP}]} - 1 ))

    # trim images:
    ${P_IMRED_ECL:?} `${P_FIND} /$1/$2/ -maxdepth 1 -name \*_${CHIP}.fits` \
        -MAXIMAGES ${NFRAMES}\
        -OVERSCAN N \
        -BIAS N \
        -FLAT N \
        -COMBINE N \
        -OUTPUT Y \
        -OUTPUT_BITPIX ${BITPIX} \
        -OUTPUT_DIR /$1/$2/ \
        -OUTPUT_SUFFIX C.fits \
        -TRIM Y \
        -TRIM_REGION ${CUTX[${CHIP}]},${MAXX},${CUTY[${CHIP}]},${MAXY}

  if [ ! -d /$1/$2/SPLIT_IMAGES ]; then
      mkdir /$1/$2/SPLIT_IMAGES
  fi
  ${P_FIND} /$1/$2/ -maxdepth 1 -name \*_${CHIP}.fits \
            -exec mv {} /$1/$2/SPLIT_IMAGES \;
done

