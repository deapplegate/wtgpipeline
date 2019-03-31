#!/bin/bash
set -xv
#adam-example# ./fix_coadd_gabodsid-update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//Zw2089/W-S-Z+/ SCIENCE Zw2089_gabodsid6192 STATS coadd -1.0 AB

#adam-tmp# source deactivate astroconda

#$1: main dir							(ex. ${SUBARUDIR}/${cluster}/${filter})
#$2: science dir						(ex. SCIENCE)
#$3: coadd identifier						(ex. ${cluster}_${coadd}, ${cluster}_gabodsid${GABODSID}, etc.)
#$4: table in coaddidentifier.cat where to find EXPTIME		(ex. STATS, CHIPS_STATS, etc.)
#$5: name of coadded image (without .fits extension)		(ex. coadd)
#    we assume that the weight has the name $4.weight.fits	
config=`dfits /$1/$2/coadd_$3/$5.fits | fitsort CONFIG | tail -n 1 | awk '{print $2}'`
. ${INSTRUMENT:?}_${config}.ini > /tmp/SUBARU.out 2>&1
. progs.ini > /tmp/SUBARU.out 2>&1
. bash_functions.include > /tmp/bash.out 2>&1

# set the coaddition condition to NONE if an empty string is
# given:

# get EXPTIME and hence effective gain from tha coaddition catalog.
EXPTIME=0.0
GAINEFF=0.0
if [ -f "/$1/$2/$3.cat" ]; then
#  ${P_LDACFILTER} -i /$1/$2/$3.cat -t $4 \
#                  -o ${TEMPDIR}/tmp_$$.cat -c "($3=1);"
#
#  EXPTIME=`${P_LDACTOASC} -b -i ${TEMPDIR}/tmp_$$.cat -t $4 -k EXPTIME |\
#           ${P_GAWK} 'BEGIN{time=0} {time=time+$1} END {print time}'`

case $4 in
"CHIPS_STATS" )
	EXPTIME=`${P_LDACTOASC} -i /$1/$2/$3.cat -t $4 -s -b \
                 -k EXPTIME $3 | \
                 ${P_GAWK} '{if($2==1) print $1}' |\
                 ${P_GAWK} 'BEGIN{time=0} {time=time+$1} END {print time/'${NCHIPS}'}'`;;
* )
	EXPTIME=`${P_LDACTOASC} -i /$1/$2/$3.cat -t $4 -s -b \
                 -k EXPTIME $3 | \
                 ${P_GAWK} '{if($2==1) print $1}' |\
                 ${P_GAWK} 'BEGIN{time=0} {time=time+$1} END {print time}'`;;
esac

  GAINEFF=`${P_GAWK} 'BEGIN {print '${GAIN}'*'${EXPTIME}'}'`

  rm -f ${TEMPDIR}/tmp_$$.cat
fi

#
# determine the seeing in the coadded image:
#

# write keywords in header

# first make sure that EXPTIME, SEEING and GAINEFF are 'real' number, i.e.
# they end with a ".0" if they are represented by integers right now.
# This ensures that FITS keywords are treated as FLOATS (and not errorneously
# as ints) afterwards.
EXPTIME=`echo ${EXPTIME} | awk '{if(($1-int($1))<1.0e-06) { print $1".0" } else {print $1}}'`
GAINEFF=`echo ${GAINEFF} | awk '{if(($1-int($1))<1.0e-06) { print $1".0" } else {print $1}}'`

value ${EXPTIME}
writekey /$1/$2/coadd_$3/$5.fits EXPTIME "${VALUE} / total Exposure Time" REPLACE


value ${GAINEFF}
writekey /$1/$2/coadd_$3/$5.fits GAIN "${VALUE} / effective GAIN for SExtractor" REPLACE

exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	echo "adam-Error writekey failed!"
	exit 1
fi

dfits /$1/$2/coadd_$3/$5.fits | fitsort GABODSID CONFIG GAIN EXPTIME
