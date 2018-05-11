#!/bin/bash
set -xv
#adam-example# ./create_scamp_astrom_photom.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-V SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-RC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-IC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+ SCIENCE PANSTARRS 2>&1 | tee -a OUT-create_scamp_astrom_photom-MACS0429-02.log
#adam-example# ./create_scamp_astrom_photom.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-J-B SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-C-RC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-S-Z+ SCIENCE SDSS-R6 2>&1 | tee -a OUT-create_scamp_astrom_photom-RXJ2129.log

# CVSID: $Id: create_scamp_astrom_photom.sh,v 1.36 2010-10-05 02:29:02 anja Exp $

# -----------------------------------------------------------------------
# File Name:           create_scamp_astrom_photom.sh
# Author:              Thomas Erben (terben@astro.uni-bonn.de)
# Last modified on:    03.09.2015 by Adam, works when both *${ending}fits & *OCFR.fits files are present
# Description:         Performs astrometric and relative photometric
#                      calibration of THELI sets with scamp V1.4.0-V1.4.6
# -----------------------------------------------------------------------

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
#
# 11.01.2008:
# The script now makes use of focal plane information if present!
# If an external header with name ${INSTRUMENT}.ahead is present in
# the reduction directory it is interpreted as containing focal plane
# information (first order astrometric information). In this case
# 'scamp' is run with the '-MOSAIC_TYPE FIX_FOCALPLANE' option. 
# Otherwise (no focal plane information available) we use
# '-MOSAIC_TYPE UNCHANGED'.
#
# 16.01.2008:
# I estimate the 'THELI' relative flux scaling zeropoint. Up to
# now I used the scamp value which is, however, scaled to a fixed
# magnitude (scamp config file). This value is not consistent with
# the THELI convention where the flux scale for each image is defined 
# as flxscale=10**(-0.4*relzp)/exptime
#
# 18.01.2008:
# Bug fix in the creation of individual header files; missing catalogs
# were not taken into account properly.
#
# 22.07.2008:
# The directory names where scamp performs its actions carry the name 
# of the used standardstar catalogue now. The same applies for the
# final header directories.
#
# 07.08.2008:
# Bug Fix for the new naming convention of appending the name of the
# reference cat to directory names

# 16.08.2008: (AvdL)
# adapted for Subaru by adding "ROTATION" to ASTRINSTRU_KEY
# note: could also sort by config and/or run
# right now this is done by GABODSID only

# 10.08.2008: (AvdL)
# .ahead files are now assigned based on configuration and rotation
# still to solve:
# why not work with config 8?
# how to pass prober number of chips

# 17.02.2008 (DA)
# Modified to not need file extensions

# 03.09.2015 (Adam W.)
# works when both *${ending}fits & *OCFR.fits files are present
# ... or any other number of different ${ending} values

# File inclusions:
if [ -z ${INSTRUMENT} ] ;then
	INSTRUMENT="SUBARU"
fi
. ${INSTRUMENT:?}.ini > /tmp/SUBARU.out 2>&1

### we can have different INSTRUMENTs
. progs.ini > /tmp/progs.out 2>&1

#adam: if there are multiple endings, you can set your preferred one here

# NCHIPSMAX needs to be set before
if [ ! -z ${NCHIPSMAX} ] ;then
	NCHIPS=${NCHIPSMAX}
fi

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
    echo "    3. main_dir.         2"
    echo "    4. set_dir.          2"
    echo "    ."
    echo "    ."
    echo "    n. standardstar_catalog"
    echo ""
    echo "    An arbitrary number of blocks 'main_dir.' and 'set_dir.'"
    echo "    can be provided."
    echo ""
    echo "    \${SET} in the description below refers to the directory(ies)"
    echo "    /main dir./set dir./"
    echo ""
    echo "DESCRIPTION: "
    echo "    This script performs astrometric and relative photometric"
    echo "    calibration of THELI sets with Emanuel Bertins scamp program. The"
    echo "    script was tested against scamp V1.4.6; The scamp program itself"
    echo "    is not contained in the THELI pipeline package and needs, together"
    echo "    with 'cdsclient' and the Python module 'pyfits', to be installed"
    echo "    separately (see the DEPNDENCY section below)"
    echo "    "
    echo "    The script substitutes the scripts"
    echo "    "
    echo "    - create_astrometrix_astrom(_run).sh"
    echo "    - create_photometrix.sh"
    echo "    "
    echo "    of the THELI ASTROMETRIX/PHOTOMETRIX processing. It ends with"
    echo "    header files in a \${SET}/headers_scamp_\${!#} directory (the \${!#}"
    echo "    stands for the used standardstar catalogue) which can then"
    echo "    directly be used for image co-addition.  To use the scamp headers"
    echo "    the 'prepare_coadd_swarp.sh' script has to be called with the '-eh"
    echo "    headers_scamp_..' option."
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
    echo "    directory \${SET}/astrom_photom_scamp (of the first given image"
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
    echo "    (3) The script checks whether a file \${INSTRUMENT}.ahead is present"
    echo "        in your reduction directory. If yes, it interprets it as a scamp"
    echo "        'additional' header containing 'focal plane' (first order "
    echo "        astrometric) information overriding corresponding entries in image"
    echo "        headers. In this case scamp is run with the "
    echo "        '-MOSAIC_TYPE FIX_FOCALPLANE' option. We use '-MOSAIC_TYPE UNCHANGED' "
    echo "        otherwise."
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
        test -f photdata.txt_$$           && rm -f photdata.txt_$$
        test -f photdata_relzp.txt_$$     && rm -f photdata_relzp.txt_$$
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
if [ $(( ($# - 1) % 2 )) -ne 0 ]; then
    printUsage
    exit 1
fi

# The number of different image directories we have to consider:
NDIRS=$(( ($# - 1) / 2 ))

# get the used reference catalogue into a variable
STARCAT=${!#}

# Test existence of image directory(ies) and create headers_scamp
# directories:
i=1 
j=2
k=1

while [ ${k} -le ${NDIRS} ]
do 
  if [ -d /${!i}/${!j} ]; then
      if [ -d /${!i}/${!j}/headers_scamp_${STARCAT} ]; then
          rm -rf /${!i}/${!j}/headers_scamp_${STARCAT}
      fi
      mkdir /${!i}/${!j}/headers_scamp_${STARCAT}
  else
      echo "Can't find directory /${!i}/${!j}"; 
      exit 1;
  fi
  i=$(( ${i} + 2 ))
  j=$(( ${j} + 2 ))
  k=$(( ${k} + 1 ))
done


##
## Here the main script starts:
##
DIR=`pwd`

ALLMISS=""
l=0
while [ ${l} -le ${NCHIPSMAX} ]
do
  ALLMISS="${ALLMISS}${l}"
  l=$(( ${l} + 1 ))
done

# all processing is performed in the 'first' image directory in
# a astrom_photom_scamp subdirectory:
cd /$1/$2/

test -d "astrom_photom_scamp_${STARCAT}" && rm -rf astrom_photom_scamp_${STARCAT}

mkdir -p astrom_photom_scamp_${STARCAT}/cat
mkdir astrom_photom_scamp_${STARCAT}/headers
mkdir astrom_photom_scamp_${STARCAT}/plots

cd astrom_photom_scamp_${STARCAT}/cat

# filter input catalogues to reject bad objects
i=1
j=2
l=1
NCATS=0

while [ ${l} -le ${NDIRS} ]
do 
  FILES=`${P_FIND} /${!i}/${!j}/cat_scamp/ -maxdepth 1 -name \*.cat`

  for CAT in ${FILES}
  do
    NCATS=$(( ${NCATS} + 1 ))

    BASE=`basename ${CAT} .cat`

    INSTRUM=`${P_LDACTOASC} -i ${CAT} \
                            -t LDAC_IMHEAD -s |\
             fold | grep INSTRUM | ${P_GAWK} '{print $3}'`

    # we filter away flagged objects except THOSE which are saturated!
    # we also require a minimum size (semi minor axis) of two pixels

    case ${INSTRUM} in
	"MEGAPRIME" | "'MEGAPRIME'" )
	    ${P_LDACFILTER} -i ${CAT} -t LDAC_OBJECTS \
		-c "(((FLAGS<2))AND(B_IMAGE>1.2));" \
		-o ${BASE}.ldac
	    ;;
	"SUBARU" | "'SUBARU'" )
            #adam: might want (IMAFLAGS_ISO<1)or (B_IMAGE>1.0) or (FLAGS<1)
            #adam-old# -c "((((FLAGS<20))AND(B_IMAGE>1.2))AND(IMAFLAGS_ISO<97));" \
	    ${P_LDACFILTER} -i ${CAT} -t LDAC_OBJECTS \
                -c "(((FLAGS<8)AND(B_IMAGE>0.8))AND((IMAFLAGS_ISO=0)OR(IMAFLAGS_ISO=2)));" \
		-o ${BASE}.ldac
	    ;;
	* )
	    ${P_LDACFILTER} -i ${CAT} -t LDAC_OBJECTS \
		-c "(((FLAGS<20))AND(B_IMAGE>1.0));" \
		-o ${BASE}.ldac
	    ;;
    esac


    # The following two arrays are necessary to put headers
    # to the correct directories lateron.
    CATBASE[${NCATS}]=`echo ${BASE} | perl -e '<STDIN> =~ /(.+_\d+)/; print "$1\n";'`
    CATDIR[${NCATS}]=/${!i}/${!j}
  done
  i=$(( ${i} + 2 ))
  j=$(( ${j} + 2 ))
  l=$(( ${l} + 1 ))
done

# from our single chip catalogues create merged MEF catalogues
# for each exposure:
# first get the basenames of all available exposures.
# The following fiddling is necessary because catalogues
# for individual chips might not be present (bad chips)

ALLIMAGES=""

j=1
k=2
m=1
while [ ${m} -le ${NDIRS} ]
do 
	curdir=/${!j}/${!k}/
	# The following 'awk' construct cuts away everything after 
	# the last '_' in the image names (including the underscore itself);
	# we implicitely assume that the image extension DOES NOT contain
	# '_'s.
	IMAGES=`${P_FIND} ${curdir} -maxdepth 1 -name \*.fits -exec basename {} \; |\
	    ${P_GAWK} '{ n = split($1, a, "_"); 
	                 name=""; 
	                 for(i = 1; i < (n-1); i++) 
	                 {
	                   name = name a[i] "_"
	                 } 
	                 name = name a[n-1]; 
	                 print name;}' | sort | uniq`
	image1=`\ls -1 ${curdir}/SUPA*_1OCF*.fits | head -n 1`
	path_supa_chip_ending=(`~/wtgpipeline/adam_quicktools_fast_get_path_supa_chip_ending.py ${image1}`)
	ending=${path_supa_chip_ending[3]}
	# now the merging with a pyfits-based Python script:
	for IMAGE in ${IMAGES}
	do
		# If an old scamp catalogue exists the python call below
		# would fail!
		test -f ./${IMAGE}_scamp.cat && rm -f ./${IMAGE}_scamp.cat
		i=1
		CATS=""
		echo "ADAMLOG: IMAGE=$IMAGE and CATS=$CATS "
		MISSCHIP=0     # contains the missing chips in the form of a pasted
		# string. If e. g. chips 19 and 25 are bad the variable
		# would contain 01925 (read 0_19_25; '0' is always at
		# the beginning)
		while [ ${i} -le ${NCHIPS} ]
		do
			# The following test for an image implicitely assumes that the
			# image ending does NOT start with a number: obvious but I mention
			# it just in case ....
			# It is necessary as we allow for images with different endings in the 
			# image directories:
			ocat=`\ls ${IMAGE}_${i}${ending}.ldac`
			if [ ! -f "${IMAGE}_${i}${ending}.ldac" ]; then
				ocat=`\ls ${IMAGE}_${i}[!0-9]*.ldac`
			fi
			if [ -f "${ocat}" ]; then
			    #CATS="${CATS} `echo ${IMAGE}_${i}[!0-9]*.ldac`"
			    CATS="${CATS} `\ls ${ocat}`"
			    echo "ADAMLOG: IMAGE=$IMAGE and CATS=$CATS "
			else
			    MISSCHIP=${MISSCHIP}${i}
			fi
			# not R.fits either?
			#adam-old# oimage=`${P_FIND} ${curdir} -maxdepth 1 -name ${IMAGE}_${i}[!0-9]*.fits | awk '{if($1!~"sub.fits" && $1!~"I.fits" && $1!~"R.fits" ) print $0}'`
			#adam-old# oimage=`${P_FIND} ${curdir} -maxdepth 1 -name ${IMAGE}_${i}[!0-9]*.fits | awk '{if($1!~"sub.fits" && $1!~"I.fits" ) print $0}'`
			oimage=`${P_FIND} ${curdir} -maxdepth 1 -name ${IMAGE}_${i}[!0-9]*.fits | awk '{if($1!~"sub.fits") print $0}'`
			if [ -n "${oimage}" ]; then
			    #ROTATION=`dfits "${oimage}" | fitsort ROTATION | awk '($1!="FILE") {print $2}'`
			    #CONFIG=`dfits "${oimage}" | fitsort CONFIG | awk '($1!="FILE") {print $2}'`
			    #INSTRUM=`dfits "${oimage}" | fitsort INSTRUM | awk '($1!="FILE") {print $2}'`
			    ROTATION=`dfits ${oimage} | fitsort ROTATION | awk '($1!="FILE") {print $2}'`
			    CONFIG=`dfits ${oimage} | fitsort CONFIG | awk '($1!="FILE") {print $2}'`
			    INSTRUM=`dfits ${oimage} | fitsort INSTRUM | awk '($1!="FILE") {print $2}'`
			    
			    if [ "${ROTATION}" == "KEY_N/A" ]; then
			        ROTATION=0
			    fi
			    
			    if [ "${INSTRUM}" = "KEY_N/A" ]; then
			        INSTRUM=${INSTRUMENT:?}
			    fi

			fi
			i=$(( ${i} + 1 ))
		done
		#TO BE CALLED ON EACH IMAGE
		if [ "${MISSCHIP}" == "${ALLMISS}" ]; then
			continue
		fi
		ALLIMAGES="${ALLIMAGES} ${IMAGE}"
		#python ${S_SCAMPCAT} ${CATS} ./${IMAGE}_scamp.cat
		echo "${CATS} ./${IMAGE}_scamp.cat" >> ${DIR}/catlist.txt_$$
		# Dummy external header containing focal plane and missing 
		# chip information.
		# They are used to distinguish different chip configurations
		# in an, otherwise, unique astrometric conetxt.
		test -f ./${IMAGE}_scamp.ahead && rm -f ./${IMAGE}_scamp.ahead
		i=1
		while [ ${i} -le ${NCHIPS} ]
		do
			ocat=`\ls ${IMAGE}_${i}${ending}.ldac`
			if [ ! -f "${IMAGE}_${i}${ending}.ldac" ]; then
				ocat=`\ls ${IMAGE}_${i}[!0-9]*.ldac`
			fi
			if [ -f "${ocat}" ]; then
			  if [ ${INSTRUM} == "SUBARU" ]; then
			     AHEADFILE=${DIR}/${INSTRUM}_c${CONFIG}_r${ROTATION}.ahead
			  else
			     AHEADFILE=${DIR}/${INSTRUM}.ahead
			  fi
			  if [ -f "${AHEADFILE}" ]; then
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
				       }' ${AHEADFILE} >> ${IMAGE}_scamp.ahead

			    echo "${IMAGE} ${AHEADFILE}" >> aheadfiles.txt
			  fi
			  echo "MISSCHIP= '${MISSCHIP}'" >> ./${IMAGE}_scamp.ahead
			  echo "END      "               >> ./${IMAGE}_scamp.ahead
			fi
			i=$(( ${i} + 1 ))
		done
	done
	j=$(( ${j} + 2 ))
	k=$(( ${k} + 2 ))
	m=$(( ${m} + 1 ))
done

#/nfs/slac/g/ki/ki05/anja/MEGAPRIME/software/THELI/ldacpipeline-0.12.33/scripts/Linux_64/scampcat.py: merge single frame THELI files to a scamp MEF catalogue                                     
#merges individual chip cats BASE_${i}${ending}.ldac to BASE_scamp.cat

#adam-new# now using ldac_cat_aper_splitter.py to split MAG_APER/FLUX_APER vectors into 6 scalars MAG_APER[0-5]/FLUX_APER[0-5], most useful is MAG_APER1/FLUX_APER1
cd ~/wtgpipeline
./ldac_cat_aper_splitter.py ${cluster} ${STARCAT}
cd /$1/$2/astrom_photom_scamp_${STARCAT}/cat
##adam: changing to a different version of scampcat.py, because the one in ${S_SCAMPCAT} uses pyfits
python ${S_SCAMPCAT} ${DIR}/catlist.txt_$$
##newer version of scampcat.py here: /u/ki/anja/THELI_DECam_pipeline/ldacpipeline/scripts/Linux_64/scampcat.py
#adam-tmp# python /u/ki/awright/wtgpipeline/scampcat.py ${DIR}/catlist.txt_$$

exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	echo "adam-Error: something wrong with python scamp call. Checkout ${DIR}/catlist.txt_$$"
	exit ${exit_stat};
fi

# now call scamp:
cd ../headers

if [ -f "${DIR}/${INSTRUM-${INSTRUMENT}}_c${CONFIG-""}_r${ROTATION-0}.ahead" ]; then
  MOSAICTYPE="-MOSAIC_TYPE FIX_FOCALPLANE"
else
  MOSAICTYPE="-MOSAIC_TYPE UNCHANGED"
fi
MOSAICTYPE="-MOSAIC_TYPE FIX_FOCALPLANE"
#MOSAICTYPE="-MOSAIC_TYPE UNCHANGED"
#MOSAICTYPE="-MOSAIC_TYPE LOOSE"
echo "MOSAICTYPE=" $MOSAICTYPE

PHOTFLUXKEY="FLUX_AUTO"
PHOTFLUXERRKEY="FLUXERR_AUTO"
#adam-tmp# PHOTFLUXKEY="FLUX_APER1"
#adam-tmp# PHOTFLUXERRKEY="FLUXERR_APER1"
#adam-SHNT#	        -ASTREFMAG_KEY iMeanApMag \
#adam-SHNT# 	        -ASTREFMAGERR_KEY iMeanApMagErr "
## scamp mode settings
scamp_mode_instrum_star="-STABILITY_TYPE INSTRUMENT -ASTREF_CATALOG ${STARCAT} " #default
scamp_mode_exp_star="-STABILITY_TYPE EXPOSURE -ASTREF_CATALOG ${STARCAT} "
scamp_mode_instrum_ref="-STABILITY_TYPE INSTRUMENT -ASTREF_CATALOG FILE -ASTREFCENT_KEYS X_WORLD,Y_WORLD -ASTREFERR_KEYS ERRA_WORLD,ERRB_WORLD,ERRTHETA_WORLD -ASTREFMAG_KEY MAG_AUTO "
scamp_mode_exp_ref="-STABILITY_TYPE EXPOSURE -ASTREF_CATALOG FILE -ASTREFCENT_KEYS X_WORLD,Y_WORLD -ASTREFERR_KEYS ERRA_WORLD,ERRB_WORLD,ERRTHETA_WORLD -ASTREFMAG_KEY MAG_AUTO "
if [ "${STARCAT}" == "PANSTARRS" ]; then
	cp /nfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}/panstarrs_cats/astrefcat.cat .
	scamp_mode_instrum_ref="-STABILITY_TYPE INSTRUMENT \
	        -ASTREF_CATALOG FILE \
	        -ASTREFCAT_NAME astrefcat.cat \
	        -ASTREFCENT_KEYS raMean,decMean \
	        -ASTREFERR_KEYS raMeanErr,decMeanErr \
	        -ASTREFMAG_LIMITS 13,30 \
	        -ASTREFMAG_KEY iMeanKronMag \
	        -ASTREFMAGERR_KEY iMeanKronMagErr "
	#adam: "iMeanPSFMag","iMeanPSFMagErr","iMeanKronMag","iMeanKronMagErr","iMeanApMag","iMeanApMagErr"
	scamp_mode_use=${scamp_mode_instrum_ref}
else
	# really very little difference when changing "-ASTREF_WEIGHT 1" to "-ASTREF_WEIGHT 10", so ignore this
	scamp_mode_use=${scamp_mode_instrum_star} #default
fi
#adam-IMPORTANT# If BACKMASK images look like crap, then I should first try out scamp_mode_use=${scamp_mode_exp_star}
#adam-IMPORTANT# If still bad, then make a coadd.fits with only the good looking exposures, make a refcat from this, and use scamp_mode_use=${scamp_mode_exp_ref}

#MACS0416# adam: for more info on making an external reference catalog to match against, checkout: /nfs/slac/kipac/fs1/u/awright/might_need_later/compare_astrom_offsets/coadd_W-C-RC_only_5_good_ims
#MACS0416# scamp_mode_use=${scamp_mode_exp_ref}
#MACS0416# echo "copying good5 cat to " ${PWD}
#MACS0416# if [ ! -f "astrefcat.cat" ]; then
#MACS0416# 	cp /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/MACS0416-24_W-C-RC_only_5_good_ims_final.cat ./astrefcat.cat
#MACS0416# fi

echo "scamp_mode_use=" $scamp_mode_use

## RUN SCAMP
posangle=1.0                                                                                                                                                                          
position=1.0
pixscale=1.003

#adam-look# these keys (FLUX_APER1 FLUXERR_APER1 MAG_APER1 MAGERR_APER1) were added (among others) using ./ldac_cat_aper_splitter.py 
#adam-look# I've changed these keys to ensure we're using APERATURE MAGS in create_scamp_astrom_photom.sh: "-PHOTFLUX_KEY FLUX_APER1 -PHOTFLUXERR_KEY FLUXERR_APER1 "

#adam-SHNT# early indications that FLUX_APER more reliable than FLUX_AUTO, so I'm switching to "-PHOTFLUX_KEY FLUX_APER1 -PHOTFLUXERR_KEY FLUXERR_APER1 "
${P_SCAMP} `${P_FIND} ../cat/ -name \*scamp.cat` \
        -c ${CONF}/scamp_astrom_photom.scamp \
        -ASTRINSTRU_KEY FILTER,INSTRUM,CONFIG,ROTATION,MISSCHIP,PPRUN \
	-PHOTFLUX_KEY ${PHOTFLUXKEY} -PHOTFLUXERR_KEY ${PHOTFLUXERRKEY} \
        -CDSCLIENT_EXEC ${P_ACLIENT} \
        -NTHREADS ${NPARA} ${MOSAICTYPE} \
        -XML_NAME ${cluster}_scamp.xml \
        -MAGZERO_INTERR 0.1 \
        -MAGZERO_REFERR 0.03 \
        -POSITION_MAXERR ${position} \
        -POSANGLE_MAXERR ${posangle} \
        -PIXSCALE_MAXERR ${pixscale} \
        -SN_THRESHOLDS 3,100 \
        -MATCH Y \
        -MATCH_NMAX 10000 \
        -MATCH_RESOL 0.0 \
        -CROSSID_RADIUS 0.3 \
        -DISTORT_DEGREES 3 \
        -FLAGS_MASK 0x00e0 \
        -ASTREF_WEIGHT 1 ${scamp_mode_use} -CHECKPLOT_RES 4000,3000

#-POSITION_MAXERR 1.0 -POSANGLE_MAXERR 0.05 -PIXSCALE_MAXERR 1.03
#starcat#           -ASTREF_CATALOG ${STARCAT} \
#refcat#           -ASTREF_CATALOG FILE \
#refcat#           -ASTREFCENT_KEYS X_WORLD,Y_WORLD \
#refcat#           -ASTREFERR_KEYS ERRA_WORLD,ERRB_WORLD,ERRTHETA_WORLD \
#refcat#           -ASTREFMAG_KEY MAG_AUTO \

#refcat_scamp_call# ${P_SCAMP} `${P_FIND} ../cat/ -name \*scamp.cat` \
#refcat_scamp_call#         -c ${CONF}/scamp_astrom_photom.scamp \
#refcat_scamp_call#         -ASTRINSTRU_KEY FILTER,INSTRUM,CONFIG,ROTATION,MISSCHIP,PPRUN \
#refcat_scamp_call#         -CDSCLIENT_EXEC ${P_ACLIENT} \
#refcat_scamp_call#         -NTHREADS ${NPARA} ${MOSAICTYPE} \
#refcat_scamp_call#         -XML_NAME ${cluster}_scamp.xml \
#refcat_scamp_call#         -MAGZERO_INTERR 0.1 \
#refcat_scamp_call#         -MAGZERO_REFERR 0.1 \
#refcat_scamp_call#         -POSITION_MAXERR 5.0 \
#refcat_scamp_call#         -POSANGLE_MAXERR 30.0 \
#refcat_scamp_call#         -SN_THRESHOLDS 3,100 \
#refcat_scamp_call#         -FLAGS_MASK 0x00e0 \
#refcat_scamp_call#         -MATCH_NMAX 10000 \
#refcat_scamp_call#         -CROSSID_RADIUS 0.3 \
#refcat_scamp_call#         -PIXSCALE_MAXERR 1.03 \
#refcat_scamp_call#         -STABILITY_TYPE EXPOSURE \
#refcat_scamp_call#         -DISTORT_DEGREES 3 \
#refcat_scamp_call#         -ASTREF_CATALOG FILE \
#refcat_scamp_call#         -ASTREFCENT_KEYS X_WORLD,Y_WORLD \
#refcat_scamp_call#         -ASTREFERR_KEYS ERRA_WORLD,ERRB_WORLD,ERRTHETA_WORLD \
#refcat_scamp_call#         -ASTREFMAG_KEY MAG_AUTO \
#refcat_scamp_call#         -ASTREF_WEIGHT 1

#scamp_doesnt_recognize# -ASTREF_CATNAME /nfs/slac/g/ki/ki18/anja/SUBARU/compare_astrom_offsets/coadd_W-C-RC_only_5_good_ims/good5_W-C-RC_final.cat \
#  so instead I copy this cat to the current dir with default name: astrefcat.cat
#scamp_doesnt_recognize# -ASTREFMAGERR_KEY MAGERR_AUTO


#adam-tmp# this is the standard operating procedure, remove all of the #usual_scamp_call# stuff before the next cluster 
#usual_scamp_call# ${P_SCAMP} `${P_FIND} ../cat/ -name \*scamp.cat` \
#usual_scamp_call#            -c ${CONF}/scamp_astrom_photom.scamp \
#usual_scamp_call#            -ASTRINSTRU_KEY FILTER,INSTRUM,CONFIG,ROTATION,MISSCHIP,PPRUN \
#usual_scamp_call#            -CDSCLIENT_EXEC ${P_ACLIENT} \
#usual_scamp_call#            -ASTREF_CATALOG ${STARCAT} \
#usual_scamp_call#            -NTHREADS ${NPARA} ${MOSAICTYPE} \
#usual_scamp_call#            -XML_NAME ${cluster}_scamp.xml \
#usual_scamp_call#            -MAGZERO_INTERR 0.1 \
#usual_scamp_call#            -MAGZERO_REFERR 0.1 \
#usual_scamp_call#            -POSITION_MAXERR 5.0 \
#usual_scamp_call#            -POSANGLE_MAXERR 30.0 \
#usual_scamp_call#            -SN_THRESHOLDS 3,100 \
#usual_scamp_call#            -FLAGS_MASK 0x00e0 \
#usual_scamp_call#            -MATCH_NMAX 10000 \
#usual_scamp_call#            -CROSSID_RADIUS 0.3 \
#usual_scamp_call#            -PIXSCALE_MAXERR 1.03 \
#usual_scamp_call#            -STABILITY_TYPE INSTRUMENT \
#usual_scamp_call#            -DISTORT_DEGREES 3

#adam_scamp_comments# THESE ARE THE NOTES I'VE ASSEMBLED WHILE TRYING TO FIX SCAMP ISSUES FOR MACS0416-24:
#adam_scamp_comments# NOTE: If I was going to try fixing these issues again, first I would look at/run the stuff in #old_scamp_comments# and the stuff in create_scamp_astrom_astrom_photom.sh FIRST, who knows, they might actually be there for a reason!
#adam_scamp_comments# 	THEN i would try out the suggestions below
#adam_scamp_comments# #orig#           -CROSSID_RADIUS 0.2 \
#adam_scamp_comments# #orig#           -PIXSCALE_MAXERR 1.02 \
#adam_scamp_comments# #def#           -CROSSID_RADIUS 2.0 \
#adam_scamp_comments# #def#           -PIXSCALE_MAXERR 1.20 \
#adam_scamp_comments# 
#adam_scamp_comments# # might want to try: ASTREF_WEIGHT change?
#adam_scamp_comments# # might want to try: ASTREF_CATALOG=USNO-B1 or ASTREF_BAND=REDDEST
#adam_scamp_comments# # might want to try: DISTORT_KEYS           X_IMAGE,Y_IMAGE,:AIRMASS
#adam_scamp_comments# # might want to try: MOSAIC_TYPE change?
#adam_scamp_comments# # might want to try: CROSSID_RADIUS or PIXSCALE_MAXERR or POSANGLE_MAXERR change?
#adam_scamp_comments# 
#adam_scamp_comments# #would like to know which detections are matched, also which MATCH_RESOL is chosen, might need to change these keys to get info:
#adam_scamp_comments# #HEADER_TYPE            NORMAL          # NORMAL or FOCAL_PLANE
#adam_scamp_comments# #VERBOSE_TYPE           NORMAL          # QUIET, NORMAL, LOG or FULL
#adam_scamp_comments# #FULLOUTCAT_TYPE
#adam_scamp_comments# #MERGEDOUTCAT_TYPE
#adam_scamp_comments# 
#adam_scamp_comments# #adam-tried# let's try changing the scamp poly degree to 4 (usually it's 3)
#adam_scamp_comments# #adam-tried# let's try changing the scamp poly degree to 2 (usually it's 3)

#old_scamp_comments# echo "${P_SCAMP} `${P_FIND} ../cat/ -name \*scamp.cat` \
#old_scamp_comments#            -c ${CONF}/scamp_astrom_photom.scamp \
#old_scamp_comments#            -ASTRINSTRU_KEY FILTER,INSTRUM,CONFIG,ROTATION,MISSCHIP \
#old_scamp_comments#            -CDSCLIENT_EXEC ${P_ACLIENT} \
#old_scamp_comments#            -ASTREF_CATALOG ${STARCAT} \
#old_scamp_comments#            -NTHREADS ${NPARA} ${MOSAICTYPE} \
#old_scamp_comments#            -XML_NAME ${cluster}_scamp.xml \
#old_scamp_comments#            -POSITION_MAXERR 5.0 \
#old_scamp_comments#            -SN_THRESHOLDS 20,100 "
#old_scamp_comments# 
#old_scamp_comments# #           -c ${CONF}/scamp_astrom_photom.scamp \
#old_scamp_comments# #           -MATCH_NMAX 10000 \
#old_scamp_comments# #           -CROSSID_RADIUS 0.2 \
#old_scamp_comments# #           -PIXSCALE_MAXERR 1.05 \
#old_scamp_comments# #           -POSANGLE_MAXERR 0.4 \
#old_scamp_comments# #           -SN_THRESHOLDS 1,100 \
#old_scamp_comments# #           -DISTORT_DEGREES 3

if [ $? -ne 0 ]
then
    echo "scamp call failed !! Exiting !!"
    cleanTmpFiles
    exit 1
fi

# scamp creates the headers in the directory where the catalogs are:
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
mv astr_refsysmap*  ../plots
mv phot_zpcorr*     ../plots
mv phot_errorvsmag* ../plots
mv ${cluster}_scamp.xml ../plots
cp ~/wtgpipeline/scamp.xsl ../plots
sed -i.old 's/href=".*"?>/href="scamp.xsl"?>/g' ../plots/${cluster}_scamp.xml

# now get the relative magnitude offsets from the FLXSCALES
# estimated by scamp:
test -f photdata.txt_$$ && rm -f photdata.txt_$$

# Because the flux scales refer to an image normalised to one
# second we need to obtain the exposure times of all frames
# first. We also get the SCAMP flux scale and the photometric 
# instrument:
for IMAGE in ${ALLIMAGES}
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

# The following 'awk' script calculates relative zeropoints 
# and THELI fluxscales for the different photometric contexts: 
${P_GAWK} 'BEGIN {maxphotinst = 1;}
           { name[NR] = $1; 
             exptime[NR] = $2; 
             flxscale_scamp[NR] = $3;
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
               flxscale_theli[i] = (10**(-0.4*relzp[i]))/exptime[i];
               printf("%s %f %e\n", 
                 name[i], relzp[i], flxscale_theli[i]);  
             }
           }' photdata.txt_$$ > photdata_relzp.txt_$$

# now split the exposure catalogues for the indivudual chips
# and add the RZP and FLXSCALE header keywords. Put the headers 
# into appropriate headers_scamp directories
#
while read NAME RELZP FLXSCALE
do
    i=1
    j=1  # counts the actually available chips!
    while [ ${i} -le ${NCHIPS} ]
    do
        # we need to take care of catalogs that may not be
        # present (bad chips)!
        ocat=`\ls ../cat/${NAME}_${i}${ending}.ldac`
        if [ ! -f "${ocat}" ]; then
            ocat=`\ls ../cat/${NAME}_${i}[!0-9]*.ldac`
    	ocat_mode=2
        else
    	ocat_mode=1
        fi
        if [ -f "${ocat}" ]; then
            if [ ${ocat_mode} -eq 1 ]; then
                headername=`basename ../cat/${NAME}_${i}${ending}.ldac .ldac | perl -e '<STDIN> =~ /(.+_\d+)/; print "$1\n";'`
            elif [ ${ocat_mode} -eq 2 ]; then
                headername=`basename ../cat/${NAME}_${i}[!0-9]*.ldac .ldac | perl -e '<STDIN> =~ /(.+_\d+)/; print "$1\n";'`
            fi
            # first rename the SCAMP header keyword FLXSCALE
            # to FLSCALE. We need FLXSCALE for the THELI
            # flux scaling later:
            sed -e 's/FLXSCALE/FLSCALE /' ${NAME}_scamp.head |\
            ${P_GAWK} 'BEGIN {ext = '${j}'; nend = 0}
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
                             printf("FLXSCALE= %20E / THELI relative flux scale\n",
                                    '${FLXSCALE}');
                         printf("END\n")
                       }' > ${headername}.head
            j=$(( $j + 1 ))
        fi
        i=$(( $i + 1 ))
    done
done < photdata_relzp.txt_$$

i=1
while [ ${i} -le ${NCATS} ]
do
  if [ -f "${CATBASE[$i]}.head" ]; then
    mv ${CATBASE[$i]}*head ${CATDIR[$i]}/headers_scamp_${STARCAT}
    exit_stat=$?
    if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
    fi
  fi
  
  i=$(( ${i} + 1 )) 
done

# clean up temporary files and bye
cleanTmpFiles

#adam-tmp#

cd ${DIR}
#log_status $exit_status
exit $exit_stat
