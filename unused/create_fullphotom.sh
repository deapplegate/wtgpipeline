#!/bin/bash -xv

# 12.10.03:
# corrected a bug in the building of the initial
# CATS variable. It missed catalogs with a chip
# number larger than 9.
#
# 10.01.04:
# If the IMAFLAGS_ISO key is not present, it is added
# before catalogs are associated and run through relphotom.
# Using the Flag key for both Flagging processes in relphotom
# (the SExtractor Flag and the IMAFLAG), results were not
# correct on little endian machines.
#
# 11.10.04:
# corrected a bug concerning the adding of IMAFLAGS_ISO. The
# flag was always added, regardless whether it existed already
# or not.
#
# 24.11.04:
# a catalog with a FIXED table is created for relphotom
# if phototmetric information is available.
#
# 26.11.2004:
# corrected a bug in the condition for the 
# creation of a FIXED table.
#
# 10.12.2004:
# I corrected two bugs in the creation of the
# FIXED table: The zeropoint has to be given at
# AIRMASS 0 and the extinction has to be positive
#
# 01.03.2005:
# Before creating chips.fixed.cat I now check that
# fixed.asc is not empty!
#
# 18.03.2005:
# I included the possibility to give the nights and 
# solutions, that should be included in the absoulte 
# photometric calibration, on the command line.
#
# 20.03.2005:
# I corrected a bug in the case where nights and zeropoints
# are expicitely passed for photometric calibration. The 
# numbering of objects in the FIXED table was not correct 
# in this case.
#
# 20.04.2005:
# - A table SOLPHOTOM is added to chips.cat4 if absolute
#   photometric calibration is done. It contains the
#   GABODSID and the ZPCHOICHE of the solutions finally
#   entering the calibration (which do not need to be the 
#   same solutions as those previously selected on RUN basis).
# - The number of minimum overlap objects between chips
#   in relphotom was increased from 3 to 10.
#
# 14.08.2005:
# The call of the UNIX 'sort' program is now done
# via a variable 'P_SORT'.

. ${INSTRUMENT:?}.ini

# $1: main dir.
# $2: science dir. (the cat dir is a subdirectory of this)
# $3-$#: pairs of GABODSID and photometric solution that should
#        be considered in the photometric solution

#
# check consistency of command line arguments
if [ $# -gt 2 ] && [ $(( ($# - 2) % 2 )) -ne 0 ]; then
  echo "wrong command line syntax !!"
  exit 1
fi

CATS=`ls /$1/$2/cat/chip_*.cat6`

if [ "${NCHIPS}" -gt "1" ]; then
  ${P_LDACPASTE} -i ${CATS} -o /$1/$2/cat/chips.cat
else
  cp ${CATS} /$1/$2/cat/chips.cat
fi
${P_APLPHOTOM} -i /$1/$2/cat/chips.cat -o /$1/$2/cat/chips.cat11 \
               -c ${DATACONF}/fullphotom.conf.aplphotom \
               -ZP_ESTIMATES 0.0 -COEFS 0.0

${P_LDACTESTEXIST} -i /$1/$2/cat/chips.cat11 -t OBJECTS -k IMAFLAGS_ISO

if [ "$?" -gt "0" ]; then
  ${P_LDACADDKEY} -i /$1/$2/cat/chips.cat11 -o /$1/$2/cat/chips.cat1 \
                  -t OBJECTS -k IMAFLAGS_ISO 0 SHORT ""
else
  cp /$1/$2/cat/chips.cat11 /$1/$2/cat/chips.cat1
fi

${P_ASSOCIATE} -i /$1/$2/cat/chips.cat1 -o /$1/$2/cat/chips.cat2 \
               -c ${DATACONF}/fullphotom.conf.associate

${P_MAKESSC} -i /$1/$2/cat/chips.cat2 -o /$1/$2/cat/chips.pairs \
             -c ${DATACONF}/fullphotom.conf.make_ssc

FIXED_SWITCH=""
#
# Generate a fixed catalog if photometric information
# is available
${P_LDACTESTEXIST} -i /$1/$2/cat/chips.cat2 -t FIELDS -k ZP

if [ "$?" -eq "0" ]; then
  if [ -f /$1/$2/cat/fixed.asc ]; then
    rm /$1/$2/cat/fixed.asc
  fi  

  if [ -f ${TEMPDIR}/nights_$$.asc ]; then
    rm ${TEMPDIR}/nights_$$.asc
  fi
  # if we have nights to calibrate on the command line take this info,
  # otherwise calibrate with all preselected photometric information
  if [ $# -gt 2 ]; then  
    NAME=""  
    NIGHT=3
    CHOICE=4

    # the following adding of a running number is necessary to have the
    # correct indices in the fixed table (after a filtering of the FIELDS
    # table).
    ${P_LDACADDKEY} -i /$1/$2/cat/chips.cat2 -o ${TEMPDIR}/tmp.cat \
                    -t FIELDS -k FIELD_COUNT 1 COUNT ""

    while [ ${NIGHT} -le $(( $# - 1 )) ]
    do
      ${P_LDACFILTER} -i ${TEMPDIR}/tmp.cat -o ${TEMPDIR}/zp_$$.cat \
                      -t FIELDS -c "(GABODSID=${!NIGHT});"
      ${P_LDACTOASC} -b -i ${TEMPDIR}/zp_$$.cat -t FIELDS -k FIELD_COUNT ZP${!CHOICE} COEFF${!CHOICE} | \
        ${P_GAWK} '{if ($1!="#" && $2!="-1") print $1, $2, (-1)*$3}' > ${TEMPDIR}/zp_$$.asc

      if [ -s ${TEMPDIR}/zp_$$.asc ]; then
	cat ${TEMPDIR}/zp_$$.asc >> /$1/$2/cat/fixed.asc  
        echo ${!NIGHT} ${!CHOICE} >> ${TEMPDIR}/nights_$$.asc
      else
	echo "problem with night ${!NIGHT} and solution ${!CHOICE}; aborting !!"
	exit 1
      fi
      NAME="${NAME}_${!NIGHT}_${!CHOICE}"
      NIGHT=$(( ${NIGHT} + 2 ))
      CHOICE=$(( ${CHOICE} + 2 ))
    done
    ${P_ASCTOLDAC} -i /$1/$2/cat/fixed.asc -o /$1/$2/cat/chips.fixed${NAME}.cat \
        -t FIXED -c ${DATACONF}/asctoldac.fixed.conf
    FIXED_SWITCH="-f /$1/$2/cat/chips.fixed${NAME}.cat"
  else
    ${P_LDACTOASC} -r -b -i /$1/$2/cat/chips.cat2 -t FIELDS -k ZP COEFF | \
        ${P_GAWK} '{if ($1!="#" && $2!="-1") print $1, $2, (-1)*$3}' > /$1/$2/cat/fixed.asc

    if [ -s "/$1/$2/cat/fixed.asc" ]; then
      ${P_ASCTOLDAC} -i /$1/$2/cat/fixed.asc -o /$1/$2/cat/chips.fixed.cat \
          -t FIXED -c ${DATACONF}/asctoldac.fixed.conf
      FIXED_SWITCH="-f /$1/$2/cat/chips.fixed.cat"
    fi
    ${P_LDACTOASC} -b -i /$1/$2/cat/chips.cat2 -t FIELDS -k GABODSID ZPCHOICE |\
                   ${P_SORT} -g | uniq | ${P_GAWK} '($2>0) {print $0}' > ${TEMPDIR}/nights_$$.asc
  fi
fi

${P_RELPHOTOM} -i /$1/$2/cat/chips.cat2 -o /$1/$2/cat/chips_tmp.cat3 \
               -p /$1/$2/cat/chips.pairs -c ${DATACONF}/fullphotom.conf.relphotom \
               ${FIXED_SWITCH} -MINOBJECTS 10

#
# create a table SOLPHOTOM containing info on the nights and
# solutions that finally went into the photometric calibration.
if [ -s ${TEMPDIR}/nights_$$.asc ]; then
  ${P_ASCTOLDAC} -a ${TEMPDIR}/nights_$$.asc -o ${TEMPDIR}/nights_$$.cat \
                 -t SOLPHOTOM -c ${DATACONF}/asctoldac_solphotom.conf

  ${P_LDACADDTAB} -i /$1/$2/cat/chips_tmp.cat3 -o /$1/$2/cat/chips.cat3 \
                  -p ${TEMPDIR}/nights_$$.cat -t SOLPHOTOM
else
  cp /$1/$2/cat/chips_tmp.cat3 /$1/$2/cat/chips.cat3
fi

${P_APLPHOTOM} -i /$1/$2/cat/chips.cat3 -o /$1/$2/cat/chips.cat4 \
               -c ${DATACONF}/fullphotom.conf.aplphotom
