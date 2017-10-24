#!/bin/bash -u

# -----------------------------------------------------------------------
# File Name:           create_scamp_astrom_photom_multiinst.sh
# Author:              Thomas Erben (terben@astro.uni-bonn.de)
# Last modified on:    31.07.2016
# Description:         Performs astrometric and relative photometric
#                      calibration of THELI sets with scamp V1.19.0
# -----------------------------------------------------------------------

# Script history information:

# 21.06.2015:
# Project started with the script create_scamp_astrom_photom.sh
# as a template.
#
# 22.06.2015:
# Bug fix in case that not all instruments have an ahead file available.
#
# 21.08.2015:
# - I extended the script to be able to have different Focal-plane
#   files for individual runs. We hope to obtain better astrometry
#   results for OMEGACAM when obviously instrument setup can change
#   between observing runs.
# - Bug fix in the creation of the final header files on chip-basis.
#   It could happen that the estimation of relative zeropoints was not
#   correct (scamp relative fluxes happened to not be constant within an
#   exposure; I do not know why this can happen - TO BE INVESTIGATED!)
#
# 16.05.2016:
# I corrected a major bug that prevented the script from working
# correctly if images with different image endings were processed.
#
# 28.07.2016:
# The variable P_PYTHON was changed to P_PYTHON3 (pipeline upgrade to python 3)
#
# 31.07.2016:
# I simplified deletion of temporary files (function cleanTmpFiles)

# File inclusions:
. ./${INSTRUMENT:?}.ini
. ./bash_functions.include
theli_start "$*"

# define THELI_DEBUG and some other variables because of the '-u'
# script flag (the use of undefined variables will be treated as
# errors!)  THELI_DEBUG is used in the cleanTmpFiles function.
#
THELI_DEBUG=${THELI_DEBUG:-""}
P_SCAMP=${P_SCAMP:-""}
P_ACLIENT=${P_ACLIENT:-""}
DIR=${DIR:-""}

##
## function definitions:
##
function printUsage
{
  echo "SCRIPT NAME:"
  echo "    create_scamp_astrom_photom_multiinst.sh"
  echo ""
  echo "ARGUMENTS:"
  echo "    -i INSTRUMENT"
  echo "    -d MD SD ENDING"
  echo "    -p POSITION_INACCURACY        (arcmin; default: 2.0)"
  echo "    -c ASTROM_CATALOG             (default: 2MASS)"
  echo "    -m all/astrom/photom MODE     (default: all)"
  echo "    -k LONG/SHORT exposed data    (default: LONG)"
  echo ""
  echo "    An arbitrary number of blocks '-i' and '-d' blocks can be given."
  echo "    (MD=main directory, SD=science directory, ENDING=image ending). If"
  echo "    no instrument '-i' is given the instrument set in the environment"
  echo "    (variable INSTRUMENT) is used. A '-i' instrument is valid for"
  echo "    all following '-d' data blocks. Hence, data from several"
  echo "    instruments can be calibrated simultaneously!"
  echo ""
  echo "    The 'max. positional offset' is an estimate of the initial maximum"
  echo "    linear offset of the data to the standardstar catalogue."
  echo ""
  echo "    SHORT data kind should be set for very short exposed data which"
  echo "    can have 20 or less objects per chip (e.g. short exposed u-band"
  echo "    data)."
  echo " "
  echo "    If a MODE is provided in the nth argument the script calls scamp"
  echo "    with optimised parameters for astrometry or relative"
  echo "    photometry. Omitting this argument (MODE ALL) runs scamp with"
  echo "    optimised parameters for astrometric calibration."
  echo ""
  echo "DESCRIPTION:"
  echo ""
  echo "    This script performs astrometric and relative photometric"
  echo "    calibration of THELI sets with Emanuel Bertins scamp program. The"
  echo "    current version of the script was tested mainly against"
  echo "    scamp-V1.19.0; The scamp program itself is not contained in the"
  echo "    THELI pipeline package and needs, together with 'cdsclient' and"
  echo "    the Python module 'pyfits', to be installed separately (see the"
  echo "    DEPNDENCY section below)"
  echo "    "
  echo "    The scripts results are header files in"
  echo "    \${MD}/\${SD}/headers_scamp_\${STANDARD}_\${MODE} directories (the"
  echo "    \${STANDARD} stands for the used standardstar catalogue. In case"
  echo "    of a manually created standardstar catalogue it is 'MANUAL'. the"
  echo "    MODE for the use processing mode; the MODE suffix is omitted if"
  echo "    the MODE is ALL). The resulting header files can then directly be"
  echo "    used for image co-addition. To use the scamp headers the"
  echo "    'prepare_coadd_swarp.sh' script has to be called with the '-eh"
  echo "    headers_scamp_..' option."
  echo ""
  echo "    If this script is run with MODES astrom and photom on some data set"
  echo "    the resulting headers can later be combined with the script "
  echo "    'merge_scamp_cats.sh'."
  echo "    "
  echo "    !! NOTE:"
  echo "       A call to 'create_absphotom_photometrix.sh' after this script"
  echo "       is still necessary to calculate the absolute zeropoint for a"
  echo "       coadded image "
  echo "    !!"
  echo ""
  echo "    The standardstar_catalog can be any astrometric catalogue"
  echo "    supported by scamp. If a manually created standardstar catalogue"
  echo "    (in LDAC format) should be used, provide the full, absolute path"
  echo "    to that catalogue."
  echo "         "
  echo "IMPORTANT DEPENDENCIES:"
  echo "    (1) The script calls the Python script 'scampcat.py' which creates"
  echo "        scamp MEF exposure catalogues from the individual THELI chip "
  echo "        catalogues. This Python script itself depends on pyfits."
  echo "    (2) scamp uses the configuration file 'scamp_astrom_photom.scamp'"
  echo "        which is set to define scamp astrometric contexts on the"
  echo "        basis of the FILTER and RUN keywords. "
  echo "    (3) The script checks whether files ${INSTRUMENT}.ahead are present"
  echo "        in your reduction directory. If yes, it interprets them as scamp"
  echo "        'additional' header containing 'focal plane' (first order "
  echo "        astrometric) information overriding corresponding entries in image"
  echo "        headers. In this case scamp is run with the "
  echo "        '-MOSAIC_TYPE SAME_CRVAL' option. We use '-MOSAIC_TYPE UNCHANGED' "
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
  echo ""
  echo "AUTHOR:"
  echo "    Thomas Erben (terben@astro.uni-bonn.de)"
  echo ""
}


function cleanTmpFiles
{
  if [ -z ${THELI_DEBUG} ]; then
    echo "Cleaning temporary files for script $0"
    for FILE in ${TEMPDIR}/*_$$
    do
      test -f ${FILE} && rm ${FILE}
    done
  else
    echo "Variable THELI_DEBUG set! No cleaning of temp. files in script $0"
  fi
}

# Handling of program interruption by CRTL-C
trap "echo 'Script $0 interrupted!! Cleaning up and exiting!'; \
      cleanTmpFiles; exit 1" INT

# declarea associateive bash arrays:
declare -A NCHIPS_FROM_INSTRU
declare -A INSTRU_FROM_DIR
declare -A ENDING
declare -A DIR_FROM_EXPOSURE
declare -A RUN_FROM_EXPOSURE
declare -A AHEAD_FROM_RUN

# give default values to crucial parameters
NCHIPS_FROM_INSTRU[${INSTRUMENT}]=${NCHIPS}
POSMAXERR=2.0 # maximum position uncertainty in arcmin
MODE=all      # processing mode (ASTROM, PHOTOM or all)
DATAKIND=LONG # LONG or SHORT esposed data
PROCESSDIR=""
STARCAT=2MASS
POSQUAN=""    # set in the main part of the script below

# read command line argumetns:
while [ $# -gt 0 ]
do
   case $1 in
   -d)
       if [ ! -d $2/$3/cat ]; then
         theli_error "Directory $2/$3/cat does not exist! Exiting!"
         exit 1;
       fi      
       INSTRU_FROM_DIR[$2/$3]=${INSTRUMENT}
       ENDING[$2/$3]=$4
       if [ "${PROCESSDIR}" = "" ]; then
         PROCESSDIR="$2/$3"  
       fi
       shift 4
       ;;
   -h)
       printUsage
       shift
       exit 0;
       ;;
   -i)
       export INSTRUMENT=${2}
       . ./${INSTRUMENT}.ini
       NCHIPS_FROM_INSTRU[${INSTRUMENT}]=${NCHIPS}
       shift 2
       ;;
   -m)
       MODE=${2}
       shift 2
       ;;
   -k)
       DATAKIND=${2}
       shift 2
       ;;
   -p)
       POSMAXERR=${2}
       shift 2
       ;;
   -c)
       STARCAT=${2}
       shift 2
       ;;
    *)
       # there might be an 'empty string' argument which we
       # can ignore:
       if [ ! -z "$1" ]; then
         theli_error "Unknown command line option: ${1}"    
         exit 1;
       else
         shift  
       fi
       ;;
   esac
done


##
## initial sanity checks
##

# check whether we need to do something at all:
if [ ${#INSTRU_FROM_DIR[@]} -eq 0 ]; then
  theli_error "No data directories given! Nothing to do!"
  exit 1;
fi

# check whether we have the external 'scamp' and 'aclient' programs at all:
if [ -z ${P_SCAMP} ] || [ -z ${P_ACLIENT} ]
then
  theli_error "You need the external 'scamp' AND 'aclient' programs to"
  theli_error "use this script! The necessary variable(s) in"
  theli_error "your progs.ini seem(s) not to be set! Exiting!!"
  exit 1;
fi

if [ "${MODE}" != "all" ] && [ "${MODE}" != "astrom" ] && \
   [ "${MODE}" != "photom" ]; then
  printUsage
  exit 1
fi

# the SUFFIX for directory names. If we have a user provided astrometric
# standard star catalogue the sufix is 'MANUAL'. Otherwise it is the
# name of the standard star catalogue.
SUFFIX=${STARCAT}
if [ -f ${STARCAT} ]; then
  SUFFIX=MANUAL
fi

if [ "${MODE}" != "all" ]; then
  SUFFIX=${SUFFIX}_${MODE}
fi

# The location of the reduction directory; we need it to have
# a reference to it below:
REDUCEDIR=`pwd`

# Test existence of image directory(ies) and create headers_scamp
# directories:
for DIR in "${!INSTRU_FROM_DIR[@]}"
do
  if [ -d ${DIR}/cat ]; then
    if [ -d ${DIR}/headers_scamp_${SUFFIX} ]; then
      theli_message "deleting old ${DIR}/headers_scamp_${SUFFIX}"
      rm -rf ${DIR}/headers_scamp_${SUFFIX}
    fi
    mkdir ${DIR}/headers_scamp_${SUFFIX}
  else
    theli_message "Can't find directory ${DIR}/cat";
    exit 1;
  fi  
done

##
## Here the main script starts:
##

# all processing is performed in the PROCESSDIR in
# a astrom_photom_scamp_${MODE} subdirectory:
cd ${PROCESSDIR}

if [ -d astrom_photom_scamp_${SUFFIX} ]; then
  theli_message "deleting old ${PROCESSDIR}/astrom_photom_scamp_${SUFFIX}"
  rm -rf ./astrom_photom_scamp_${SUFFIX}
fi

mkdir -p astrom_photom_scamp_${SUFFIX}/cat
mkdir astrom_photom_scamp_${SUFFIX}/headers
mkdir astrom_photom_scamp_${SUFFIX}/plots

cd astrom_photom_scamp_${SUFFIX}/cat

# filter input catalogues to reject bad objects
test -f ${TEMPDIR}/allscampfiles.txt_$$ && rm ${TEMPDIR}/allscampfiles.txt_$$
AHEAD=1 # we assume that we have ahead files for all instruments.
        # The variable is modified within the following loop if
        # this is not the case!

for DIR in "${!INSTRU_FROM_DIR[@]}"
do
  ${P_FIND} ${DIR}/cat/ -maxdepth 1 -name \*${ENDING[${DIR}]}.cat > \
    ${TEMPDIR}/files.txt_$$

  # do we need to do something for this directory at all?
  if [ -s ${TEMPDIR}/files.txt_$$ ]; then
    # we need to determine whether we need to use 'normal' or 'windowed'
    # object quantities in scamp. Newer versions of THELI should use
    # windowed but we still want to be able to process old catalogues:
    if [ "${POSQUAN}" = "" ]; then
      CAT=`head -1 ${TEMPDIR}/files.txt_$$`
  
      POSQUAN="UNWINDOWED"
  
      ${P_LDACTESTEXIST} -i ${CAT} -t LDAC_OBJECTS -k XWIN_IMAGE
      if [ "$?" -eq "0" ]; then
        POSQUAN="WINDOWED"
      else
        POSQUAN="UNWINDOWED"
      fi
    fi
  
    # The following 'gawk/sed' mimicking a 'filename' command is much
    # faster than performing an explicit filename command on each file
    # in the 'while' loop:
    ${P_GAWK} -F/ '{print $NF}' ${TEMPDIR}/files.txt_$$ | \
      sed -e 's/_[1-9][0-9]*'${ENDING[${DIR}]}'\.cat$//' | sort | uniq > \
      ${TEMPDIR}/tmp.txt_$$

    while read CAT
    do
      # The follwowing array is necessary to redistribute output scamp
      # headers to the correct directories lateron
      DIR_FROM_EXPOSURE[${CAT}]=${DIR}

      # We also need the run each exposure belongs to. This is necessary
      # for instruments where we have run-specific focal-plane headers:
      RUN=$(${P_LDACTOASC} -i $(grep ${CAT} ${TEMPDIR}/files.txt_$$ |\
            ${P_GAWK} '(NR==1)') -t LDAC_IMHEAD -s | fold | \
            ${P_GAWK} '($1 == "RUN") && ($2 == "=") {print $3}' | \
            sed -e "s/'//")

      if [ "${RUN}" = "" ]; then
        RUN="DUMMY_RUN"  
      fi
      RUN_FROM_EXPOSURE[${CAT}]=${RUN}
    done < ${TEMPDIR}/tmp.txt_$$

    # to be able to easily iterate over present runs:
    UNIQUE_RUNS=($(printf "%s\n" "${RUN_FROM_EXPOSURE[@]}" | sort -u))

    # we filter away flagged objects except THOSE which are saturated!
    # we also require a minimum size (semi minor axis) of two pixels
    SIZEQUAN="B_IMAGE"
    SIZEVAL="1.7"
    if [ "${POSQUAN}" = "WINDOWED" ]; then
      SIZEQUAN="BWIN_IMAGE"
      # a limit of 1.0 was too large for OMEGACAM@VST images in exceptionally
      # good seeing conditions. The new value of 0.7 is still sufficiently
      # far away from the size of cosmic rays (around 0.5)
      SIZEVAL="0.7"
    fi
  
    # create input file for 'parallel' filtering:
    ${P_GAWK} -F/ '{ tmp = $NF;
                     sub(/.cat$/, ".ldac", tmp);
                     print $0, tmp }' \
       ${TEMPDIR}/files.txt_$$ > ${TEMPDIR}/tmp.txt_$$
  
    ${P_PERL} ${S_PARALLEL} -j ${NPARA} -q --colsep ' ' \
        ${P_LDACFILTER} -i {1} -t LDAC_OBJECTS \
            -c "((FLAGS<16)AND(${SIZEQUAN}>${SIZEVAL}));" \
            -o {2} < ${TEMPDIR}/tmp.txt_$$
    
    # The aim of the next code part (up to the python call to S_SCAMPCAT)
    # is to create merged MEF catalogues for each exposures. In addition,
    # scamp ahaed files need to be created. Most of the fiddling in the
    # following is necessary because catalogues for individual chips might
    # not be present (bad chips)
  
    # First a simple list of all available individual catalogues.  Its main
    # purpose is to use it later to check whether certain catalogues are
    # present or not (The file '${TEMPDIR}/files.txt_$$' was created above).
    ${P_GAWK} -F/ '{print $NF}' ${TEMPDIR}/files.txt_$$ | \
      sed -e 's/.cat$/.ldac/' >> ${TEMPDIR}/allscampfiles.txt_$$
  
    EXPOSURES=`${P_GAWK} -F/ '{print $NF}' ${TEMPDIR}/files.txt_$$ | \
               sed -e 's/_[1-9][0-9]*'${ENDING[${DIR}]}'.cat//' | \
               sort | uniq`
  
    # Modify the initial instrument ahaed file(s) with a default 'MISSCHIP'
    # setting which should be valid for most exposures. These default
    # files are then just copied and linked for exposures following the default
    # rules (all chips of the mosaic are valid):

    # first the 'default' ahead file:
    if [ ! -f ./${INSTRU_FROM_DIR[${DIR}]}_default.ahead ]; then
      if [ -f ${REDUCEDIR}/${INSTRU_FROM_DIR[${DIR}]}.ahead ]; then
        ${P_GAWK} '{if($0 !~ /^END/) {
            print $0
          } else {
            print "MISSCHIP= '\''0'\''"; print $0;
          }}' ${REDUCEDIR}/${INSTRU_FROM_DIR[${DIR}]}.ahead > \
            ./${INSTRU_FROM_DIR[${DIR}]}_default.ahead
      else
        AHEAD=0 # we do not have a default ahead files for all instruments!  
      fi
    fi

    # bow run specific ahead files:
    for RUN in ${UNIQUE_RUNS[@]}
    do
      if [ ! -f ./${INSTRU_FROM_DIR[${DIR}]}_${RUN}.ahead ]; then
        if [ -f ${REDUCEDIR}/${INSTRU_FROM_DIR[${DIR}]}_${RUN}.ahead ]; then
          ${P_GAWK} '{if($0 !~ /^END/) {
              print $0
            } else {
              print "MISSCHIP= '\''0'\''"; print $0;
            }}' ${REDUCEDIR}/${INSTRU_FROM_DIR[${DIR}]}_${RUN}.ahead > \
              ./${INSTRU_FROM_DIR[${DIR}]}_${RUN}.ahead
          AHEAD_FROM_RUN[${RUN}]=1
        else
          AHEAD_FROM_RUN[${RUN}]=0
        fi
      fi
    done


    # The file catlist.txt_$$ is built for the python call to scampcat:
    test -f ${TEMPDIR}/catlist.txt_$$ && rm ${TEMPDIR}/catlist.txt_$$
    
    for EXPOSURE in ${EXPOSURES}
    do
      MISSCHIPSTRING=0   # contains the missing chips in the form of a
                         # pasted string. If e. g. chips 19 and 25 are
                         # bad the variable would contain 02519 (read
                         # 0_25_19; '0' is always at the beginning)
      MISSCHIPS=""       # contains missed strings, e.g. "29 15" if
                         # chips 29 and 15 are missing. The variable
                         # is needed the modify the default ahead file
                         # is necessary. Missing chips must appear in
                         # decreasing order here.
      RUN=${RUN_FROM_EXPOSURE[${EXPOSURE}]}
    
      # add the current exposure to the catalogue list to create an exposure
      # catalogue for the scamp call (python call below) and deal with missing
      # chips:
      grep "^${EXPOSURE}" ${TEMPDIR}/allscampfiles.txt_$$  | \
        ${P_GAWK} -F_ '{a = $NF; gsub(/[^0-9]/, "", a); print a, $0}' |\
        ${P_SORT} -n -k1,1 | tee ${TEMPDIR}/tmp.txt_$$ |\
        ${P_GAWK} '{printf("%s ", $2)} END {
           print "./'${EXPOSURE}'_scamp.cat"}' >> ${TEMPDIR}/catlist.txt_$$

      if [ ${AHEAD} -eq 1 ] || [ ${AHEAD_FROM_RUN[${RUN}]} -eq 1 ]; then
        MISSCHIPS="`seq 1 ${NCHIPS_FROM_INSTRU[${INSTRU_FROM_DIR[${DIR}]}]} | \
                    ${P_GAWK} '{print $1}' - ${TEMPDIR}/tmp.txt_$$ |\
                    ${P_SORT} -nr | uniq -c | awk '($1 == 1) {print $2}'`"
      
        # Dummy external header containing focal plane and missing
        # chip information.
        # They are used to distinguish different chip configurations
        # in an, otherwise, unique astrometric conetxt.
        test -f ./${EXPOSURE}_scamp.ahead && rm ./${EXPOSURE}_scamp.ahead
      
        # If there are no missing chips we just link the default (or
        # run specific) ahead file.  Otherwise we create a special
        # one:
        if [ "${MISSCHIPS}" = "" ]; then
          if [ ${AHEAD_FROM_RUN[${RUN}]} -eq 1 ]; then
            ln -s ./${INSTRU_FROM_DIR[${DIR}]}_${RUN}.ahead \
               ./${EXPOSURE}_scamp.ahead
          else  
            ln -s ./${INSTRU_FROM_DIR[${DIR}]}_default.ahead \
               ./${EXPOSURE}_scamp.ahead
          fi
        else
          for CHIP in ${MISSCHIPS}
          do
            MISSCHIPSTRING="${MISSCHIPSTRING}${CHIP}"
          done

          FILE="./${INSTRU_FROM_DIR[${DIR}]}_default.ahead"

          if [ ${AHEAD_FROM_RUN[${RUN}]} -eq 1 ]; then
            FILE="./${INSTRU_FROM_DIR[${DIR}]}_${RUN}.ahead"
          fi
          sed -e 's/MISSCHIP= '\''0'\''/MISSCHIP= '\'${MISSCHIPSTRING}\''/' \
            ${FILE} > ${TEMPDIR}/tmp.txt_$$
      
          # remove from the ahead file all sections that correspond to
          # missing chips.
          for CHIP in ${MISSCHIPS}
          do
            ${P_GAWK} 'BEGIN {chipsread = 0} {
                       if(chipsread != ('${CHIP}' - 1)) {
                         print $0;
                       }
                       if($0 ~ /^END/) {
                         chipsread++;
                       }}' ${TEMPDIR}/tmp.txt_$$ > ${TEMPDIR}/tmp1.txt_$$
            mv ${TEMPDIR}/tmp1.txt_$$ ${TEMPDIR}/tmp.txt_$$
          done
          mv ${TEMPDIR}/tmp.txt_$$ ./${EXPOSURE}_scamp.ahead
        fi
      fi
    done
    ${P_PYTHON3} ${S_SCAMPCAT} ${TEMPDIR}/catlist.txt_$$
  else # if [ -s ${TEMPDIR}/files.txt_$$ ]
    theli_warn "Nothing to do for ${DIR}! Skipping!"   
  fi
done

if [ -s ${TEMPDIR}/allscampfiles.txt_$$ ]; then
  # now call scamp:
  cd ../headers
  
  # scamp mosaic type dependent on the availability of a first order
  # astrometric solution for all(!) involved instruments:
  if [ ${AHEAD} -eq 1 ]; then
    MOSAICTYPE="-MOSAIC_TYPE SAME_CRVAL"
  else
    MOSAICTYPE="-MOSAIC_TYPE UNCHANGED"
  fi
  
  # for some reason scamp gives better results if the
  # 'ordering' of files is shuffled in time! Do not ask!
  if [ "${MODE}" != "photom" ]; then
    FILES=`${P_FIND} ../cat/ -name \*scamp.cat |\
           awk '{line[NR] = $0} END { srand();
             for (i = 1; i <= NR; i++) {
               n = int(rand() * NR) + 1;
               temp = line[i];
               line[i] = line[n];
               line[n] = temp;
             }
             for (i = 1; i <= NR; i++) {
               print line[i];
             }}'`
    # For astrometric calibration we can
    # consider saturated sources:
    FLAGS="-FLAGS_MASK 240"
  else
    FILES=`${P_FIND} ../cat/ -name \*scamp.cat | ${P_SORT}`
    # For photometric calibration we do not want to
    # consider saturated sources:
    FLAGS="-FLAGS_MASK 244"
  fi
  
  ASTREF=""
  if [ -f ${STARCAT} ]; then
    ASTREF="-ASTREF_CATALOG FILE -ASTREFCAT_NAME ${STARCAT}"
  else
    ASTREF="-ASTREF_CATALOG ${STARCAT}"
  fi
  
  # positional quantities to use:
  if [ "${POSQUAN}" = "WINDOWED" ]; then
    POSPAR="-CENTROID_KEYS  XWIN_IMAGE,YWIN_IMAGE"
    POSPAR="${POSPAR} \
            -CENTROIDERR_KEYS ERRAWIN_IMAGE,ERRBWIN_IMAGE,ERRTHETAWIN_IMAGE"
    POSPAR="${POSPAR} -DISTORT_KEYS XWIN_IMAGE,YWIN_IMAGE"
  else
    POSPAR="-CENTROID_KEYS  X_IMAGE,Y_IMAGE"
    POSPAR="${POSPAR} \
            -CENTROIDERR_KEYS ERRA_IMAGE,ERRB_IMAGE,ERRTHETA_IMAGE"
    POSPAR="${POSPAR} -DISTORT_KEYS X_IMAGE,Y_IMAGE"
  fi
  
  # polynomial order used to map astrometric distortions:
  DISTORTDEG="-DISTORT_DEGREES 3"
  if [ "${DATAKIND}" = "SHORT" ]; then
    DISTORTDEG="-DISTORT_DEGREES 2"
  fi
  
  ${P_SCAMP} ${FILES} \
             -c ${CONF}/scamp_astrom_photom.scamp \
             -CDSCLIENT_EXEC ${P_ACLIENT} \
             -POSITION_MAXERR ${POSMAXERR} \
             -NTHREADS ${NPARA} ${POSPAR} \
             ${DISTORTDEG} ${ASTREF} ${FLAGS} ${MOSAICTYPE}
  
  if [ $? -ne 0 ]
  then
    echo "scamp call failed!! Exiting!!"
    cleanTmpFiles
    exit 1
  fi
  
  # scamp creates the headers in the directory where the catalogs
  # are:
  ${P_FIND} ../cat/ -name \*.head | xargs mv --target-directory=.
  
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
  test -f ${TEMPDIR}/photdata.txt_$$ && rm ${TEMPDIR}/photdata.txt_$$
  
  EXPOSURES=`sed -e 's/_[1-9][0-9]*[^0-9]*.ldac//' \
                 ${TEMPDIR}/allscampfiles.txt_$$ | sort | uniq`
  
  # Because the flux scales refer to an image normalised to one
  # second we need to obtain the exposure times of all frames
  # first. We also get the SCAMP flux scale, the photometric
  # instrument and the photometric group:
  for EXPOSURE in ${EXPOSURES}
  do
    EXPTIME=`${P_LDACTOASC} -i ../cat/${EXPOSURE}_scamp.cat \
                       -t LDAC_IMHEAD -s |\
             fold | grep EXPTIME | ${P_GAWK} '{print $3}'`
    FLXSCALE=`grep FLXSCALE ${EXPOSURE}_scamp.head |\
              ${P_GAWK} '(NR == 1) {print $2}'`
    PHOTINST=`grep PHOTINST ${EXPOSURE}_scamp.head |\
              ${P_GAWK} '(NR == 1) {print $2}'`
    PHOTGRP=`grep FGROUPNO ${EXPOSURE}_scamp.head |\
              ${P_GAWK} '(NR == 1) {print $2}'`
  
    echo ${EXPOSURE}" "${EXPTIME}" "${FLXSCALE}" "${PHOTINST}" "${PHOTGRP} >> \
       ${TEMPDIR}/photdata.txt_$$
  done
  
  # The following 'awk' script calculates relative zeropoints
  # and THELI fluxscales for the different photometric contexts:
  ${P_GAWK} 'BEGIN {maxphotinst = 1;}
             { exposure[NR]       = $1;
               exptime[NR]        = $2;
               flxscale_scamp[NR] = $3;
               photinst[NR]       = $4;
               photgrp[NR]        = $5;
               val[NR]            = -2.5 * log($3 * $2) / log(10);
               m[$4, $5]          = m[$4, $5] + val[NR]
               nphotinst[$4, $5]  = nphotinst[$4, $5] + 1
               if ($4 > maxphotinst) {maxphotinst = $4}
               if ($5 > maxgrp[$4]) {maxgrp[$4] = $5}}
             END {
               for (i = 1; i <= maxphotinst; i++) {
                 for (j = 1; j <= maxgrp[i]; j++) {
                   if (nphotinst[i, j] > 0) {
                     m[i, j] = m[i, j] / nphotinst[i, j];
                   }
                 }
               }
               for (i = 1; i <= NR; i++) {
                 relzp[i] = val[i] - m[photinst[i], photgrp[i]];
                 flxscale_theli[i] = (10**(-0.4 * relzp[i])) / exptime[i];
                 printf("%s %f %e\n",
                   exposure[i], relzp[i], flxscale_theli[i]);
               }
             }' ${TEMPDIR}/photdata.txt_$$ > ${TEMPDIR}/photdata_relzp.txt_$$

  # now split the exposure catalogues for the individual chips
  # and add the RZP and FLXSCALE header keywords. Put the headers
  # into appropriate headers_scamp directories
  #
  while read EXPOSURE RELZP FLXSCALE
  do
    # get all chips available for the current exposure:
    grep "^${EXPOSURE}" ${TEMPDIR}/allscampfiles.txt_$$  | \
    ${P_GAWK} -F_ '{a = $NF; gsub(/[^0-9]/, "", a); print a}' |\
    ${P_SORT} -n > ${TEMPDIR}/chips.txt_$$

    # first rename the SCAMP header keyword FLXSCALE to FLSCALE. We
    # need FLXSCALE for the THELI flux scaling later. Then create a
    # separate header file for each chip:
    sed -e 's/FLXSCALE/FLSCALE /' ${EXPOSURE}_scamp.head | \
    ${P_GAWK} 'BEGIN {getline < "'${TEMPDIR}'/chips.txt_'$$'"; chip = $1} {
               if ($1 == "END") {
                 printf("RZP     = %20f / THELI relative zeropoint\n",
                        '${RELZP}') >> "'${EXPOSURE}'_" chip ".head";
                 printf("FLXSCALE= %20E / THELI relative flux scale\n",
                        '${FLXSCALE}') >> "'${EXPOSURE}'_" chip ".head";
                 printf("END\n") >> "'${EXPOSURE}'_" chip ".head";

                 if (getline < "'${TEMPDIR}'/chips.txt_'$$'" > 0) {
                   chip = $1;
                 }
               } else {
                 print $0 >> "'${EXPOSURE}'_" chip ".head";
               }}'
  done < ${TEMPDIR}/photdata_relzp.txt_$$

  for EXPOSURE in ${EXPOSURES}
  do
    mv ${EXPOSURE}_[1-9]*.head \
       ${DIR_FROM_EXPOSURE[${EXPOSURE}]}/headers_scamp_${SUFFIX}
  done
else # -s ..allscampfiles....
  # In case that this script did nothing we also
  # remove the created directory structure:
  theli_error "No catalogues available! Nothing to be done!"

  cd ../..
  rm -rf astrom_photom_scamp_${SUFFIX}

  for DIR in "${!INSTRU_FROM_DIR[@]}"
  do
    test -d ${DIR}/headers_scamp_${SUFFIX} && \
      rmdir ${DIR}/headers_scamp_${SUFFIX}
  done

  cleanTmpFiles
  exit 1;
fi

# clean up temporary files and bye
cleanTmpFiles

cd ${DIR}

theli_end
exit 0;
