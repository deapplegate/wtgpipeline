#!/bin/bash

# the script creates a plot for the distribution of
# absolutely corrected magnitude zeropoints in our
# photometric calibration, i.e. it plots the distribution
# of MAG_AUTO_CORRZP-MAG_AUTO_ZP_AVER which are found in
# the RELPHOTOM table.

#$1: main dir.
#$2: science dir.

. ${INSTRUMENT:?}.ini

if [ ! -f /$1/$2/cat/chips.cat4 ]; then
  echo "no chips.cat4 in /$1/$2/cat/; exiting"
  exit 1
fi
 
${P_LDACFILTER} -i  /$1/$2/cat/chips.cat4 -o ${TEMPDIR}/tmp.cat\
                -t RELPHOTOM -c "(MAG_AUTO_PHOT=1);"

if [ "$?" -eq "0" ]; then
  ${P_LDACTOASC} -b -i ${TEMPDIR}/tmp.cat -t RELPHOTOM \
                 -k MAG_AUTO_CORRZP MAG_AUTO_ZP_AVER | ${P_GAWK} \
                    '{print $1-$2}' > /$1/$2/cat/zps_$2.asc

  {
  echo 'macro read "'${SMMACROS}'/corrzpphot.sm"'
  echo 'corrzpdist "psfile /'$1'/'$2'/plots/zps_'$2'.eps" "/'$1'/'$2'/cat/zps_'$2'.asc"'
  } | ${P_SM}
  rm ${TEMPDIR}/tmp.cat
else
  echo "no photometric nights in this set selected !!"
fi

