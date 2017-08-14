#!/usr/local/bin/bash -xv

# script to determine the seeing of an image 
# (in a specified region around the image centre)

# 24.07.2008:
# The seeing is now determined with the preanisotropy program;
# only objects with MAG_AUTO between 18 and 22 and a magnitude error
# less than 0.01 are considered (note that images need to have correct
# values for GAIN and MAGZP for this to work; values are optimised
# for CFHTLS Wide data). It turned out that this gives much
# more stable estimates than simply estimating the mode in a size 
# distribution.
#
# 28.11.2008:
# temporary files are deleted at the end of the script

#$1: path to image
#$2: image name
#$3: weight image name
#$4: flag image name
#$5: subimage dimensions (around the image center)
#    where seeing is to be determined
#    (argument has to be given withim double quotes)
#$6: directory for subimages (optional)
#$7: name of science subimage
#$8: name of weight subimage
#$9: name of flag subimage

. progs.ini

PIXSCALE=`dfits $1/$2 | fitsort -d CDELT1 | awk '{print -3600*$2}'`

# first create subimages:

SIZEX=`echo $5 | ${P_GAWK} '{print $1}'`
SIZEY=`echo $5 | ${P_GAWK} '{print $2}'`

MAKE_SUBIMAGES=1
if [ $# -gt 5 ] && [ -e $6/$7 ] && [ -s $6/$7 ] && [ $6/$7 -nt $1/$2 ]; then
    
    IMAGEX=`${P_DFITS} $6/$7 | ${P_FITSORT} -d NAXIS1 | awk '{print $2}'`
    IMAGEY=`${P_DFITS} $6/$7 | ${P_FITSORT} -d NAXIS2 | awk '{print $2}'`
    
    if [ $IMAGEX -eq $SIZEX ] && [ $IMAGEY -eq $SIZEY ]; then
	FWHM=`dfits $6/$7 | fitsort -d SEEING | awk '{print $2}'`
	if [ "${FWHM}" = "ERROR" ]; then
	    echo "Recreating Images"
	elif [ "${FWHM}" != "KEY_N/A" ] && [ "${FWHM}" != "KEY_EMPTY" ]; then
	    echo "The seeing is: ${FWHM}"	    
	    exit 0
	else
	    ln -s $6/$7 ${TEMPDIR}/science_seeing_$$.fits
	    ln -s $6/$8 ${TEMPDIR}/science_seeing_$$.weight.fits
	    ln -s $6/$9 ${TEMPDIR}/science_seeing_$$.flag.fits
	    MAKE_SUBIMAGES=0
	fi
    fi
fi
if [ ${MAKE_SUBIMAGES} -eq 1 ]; then
	
    IMAGEX=`${P_DFITS} $1/$2 | ${P_FITSORT} -d NAXIS1 | awk '{print $2}'`
    IMAGEY=`${P_DFITS} $1/$2 | ${P_FITSORT} -d NAXIS2 | awk '{print $2}'`
    
    if [ ${SIZEX} -gt ${IMAGEX} ]; then
	SIZEX=${IMAGEX}  
	echo "subimage size adapted to ${SIZEX}"
    fi
    
    if [ ${SIZEY} -gt ${IMAGEY} ]; then
	SIZEY=${IMAGEY}  
	echo "subimage size adapted to ${SIZEY}"
    fi
    
    CORNER_ULX=`${P_DFITS} $1/$2 | ${P_FITSORT} -d NAXIS1 |\
            ${P_GAWK} '{print int(($2 / 2) - ('${SIZEX}' / 2))}'` 
    
    CORNER_ULY=`${P_DFITS} $1/$2 | ${P_FITSORT} -d NAXIS2 |\
            ${P_GAWK} '{print int(($2 / 2) - ('${SIZEY}' / 2))}'` 
    
    if [ $CORNER_ULX -eq 0 ] && [ $CORNER_ULY -eq 0 ] && [ $SIZEX -eq $IMAGEX ] && [ $SIZEY -eq $IMAGEY ]; then
	
	ln -s $1/$2 ${TEMPDIR}/science_seeing_$$.fits
	ln -s $1/$3 ${TEMPDIR}/science_seeing_$$.weight.fits
	ln -s $1/$4 ${TEMPDIR}/science_seeing_$$.flag.fits
    else
	
	echo "Creating subimages"
	
	${P_MAKESUBIMAGE} ${CORNER_ULX} ${CORNER_ULY} ${SIZEX} ${SIZEY} \
	    < $1/$2 > ${TEMPDIR}/science_seeing_$$.fits
	
	if [ $? -gt 0 ]; then
	    echo "ERROR"
	    exit 1
	else
	    echo "${TEMPDIR}/science_seeing_$$.fits done!"
	fi
	
	${P_MAKESUBIMAGE} ${CORNER_ULX} ${CORNER_ULY} ${SIZEX} ${SIZEY} \
	    < $1/$3 > ${TEMPDIR}/science_seeing_$$.weight.fits

	if [ $? -gt 0 ]; then
	    echo "ERROR"
	    exit 1
	else
	    echo "${TEMPDIR}/science_seeing_$$.weight.fits done!"
	fi
	
	
	${P_MAKESUBIMAGE} ${CORNER_ULX} ${CORNER_ULY} ${SIZEX} ${SIZEY} \
	    < $1/$4 > ${TEMPDIR}/science_seeing_$$.flag.fits

	if [ $? -gt 0 ]; then
	    echo "ERROR"
	    exit 1
	else
	    echo "${TEMPDIR}/science_seeing_$$.flag.fits done!"

	fi
	

    fi
fi


echo "Running SExtractor"

GAIN=`${P_DFITS} $1/$2 | ${P_FITSORT} -d GAIN | awk '{print $2}'`

if [ "${GAIN}" = "KEY_N/A" ]; then
  GAIN=1.0
fi

MAGZP=`${P_DFITS} $1/$2 | ${P_FITSORT} -d MAGZP | awk '{print $2}'`
MAGZPCONF="-MAG_ZEROPOINT ${MAGZP}"
MAGZPCOND="MAG_AUTO 18.0 22.0"

if [ "${MAGZP}" = "KEY_N/A" ] || [ "${MAGZP}" = "-1.0" ] || [ "${MAGZP}" = "-1" ]; then
  MAGZPCONF=""
  MAGZPCOND=""
fi

${P_SEX} ${TEMPDIR}/science_seeing_$$.fits \
        -c ${SCIENCECONF}/seeing.conf.sex \
  	-CATALOG_NAME ${TEMPDIR}/seeing.cat_$$ \
        -FILTER_NAME ${SCIENCECONF}/default.conv\
  	-CATALOG_TYPE FITS_LDAC \
  	-DETECT_MINAREA 10 -DETECT_THRESH 10.\
  	-ANALYSIS_THRESH 1.2 \
  	-PARAMETERS_NAME ${SCIENCECONF}/seeing.param.sex\
        -WEIGHT_IMAGE ${TEMPDIR}/science_seeing_$$.weight.fits\
        -WEIGHT_TYPE MAP_WEIGHT \
        -FLAG_IMAGE ${TEMPDIR}/science_seeing_$$.flag.fits\
        -FLAG_TYPE MAX \
        -GAIN ${GAIN} ${MAGZPCONF}


echo "Determining seeing"
FWHM=`${P_PREANISOTROPY} -i ${TEMPDIR}/seeing.cat_$$ \
                   -t LDAC_OBJECTS \
                   -c MAGERR_AUTO 0.0 0.01 IMAFLAGS_ISO 0.0 0.5 ${MAGZPCOND}\
                   -k FWHM_IMAGE MAG_AUTO 2>&1 |\
                    ${P_GAWK} '($1 ~ /best/) {print $3 * '${PIXSCALE}'}'`
if [ -z "${FWHM}" ]; then
    FWHM="ERROR"
fi
echo "The seeing is: ${FWHM}"

# save subimages if requested:
if [ $# -gt 5 ] && [ "${FWHM}" != "ERROR" ]; then
   test -d $6 || mkdir $6
   cp ${TEMPDIR}/science_seeing_$$.fits $6/$7
   cp ${TEMPDIR}/science_seeing_$$.weight.fits $6/$8
   cp ${TEMPDIR}/science_seeing_$$.flag.fits $6/$9

    # update the SEEING header keyword in the filtered image:
   replacekey $6/$7 "SEEING  = ${FWHM}" SEEING  

fi

# clean up:
rm ${TEMPDIR}/science_seeing_$$.fits
rm ${TEMPDIR}/science_seeing_$$.weight.fits 
rm ${TEMPDIR}/science_seeing_$$.flag.fits 
rm ${TEMPDIR}/seeing.cat_$$

exit 0

