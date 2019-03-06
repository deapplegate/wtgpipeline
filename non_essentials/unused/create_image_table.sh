#!/bin/bash -xv

# this script creates a IMAGES table in
# the chips.cat4 catalog containing 
# exposure names, mean seeing and mean
# relative zeropoint.


# 02.03.2004:
# added EXPTIME to the image table
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 07.10.2004:
# added GABODSID for photometry to
# the image table (JD)
#
# 11.10.04:
# Added the RUN/SET mode (JD)
# In the RUN mode, no RELPHOTOM information
# is used.
#
# 24.11.04:
# The OBJECT keyword is now included
# in the IMAGE table.
#
# 20.03.2005:
# The image names were not processed correctly
# on cameras with more than 10 chips.
#
# 23.01.2006:
# I rewrote the script so that under the 'RUN'
# mode the script can be used under less strict
# conditions. It is no longer necessary to run
# astrom but only preastrom to obtain the necessary 
# products of this script.

#
#$1: main directory
#$2: science directory
#$3: extension of the images for which
#    catalogs have been created (OFCSFF etc.)
#$4: Mode, RUN or SET, for RUN we skip the fullphotom step
#    and first have to create a chips.cat4 on our own

. ${INSTRUMENT:?}.ini

# determine the number of exposures

if [ $4 = "RUN" ]; then
    CATS=`ls /$1/$2/cat/chip_*.cat2`
    if [ "${NCHIPS}" -gt "1" ]; then
	${P_LDACPASTE} -i ${CATS} -o /$1/$2/cat/chips.cat4
    else
	cp ${CATS} /$1/$2/cat/chips.cat4
    fi
fi

NEXP=`${P_LDACTOASC} -i /$1/$2/cat/chips.cat4 -t FIELDS\
               -k FITSFILE -s -b | wc \
                | ${P_GAWK} '{print $1/'${NCHIPS}'}'`

# get a text file "images.dat" with image names

rm ${TEMPDIR}/image.dat

${P_LDACTOASC} -i /$1/$2/cat/chips.cat4 -t FIELDS \
               -k FITSFILE OBJECT -s -b \
                | ${P_GAWK} '(NR<='${NEXP}') {print $1, $2}'\
                > ${TEMPDIR}/tmp.dat

cat ${TEMPDIR}/tmp.dat |\
{
  while read line
  do
    file=`echo ${line} | ${P_GAWK} '{print $1}'`
    file=`basename ${file}`
    object=`echo ${line} | ${P_GAWK} '{print $2}'`
    echo ${file%_*} ${object} >> ${TEMPDIR}/image.dat
  done
}

rm ${TEMPDIR}/tmp.dat

i=1
while [ "${i}" -le "${NCHIPS}" ]
do
  j=1
  while [ "${j}" -le "${NEXP}" ]
  do
    echo $j >> ${TEMPDIR}/tmp.dat
    j=$(( $j + 1 ))
  done
  i=$(( $i + 1 ))    
done

echo 'COL_NAME  = EXPOSURE' > ${TEMPDIR}/asctoldac.conf
echo 'COL_TTYPE = LONG'     >> ${TEMPDIR}/asctoldac.conf
echo 'COL_HTYPE = INT'      >> ${TEMPDIR}/asctoldac.conf
echo 'COL_COMM = ""'        >> ${TEMPDIR}/asctoldac.conf
echo 'COL_UNIT = ""'        >> ${TEMPDIR}/asctoldac.conf
echo 'COL_DEPTH = 1'        >> ${TEMPDIR}/asctoldac.conf

${P_ASCTOLDAC} -i ${TEMPDIR}/tmp.dat -o ${TEMPDIR}/exp.cat -t FIELDS \
               -c ${TEMPDIR}/asctoldac.conf
${P_LDACJOINKEY} -i /$1/$2/cat/chips.cat4 -o ${TEMPDIR}/tmp.cat -p ${TEMPDIR}/exp.cat \
                 -t FIELDS -k EXPOSURE

if [ $4 = "SET" ]; then
	${P_LDACRENTAB} -i ${TEMPDIR}/exp.cat -o ${TEMPDIR}/exp1.cat -t FIELDS RELPHOTOM
	${P_LDACJOINKEY} -i ${TEMPDIR}/tmp.cat -o ${TEMPDIR}/tmp11.cat -p ${TEMPDIR}/exp1.cat \
	                 -t RELPHOTOM -k EXPOSURE
else
    mv tmp.cat tmp11.cat
fi

if [ $4 = "SET" ]; then
  ${P_LDACRENTAB} -i ${TEMPDIR}/exp.cat -o ${TEMPDIR}/exp2.cat -t FIELDS DISTORTIONS
  ${P_LDACJOINKEY} -i ${TEMPDIR}/tmp11.cat -o ${TEMPDIR}/tmp1.cat -p ${TEMPDIR}/exp2.cat \
                   -t DISTORTIONS -k EXPOSURE
else
  cp tmp11.cat tmp1.cat
fi  

echo 'COL_NAME  = IMAGENAME' > ${TEMPDIR}/asctoldac.conf
echo 'COL_TTYPE = STRING'    >> ${TEMPDIR}/asctoldac.conf
echo 'COL_HTYPE = STRING'    >> ${TEMPDIR}/asctoldac.conf
echo 'COL_COMM = ""'         >> ${TEMPDIR}/asctoldac.conf
echo 'COL_UNIT = ""'         >> ${TEMPDIR}/asctoldac.conf
echo 'COL_DEPTH = 128'       >> ${TEMPDIR}/asctoldac.conf
echo 'COL_NAME  = OBJECT'    >> ${TEMPDIR}/asctoldac.conf
echo 'COL_TTYPE = STRING'    >> ${TEMPDIR}/asctoldac.conf
echo 'COL_HTYPE = STRING'    >> ${TEMPDIR}/asctoldac.conf
echo 'COL_COMM = ""'         >> ${TEMPDIR}/asctoldac.conf
echo 'COL_UNIT = ""'         >> ${TEMPDIR}/asctoldac.conf
echo 'COL_DEPTH = 128'       >> ${TEMPDIR}/asctoldac.conf


${P_ASCTOLDAC} -i ${TEMPDIR}/image.dat -o ${TEMPDIR}/image.cat \
               -t IMAGES -c ${TEMPDIR}/asctoldac.conf

${P_LDACADDTAB} -i ${TEMPDIR}/tmp1.cat -o ${TEMPDIR}/tmp2.cat \
                -p ${TEMPDIR}/image.cat \
                -t IMAGES

${P_LDACCALC} -i ${TEMPDIR}/tmp2.cat -o ${TEMPDIR}/tmp21.cat -c "(EXPTIME);" \
              -n "EXPTIME" "" -k FLOAT -t FIELDS -r IMAGES \
              -x EXPOSURE -s mean\
	      -c "(GABODSID);" -n "GABODSID" "" -k LONG -t FIELDS -r IMAGES \
              -x EXPOSURE -s mean
${P_LDACCALC} -i ${TEMPDIR}/tmp21.cat -o ${TEMPDIR}/tmp3.cat -c "(SEXSFWHM);" \
              -n "SEEING" "" -k FLOAT -t FIELDS -r IMAGES \
              -c "(SEXBKGND/EXPTIME);" -n "BACKGR" "sky per second" \
              -k FLOAT -x EXPOSURE -s mean
${P_LDACCALC} -i ${TEMPDIR}/tmp3.cat -o ${TEMPDIR}/tmp4.cat -c "(SEXSFWHM);" \
              -n "SEEING_SDEV" "" -k FLOAT -t FIELDS -r IMAGES \
              -c "(SEXBKGND/EXPTIME);" -n "BACKGR_SDEV" "" \
              -k FLOAT -x EXPOSURE -s stddev

if [ $4 = "SET" ]; then
	${P_LDACCALC} -i ${TEMPDIR}/tmp4.cat -o ${TEMPDIR}/tmp5.cat -c "(MAG_AUTO_ZP);" \
	              -n "AUTO_ZP" "" -k FLOAT -t RELPHOTOM -r IMAGES \
	              -x EXPOSURE -s mean
	${P_LDACCALC} -i ${TEMPDIR}/tmp5.cat -o ${TEMPDIR}/tmp6.cat -c "(MAG_AUTO_ZP);" \
	              -n "AUTO_ZP_SDEV" "" -k FLOAT -t RELPHOTOM -r IMAGES \
	              -x EXPOSURE -s stddev
else
    mv tmp4.cat tmp6.cat
fi

if [ $4 = "SET" ]; then

  ${P_LDACCALC} -i ${TEMPDIR}/tmp6.cat -o ${TEMPDIR}/tmp7.cat -c "(PV1_1*206264);" \
              -n "RA_OFF" "RA offset in arcsec" -k FLOAT \
	      -c "(PV1_2*206264);" -n "DEC_OFF" "DEC offset in arcsec" -k FLOAT \
              -t DISTORTIONS -r IMAGES \
              -x EXPOSURE -s mean 
  ${P_LDACCALC} -i ${TEMPDIR}/tmp7.cat -o /$1/$2/cat/chips.cat5 -c "(PV1_1*206264);" \
              -n "RA_OFF_SDEV" "" -k FLOAT \
	      -c "(PV1_2*206264);" -n "DEC_OFF_SDEV" "" -k FLOAT \
              -t DISTORTIONS -r IMAGES \
              -x EXPOSURE -s stddev
else
  cp tmp6.cat /$1/$2/cat/chips.cat5
fi
  
# see whether lensing information is available;
# if yes, add them to the IMAGES table as well
${P_LDACTESTEXIST} -i /$1/$2/cat/chips.cat5 -t OBJECTS -k e1 e2 cl

if [ "$?" -gt "0" ]; then
  rm ${TEMPDIR}/ tmp*.cat
  rm ${TEMPDIR}/exp*cat
  exit 1;
fi

echo "COL_REF = FIELD_POS"   > ${TEMPDIR}/make_join.conf
echo "COL_NAME = EXPOSURE"  >> ${TEMPDIR}/make_join.conf
echo "COL_INPUT = EXPOSURE" >> ${TEMPDIR}/make_join.conf

${P_MAKEJOIN} -i /$1/$2/cat/chips.cat5 -o ${TEMPDIR}/tmp8.cat \
              -c ${TEMPDIR}/make_join.conf -m OBJECTS -r FIELDS

${P_LDACFILTER} -i ${TEMPDIR}/tmp8.cat -o ${TEMPDIR}/tmp9.cat -c "(cl=2);"

${P_LDACCALC} -i ${TEMPDIR}/tmp9.cat -o ${TEMPDIR}/tmp10.cat -c "(e1);" \
              -n "e1" "e1_starellipticity" -k FLOAT \
	      -c "(e2);" -n "e2" "e2_starellipticity" -k FLOAT \
              -t OBJECTS -r IMAGES \
              -x EXPOSURE -s mean

${P_LDACCALC} -i ${TEMPDIR}/tmp10.cat -o /$1/$2/cat/chips.cat6 -c "(e1);" \
              -n "e1_SDEV" "" -k FLOAT \
	      -c "(e2);" -n "e2_SDEV" "" -k FLOAT \
              -t OBJECTS -r IMAGES \
              -x EXPOSURE -s stddev

rm ${TEMPDIR}/tmp*.cat
rm ${TEMPDIR}/exp*cat











