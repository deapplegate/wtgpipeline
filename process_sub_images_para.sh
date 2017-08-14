#!/bin/bash -xv
. BonnLogger.sh
. log_start

###############
# $Id: process_sub_images_para.sh,v 1.6 2009-06-02 01:27:50 anja Exp $
###############

################
# Takes OC science images, applies flat field and creates object subtracted images

#$1 Run directory
#$2 FLAT Directory
#$3 SCIENCE directory
#$4 FRINGE/NOFRINGE
#$5 CHIPS



# preliminary work:
. ${INSTRUMENT:?}.ini

OCFDIR=${3}_${2}/


for CHIP in $5
do

    if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then

	MAXX=$(( ${CUTX[${CHIP}]} + ${SIZEX[${CHIP}]} - 1 ))
	MAXY=$(( ${CUTY[${CHIP}]} + ${SIZEY[${CHIP}]} - 1 ))
	
	
	FILES=`ls $1/$3/${PREFIX}*_${CHIP}OC.fits`
	if [ "$FILES" = "" ]; then
	    FILES=`ls $1/$3/OC_IMAGES/${PREFIX}*_${CHIP}OC.fits`
	fi

	if [ "$5" = "RESCALE" ]; then   
	    FLATFLAG="-FLAT_SCALE Y -FLAT_SCALEIMAGE ${FLATSTR}" 
	fi

        # build up list of all flatfields necessary for rescaling
        # when gains between chips are equalised here.
	i=1
	j=1
	FLATSTR=""
	while [ "${i}" -le "${NCHIPS}" ]
	do
	    if [ "${j}" = "1" ]; then
		FLATSTR="$1/$2/$2_${i}.fits"
		j=2
	    else
		FLATSTR="${FLATSTR},$1/$2/$2_${i}.fits"
	    fi

	    i=$(( $i + 1 ))
	done


    #flatfield science images:
	${P_IMRED_ECL:?} $FILES \
	    -MAXIMAGES ${NFRAMES} \
	    -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
	    -OVERSCAN N \
	    -BIAS N \
	    -FLAT Y \
	    -FLAT_SCALE Y \
	    -FLAT_SCALEIMAGE ${FLATSTR} \
	    -FLAT_IMAGE $1/$2/${2}_${CHIP}.fits \
	    -FLAT_THRESHHOLD 0.1 \
	    -COMBINE N \
	    -OUTPUT Y \
	    -OUTPUT_DIR $1/$OCFDIR \
	    -OUTPUT_SUFFIX F.fits \
	    -TRIM N

	if [ $? -gt 0 ]; then
	    log_status 1 "Preprocess Failed. Chip $CHIP"
	    exit 1
	fi
	

	ls -1 $1/$OCFDIR/*_${CHIP}OCF.fits > images-objects_$$
    
	cat images-objects_$$ |\
        {
	    while read file
	    do
  		BASE=`basename ${file} .fits`
  	#
  	# now run sextractor to subtract objects from the image
  	#
  		if [ "$4" = "FRINGE" ]; then
  		    ${P_SEX} ${file} -c ${DATACONF}/image-objects.sex\
  		  -CHECKIMAGE_NAME $1/$OCFDIR/${BASE}"_sub.fits"\
  	          -DETECT_MINAREA 7 -DETECT_THRESH 5 -ANALYSIS_THRESH 5
  		else
  		    ${P_SEX} ${file} -c ${DATACONF}/image-objects.sex\
			-DETECT_THRESH 0.7 -DETECT_MINAREA 5 -BACK_SIZE 1024 \
  		  -CHECKIMAGE_NAME $1/$OCFDIR/${BASE}"_sub.fits"
  		fi

  		${P_IC} '%1 -70000 %2 fabs 1.0e-06 > ?' ${file} \
		    $1/$OCFDIR/${BASE}"_sub.fits" \
  		    > $1/$OCFDIR/${BASE}"_sub1.fits"

		mv $1/$OCFDIR/${BASE}"_sub1.fits" $1/$OCFDIR/${BASE}"_sub.fits"
  
	    done
	}

	rm images-objects_$$
    fi
done



log_status $?
