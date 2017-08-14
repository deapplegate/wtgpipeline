#!/bin/bash -xv
. BonnLogger.sh
. log_start
# the script collects some header keywords of a directory with raw fits
# files into an LDAC catalog with a FILES table. These data are then
# used to distinguish 'sets' of images
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 03.12.2004:
# I substituted the initial 'ls' listing all
# to be looked at by a find command. With 'ls'
# it could happen that we exceed its argument list.
#
# 14.08.2005:
# The call of the UNIX 'find' program is now done
# via a variable 'P_FIND'.
#
# 30.11.2005:
# A ${TEMPDIR} was mssing when creating the initial
# file list.

#$1: main directory
#$2: science directory
#$3: image extension (ext) on ..._iext.fits (i is the chip number)
#$4: minimum overlap for counting exposures to the same set

. ${INSTRUMENT:?}.ini

# configuration parameters:

FILTERKEY="FILTER"
OBJECTKEY="OBJECT"
RAKEY="CRVAL1"
DECKEY="CRVAL2"
ROTKEY="ROTATION"

${P_FIND} $1/$2/ -name \*$3.fits -print > ${TEMPDIR}/images_$$

if [ -f "${TEMPDIR}/images_tmp.dat_$$" ]; then
  rm ${TEMPDIR}/images_tmp.dat_$$
fi

cat ${TEMPDIR}/images_$$ |\
{
  while read IMAGE
  do
    NAME=`basename ${IMAGE}`
    RA=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${RAKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`
    DEC=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${DECKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`
    OBJECT=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${OBJECTKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`
    FILTER=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${FILTERKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`
    ROTATION=`${P_DFITS}  ${IMAGE} | ${P_FITSORT} ${ROTKEY}  | ${P_GAWK} '($1!="FILE") {print $2}'`

    echo ${NAME} ${OBJECT} ${FILTER} ${RA} ${DEC} ${ROTATION} >> ${TEMPDIR}/images_tmp.dat_$$
  done
}

${P_GAWK} '{print NR, $0}' ${TEMPDIR}/images_tmp.dat_$$ > ${TEMPDIR}/images.dat_$$
${P_ASCTOLDAC} -i ${TEMPDIR}/images.dat_$$ -o ${TEMPDIR}/science.cat_$$ \
               -c ${CONF}/make_files_cat_asctoldac.conf \
               -t FILES

${P_SELECTOVERLAPS} -i ${TEMPDIR}/science.cat_$$ -o ${TEMPDIR}/science_set.cat_$$ -MIN_OVER $4

${P_LDACTOASC} -i ${TEMPDIR}/science_set.cat_$$ -b -t FILES -k FITSFILE POSSET -s > ${TEMPDIR}/tmp.asc_$$

cat ${TEMPDIR}/tmp.asc_$$ |\
{
  while read FILE SET
  do
    if [ ! -d "/$1/set_${SET}" ]; then
      mkdir "/$1/set_${SET}"
    fi
    
    mv /$1/$2/${FILE} /$1/set_${SET}
  done
}
log_status $?
