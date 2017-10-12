#!/bin/bash
set -xv
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# the script processes a set of Standard star frames
# the images are overscan corrected, debiased and flatfielded.
# For further processing superflats are NOT created from the
# preprocessed standards but the corresponding files from
# the SCIENCE frames are copied. 
# The script uses the 'preprocess' program to perform the
# reduction. 
# It assumes that all images from ONE chip reside
# in the same physical directory
#

#$1: main directory (filter)
#$2: Bias directory
#$3: Flat directory
#$4: Science directory
#$5: Standard directory
#$6: RESCALE/NORESCALE
#$7: chips to be processed

# preliminary work:
. ${INSTRUMENT:?}.ini

# the resultdir is where the output coadded images
# will go. If ONE image of the corresponding chip
# is a link the image will go to THIS directory

if [ ! -d /$1/$3/OC_IMAGES ]; then
    mkdir /$1/$3/OC_IMAGES
fi

for CHIP in $7
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    SCIRESULTDIR[${CHIP}]="$1/$4/"
    STDRESULTDIR[${CHIP}]="$1/$5/"
  else
    echo "Chip ${CHIP} will not be processed in $0"  
  fi
done

# perform preprocessing (overscan correction,
# BIAS subtraction, first flatfield pass)
for CHIP in $7
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    FILES=`ls $1/$5/SUPA*_${CHIP}.fits`
  
    for FILE in ${FILES}
    do
      if [ -L ${FILE} ]; then
  	     LINK=`${P_READLINK} ${FILE}`
  	     BASE=`basename ${LINK} .fits`
  	     DIR=`dirname ${LINK}`
  	     ln -s ${DIR}/${BASE}OCF.fits $1/$5/${BASE}OCF.fits
  	     STDRESULTDIR[${CHIP}]=`dirname ${LINK}`    
      fi
    done 
  
    MAXX=$(( ${CUTX[${CHIP}]} + ${SIZEX[${CHIP}]} - 1 ))
    MAXY=$(( ${CUTY[${CHIP}]} + ${SIZEY[${CHIP}]} - 1 ))
  
    # build up list of all flatfields necessary for rescaling
    # when gains between chips are equalised here.
    i=1
    j=1
    FLATSTR=""
    while [ "${i}" -le "${NCHIPS}" ]
    do
      if [ ${NOTUSE[${i}]:=0} -eq 0 ] && [ ${NOTPROCESS[${i}]:=0} -eq 0 ]; then
        if [ "${j}" = "1" ]; then
          FLATSTR="/$1/$3/$3_${i}.fits"
	  j=2
        else
          FLATSTR="${FLATSTR},/$1/$3/$3_${i}.fits"
        fi
      fi    
      i=$(( $i + 1 ))
    done
  
    FLATFLAG=""
    if [ "$6" = "RESCALE" ]; then   
      FLATFLAG="-FLAT_SCALE Y -FLAT_SCALEIMAGE ${FLATSTR}" 
    fi
  
    # overscan correct, bias subtract and flatfield
    # science images:
    FILES=`ls /$1/$5/SUPA*_${CHIP}OC.fits`
    ${P_IMRED_ECL:?} ${FILES} \
      -MAXIMAGES ${NFRAMES}\
      -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
      -OVERSCAN N \
      -BIAS N \
      -FLAT Y \
      -FLAT_IMAGE /$1/$3/$3_${CHIP}.fits \
      -FLAT_THRESHHOLD .1 \
      -COMBINE N \
      -OUTPUT Y \
      -OUTPUT_DIR /$1/$5/ \
      -OUTPUT_SUFFIX F.fits \
      -TRIM N  ${FLATFLAG}
      
  
  fi

  if [ ! -d /$1/$5/OC_IMAGES ]; then
      mkdir /$1/$5/OC_IMAGES
  fi
  mv /$1/$5/*_${CHIP}OC.fits /$1/$5/OC_IMAGES

done

for CHIP in $7
do
    cp /${SCIRESULTDIR[${CHIP}]}/$4_${CHIP}.fits \
       /${STDRESULTDIR[${CHIP}]}/$5_${CHIP}.fits

    # create link if necessary
    if [ ! -f $1/$5/$5_${CHIP}.fits ]; then
      ln -s /${STDRESULTDIR[${CHIP}]}/$5_${CHIP}.fits $1/$5/$5_${CHIP}.fits
    fi
done
#adam-BL# log_status $?
