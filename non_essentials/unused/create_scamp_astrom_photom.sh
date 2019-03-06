#!/bin/bash -u

# ----------------------------------------------------------------
# File Name:           create_scamp_astrom_photom.sh
# Author:              Thomas Erben (terben@astro.uni-bonn.de)
# Last modified on:    08.01.2007
# Description:         Performs astrometric and relative photometric
#                      calibration of THELI sets with scamp V1.4.0
# ----------------------------------------------------------------

# Script history information:
# 14.09.2007:
# Project started 
#
# 17.09.2007:
# - I updated the documentation
# - I fixed some bugs concerning the location of
#   resulting files
# - I appended NTHREADS to the scamp command line
#   which uses a multi-processor architecture if available.
#   NTHREADS is set to NPARA.
#
# 24.09.2007:
# - Update of documentation text
# - Bug fix for the location of catalogue files
# - FITS conform output of the RZP header keyword in
#   scamp catalogues
#
# 02.10.2007:
# I made the script a bit more robust by adding more sanity
# checks.
#
# 21.12.2007:
# - I extended the script so that different mosaic configurations
#   within one astrometric set can be handled now. To this end we
#   create an artificial external header containing the keyword
#   MISSCHIP listing the missing chips. This keyword is then added
#   to the FITS cards distinguishing astrometric runs.
# - One explicit call to 'ldactoasc' was replaced by an implicit one.
#
# 30.12.2007:
# - I extended the script to treat data from different image directories
#   simultaneously.
# - Multiple photometric contexts are now handled correctly.
#
# 08.12.2008:
# I updated the script documentation

# File inclusions:
. ${INSTRUMENT:?}.ini

# define THELI_DEBUG and some other variables because of the '-u'
# script flag (the use of undefined variables will be treated as
# errors!)  THELI_DEBUG is used in the cleanTmpFiles function.
# 
THELI_DEBUG=${THELI_DEBUG:-""}
P_SCAMP=${P_SCAMP:-""}
P_ACLIENT=${P_ACLIENT:-""}

##
## function definitions:
##
function printUsage 
{
    echo "SCRIPT NAME:"
    echo "    create_scamp_astrom_photom.sh"
    echo ""
    echo "ARGUMENTS:"
    echo "    1. main_dir.         1"
    echo "    2. set_dir.          1"
    echo "    3. image_extension   1"
    echo "    4. main_dir.         2"
    echo "    5. set_dir.          2"
    echo "    6. image_extension   2"
    echo "    ."
    echo "    ."
    echo "    n. standardstar_catalog"
    echo ""
    echo "    An arbitrary number of blocks 'main_dir.', 'set_dir.' and"
    echo "    'image_extension' can be provided."
    echo ""
    echo "    ${SET} in the description below refers to the directory(ies)"
    echo "    /main dir./set dir./"
    echo ""
    echo "DESCRIPTION: "
    echo "     This script performs astrometric and relative photometric"
    echo "    calibration of THELI sets with Emanuel Bertins scamp program. The"
    echo "    script works with scamp V1.4.0; The scamp program itself is not"
    echo "    contained in the THELI pipeline package and needs, together with"
    echo "    'cdsclient' and the Python module 'pyfits', to be installed"
    echo "    separately (see the DEPNDENCY section below)"
    echo "    "
    echo "    The script substitutes the scripts"
    echo "    "
    echo "    - create_astrometrix_astrom(_run).sh"
    echo "    - create_photometrix.sh"
    echo "    "
    echo "    of the THELI ASTROMETRIX/PHOTOMETRIX processing. It ends with"
    echo "    header files in a ${SET}/headers_scamp directory which can then"
    echo "    directly be used for image co-addition.  To use the scamp headers"
    echo "    the 'prepare_coadd_swarp.sh' script has to be called with the '-eh"
    echo "    headers_scamp' option."
    echo "    "
    echo "    !! NOTE:"
    echo "       A call to 'create_absphotom_photometrix.sh' after this script"
    echo "       is still necessary to calculate the absolute zeropoint for a"
    echo "       coadded image "
    echo "    !!"
    echo ""
    echo "    The standardstar_catalog (n-th command line argument) can be any"
    echo "    astrometric catalogue supported by scamp."
    echo ""
    echo "    Unless with Astrometrix it is possible to astrometrically and"
    echo "    photometrically calibrate multiple, associated sets"
    echo "    (e.g. multi-coour observations of the same target) simultaneously."
    echo "    The script performs its tasks and puts resulting files in the"
    echo "    directory ${SET}/astrom_photom_scamp (of the first given image"
    echo "    set) and subdirectories therein. From there, final headers are"
    echo "    moved to the appropriate directories at the end of processing."
    echo "         "
    echo "IMPORTANT DEPENDENCIES:"
    echo "    (1) The script calls the Python script 'scampcat.py' which creates"
    echo "        scamp MEF exposure catalogues from the individual THELI chip "
    echo "        catalogues. This Python script itself depends on pyfits."
    echo "        The presence of pyfits and associated packages (numarray or "
    echo "        numpy) is NOT verified during THELI installation."
    echo "    (2) scamp uses the configuration file 'scamp_astrom_photom.scamp'"
    echo "        which is set to define scamp astrometric contexts on the"
    echo "        basis of the FILTER and GABODSID keywords. For the CFHTLS this "
    echo "        turned out to produce too many astrometric contexts to handle! "
    echo "        If this is the case GABODSID should be replaced by the RUN "
    echo "        identifier."
    echo ""
    echo "TECHNICAL/IMPLEMENTATION INFORMATION:    "
    echo "    Most parts of the scripts concern transformations between"
    echo "    files that scamp needs/returns and the formats needed by"
    echo "    our THELI pipeline. Main differences and some more (random)"
    echo "    comments are:"
    echo "    "
    echo "    (1) Our THELI 'runs' are called 'astrometric contexts' in the scamp"
    echo "        language."
    echo "    (2) For each multi-chip exposure scamp expects ONE object catalogue"
    echo "        in MEF format. In THELI we work with individual catalogues"
    echo "        for each chip. If we would feed all individual chips into scamp"
    echo "        they are not recognised as being part of a specific exposure."
    echo "    (3) scamp outputs ONE header file with all chips for each exposure."
    echo "        In THELI we need one header per chip."
    echo "    (4) scamp only gives a final flux scale w.r.t. a specified zeropoint."
    echo "        We need the 'relative' magnitude offsets of each exposure w.r.t."
    echo "        a zero mean offset."
    echo "    (5) Absolute magnitudes are calculated in THELI outside the "
    echo "        astrometry/relative photometry step. For the time being we"
    echo "        do not provide the necessary interface (header keywords) to use "
    echo "        the absolute calibration within scamp."
    echo "    (6) Note that names for astrometric standardstar catalogues are slightly"
    echo "        different for scmap and THELI/ASTROMETRIX; "
    echo "        e.g. USNOB1 (THELI), but USNO-B1 (scamp)"
    echo "    (7) scamp crashes if images with a different number of chips "
    echo "        (same instrument) are found within one astrometric context. "
    echo "        Images with a different number of chips in different contexts "
    echo "        pose no problem. This can for instance happen because of "
    echo "        readout-problems for some chips in some exposures."
    echo ""
    echo "AUTHOR:"
    echo "    Thomas Erben (terben@astro.uni-bonn.de)"
    echo ""
}


function cleanTmpFiles
{
    if [ -z ${THELI_DEBUG} ]; then
        echo "Cleaning temporary files for script $0"
        test -f photdata.txt_$$           && rm photdata.txt_$$
        test -f photdata_relzp.txt_$$     && rm photdata_relzp.txt_$$
    else
        echo "Variable THELI_DEBUG set! No cleaning of temp. files in script $0"    
    fi
}

# Handling of program interruption by CRTL-C
trap "echo 'Script $0 interrupted!! Cleaning up and exiting!'; \
      cleanTmpFiles; exit 1" INT

##
## initial sanity checks
##
# check whether we have the external 'scamp' and 'aclient' programs at all:
if [ -z ${P_SCAMP} ] || [ -z ${P_ACLIENT} ] 
then
    echo "You need the external 'scamp' AND 'aclient' programs to"
    echo "use this script! The necessary variable(s) in"
    echo "your progs.ini seem(s) not to be set! Exiting!!"
    exit 1;
fi

# check validity of command line arguments:
# First a check on the number of the arguments:
if [ $(( ($# - 1) % 3 )) -ne 0 ]; then
    printUsage
    exit 1
fi

# The number of different image directories we have to consider:
NDIRS=$(( ($# - 1) / 3 ))

# Test existence of image directory(ies) and create headers_scamp
# directories:
i=1 
j=2
k=1

while [ ${k} -le ${NDIRS} ]
do 
  if [ -d /${!i}/${!j} ]; then
      if [ -d /${!i}/${!j}/headers_scamp ]; then
          rm -rf /${!i}/${!j}/headers_scamp
      fi
      mkdir /${!i}/${!j}/headers_scamp
  else
      echo "Can't find directory /${!i}/${!j}"; 
      exit 1;
  fi
  i=$(( ${i} + 3 ))
  j=$(( ${j} + 3 ))
  k=$(( ${k} + 1 ))
done


##
## Here the main script starts:
##
STARCAT=${!#}
DIR=`pwd`

# all processing is performed in the 'first' image directory in
# a astrom_photom_scamp subdirectory:
cd /$1/$2/

test -d "astrom_photom_scamp" && rm -rf astrom_photom_scamp

mkdir -p astrom_photom_scamp/cat
mkdir astrom_photom_scamp/headers
mkdir astrom_photom_scamp/plots

cd astrom_photom_scamp/cat

# filter input catalogues to reject bad objects
i=1
j=2
k=3
l=1
NCATS=0

while [ ${l} -le ${NDIRS} ]
do 
  FILES=`${P_FIND} /${!i}/${!j}/cat/ -maxdepth 1 -name \*${!k}.cat`

  for CAT in ${FILES}
  do
    NCATS=$(( ${NCATS} + 1 ))

    BASE=`basename ${CAT} ${!k}.cat`
    # we filter away flagged objects except THOSE which are saturated!
    # we also require a minimum size (semi minor axis) of two pixels
    ${P_LDACFILTER} -i ${CAT} -t LDAC_OBJECTS \
                    -c "((FLAGS<2)OR(FLAGS=16))AND(B_IMAGE>2.0);" \
                    -o ${BASE}${!k}.ldac

    # The follwowing two arrays are necessary to put headers
    # to the correct directories lateron.
    CATBASE[${NCATS}]=${BASE}
    CATDIR[${NCATS}]=/${!i}/${!j}
  done

  i=$(( ${i} + 3 ))
  j=$(( ${j} + 3 ))
  k=$(( ${k} + 3 ))
  l=$(( ${l} + 1 ))
done

# from our single chip catalogues create merged MEF catalogues
# for each exposure:
# first get the basenames of all available exposures.
# The following fiddling is necessary because catalogues
# for individual chips might not be present (bad chips)

# The following 'awk' construct cuts away everything after 
# the last '_' in the image names (including the underscore itself)
IMAGES=`${P_FIND} . -name \*ldac -exec basename {} \; |\
        ${P_GAWK} '{ n = split($1, a, "_"); 
                     name=""; 
                     for(i = 1; i < (n-1); i++) 
                     {
                       name = name a[i] "_"
                     } 
                     name = name a[n-1]; 
                     print name;}' | sort | uniq`

# now the merging with a pyfits-based Python script:
for IMAGE in ${IMAGES}
do
  # If an old scamp catalogue exists the python call below
  # would fail!
  test -f ./${IMAGE}_scamp.cat && rm -f ./${IMAGE}_scamp.cat

  i=1
  CATS=""
  MISSCHIP=0     # contains the missing chips in the form of a pasted
                 # string. If e. g. chips 19 and 25 are bad the variable
                 # would contain 01925 (read 0_19_25; '0' is always at
                 # the beginning)
  NREALCHIPS=0
  while [ ${i} -le ${NCHIPS} ]
  do
    # The following test for an image implicitely assumes that the
    # image ending does NOT start with a number: obvious but I mentoin
    # it just in case ....
    # It is necessary as we allow for images with different endings in the 
    # image directories:
    if [ -f ${IMAGE}_${i}[!0-9]*.ldac ]; then
      CATS="${CATS} ${IMAGE}_${i}[!0-9]*.ldac"
      NREALCHIPS=$(( ${NREALCHIPS} + 1 ))
    else
      MISSCHIP=${MISSCHIP}${i}
    fi
    i=$(( ${i} + 1 ))
  done
  python ${S_SCAMPCAT} ${CATS} ./${IMAGE}_scamp.cat

  # Dummy external header containing missing chip information.
  # They are used to distinguish different chip configurations
  # in an, otherwise, unique astrometric conetxt.
  test -f ./${IMAGE}_scamp.ahead && rm ./${IMAGE}_scamp.ahead
  i=1
  while [ ${i} -le ${NREALCHIPS} ]
  do
    echo "MISSCHIP= '${MISSCHIP}'" >> ./${IMAGE}_scamp.ahead
    echo "END      "               >> ./${IMAGE}_scamp.ahead
    i=$(( ${i} + 1 ))
  done
done

# now call scamp:
cd ../headers

${P_SCAMP} `${P_FIND} ../cat/ -name \*scamp.cat` \
           -c ${CONF}/scamp_astrom_photom.scamp \
           -CDSCLIENT_EXEC ${P_ACLIENT} \
           -ASTREF_CATALOG ${STARCAT} \
           -NTHREADS ${NPARA}

if [ $? -ne 0 ]
then
  echo "scamp call failed !! Exiting !!"
  cleanTmpFiles
  exit 1
fi

# scamp creates the headers in the directory where the catalogs
# are:
${P_FIND}  ../cat/ -name \*.head -exec mv {} . \;

# we want the diagnostic plots in an own directory:
mv fgroups*         ../plots
mv distort*         ../plots
mv astr_interror2d* ../plots
mv astr_interror1d* ../plots
mv astr_referror2d* ../plots
mv astr_referror1d* ../plots
mv astr_chi2*       ../plots
mv psphot_error*    ../plots

# now get the relative magnitude offsets from the FLXSCALES
# estimated by scamp:
test -f photdata.txt_$$ && rm photdata.txt_$$

# Because the flux scales refer to an image normalised to one
# second we need to obtain the exposure times of all frames
# first. We also get the SCAMP flux scale and the photometric 
# instrument:
for IMAGE in ${IMAGES}
do
  NAME=${IMAGE}
  EXPTIME=`${P_LDACTOASC} -i ../cat/${IMAGE}_scamp.cat \
                     -t LDAC_IMHEAD -s |\
           fold | grep EXPTIME | ${P_GAWK} '{print $3}'`
  FLXSCALE=`grep FLXSCALE ${IMAGE}_scamp.head | uniq |\
            ${P_GAWK} '{print $2}'`
  PHOTINST=`grep PHOTINST ${IMAGE}_scamp.head | uniq |\
            ${P_GAWK} '{print $2}'`

  echo ${NAME}" "${EXPTIME}" "${FLXSCALE}" "${PHOTINST} >> photdata.txt_$$
done

# The following 'awk' script caculates relative zeropoints for the
# different photometric contexts: 
${P_GAWK} 'BEGIN {maxphotinst = 1;}
           { name[NR] = $1; exptime[NR] = $2; flxscale[NR] = $3;
             photinst[NR] = $4
             val[NR] = -2.5*log($3*$2)/log(10); 
             m[$4] = m[$4] + val[NR]
             nphotinst[$4] = nphotinst[$4] + 1 
             if($4 > maxphotinst) {maxphotinst = $4}} 
           END {
             for(i = 1; i <= maxphotinst; i++)
             {  
               m[i] = m[i] / nphotinst[i];
             } 
             for(i = 1; i <= NR; i++) 
             {
               relzp[i] = val[i] - m[photinst[i]];   
               printf("%s %f\n", 
                 name[i], relzp[i]);  
             }
           }' photdata.txt_$$ > photdata_relzp.txt_$$

# now split the exposure catalogues for the indivudual chips
# and add the RZP header keyword. Put the headers into
# appropriate headers_scamp directories
#
while read NAME RELZP
do
  i=1
  while [ ${i} -le ${NCHIPS} ]
  do
    # we need to take care of catalogs that may not be
    # present (bad chips)!
    if [ -f ../cat/${NAME}_${i}[!0-9]*.ldac ]
    then
      ${P_GAWK} 'BEGIN {ext = '${i}'; nend = 0} 
                 {
                   if(nend < ext) 
                   {
                     if($1 == "END") 
                     {
                       nend++; 
                       next; 
                     } 
                     if(nend == (ext-1)) { print $0 } 
                   } 
                 }
                 END { printf("RZP     = %20f / THELI relative zeropoint\n", 
                              '${RELZP}');
                   printf("END\n")
                 }' ${NAME}_scamp.head > ${NAME}_$i.head
    fi

    i=$(( $i + 1 ))
  done
done < photdata_relzp.txt_$$

i=1
while [ ${i} -le ${NCATS} ]
do
  if [ -f ${CATBASE[$i]}.head ]; then
    mv ${CATBASE[$i]}*head ${CATDIR[$i]}/headers_scamp
  fi
  
  i=$(( ${i} + 1 )) 
done

# clean up temporary files and bye
cleanTmpFiles

cd ${DIR}

exit 0
