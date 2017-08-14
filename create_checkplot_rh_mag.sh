#!/bin/bash -xv
. BonnLogger.sh
. log_start
# last update: 27.02.2004 
# author     : Marco Hetterscheidt

# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 05.07.2004:
# corrected an error in giving the TEMPDIR to sm

# The script creates a mag-rh plot showing objects
# that SExtractor classifies as stars as red dots.
#

. progs.ini

#$1: main dir.
#$2: science dir.
#$3: name of coadded image (without FITS extension)
#$4 : CLASS_STAR value    -
#$5 : FLUX_RADIUS value   --- for separation between stars and galaxies and
#$6 : MAG_AUTO value      -   fitting range (MAG_AUTO)          

# The sm-script only plots MAG_AUTO against half light radius (FLUX_RADIUS),
# where the red dots indicate the stars to check separation values.

${P_LDACFILTER} -i /$1/$2/postcoadd/cats/$3_sex_ldac.cat -o ${TEMPDIR}/tmp.cat -c '(CLASS_STAR > '$4');'
${P_LDACFILTER} -i ${TEMPDIR}/tmp.cat -o /$1/$2/postcoadd/cats/$3_sex_ldac_stars.cat \
                -c '((FLUX_RADIUS < '$5') OR (MAG_AUTO < '$6'))AND(MAG_AUTO > 16);'

${P_LDACTOASC} -i /$1/$2/postcoadd/cats/$3_sex_ldac.cat -t OBJECTS \
               -k FLUX_RADIUS MAG_AUTO -b > ${TEMPDIR}/tmp.asc
${P_LDACTOASC} -i /$1/$2/postcoadd/cats/$3_sex_ldac_stars.cat \
               -t OBJECTS -k FLUX_RADIUS MAG_AUTO -b > ${TEMPDIR}/tmp2.asc

{
  echo "define TeX_strings 0"
  echo 'macro read "'${SMMACROS}'/magrh.sm"'
  echo 'dev postencap "/'$1'/'$2'/postcoadd/plots/'$3'_magrh.ps"'
  echo "plot \"${TEMPDIR}/tmp.asc\" \"${TEMPDIR}/tmp2.asc\""
} | ${P_SM}


log_status $?
