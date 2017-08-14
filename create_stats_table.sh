#!/bin/bash -xv
. BonnLogger.sh
. log_start
# this script creates a STATS table from
# the catalogs created with
# 'create_astromcats_weights_para.sh'
# and, if present the headers created by
# ASTROMETRIX and PHOTOMETRIX.

# 28.07.2005:
# I included relative photometric information
# from PHOTOMETRIX.
#
# 14.08.2005:
# I included a missing ${TEMPDIR}
#
# 05.12.2005:
# - Chips, whose NOTUSE or NOTPROCESS flag is set do not contribute
#   to the statistics of the STATS table.
# - I included information on absolute magnitude zeropoints
#   and extinction coefficients (if present) in the STATS table.
# - I corrected a bug in the indexing of NOTPROCESS flags.
#
# 22.01.2006:
# - I added information about the zeropoint and extinction
#   coefficient that was chosen in the standard star calibration
#   phase.
# - I corrected an error in a NOTUSE, NOTPROCESS check.
#
# 21.07.2006:
# I rewrote the code to change from the NOTUSE, NOTPROCESS
# concept to a 'BADCCD' formalism. This allows for cases
# where in certain images some chips are faulty but which
# are ok in general. The old NOTUSE/NOTPROCESS concept is
# naturally included. Those chips now simply need to get
# the 'BADCCD' flag.
#
# 30.08.2007:
# I added RA and DEC values of the observations to the STATS table.
# This allows us to create checkplots on dithering patterns.
#
# 15.09.2007:
# A new (optional) command line argument points to the
# directory with ASTROMETRIX or scamp headers with relative
# photometric zeropoint information. It was introduced because
# with the inclusion of scamp different header directories
# can exist.
#
# 19.10.2007:
# Typo correction in testing the existence of a file.

#
#$1: main directory
#$2: science directory
#$3: extension of the images for which
#    catalogs have been created (OFCSFF etc.)
#$4: headers directory (OPTIONAL)

. ${INSTRUMENT:?}.ini

# paste catalogs; but only consider those whose image
# BADCCD flag is not set! Get at the same time the number
# of 'real' chips, i.e. chips who really contribute.

NREALCHIPS=0
i=1
while [ "${i}" -le ${NCHIPS} ]
do
  RAWCATS=`ls /$1/$2/cat/*_${i}$3.cat`
  REALCATS=""

  for CAT in ${RAWCATS}
  do
    BASE=`basename ${CAT} .cat`
    BADCCD=`${P_DFITS} /$1/$2/${BASE}.fits | ${P_FITSORT} -d BADCCD | awk '{print $2}'`

    if [ "${BADCCD}" != "1" ]; then
      REALCATS="${REALCATS} ${CAT}"
    fi 
  done

  if [ "${REALCATS}_A" != "_A" ]; then
    ${P_LDACCONV} -b ${i} -c ${INSTRUMENT} -i ${REALCATS} -o /$1/$2/cat/chip_${i}.cat0
    NREALCHIPS=$(( ${NREALCHIPS} + 1 ))
  fi
  i=$(( $i + 1 ))
done

CATS=`ls /$1/$2/cat/chip_*.cat0`

if [ ${NREALCHIPS} -gt 1 ]; then
  ${P_LDACPASTE} -i ${CATS} -o /$1/$2/cat/chips.cat
else
  cp ${CATS} /$1/$2/cat/chips.cat
fi

# get a text file "image.dat" with image names, object name
# and absolute photometric info if present!!

if [ -f ${TEMPDIR}/image_$$.dat ]; then
  rm ${TEMPDIR}/image_$$.dat
fi

# do we have information on absolute photometric calibration?
ABSPHOTINFO=0
${P_LDACTESTEXIST} -i /$1/$2/cat/chips.cat -t FIELDS -k ZPCHOICE

if [ "$?" -gt "0" ]; then
  ${P_LDACTOASC} -i /$1/$2/cat/chips.cat -t FIELDS \
                 -k FITSFILE OBJECT -s -b \
                  > ${TEMPDIR}/tmp_$$.dat
else
  ABSPHOTINFO=1
  ${P_LDACTOASC} -i /$1/$2/cat/chips.cat -t FIELDS \
                 -k FITSFILE OBJECT ZPCHOICE ZP COEFF ZP1 COEFF1 ZP2 COEFF2 ZP3 COEFF3 -s -b \
                  > ${TEMPDIR}/tmp_$$.dat
fi

# check whether relative photometric zeropoints
# are available from Photometrix.. We only test for
# the first image and assume that all images have
# this information if the test for the first is
# successful.
RELZP=0
file=`${P_GAWK} '(NR==1) {print $1}' ${TEMPDIR}/tmp_$$.dat`
file=`basename ${file} $3.fits`

if [ -f /$1/$2/$4/${file}.head ]; then
  ${P_GAWK} 'BEGIN {FS = "[=/]"} {if ($1 ~ /^RZP/) {print $2}}' \
            /$1/$2/$4/${file}.head > ${TEMPDIR}/zp_$$.txt
  if [ -s ${TEMPDIR}/zp_$$.txt ]; then
      RELZP=1
      rm ${TEMPDIR}/zp_$$.txt
  fi
fi

cat ${TEMPDIR}/tmp_$$.dat |\
{
  while read line
  do
    file=`echo ${line} | ${P_GAWK} '{print $1}'`
    file=`basename ${file} $3.fits`
    object=`echo ${line} | ${P_GAWK} '{print $2}'`
    if [ "${ABSPHOTINFO}" -eq 1 ]; then
	phot=`echo ${line} | ${P_GAWK} '{print $3, $4, $5, $6, $7, $8, $9, $10, $11}'`
    else
	phot=""
    fi
    if [ "${RELZP}" -eq 1 ]; then
      ZP=`${P_GAWK} 'BEGIN {FS = "[=/]"} {if ($1 ~ /^RZP/) {print $2}}' \
            /$1/$2/$4/${file}.head`
      echo ${file%_*} ${object} ${phot} ${ZP} >> ${TEMPDIR}/image_$$.dat
    else
      echo ${file%_*} ${object} ${phot} >> ${TEMPDIR}/image_$$.dat
    fi
  done
}

# NOTE that we assume in the following that lines corresponding
# to one image are absolutely identical in ${TEMPDIR}/image_$$.dat
# (e.g. it is not allowed to have different relative zeropoints
# for individual chips)
${P_SORT} -k 1,1 ${TEMPDIR}/image_$$.dat | \
      uniq > ${TEMPDIR}/imagesinset_$$.txt

i=1
while read image bla
do
  EXPNAME[${i}]=${image}
  i=$(( $i + 1 ))
done < ${TEMPDIR}/imagesinset_$$.txt

NEXP=$(( ${i} - 1 ))

# get a correspondence of files present in chips.cat 
# or ${TEMPDIR}/image_$$.dat and
# an exposure number:

rm ${TEMPDIR}/tmp_$$.dat

while read image bla
do
  i=1
  while [ ${i} -le ${NEXP} ]
  do
    if [ "${EXPNAME[${i}]}" = "${image}" ]; then
      echo $i >> ${TEMPDIR}/tmp_$$.dat 
    fi
    i=$(( $i + 1 ))
  done
done < ${TEMPDIR}/image_$$.dat

echo 'COL_NAME  = EXPOSURE' > ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_TTYPE = LONG'     >> ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_HTYPE = INT'      >> ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_COMM = ""'        >> ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_UNIT = ""'        >> ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_DEPTH = 1'        >> ${TEMPDIR}/asctoldac.conf_$$

${P_ASCTOLDAC} -i ${TEMPDIR}/tmp_$$.dat -o ${TEMPDIR}/exp_$$.cat -t FIELDS \
               -c ${TEMPDIR}/asctoldac.conf_$$

# transfer the exposure number to the FIELDS table of chips.cat
${P_LDACJOINKEY} -i /$1/$2/cat/chips.cat -o ${TEMPDIR}/tmp1_$$.cat -p ${TEMPDIR}/exp_$$.cat \
                 -t FIELDS -k EXPOSURE

echo 'COL_NAME  = IMAGENAME' > ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_TTYPE = STRING'    >> ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_HTYPE = STRING'    >> ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_COMM = ""'         >> ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_UNIT = ""'         >> ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_DEPTH = 128'       >> ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_NAME  = OBJECT'    >> ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_TTYPE = STRING'    >> ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_HTYPE = STRING'    >> ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_COMM = ""'         >> ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_UNIT = ""'         >> ${TEMPDIR}/asctoldac.conf_$$
echo 'COL_DEPTH = 128'       >> ${TEMPDIR}/asctoldac.conf_$$

if [ "${ABSPHOTINFO}" -eq 1 ]; then
  echo 'COL_NAME  = ZPCHOICE'     >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_TTYPE = SHORT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_HTYPE = INT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_COMM = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_UNIT = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_DEPTH = 1'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_NAME  = ZP'      >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_TTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_HTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_COMM = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_UNIT = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_DEPTH = 1'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_NAME  = COEFF'     >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_TTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_HTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_COMM = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_UNIT = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_DEPTH = 1'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_NAME  = ZP1'     >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_TTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_HTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_COMM = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_UNIT = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_DEPTH = 1'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_NAME  = COEFF1'     >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_TTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_HTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_COMM = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_UNIT = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_DEPTH = 1'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_NAME  = ZP2'     >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_TTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_HTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_COMM = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_UNIT = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_DEPTH = 1'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_NAME  = COEFF2'     >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_TTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_HTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_COMM = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_UNIT = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_DEPTH = 1'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_NAME  = ZP3'     >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_TTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_HTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_COMM = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_UNIT = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_DEPTH = 1'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_NAME  = COEFF3'     >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_TTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_HTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_COMM = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_UNIT = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_DEPTH = 1'       >> ${TEMPDIR}/asctoldac.conf_$$
fi

if [ "${RELZP}" -eq 1 ]; then
  echo 'COL_NAME  = RZP'     >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_TTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_HTYPE = FLOAT'   >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_COMM = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_UNIT = ""'       >> ${TEMPDIR}/asctoldac.conf_$$
  echo 'COL_DEPTH = 1'       >> ${TEMPDIR}/asctoldac.conf_$$
fi

# finally create the STATS table:
${P_ASCTOLDAC} -i ${TEMPDIR}/imagesinset_$$.txt -o ${TEMPDIR}/image_$$.cat \
               -t STATS -c ${TEMPDIR}/asctoldac.conf_$$
${P_LDACADDTAB} -i ${TEMPDIR}/tmp1_$$.cat -o ${TEMPDIR}/tmp2_$$.cat \
                -p ${TEMPDIR}/image_$$.cat \
                -t STATS

# transfer information on exposure time, gabodsid, airmass and pointing; of
# course the calculation of a 'mean' of qantities that all have the
# same value is an 'overkill'.
${P_LDACCALC} -i ${TEMPDIR}/tmp2_$$.cat -o ${TEMPDIR}/tmp21_$$.cat -c "(EXPTIME);" \
              -n "EXPTIME" "" -k FLOAT -t FIELDS -r STATS \
              -x EXPOSURE -s mean\
	      -c "(GABODSID);" -n "GABODSID" "" -k LONG -t FIELDS -r STATS \
              -x EXPOSURE -s mean\
	      -c "(AIRMASS);" -n "AIRMASS" "" -k FLOAT -t FIELDS -r STATS \
              -x EXPOSURE -s mean\
	      -c "(CRVAL1);" -n "RA" "" -k FLOAT -t FIELDS -r STATS \
              -x EXPOSURE -s mean\
	      -c "(CRVAL2);" -n "DEC" "" -k FLOAT -t FIELDS -r STATS \
              -x EXPOSURE -s mean

# add statistical information seeing and sky background:
${P_LDACCALC} -i ${TEMPDIR}/tmp21_$$.cat -o ${TEMPDIR}/tmp3_$$.cat -c "(SEXSFWHM);" \
              -n "SEEING" "" -k FLOAT -t FIELDS -r STATS \
              -c "(SEXBKGND/EXPTIME);" -n "BACKGR" "sky per second" \
              -k FLOAT -x EXPOSURE -s mean
${P_LDACCALC} -i ${TEMPDIR}/tmp3_$$.cat -o /$1/$2/cat/chips.cat5 -c "(SEXSFWHM);" \
              -n "SEEING_SDEV" "" -k FLOAT -t FIELDS -r STATS \
              -c "(SEXBKGND/EXPTIME);" -n "BACKGR_SDEV" "" \
              -k FLOAT -x EXPOSURE -s stddev

# see whether lensing information is available;
# if yes, add them to the STATS table as well
${P_LDACTESTEXIST} -i /$1/$2/cat/chips.cat5 -t OBJECTS -k e1 e2 cl

if [ "$?" -gt "0" ]; then
  rm ${TEMPDIR}/tmp*_$$.dat
  rm ${TEMPDIR}/tmp*_$$.cat
  rm ${TEMPDIR}/exp*_$$.cat
  log_status 1
  exit 1;
fi

echo "COL_REF = FIELD_POS"   > ${TEMPDIR}/make_join.conf_$$
echo "COL_NAME = EXPOSURE"  >> ${TEMPDIR}/make_join.conf_$$
echo "COL_INPUT = EXPOSURE" >> ${TEMPDIR}/make_join.conf_$$

${P_MAKEJOIN} -i /$1/$2/cat/chips.cat5 -o ${TEMPDIR}/tmp8_$$.cat \
              -c ${TEMPDIR}/make_join.conf_$$ -m OBJECTS -r FIELDS

${P_LDACFILTER} -i ${TEMPDIR}/tmp8_$$.cat -o ${TEMPDIR}/tmp9_$$.cat -c "(cl=2);"

${P_LDACCALC} -i ${TEMPDIR}/tmp9_$$.cat -o ${TEMPDIR}/tmp10_$$.cat -c "(e1);" \
              -n "e1" "e1_starellipticity" -k FLOAT \
	      -c "(e2);" -n "e2" "e2_starellipticity" -k FLOAT \
              -t OBJECTS -r STATS \
              -x EXPOSURE -s mean

${P_LDACCALC} -i ${TEMPDIR}/tmp10_$$.cat -o /$1/$2/cat/chips.cat6 -c "(e1);" \
              -n "e1_SDEV" "" -k FLOAT \
	      -c "(e2);" -n "e2_SDEV" "" -k FLOAT \
              -t OBJECTS -r STATS \
              -x EXPOSURE -s stddev

rm ${TEMPDIR}/tmp*_$$.dat
rm ${TEMPDIR}/tmp*_$$.cat
rm ${TEMPDIR}/exp*_$$.cat



log_status $?
