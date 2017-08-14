#!/bin/bash -u
# ----------------------------------------------------------------
# File Name:           create_binnedmosaics.sh
# Author:              Thomas Erben (terben@astro.uni-bonn.de)
# Last modified on:    20.09.2007
# Description:         creation of binned mosaic images for 
#                      regularly shaped multi-chip cameras
# ----------------------------------------------------------------

# Script history information:
#
# 20.09.2007:
# script written

. ${INSTRUMENT:?}.ini

# define THELI_DEBUG because of the '-u' script flag
# (the use of undefined variables will be treated as errors!)
# THELI_DEBUG is used in the cleanTmpFiles function.
THELI_DEBUG=${THELI_DEBUG:-""}

# function definitions:
function printUsage 
{
  echo "SCRIPT NAME:"
  echo "    create_binnedmosaics.sh"
  echo ""
  echo "ARGUMENTS:"
  echo "    1. main_dir."
  echo "    2. science_dir."
  echo "    3. image_prefix"
  echo "    4. image_extension"
  echo "    5. binning_factor"
  echo "    6. BITPIX of output images (16 or -32)"
  echo "       (OPTIONAL; default is 16)"
  echo ""
  echo "DESCRIPTION:"
  echo "    The script creates binned mosaic images from individual chip FITS"
  echo "    files of a multi-chip instrument. The mosaic must be 'regualrly'"
  echo "    shaped, i. e. the mosaic must form a rectangle with each chip"
  echo "    having the SAME x- and y-dimensions. If this is not the case"
  echo "    you have to rpovide an own, instrument dependent version of this"
  echo "    script."
  echo "    The created image mosaics allow us an easy"
  echo "    evaluation of prereduction quality and a comfortable detection of"
  echo "    image defects that might need manual intervention."
  echo ""
  echo "    The script takes its input images from /main_dir/science_dir/,"
  echo "    creates a subdirectory BINNED and puts its results therein."
  echo ""
  echo "    Given that individual chip FITS files have names like"
  echo "    prefix*_'CHIPNUMBER'image_extension.fits (The '*' stands"
  echo "    for an arbitrary character string) the output images"
  echo "    get the names prefix*.fits"
  echo "     "
  echo "EXAMPLES:"
  echo "    create_binnedmosaics.sh /aibn85_2/terben/DATA \\"
  echo "       SCIENCE_R WFI OFCSF 8 -32"
  echo ""
  echo "    This bins all images in /aibn85_2/terben/DATA/SCIENCE_R"
  echo "    with names WFI*_'CHIP'OFCSF.fits, where 'CHIPS' stands "
  echo "    for numbers ranging from 1 to the number of chips for"
  echo "    the considered instrument.    "
  echo "    (e.g. WFI.2000-12-27T07:50:38.198_1OFCSF.fits,"
  echo "          WFI.2000-12-27T07:50:38.198_1OFCSF.fits and so on)"
  echo "    The name of the output images would be"
  echo "    WFI.2000-12-27T07:50:38.198.fits and so on."
  echo ""
  echo "    If you want an arbitrary image_prefix, use "" as "
  echo "    command line argument, e.g."
  echo "    "
  echo "    create_binnedmosaics_MEGAPRIME.sh /aibn85_2/terben/DATA \\"
  echo "       SCIENCE_R "" C.sub 8 -32"
  echo "    "
  echo "AUTHOR:"
  echo "    Thomas Erben (terben@astro.uni-bonn.de)"
  echo ""
}

function cleanTmpFiles
{
    if [ -z ${THELI_DEBUG} ]; then
        echo "Cleaning temporary files for script $0"

        rm ${TEMPDIR}/image_list_$$
    else
        echo "Variable THELI_DEBUG set! No cleaning of temp. files in script $0"    
    fi
}

# Handling of program interruption by CRTL-C
trap "echo 'Script $0 interrupted!! Cleaning up and exiting!'; \
      cleanTmpFiles; exit 1" INT

# check validity of command line arguments:
if [ $# -lt 5 ] || [ $# -gt 6 ] ; then
    printUsage
    exit 1
fi

# set default for output BITPIX to 16:
if [ $# -lt 6 ]; then
  BITPIX=16
else
  BITPIX=$6
fi

# Here the main tasks of the script begin:

# Decompose chip geometry variable:
NCHIPSX=`echo ${CHIPGEOMETRY} | ${P_GAWK} '{print $1}'`
NCHIPSY=`echo ${CHIPGEOMETRY} | ${P_GAWK} '{print $2}'`

# Crude check whether Isomething is wrong with the CHIPGEOMETRY var.
test -z ${NCHIPSY} && \
     { echo "Malformed CHIPGEOMETRY variable! Exiting !!"; exit 1; }

cd $1/$2 || { echo "Directory $1/$2 does not exist! Exiting"; exit 1; }

if [ ! -d BINNED ]; then
  mkdir BINNED
fi

test -f ${TEMPDIR}/image_list_$$ && rm ${TEMPDIR}/image_list_$$

# note that we assume that FITS images are always present for
# ALL chips; also if they have the BADCCD flag set!
${P_FIND} . -name $3\*_2$4.fits > ${TEMPDIR}/image_list_$$

while read file
do
  BASE=`basename ${file} _2$4.fits`
  echo ${BASE}

  # build up image list for the album command:
  LIST=""
  i=1
  while [ ${i} -le ${NCHIPS} ]
  do
    LIST="${LIST} ${BASE}_${i}$4.fits"
    if [ ! -f ${BASE}_${i}$4.fits ]; then
	mode2=`imstats -s 800 1200 1800 2200 -t 0 22000 ${BASE}_2$4.fits | awk '{if($1!~"#") print $2}'`
	${P_IC} -c ${SIZEX[${i}]} ${SIZEY[${i}]} "${mode2}" > ${BASE}_${i}$4.fits
    fi

    i=$(( $i + 1 ))
  done

  # and do the mosaicing:
  ${P_ALBUM} -l -p ${BITPIX} -b $5 ${NCHIPSX} ${NCHIPSY} ${LIST}\
             > BINNED/${BASE}_mos$4.fits

done < ${TEMPDIR}/image_list_$$

# clean temporary files and bye
cleanTmpFiles
