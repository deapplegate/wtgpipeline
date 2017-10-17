#!/bin/bash
set -xv
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# the script processes a set of Science frames
# the images are overscan corrected, debiased, flatfielded 
# and stacked with
# mode rescaling (Superflat). We assume that we do NOT work
# with a normalised flat
# The script uses the 'preprocess' program to perform the
# reduction. 
# It assumes that all images from ONE chip reside
# in the same physical directory
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 24.08.04:
# - in bands containing strong fringes (I and Z), we have
#   to use special detection/pixel threshholds in the
#   creation of sky subtracted images (In introduced a new
#   argument to indicate this feature)
# - new RESCALE flag; it was introduced so that the user can decide
#   whether the gain equalisation is done here with skyflats
#   or in the process_science_illum step with superflats. 
#
# 25.11.04:
# We introduced the possibility to exclude certain chips in
# the creation of a superflat. To this end a list with the
# chips to be excluded has to reside in $1/superflat_exclusion.
# Each line of this file has to contain a filename with
# blabla_CHIP, where CHIP represents the chipnumber to be
# excluded.
#
# 28.11.2004:
# corrected a bug in the case where the gain equalisation
# is performed here. There was no FLAT_SCALEIMAGE specified.
#
# 14.02.2005:
# the 'stats' program is now called via the P_STATS variable
# to avoid that it is not executed if it is not in the users
# path.
#
# 25.02.2005:
# I removed a '-COMBINE_MINVAL "-69999"' statement so that
# the default minimum value of -10000 is used. -69999 seems
# to lead to wrong problems if we have -70000 in some images.
#
# 26.02.2005:
# I substituted the call to the Python script filter.py by
# a gawk call. This enables the use of this script on machines
# where Python is not available.
#
# 02.05.2005:
# I rewrote the script to use the MAXIMAGE parameter in preprocess
# and the imcat-based imcombflat for the coaddition of the superflat.
#
# 14.08.2005:
# The preprocess calls now explicitely declare the statistics
# region on the command line.
#
# 05.12.2005:
# - Chips whose NOTPROCESS flag is set are not processed at all.
# - Chips whose NOTUSE flag is set are not used in the set of
#   Flatscale images.
# - The superflat combination now uses the clipped mean algorithm
#   from imcombflat.
# - I corrected a bug in the indexing of NOTPROCESS flags.
#
# 22.12.2005:
# - I changed back the final co-addition to median stacking
#   (with initial rejection of the highest value at each pixel 
#   position).
#   The clipped mean turned out to be too affected by outliers.
# - background statistics for the superflat are now estimated 
#   from the whole frame and not only from a subsection in the 
#   middle of a chip.
#   Bright features in the middle of the chip tended to bias
#   the final result.
#
# 10.02.2006:
# - I corrected a major bug in the selection of images entering the
#   superflats. In cameras with more than 9 chips too many images
#   were rejected.
# - I made the reading of the superflat_exclusion file more robust
#   against empty lines

#$1: main directory (filter)
#$2: Bias directory
#$3: Flat directory
#$4: Science directory
#$5: RESCALE/NORESCALE
#$6: FRINGE/NOFRINGE
#$7: chips to be processed

# preliminary work:
. ${INSTRUMENT:?}.ini > /tmp/instrum.out 2>&1

# the resultdir is where the output coadded images
# will go. If ONE image of the corresponding chip
# is a link the image will go to THIS directory
for CHIP in $7
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    RESULTDIR[${CHIP}]="$1/$4"
  else
    echo "Chip ${CHIP} will not be processed in $0"  
  fi
done

# perform preprocessing (overscan correction,
# BIAS subtraction, first flatfield pass)
for CHIP in $7
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then

    #adam-added# I added this so that I don't keep getting this trying to process SCIENCE_#.fits
    \ls -1 $1/$4/*_${CHIP}.fits > files_${CHIP}_$$
    FILES=`grep -v "SCIENCE_${CHIP}.fits" files_${CHIP}_$$`
    rm -f files_${CHIP}_$$
    if [ -z "${FILES}" ]; then
	    continue
    fi

    for FILE in ${FILES}
    do
      if [ -L ${FILE} ]; then
  	     LINK=`${P_READLINK} ${FILE}`
  	     BASE=`basename ${LINK} .fits`
  	     DIR=`dirname ${LINK}`
  	     ln -s ${DIR}/${BASE}OFC.fits $1/$4/${BASE}OFC.fits
  	     RESULTDIR[${CHIP}]=`dirname ${LINK}`    
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
    if [ "$5" = "RESCALE" ]; then   
      FLATFLAG="-FLAT_SCALE Y -FLAT_SCALEIMAGE ${FLATSTR}" 
    fi
  
    # overscan correct, bias subtract and flatfield
    # science images:

    CHANNEL=1
    while [ "${CHANNEL}" -le "${NCHANNELS}" ]
    do

      NCHIP=$(( ${NCHIPS}*( ${CHANNEL} -1 ) + ${CHIP}))

      MAXX=$(( ${CUTX[${NCHIP}]} + ${SIZEX[${NCHIP}]} - 1 ))
      MAXY=$(( ${CUTY[${CHIP}]} + ${SIZEY[${CHIP}]} - 1 ))
  
      # overscan correct and trim frames
      ${P_IMRED_ECL:?} ${FILES} \
	  -MAXIMAGES ${NFRAMES}\
	  -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
	  -OVERSCAN Y \
	  -OVERSCAN_REGION ${OVSCANX1[${NCHIP}]},${OVSCANX2[${NCHIP}]} \
	  -OUTPUT Y \
	  -OUTPUT_DIR /$1/$4/ \
	  -TRIM Y \
	  -OUTPUT_SUFFIX OC_CH${CHANNEL}.fits \
	  -TRIM_REGION ${CUTX[${NCHIP}]},${MAXX},${CUTY[${CHIP}]},${MAXY}
  
    CHANNEL=$(( ${CHANNEL} + 1 ))
    done

    #---> paste four fits files
    for file in ${FILES}
    do
	basename=`basename $file .fits`
	./horizontal_paste.py -o ${1}/${4}/${basename}OC_CHall.fits `\ls ${1}/${4}/${basename}OC_CH?.fits`
    done

    # bias subtraction and flat-fielding
    ${P_IMRED_ECL:?} `\ls /$1/$4/*_${CHIP}OC_CHall.fits` \
        -MAXIMAGES ${NFRAMES} \
        -STATSSEC ${STATSXMIN},${STATSXMAX},${STATSYMIN},${STATSYMAX} \
        -BIAS Y \
        -BIAS_IMAGE /$1/$2/$2_${CHIP}.fits \
	-FLAT Y \
	-FLAT_IMAGE /$1/$3/$3_${CHIP}.fits \
	-COMBINE N \
	-OUTPUT Y \
	-OUTPUT_DIR /$1/$4/ \
	-OUTPUT_SUFFIX OCF.fits \
	${FLATFLAG}

    #adam# rename clobber/overwrite
    mkdir /$1/$4/tmp_OCF/
    mv /$1/$4/*_${CHIP}OCF.fits /$1/$4/tmp_OCF/
    ${P_RENAME} 's/OC_CHallOCF/OCF/g' /$1/$4/*_${CHIP}OC_CHallOCF.fits
    mv -n /$1/$4/tmp_OCF/*_${CHIP}OCF.fits /$1/$4/

    #rm -rf /$1/$4/tmp_OCF/
    rm -f /$1/$4/*_${CHIP}OC_CH?.fits /$1/$4/*_${CHIP}OC_CHall.fits
  
  fi

  if [ ! -d /$1/$4/SPLIT_IMAGES ]; then
      mkdir /$1/$4/SPLIT_IMAGES
  fi
  mv /$1/$4/*_${CHIP}.fits /$1/$4/SPLIT_IMAGES

done

# we create object-subtracted images to avoid dark regions
# around bright objects in later images

for CHIP in $7
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    \ls -1 /${RESULTDIR[${CHIP}]}/*_${CHIP}OCF.fits > ${TEMPDIR}/images-objects_$$
    
    cat ${TEMPDIR}/images-objects_$$ |\
    {
      while read file
      do
  	BASE=`basename ${file} .fits`
  	#
  	# now run sextractor to subtract objects from the image
  	#
  	# if the SCIENCE images contain fringes ($6=FRINGE) we
  	# have to use special detection/pixel threshholds
  	# to keep the fringes.
  	if [ "$6" = "FRINGE" ]; then
  	  ${P_SEX} ${file} -c ${DATACONF}/image-objects.sex\
  		  -CHECKIMAGE_NAME ${RESULTDIR[${CHIP}]}/${BASE}"_sub.fits"\
  	          -DETECT_MINAREA 7 -DETECT_THRESH 5 -ANALYSIS_THRESH 5
  	else
  	  ${P_SEX} ${file} -c ${DATACONF}/image-objects.sex\
  		  -CHECKIMAGE_NAME ${RESULTDIR[${CHIP}]}/${BASE}"_sub.fits"
  	fi
  	${P_IC} '%1 -70000 %2 fabs 1.0e-06 > ?' ${file} ${RESULTDIR[${CHIP}]}/${BASE}"_sub.fits"\
  		> ${RESULTDIR[${CHIP}]}/${BASE}"_sub1.fits"
  	mv ${RESULTDIR[${CHIP}]}/${BASE}"_sub1.fits" ${RESULTDIR[${CHIP}]}/${BASE}"_sub.fits"
  
  	if [ "${RESULTDIR[${CHIP}]}" != "$1/$4" ]; then
  	  ln -s ${RESULTDIR[${CHIP}]}/${BASE}"_sub.fits" $1/$4/${BASE}"_sub.fits"
  	fi
      done
    }
  fi
done

for CHIP in $7
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    if [ "${RESULTDIR[${CHIP}]}" != "$1/$4" ]; then
       ln -s ${RESULTDIR[${CHIP}]}/$4_${CHIP}.fits $1/$4/$4_${CHIP}.fits
    fi
  
    # do statistics from all science frames.
    # This is necessary to get the mode
    # of the combination from all images, so that
    # the combination where images have been excluded
    # can be scaled accordingly.
    ${P_IMSTATS} `\ls /$1/$4/*_${CHIP}OCF_sub.fits` \
                 -o science_images_$$
  
    RESULTMODE=`${P_GAWK} 'BEGIN {mean=0.0; n=0} ($1!="#") {
                           n=n+1; mean=mean+$2} END {print mean/n}' science_images_$$`
  
    # modify the input list of images
    # in case we have to reject files for the superflat:
    if [ -s /$1/superflat_exclusion ]; then
      ./adam_superflat_exclusion_fixer.py /$1/superflat_exclusion
      ${P_GAWK} 'BEGIN {nex = 0; while (getline <"/'$1'/superflat_exclusion" > 0) {
                 gsub(" ", "", $1); if (length($1) >0) {ex[nex]=$1; nex++; }}}
                 {exclude = 0; i=0;
                  while (i<nex) {
                    if ((ind=index($1, ex[i]))!=0) {
                      tmp=$1;
                      gsub(ex[i],"",tmp);
                      first=substr(tmp,ind,1);
                      if (first !~ /[0-9]/) {
                        exclude = 1;
                      }
                    }
  	          i++;
                  }
                  if(exclude == 0) {print $0}}' science_images_$$ > science_coadd_images_$$
    else
      cp science_images_$$ science_coadd_images_$$
    fi
  
    # do the combination
  
    #make SCIENCE_#.fits
    ${P_IMCOMBFLAT_IMCAT} -i science_coadd_images_$$\
                    -o ${RESULTDIR[${CHIP}]}/$4_${CHIP}.fits \
                    -s 1 -e 0 1 -m ${RESULTMODE}
  
    if [ ! -d /$1/$4/SUB_IMAGES ]; then
       mkdir /$1/$4/SUB_IMAGES
    fi
    mv /$1/$4/*_${CHIP}OCF_sub.fits /$1/$4/SUB_IMAGES/

  fi
done


#adam-BL# log_status $?

rm -f science_images_$$ science_coadd_images_$$ images-objects_$$
