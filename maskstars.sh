#!/bin/bash -u

# ----------------------------------------------------------------
# File Name:           maskstars.sh
# Author:              Thomas Erben (terben@astro.uni-bonn.de)
# Last modified on:    21.11.2007
# Description:         Creates object masks around sources identified
#                      in standard star catalogues
# Version:             $$VERSION$$
# ----------------------------------------------------------------

# Script history information:
# 17.07.2007:
# first script version written
#
# 02.08.2007:
# - Bug correction due to inconsistencies in the output
#   of different versions of the 'xy2sky' program.
#   (Thanks to Mike Lechster)
# - Clean up at the end of the script
#
# 03.08.2007:
# More robust treatment of 'awk' and 'sed' calls
# (MAC/Linux ASCII issues)
#
# 28.08.2007:
# - findusnob1 is called via a variable to ensure
#   the correct script to be executed.
# - More robust treatment of the special case of
#   a 'last element' with an 'awk'/'sed' construct.
#   The old way of replacing '\n' for a line feed
#   led to problems on non-Linux architectures.
#
# 19.11.2007:
# I included the LDAC PMM catalogue and rewrote the script
# to use the 'getopts' function to process command line 
# arguments.
#
# 21.11.2007:
# - correction of an errorneous 'if' statement
# - update of documentation
#
# 22.11.2007:
# update of documentation

# preliminary stuff:
# Temporarily expand the PATH variable to include needed
# programs:
BINPATH=/u/ki/anja/software/automask-0.5/ext_libs/Linux_64/bin
P_XY2SKY=${BINPATH}/xy2sky
P_SKY2XY=${BINPATH}/sky2xy
S_FINDUSNOB1=${BINPATH}/findusnob1

# To make sure that 'awk' behaves in a reasonable way
# (no commas separating entries etc.)
LANG=C

# define THELI_DEBUG because of the '-u' script flag
# (the use of undefined variables will be treated as errors!)
THELI_DEBUG=${THELI_DEBUG:-""}

# function definitions
function printUsage 
{
    echo "SCRIPT NAME:"
    echo "    maskstars.sh - create ds9 region files for masks around bright stars"
    echo ""
    echo "SYNOPSIS:"
    echo "    maskstars.sh -i input_image"
    echo "                 -a astrometric_catalogue (USNOB1, PMM)"
    echo "                 -s star_mask"
    echo "                 -p pivot_magnitude"
    echo "                 -m mask_scaling_slope"
    echo "                 -l limiting_magnitude"
    echo "                 -o output_region_file"
    echo "               [ -d PMM_catalogue_directory ]"
    echo ""
    echo "    If the astrometric catalogue is 'PMM', the option '-d'"
    echo "    with its argument has to be given."
    echo ""
    echo "DESCRIPTION:"
    echo "    The script creates a saoimage/ds9 region file around"
    echo "    objects listed in an astronomical standardstar catalogue."
    echo "    Its intention is to automatically mask areas around "
    echo "    moderately bright stars with magnitudes up to about 17."
    echo "    Areas around very bright sources and large galaxies "
    echo "    should be treated with 'maskvoids.sh' instead."
    echo ""
    echo "    The form of the regions is given in an ASCII file"
    echo "    'star_mask'. Each line contains one node of a polygon and the"
    echo "    polygon centre is assumed to be at (0,0); see the files"
    echo "    'WFI_star_R_14.1.reg' (mask for a star of mag 14.1 in broad-band"
    echo "    'R' for WFI@MPG/ESO2.2m) and 'MEGAPRIME_star_i_13.8.reg' (mask for"
    echo "    a star of mag 13.8 in broad-band 'i' for MEGAPRIME@CFHT) in the"
    echo "    automask 'config' subdirectory as examples. "
    echo ""
    echo "    Positions of candidate stars in 'input_image' are retrieved via an"
    echo "    LDAC PMM object catalogue on disk or via the WWW with Francois"
    echo "    Ochsenbeins 'cdsclient' tools. We obtain positions and"
    echo "    magnitudes. All sources up to 'limiting_magnitude' are then"
    echo "    enclosed by an object mask. Before the mask is applied its 'size'"
    echo "    is scaled linearily with source magnitude according to:"
    echo ""
    echo "    scale = 1. - 'mask_scaling_slope' * (mag - 'pivot_magnitude')"
    echo "    "
    echo "    All lines connecting the mask centre with the individual"
    echo "    nodes in 'star_mask' are then stretched with 'scale'."
    echo "    The 'mask_scaling_slope' has to be found empirically for"
    echo "    each telescope/instrument/color configuration."
    echo "    'pivot_magnitude' is the magnitude of the star from which"
    echo "    you created the input mask file 'star_mask'."
    echo ""
    echo "    Finally all polygons are written in ds9/saoimage format"
    echo "    to 'output_region_file'."
    echo ""
    echo "    Be aware that all objects found in the standardstar catalogue are"
    echo "    marked with the SAME mask found in 'star_mask', i.e. also galaxies"
    echo "    are treated with stellar masks and the created region files should"
    echo "    be inspected and adapted manually. Also note that the mask size"
    echo "    needed for very bright stars typically does not scale linearily"
    echo "    and also the form of the masks for those objects would need to be"
    echo "    adapted. Areas around such objects and large galaxies should be"
    echo "    catched with the 'maskvoids.sh' script instead."
    echo "     "
    echo "    The supported astrometric standardstar catalogues up to now are:"
    echo ""
    echo "    - PMM (LDAC 'PMM' USNO-A2 object catalogue) with its red magnitude"
    echo "    - USNOB1 with its red magnitudes"
    echo ""
    echo "    For the script to work your images need an appropriate"
    echo "    astrometric system in their image headers. It has to be"
    echo "    compatible with the standardstar catalogue you use."
    echo ""
    echo "EXAMPLES:"
    echo "    - THELI processed WFI data:"
    echo "      maskstars.sh -i ./Deep3a_R.D3AA.swarp.fits \\"
    echo "                   -a USNOB1 \\"
    echo "                   -s ./WFI_star_R_14.1.reg \\"
    echo "                   -p 14.1 -m 0.3 -l 16.0 \\"
    echo "                   -o Deep3a_stars.reg"
    echo ""
    echo "    - THELI processed CFHTLS Wide data:"
    echo "      maskstars.sh -i ./W4p2m2_i.V1.7A.swarp.fits \\"
    echo "                   -a PMM -d /aibn202_2/thomas/USNO-A2/ \\"
    echo "                   -s ./MEGAPRIME_star_i_13.8.reg \\"
    echo "                   -p 13.8 -l 16.0 -m 0.3 \\"
    echo "                   -o W4p2m1_stars.reg"
    echo ""
    echo "KNOWN BUGS:"
    echo "    Using the USNOB1 standard star catalogue can lead to 'ghost masks'."
    echo "    Masks appear in areas where apparently no astronomical source is "
    echo "    located."
    echo ""
    echo "AUTHOR:"
    echo "    Thomas Erben         (terben@astro.uni-bonn.de)"
    echo ""
    echo "    The script is heavily based on codes from"
    echo "    Ludovic van Waerbeke (waerbeke@phas.ubc.ca) and"
    echo "    Hendrik Hildebrandt  (hendrik@astro.uni-bonn.de)"
}

function cleanTmpFiles
{
    if [ -z ${THELI_DEBUG} ]; then
        echo "Cleaning temporary files for script $0"
        test -f pos.txt_$$     && rm pos.txt_$$ 
        test -f mag.txt_$$     && rm mag.txt_$$ 
        test -f starcat.txt_$$ && rm starcat.txt_$$ 
    else
        echo "Variable THELI_DEBUG set! No cleaning of temp. files in script $0"    
    fi
}

# Handling of program interruption by CRTL-C
trap "echo 'Script $0 interrupted!! Cleaning up and exiting!'; \
      cleanTmpFiles; exit 0" INT TERM

# Handle command line arguments
#
# Default values:
INPUT_IMAGE=""
STANDARD_CATALOGUE=""
STELLAR_MASK=""
PIVOT_MAGNITUDE=""
LIMITING_MAG=""
OUTPUT_REGIONFILE=""
PMM_DIRECTORY=""
MASK_SCALING_SLOPE=""

# to satisfy the '-u' bash shell flag for unbound
# variables:
OPTARG=""

while getopts ':i:a:s:p:m:l:o:d:h' OPTION ; do
  case $OPTION in
    a)   STANDARD_CATALOGUE=$OPTARG;;
    d)   PMM_DIRECTORY=$OPTARG;;
    h)   printUsage; exit 0; ;;
    i)   INPUT_IMAGE=$OPTARG;;
    l)   LIMITING_MAG=$OPTARG;;
    m)   MASK_SCALING_SLOPE=$OPTARG;;
    o)   OUTPUT_REGIONFILE=$OPTARG;;
    p)   PIVOT_MAGNITUDE=$OPTARG;;
    s)   STELLAR_MASK=$OPTARG;;
    \?)  echo "Unknown Option \"-$OPTARG\"."
         printUsage; exit 1; ;;
    :)   echo "Option \"-$OPTARG\" needs an argument"
         printUsage; exit 1; ;;
    *)   echo "This cannot hapen !! ...\"$OPTION\"... "
         printUsage; exit 1; ;;
  esac
done

# check validity of command line arguments:
if [ -z ${INPUT_IMAGE} ]          || [ -z ${STANDARD_CATALOGUE} ]\
     || [ -z ${LIMITING_MAG} ]    || [ -z ${OUTPUT_REGIONFILE} ]\
     || [ -z ${PIVOT_MAGNITUDE} ] || [ -z ${STELLAR_MASK} ]\
     || [ -z ${MASK_SCALING_SLOPE} ]; then

    printUsage
    exit 1
fi

if [ "${STANDARD_CATALOGUE}" = "PMM" ] && [ -z ${PMM_DIRECTORY} ]
then
    printUsage
    exit 1  
fi

# get radial extend of imaging data:
NAXIS1=`dfits ${INPUT_IMAGE} | fitsort -d NAXIS1 | awk '{print $2}'`
NAXIS2=`dfits ${INPUT_IMAGE} | fitsort -d NAXIS2 | awk '{print $2}'`

# to retrieve entries from a standardstar catalogue
# we consider a circle around the middle of the image
# with half the diagonal as radius (in arcmin):
RAZERO=`${P_XY2SKY} -d ${INPUT_IMAGE} 0 0 | awk '{print $1}'`
DECZERO=`${P_XY2SKY} -d ${INPUT_IMAGE} 0 0 | awk '{print $2}'`
RAMAX=`${P_XY2SKY} -d ${INPUT_IMAGE} ${NAXIS1} ${NAXIS2} | awk '{print $1}'`
DECMAX=`${P_XY2SKY} -d ${INPUT_IMAGE} ${NAXIS1} ${NAXIS2} | awk '{print $2}'`
RAMIDDLE=`awk 'BEGIN {print ('${RAZERO}' + ('${RAMAX}')) / 2.}'`
DECMIDDLE=`awk 'BEGIN {print ('${DECZERO}' + ('${DECMAX}')) / 2.}'`
RADIUS=`awk 'function sqr(x) {
               return (x*x)
             } 
             BEGIN {radiff  = ('${RAMAX}'-('${RAZERO}'));
                    decdiff = ('${DECMAX}'-('${DECZERO}'));
                    print sqrt(sqr(radiff) + sqr(decdiff)) / 2. * 60.}'`


# code to retrieve star positions from the different
# standardstar catalogues:

# PMM is the only catalogue read from disk! We use the THELI program
# 'get_pmm_objects' and the associated '.pmm' catalogue format:
if [ "${STANDARD_CATALOGUE}" = "PMM" ]; then
    # The size parameter of the 'get_pmm_objects' program is a box
    # with a given sidelength (in degrees). To be sure to cover the 
    # whole field we take two times the diagonal radius which is 
    # calculated above:
    RADIUS=`awk 'BEGIN {print '${RADIUS}' * 2 / 60.}'`
    get_pmm_objects -i ${PMM_DIRECTORY} -r ${RAMIDDLE} -d ${DECMIDDLE} \
                    -s ${RADIUS}\
      | awk '$3 < '${LIMITING_MAG}' {print $1, $2 > "pos.txt_'$$'"; 
                                     print $3 > "mag.txt_'$$'" }' 
fi

# For USNO-B1 we consider the 'red' magnitude. The
# catalogue contains up to two measurement for each object.
# We take the mean of what is present:
if [ "${STANDARD_CATALOGUE}" = "USNOB1" ]; then
    ${S_FINDUSNOB1} -c ${RAMIDDLE} ${DECMIDDLE} -r ${RADIUS} -m 1000000 |\
	awk '(NR>4 && $0 !~/to/ && $0 !~/required/ && $0 !~/matches/ && 
          NF == 41) { avmag=0
                sum=0
                if ($20 !~ /---/) {avmag = avmag + $20; sum++;}
                if ($30 !~ /---/) {avmag = avmag + $30; sum++;}

                if (sum != 0) 
                {
                    avmag = avmag / sum;
                    if(avmag < '${LIMITING_MAG}')
                    {
                        printf ("%s %f\n", $2, avmag);
                    }
                }
              }' | \
        sed -e 's/+/ +/g' -e 's/-/ -/g' |\
        awk '{print $1, $2 > "pos.txt_'$$'"; print $3 > "mag.txt_'$$'" }'
fi

# For the polygons we need pixel coordinates of the image
# under consideration. We also calculate the mask scaling
# size according to the formula:
#
# scale = 1. - 'mask slope' * (mag - 'pivot magnitude')
#
# Note that this gives a formal scaling of zero for
# stars of a certain magnitude magnitude!!
# Hence, take care that the limiting magnitude is in
# an appropriate range.
${P_SKY2XY} ${INPUT_IMAGE} @pos.txt_$$\
 | awk '{x = $5; y = $6; getline < "mag.txt_'$$'";
         print x, y, 1. - '${MASK_SCALING_SLOPE}' * ($1 - '${PIVOT_MAGNITUDE}')}' > starcat.txt_$$

test -f ${OUTPUT_REGIONFILE} && rm ${OUTPUT_REGIONFILE}

# now do the polygon file writing.
#
# The input mask is a simple ASCII file
# having a polygon point in each line.
# The 'centre' of the polygon is assumed
# to be at coordinates (0,0).
# 
# Printing the ')' in the END statement of 
# awk allows us to treat the special 
# case of the last element. After it, no ','
# should be printed before the closing ')'. 
# Instead of dealing with it within awk we 
# remove the extra ',' with a subsequent 
# 'sed' call.
while read XPOS YPOS SCALING
do
    awk 'BEGIN {printf("polygon(");}
         {angle = atan2($2, $1);
          len = '${SCALING}' * sqrt($1 * $1 + $2 * $2);
          xnew = len * cos(angle);
          ynew = len * sin(angle);
          printf("%d,%d,", 
            int('${XPOS}' + xnew + 0.5), int('${YPOS}' + ynew + 0.5));}
         END {printf(")\n");}' ${STELLAR_MASK} |\
    sed -e 's/,)/)/' >> ${OUTPUT_REGIONFILE}
done < starcat.txt_$$
 
# The end: clean up
cleanTmpFiles

exit 0;
