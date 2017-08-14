#!/bin/bash -xv

# script to estimate instrumental zeropoints,
# extinction coefficients and colorterms for
# photometric standard star observations

# 30.05.04:
# temporary files go to a TEMPDIR directory 

#$1: main directory
#$2: standard dir.
#$3: filter
#$4: color index (e.g. BmV)

# 04.09.2003 (Joerg Dietrich)
# Made filter and color index configurable
# Note problem: Needs GNU sort (-g option)!
#
# 18.02.2004:
# changed the location of the phot.sm script 
# to the sm_macros directory.
#
# 16.07.2004:
# corrected a bug in the TEMPDIR setting.
#
# 14.08.2005:
# The call of the UNIX 'sort' program is now done
# via a variable 'P_SORT'.

. ${INSTRUMENT}.ini

CI=`echo $4 | sed 's/m/-/g;'`
echo $CI

if [ ! -d "/$1/$2/calib" ]; then
  mkdir /$1/$2/calib
fi

${P_LDACPASTE} -i /$1/$2/cat/chip_*_merg.cat -t PSSC\
               -o ${TEMPDIR}/tmp_chips_$$.cat

${P_LDACFILTER} -i ${TEMPDIR}/tmp_chips_$$.cat -t PSSC\
		-c "(${3}mag < 99) AND ($4 < 99);"\
		-o /$1/$2/cat/allchips_merg.cat

${P_LDACTOASC} -i /$1/$2/cat/allchips_merg.cat  -t PSSC\
               -b -k Mag ${3}mag ${4} AIRMASS GABODSID IMAGEID > ${TEMPDIR}/phot_$$.asc

# get the nights and chips in the catalog
NIGHTMINMAX=`awk '{print $5}' phot_$$.asc | ${P_SORT} -g | uniq | tee ${TEMPDIR}/nights_$$.asc |\
awk '{if(NR==1) {min=$1}; max=$1} END {print min, max}'`

echo $NIGHTMINMAX
 
CHIPMINMAX=`awk '{print $6}' phot_$$.asc | ${P_SORT} -g | uniq | tee ${TEMPDIR}/chips_$$.asc |\
awk '{if(NR==1) {min=$1}; max=$1} END {print min, max}'`

echo $CHIPMINMAX
 
{
  echo 'macro read "'${SMMACROS}'/phot.sm"'
  echo 'myphot "psfile allchips.ps" "'${TEMPDIR}'/phot_'$$'.asc" '${NIGHTMINMAX} ${CHIPMINMAX} ${CI}''
} | ${P_SM}
mv allchips.ps /$1/$2/calib/

cat ${TEMPDIR}/nights_$$.asc |\
{
  while read night
  do
    {
      echo 'macro read "'${SMMACROS}'/phot.sm"'
      echo 'myphot "psfile night_'${night}'.ps" phot_'$$'.asc '${night} ${night} ${CHIPMINMAX} ${CI}''
    } | ${P_SM}
    mv night_${night}.ps /$1/$2/calib/
  done
}

cat ${TEMPDIR}/nights_$$.asc |\
{
  while read night
  do
    {
      cat ${TEMPDIR}/chips_$$.asc |\
      {
        while read chip 
        do
         {
           echo 'macro read "'${SMMACROS}'/phot.sm"'
           echo 'myphot "psfile night_'${night}'_'${chip}'.ps" "'${TEMPDIR}'/phot_'$$'.asc" '${night} ${night} ${chip} ${chip} ${CI}''
         } | ${P_SM}
	 mv night_${night}_${chip}.ps /$1/$2/calib/
	done 
      }
    }
  done
}

