#!/bin/bash -xv

# 28.08.: I included the new cut possibility in the
#         imred part
#         The flat fielding is now done by a normaliced flat for
#         every chip
#
# 14.08.02:
#         the gain of the science frames is now brought
#         to a common level in this script with the skyflats.
#
# 03.09.2003:
# adapted script for new estimation of overscan:
#   - Instead of estimating the overscan of each line with the
#     median of the pixels in the overscan region, I now consider
#     the mean. From its calculation the 'minreject' lowest and
#     'maxreject' highest values are excluded.
#   - The smoothing of overscan over several lines is no longer done.
#
# 08.09.2003:
# changed /${RESULTDIR[${CHIP}]}/ to /$1/$4/ in one of the file
# listings. In this way only the images that are currently worked
# on are affected and not others that may still reside in scratch
# directories.
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 01.07.2004:
# - in bands containing strong fringes (I and Z), we have
#   to use special detection/pixel threshholds in the
#   creation of sky subtracted images (In introduced a new
#   argument to indicate this feature)
# - new RESCALE flag; it was introduced so that the user can decide
#   whether the gain equalisation is done here with skyflats
#   or in the process_science_illum step with superflats. 


# the script processes a set of Science frames
# the images are overscan corrected, debiased, flatfielded 
# and stacked with
# mode rescaling (Superflat). We assume that we do NOT work
# with a normaliced flat

#$1: main directory (filter)
#$2: Bias directory
#$3: Flat directory
#$4: Science directory
#$5: RESCALE/NORESCALE
#$6: FRINGE/NOFRINGE
#$7: chips to be processed

# preliminary work:
. ${INSTRUMENT:?}.ini

# the resultdir is where the output coadded images
# will go. If ONE image of the corresponding chip
# is a link the image will go to THIS directory
for CHIP in $7
do
  RESULTDIR[${CHIP}]="$1/$4"
done

#rm @in-imred

# Correction overscan, Bias and flat; create config file on the fly
# we do not assume that the overscan is the same for all chips

# first find out the modes of the flat images as factor
# for flat fielding

# create input file and config file on the fly for mode determination:

# We MUST use all ccds here since the chips should be brought to the 
# same gain!


k=1
while [ "${k}" -le "${NCHIPS}" ]
do
  ALLCHIPS="${ALLCHIPS} ${k}"
  k=$(( $k + 1 ))
done

${S_LISTEXT_PARA} $1/$3/$3 .fits immode $$ "${ALLCHIPS}"

echo "INPUT"                       >  ${TEMPDIR}/immode.param_$$
echo "     name   ${TEMPDIR}/@in-immode_$$"   >> ${TEMPDIR}/immode.param_$$
echo "     dyn_min  -66000.0 "     >> ${TEMPDIR}/immode.param_$$
echo "     dyn_max  66000.0 "      >> ${TEMPDIR}/immode.param_$$
echo "end"                         >> ${TEMPDIR}/immode.param_$$
echo "RASTER"                      >> ${TEMPDIR}/immode.param_$$
echo "     xc    ${STATSALLIM[1]}" >> ${TEMPDIR}/immode.param_$$
echo "     yc    ${STATSALLIM[2]}" >> ${TEMPDIR}/immode.param_$$
echo "     sizex ${STATSALLIM[3]}" >> ${TEMPDIR}/immode.param_$$
echo "     sizey ${STATSALLIM[4]}" >> ${TEMPDIR}/immode.param_$$
echo "end"                         >> ${TEMPDIR}/immode.param_$$
echo "STAT"                        >> ${TEMPDIR}/immode.param_$$
echo "percent 40"                  >> ${TEMPDIR}/immode.param_$$
echo "end"                         >> ${TEMPDIR}/immode.param_$$
echo "END"                         >> ${TEMPDIR}/immode.param_$$

if [ -f ${TEMPDIR}/immode.dat_$$ ]; then
  rm ${TEMPDIR}/immode.dat_$$
fi
if [ -f ${TEMPDIR}/immode-stat.dat_$$ ]; then
  rm ${TEMPDIR}/immode-stat.dat_$$
fi

${P_IMMODE} ${TEMPDIR}/immode.param_$$ ${TEMPDIR}/immode.dat_$$ ${TEMPDIR}/immode-stat.dat_$$

# get the factors to normalise flats
FACT=`${P_GAWK} '($1!="->" && $1!="") {printf ("%f ", $2)}' ${TEMPDIR}/immode.dat_$$`
MAXFACT=`${P_GAWK} 'BEGIN {max=0} ($1!="->" && $1!="") {if($2>max) max=$2} END {print max}' ${TEMPDIR}/immode.dat_$$`

for CHIP in $7
do
  ACTUFACT=`echo ${FACT} | ${P_GAWK} '{print $'${CHIP}'}'`
  if [ "$5" = "RESCALE" ]; then
    ACTUFACT=${MAXFACT}
  fi
  echo "INPUT"                        >  ${TEMPDIR}/imred.param_$$
  echo "     name   ${TEMPDIR}/@in-imred_$$"     >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "OUTPUT"                       >> ${TEMPDIR}/imred.param_$$
  echo "     name   ${TEMPDIR}/@out-imred_$$"    >> ${TEMPDIR}/imred.param_$$
  echo "     outbitpix -32"           >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "OVERSCAN"                     >> ${TEMPDIR}/imred.param_$$
  echo "     doover 1"                >> ${TEMPDIR}/imred.param_$$
  echo "     modline  1"              >> ${TEMPDIR}/imred.param_$$
  echo "     ovscan ${OVSCANX1[${CHIP}]} ${OVSCANX2[${CHIP}]}" >> ${TEMPDIR}/imred.param_$$
  echo "     reject 5 5"              >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "DARK"                         >> ${TEMPDIR}/imred.param_$$
  echo "     file 1"                  >> ${TEMPDIR}/imred.param_$$
  echo "     dodark 1"                >> ${TEMPDIR}/imred.param_$$
  echo "     fact 1.0"                >> ${TEMPDIR}/imred.param_$$
  echo "     name ${TEMPDIR}/@dark-imred_$$"     >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "FLAT"                         >> ${TEMPDIR}/imred.param_$$
  echo "     doflat 1"                >> ${TEMPDIR}/imred.param_$$
  echo "     fact ${ACTUFACT}"        >> ${TEMPDIR}/imred.param_$$
  echo "     subst 50.0"              >> ${TEMPDIR}/imred.param_$$
  echo "     name ${TEMPDIR}/@flat-imred_$$"     >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "MASK"                         >> ${TEMPDIR}/imred.param_$$
  echo "     domask 0"                >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "FRINGE"                       >> ${TEMPDIR}/imred.param_$$
  echo "     dofringe 0"              >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "RASTER"                       >> ${TEMPDIR}/imred.param_$$
  echo "     cut 1"                   >> ${TEMPDIR}/imred.param_$$ 
  echo "     x ${CUTX[${CHIP}]}"      >> ${TEMPDIR}/imred.param_$$
  echo "     y ${CUTY[${CHIP}]}"      >> ${TEMPDIR}/imred.param_$$
  echo "     sizex ${SIZEX[${CHIP}]}" >> ${TEMPDIR}/imred.param_$$
  echo "     sizey ${SIZEY[${CHIP}]}" >> ${TEMPDIR}/imred.param_$$
  echo "end"                          >> ${TEMPDIR}/imred.param_$$
  echo "END"                          >> ${TEMPDIR}/imred.param_$$
  

  if [ -f ${TEMPDIR}/@in-imred_$$ ]; then
    rm ${TEMPDIR}/@in-imred_$$
  fi
  if [ -f ${TEMPDIR}/@out-imred_$$ ]; then
    rm ${TEMPDIR}/@out-imred_$$
  fi
  if [ -f ${TEMPDIR}/@dark-imred_$$ ]; then
    rm ${TEMPDIR}/@dark-imred_$$
  fi
  if [ -f ${TEMPDIR}/@flat-imred_$$ ]; then
    rm ${TEMPDIR}/@flat-imred_$$
  fi

  ls $1/$2/$2_${CHIP}.fits > ${TEMPDIR}/@dark-imred_$$
  ls $1/$3/$3_${CHIP}.fits > ${TEMPDIR}/@flat-imred_$$

  FILES=`ls $1/$4/*_${CHIP}.fits`

  for FILE in ${FILES}
  do
    if [ -L ${FILE} ]; then
	     LINK=`${P_READLINK} ${FILE}`
	     echo ${LINK} >> ${TEMPDIR}/@in-imred_$$ 
	     BASE=`basename ${LINK} .fits`
	     DIR=`dirname ${LINK}`
	     ln -s ${DIR}/${BASE}OFC.fits $1/$4/${BASE}OFC.fits
	     RESULTDIR[${CHIP}]=`dirname ${LINK}`    
    else
	     echo "${FILE}" >> ${TEMPDIR}/@in-imred_$$
    fi
  done 
  
  ${S_LIO} ${TEMPDIR}/@in-imred_$$ ${TEMPDIR}/@out-imred_$$ .fits OFC
  ${P_IMRED} ${TEMPDIR}/imred.param_$$

  if [ ! -d /$1/$4/SPLIT_IMAGES ]; then
	    mkdir /$1/$4/SPLIT_IMAGES
  fi
  mv /$1/$4/*_${CHIP}.fits /$1/$4/SPLIT_IMAGES

done


# We do a mode rescaling when combining superflat images,
# so we run the mode on the overscan and bias subtracted
# images

# we create object-subtracted images to avoid dark regions
# around bright objects in later images

for CHIP in $7
do
  ls -1 /$1/$4/*_${CHIP}OFC.fits > ${TEMPDIR}/images-objects_$$
  
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
done

# create input file and config file on the fly:

if [ -f ${TEMPDIR}/@in-immode_$$ ]; then
  rm ${TEMPDIR}/@in-immode_$$
fi
if [ -f @${TEMPDIR}/immode.param_$$ ]; then
  rm @${TEMPDIR}/immode.param_$$
fi

${S_LISTEXT_PARA} $1/$4/ OFC_sub.fits immode $$ "$7"

echo "INPUT"                       >  ${TEMPDIR}/immode.param_$$
echo "     name   ${TEMPDIR}/@in-immode_$$"   >> ${TEMPDIR}/immode.param_$$
echo "     dyn_min  -66000.0     " >> ${TEMPDIR}/immode.param_$$
echo "     dyn_max  66000.0 "      >> ${TEMPDIR}/immode.param_$$
echo "end"                         >> ${TEMPDIR}/immode.param_$$
echo "RASTER"                      >> ${TEMPDIR}/immode.param_$$
echo "     xc    ${STATSALLIM[1]}" >> ${TEMPDIR}/immode.param_$$
echo "     yc    ${STATSALLIM[2]}" >> ${TEMPDIR}/immode.param_$$
echo "     sizex ${STATSALLIM[3]}" >> ${TEMPDIR}/immode.param_$$
echo "     sizey ${STATSALLIM[4]}" >> ${TEMPDIR}/immode.param_$$
echo "end"                         >> ${TEMPDIR}/immode.param_$$
echo "STAT"                        >> ${TEMPDIR}/immode.param_$$
echo "percent 40"                  >> ${TEMPDIR}/immode.param_$$
echo "end"                         >> ${TEMPDIR}/immode.param_$$
echo "END"                         >> ${TEMPDIR}/immode.param_$$

${P_IMMODE} ${TEMPDIR}/immode.param_$$ ${TEMPDIR}/immode.dat_$$ ${TEMPDIR}/immode-stat.dat_$$


if [ -f ${TEMPDIR}/@out-imcombine_$$ ]; then
  rm ${TEMPDIR}/@out-imcombine_$$
fi
if [ -f ${TEMPDIR}/imcombflat.param_$$ ]; then
  rm ${TEMPDIR}/imcombflat.param_$$
fi
if [ -f @@in-imcombine.${INSTRUMENT}_$$ ]; then
  rm @@in-imcombine.${INSTRUMENT}_$$
fi

touch ${TEMPDIR}/@@in-imcombine.${INSTRUMENT}_$$
for CHIP in $7
do
  echo "${TEMPDIR}/@in-imcombine.${CHIP}_$$" >> ${TEMPDIR}/@@in-imcombine.${INSTRUMENT}_$$
done

# Combine flat frames; create config file on the fly
echo "INPUT"                                       >  ${TEMPDIR}/imcombflat.param_$$
echo "     name   ${TEMPDIR}/@@in-imcombine.${INSTRUMENT}_$$" >> ${TEMPDIR}/imcombflat.param_$$
echo "end"                                         >> ${TEMPDIR}/imcombflat.param_$$
echo "OUTPUT"                                      >> ${TEMPDIR}/imcombflat.param_$$
echo "     name   ${TEMPDIR}/@out-imcombine_$$"               >> ${TEMPDIR}/imcombflat.param_$$
echo "     outbitpix -32"                          >> ${TEMPDIR}/imcombflat.param_$$
echo "     rescale 2"                              >> ${TEMPDIR}/imcombflat.param_$$
echo "end"                                         >> ${TEMPDIR}/imcombflat.param_$$
echo "CLIPPING"                                    >> ${TEMPDIR}/imcombflat.param_$$
echo "     median 1"                               >> ${TEMPDIR}/imcombflat.param_$$
echo "     lsigmas 3.5"                            >> ${TEMPDIR}/imcombflat.param_$$
echo "     hsigmas 2.5"                            >> ${TEMPDIR}/imcombflat.param_$$
echo "     lcut -66000"                            >> ${TEMPDIR}/imcombflat.param_$$
echo "     hcut 66000"                             >> ${TEMPDIR}/imcombflat.param_$$
echo "     hrej 3"                                 >> ${TEMPDIR}/imcombflat.param_$$
echo "     sigmare 4.0"                            >> ${TEMPDIR}/imcombflat.param_$$
echo "end"                                         >> ${TEMPDIR}/imcombflat.param_$$
echo "CCDCLIPPING"                                 >> ${TEMPDIR}/imcombflat.param_$$
echo "     ccdclip 0"                              >> ${TEMPDIR}/imcombflat.param_$$
echo "end"                                         >> ${TEMPDIR}/imcombflat.param_$$
echo "BUFFER"                                      >> ${TEMPDIR}/imcombflat.param_$$
echo "     height 1"                               >> ${TEMPDIR}/imcombflat.param_$$
echo "end"                                         >> ${TEMPDIR}/imcombflat.param_$$
echo "VERBOSE"                                     >> ${TEMPDIR}/imcombflat.param_$$
echo "     verbose 0"                              >> ${TEMPDIR}/imcombflat.param_$$
echo "end"                                         >> ${TEMPDIR}/imcombflat.param_$$
echo "END"                                         >> ${TEMPDIR}/imcombflat.param_$$

${S_LISTMODE_SIGMA_PARA} ${TEMPDIR}/immode.dat_$$ OFC_sub imcombine $$ "$7"

touch ${TEMPDIR}/@out-imcombine_$$

for CHIP in $7
do
  echo "/${RESULTDIR[${CHIP}]}/$4_${CHIP}.fits" >>  ${TEMPDIR}/@out-imcombine_$$

  if [ "${RESULTDIR[${CHIP}]}" != "$1/$4" ]; then
     ln -s ${RESULTDIR[${CHIP}]}/$4_${CHIP}.fits $1/$4/$4_${CHIP}.fits
  fi
done

${P_IMCOMBFLAT} ${TEMPDIR}/imcombflat.param_$$

for CHIP in $7
do
  if [ ! -d /$1/$4/SUB_IMAGES ]; then
     mkdir /$1/$4/SUB_IMAGES
  fi
  mv /$1/$4/*_${CHIP}OFC_sub.fits /$1/$4/SUB_IMAGES/
done


