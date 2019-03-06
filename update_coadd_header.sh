#!/bin/bash
set -xv
#adam-example# ./update_coadd_header.sh /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-J-B SCIENCE MACS1115+01_all STATS coadd -1.0 AB '((((RA>(168.96708333-0.5))AND(RA<(168.96708333+0.5)))AND((DEC>(1.49805556-0.5))AND(DEC<(1.49805556+0.5))))AND(SEEING<1.9));' 2>&1 | tee -a OUT-uch.log4

#adam-tmp# source deactivate astroconda

#adam-BL#. BonnLogger.sh
#adam-BL#. log_start
# The script makes an update of headers from finally coadded
# images. For the moment, the added header keywords are:
# Total exposure time, total gain, magnitude
# zeropoint and coaddition condition.
#
# We assume that there is a catalog coaddidentifier.cat
# in the catalogs directory of the set and that
# keywords DUMMY0, DUMMY1 and so on are in the coadded
# image (how many of the DUMMY keywords are needed is not
# clear in the beginning)

#
# 29.01.2006:
# The table in the coaddidentifier.cat catalog in which
# to find EXPTIME keyword is now a command line argument.
#
# 02.02.2006:
# Bug fix: The table given as 4th command line argument
# actually was not used.
#
# 26.04.2006:
# The catalog table from which to read ($3.cat) was 
# hardcoded to STATS instead of using the 4th command 
# line argument.
#
# 30.04.2006:
# gawk was called directly one time instead via the
# P_GAWK variable. 
#
# 06.11.2006:
# - The type of magnitude zeropoint (AB or Vega) is
#   now a command line argument. It is written to the
#   corresponding comment line; before always Vega was
#   written as comment.
# - some temporary files now get unique names including
#   the process number.
#
# 06.12.2006:
# The FITS key strings for coaddition conditions and
# photometric solutions are up to 70 characters now
# (instead of 20 as before).
#
# 16.02.2007:
# - The seeing is now calculated from object catalogues cleaned
#   for sources having an external flag unequal to zero.
#
# 24.04.2007:
# I make sure that EXPTIME, SEEING and GAINEFF are FLOAT FITS
# cards (if they could be represented as integers they were stored
# as INTEGER FITS cards).

# TODO:
# Include a proper calculation of the GAIN if the
# co-addition is not weighted mean.

#$1: main dir							(ex. ${SUBARUDIR}/${cluster}/${filter})
#$2: science dir						(ex. SCIENCE)
#$3: coadd identifier						(ex. ${cluster}_${coadd}, ${cluster}_gabodsid${GABODSID}, etc.)
#$4: table in coaddidentifier.cat where to find EXPTIME		(ex. STATS, CHIPS_STATS, etc.)
#$5: name of coadded image (without .fits extension)		(ex. coadd)
#    we assume that the weight has the name $4.weight.fits	
#$6: Mag Zeropoint						(ex. ${MAGZP})
#$7: 'AB' or 'Vega'. The type of the magnitude zeropoint.	(ex. AB or Vega)
#    It is used for the comment of the MAGZP header keyword	
#$8: coaddition condition					(ex. ${CONDITION})

. ${INSTRUMENT:?}.ini > /tmp/SUBARU.out 2>&1
. progs.ini > /tmp/SUBARU.out 2>&1
. bash_functions.include > /tmp/bash.out 2>&1

# set the coaddition condition to NONE if an empty string is
# given:
if [ -n $8 ]; then
  COADDCONDITION=$8
else
  COADDCONDITION="NONE"
fi

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

CDELT2=`${P_DFITS} /$1/$2/coadd_$3/$5.fits | ${P_FITSORT} -d CDELT2 | awk '{print $2}'`
CD22=`${P_DFITS} /$1/$2/coadd_$3/$5.fits | ${P_FITSORT} -d CD2_2 | awk '{print $2}'`

if [ "${CDELT2}" != "KEY_N/A" ]; then
	PXSCALE=`${P_GAWK} 'BEGIN{print '${CDELT2}'*3600.}'`
elif [ "${CD22}" != "KEY_N/A" ]; then
	PXSCALE=`${P_GAWK} 'BEGIN{print '${CD22}'*3600.}'`
fi

#
# determine the seeing in the coadded image:
#

image=/$1/$2/coadd_$3/$5.fits
fwhm=`${P_DFITS} ${image} | ${P_FITSORT} -d MYSEEING | awk '{print $2}'`
if [ "${fwhm}" == "KEY_N/A" ]; then
	echo "adam update_coadd_header.sh: SEEING header keyword and MYSEEING header keyword isn't in " ${image}
	#adam-SEEING# use myseeing from CRNitschke pipeline if it's possible!
	BASE=${3##${cluster}_}
	rms_fwhm_dt_ft=( `grep -h $BASE /u/ki/awright/wtgpipeline/CRNitschke_final_${cluster}_*.txt | head -n 1 | awk '{print $2, $3, $4, $5}'`)
	Nelements=${#rms_fwhm_dt_ft[@]}
	if [ ${Nelements} -eq 4 ]; then
		fwhm=${rms_fwhm_dt_ft[1]}
		echo "adam FIXED: MYSEEING has been found in ascii file: fwhm=" $fwhm
	fi
fi
#       echo "MYSEEING header keyword isn't in " ${image}
#	fwhm=`${P_DFITS} ${image} | ${P_FITSORT} -d SEEING | awk '{print $2}'`
#	if [ "${fwhm}" == "KEY_N/A" ]; then
if [ "${fwhm}" == "KEY_N/A" ]; then
	fwhm_test="0"
else
	echo "MYSEEING: fwhm=" $fwhm
	fwhm_gt_test=$(echo "${fwhm}>0.1" | bc)
	fwhm_lt_test=$(echo "${fwhm}<1.9" | bc)
	fwhm_test=$(echo "${fwhm_lt_test}*${fwhm_gt_test}" | bc)
fi
echo "fwhm_test=" $fwhm_test

export HEADASNOQUERY=
export HEADASPROMPT=/dev/null
fthedit /$1/$2/coadd_$3/$5.fits DUMMY0 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY1 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY2 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY3 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY4 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY5 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY6 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY7 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY8 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY9 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY10 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY11 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY12 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY13 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY14 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY15 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY16 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY17 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY18 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY19 add 0
fthedit /$1/$2/coadd_$3/$5.fits DUMMY20 add 0
#adam-SEEING# if not 0.1<MYSEEING<1.9 or Nelements!=4 then use the crappy method!
if [ "${fwhm_test}" == "1" ]; then
	MYSEEING=$fwhm
	value ${MYSEEING}
	writekey /$1/$2/coadd_$3/$5.fits MYSEEING "${VALUE} / my calculated seeing value (arcsec)" REPLACE
else
	echo "update_coadd_header.sh: MYSEEING header keyword can not be found! calculating fwhm using get_seeing method."
fi

## now put the SEEING in there regardless
# first create a simple SExtractor parameter file. It
# only contains three entries and is very special for
# this script. Hence we do not create a new pipeline
# config file:
{
    echo "NUMBER"
    echo "X_IMAGE "
    echo "Y_IMAGE "
    echo "FWHM_IMAGE"
    echo "IMAFLAGS_ISO"
} > ${TEMPDIR}/seeing_sexparam.asc_$$

${BIN}/sex_theli /$1/$2/coadd_$3/$5.fits -c ~/wtgpipeline/postcoadd.conf.sex \
	   -CATALOG_NAME ${TEMPDIR}/seeing_$$.cat \
	   -FILTER_NAME ${DATACONF}/default.conv \
	   -WEIGHT_IMAGE /$1/$2/coadd_$3/$5.weight.fits \
	   -WEIGHT_TYPE MAP_WEIGHT -FLAG_IMAGE /$1/$2/coadd_$3/$5.flag.fits \
	   -FLAG_TYPE MAX \
	   -DETECT_THRESH 10 -DETECT_MINAREA 10 \
	   -ANALYSIS_THRESH 15 \
	   -BACK_TYPE MANUAL -BACK_VALUE 0.0 \
	   -PARAMETERS_NAME ${TEMPDIR}/seeing_sexparam.asc_$$
#adam-old#START
#${P_SEX} /$1/$2/coadd_$3/$5.fits -c ${CONF}/postcoadd.conf.sex \
#	   -CATALOG_NAME ${TEMPDIR}/seeing_$$.cat \
#	   -FILTER_NAME ${DATACONF}/default.conv \
#	   -WEIGHT_IMAGE /$1/$2/coadd_$3/$5.weight.fits \
#	   -WEIGHT_TYPE MAP_WEIGHT -FLAG_IMAGE /$1/$2/coadd_$3/$5.flag.fits \
#	   -FLAG_TYPE MAX \
#	   -DETECT_THRESH 10 -DETECT_MINAREA 10 \
#	   -ANALYSIS_THRESH 15 \
#	   -BACK_TYPE MANUAL -BACK_VALUE 0.0 \
#	   -PARAMETERS_NAME ${TEMPDIR}/seeing_sexparam.asc_$$
#adam-old#END



#adam: try this out -BACK_TYPE MANUAL -BACK_VALUE 0.0 \

#adam: having thresholds of 10 is too high, using the defaults in postcoadd.conf.sex, which are like 2.5
#adam: filtering gives us less detections (maybe that's good, maybe not?), I'll keep it on for now.
#${P_SEX} /$1/$2/coadd_$3/$5.fits -c ${CONF}/postcoadd.conf.sex \
#           -CATALOG_NAME ${TEMPDIR}/seeing_$$.cat \
#           -FILTER_NAME ${DATACONF}/default.conv\
#	   -FLAG_IMAGE /$1/$2/coadd_$3/$5.flag.fits \
#	   -DETECT_THRESH 2 -ANALYSIS_THRESH 5 \
#           -FLAG_TYPE MAX \
#	   -GAIN ${GAIN} -PIXEL_SCALE ${PXSCALE} -FILTER N \
#           -PARAMETERS_NAME ${TEMPDIR}/seeing_sexparam.asc_$$
#           -WEIGHT_IMAGE /$1/$2/coadd_$3/$5.weight.fits \
#           -WEIGHT_TYPE MAP_WEIGHT 

${P_LDACCONV}  -i ${TEMPDIR}/seeing_$$.cat -o ${TEMPDIR}/seeing_ldac.cat_$$\
               -b 1 -c "sex" -f R

${P_LDACFILTER} -i ${TEMPDIR}/seeing_ldac.cat_$$ \
                -o ${TEMPDIR}/seeing_ldac_filt.cat_$$ -c "(IMAFLAGS_ISO<16);"

${P_LDACTOASC} -b -i ${TEMPDIR}/seeing_ldac_filt.cat_$$ -t OBJECTS\
               -k FWHM_IMAGE | sed '/0.00/d' > ${TEMPDIR}/seeing_$$.asc
${P_LDACTOASC} -b -i ${TEMPDIR}/seeing_ldac_filt.cat_$$ -t OBJECTS\
               -k Xpos Ypos FWHM_IMAGE | sed '/0.00/d' > $1/$2/coadd_$3/$5.get_seeing.filtered.tsv
${P_LDACTOASC} -b -i ${TEMPDIR}/seeing_ldac.cat_$$ -t OBJECTS\
               -k Xpos Ypos FWHM_IMAGE | sed '/0.00/d' > $1/$2/coadd_$3/$5.get_seeing.unfiltered.tsv

NLINES=`wc ${TEMPDIR}/seeing_$$.asc | awk '{print $1}'`

SEEING=`${P_GAWK} 'BEGIN {
                       binsize=10./'${NLINES}';
                       if(binsize<0.01) { binsize=0.01 } 
          	           nbins=int(((3.0-0.3)/binsize)+0.5);
                       for(i=1; i<=nbins; i++) { bin[i]=0 }
                   }
                   { 
                       if(($1*'${PXSCALE}' > 0.3) && ($1*'${PXSCALE}' < 3.0))
                       { 
                           actubin=int(($1*'${PXSCALE}'-0.3)/binsize);
		                   bin[actubin]+=1; 
                       }
                   }
	               END {
                       max=0; k=0 
		               for(i=1;i<=nbins; i++)
		               {
		                   if(bin[i]>max)
		                   { 
		                       max=bin[i];
		                       k=i;
		                   }
		               }
		               print 0.3+k*binsize
                   }' ${TEMPDIR}/seeing_$$.asc`
#adam-tmp# rm -f ${TEMPDIR}/seeing_sexparam.asc_$$
#adam-tmp# rm -f ${TEMPDIR}/seeing_$$.cat
#adam-tmp# rm -f ${TEMPDIR}/seeing_$$.asc
#adam-tmp# rm -f ${TEMPDIR}/seeing_ldac.cat_$$
#adam-tmp# rm -f ${TEMPDIR}/seeing_ldac_filt.cat_$$

#
# write keywords in header

# first make sure that EXPTIME, SEEING and GAINEFF are 'real' number, i.e.
# they end with a ".0" if they are represented by integers right now.
# This ensures that FITS keywords are treated as FLOATS (and not errorneously
# as ints) afterwards.
EXPTIME=`echo ${EXPTIME} | awk '{if(($1-int($1))<1.0e-06) { print $1".0" } else {print $1}}'`
GAINEFF=`echo ${GAINEFF} | awk '{if(($1-int($1))<1.0e-06) { print $1".0" } else {print $1}}'`
SEEING=`echo ${SEEING} | awk '{if(($1-int($1))<1.0e-06) { print $1".0" } else {print $1}}'`

value ${EXPTIME}
writekey /$1/$2/coadd_$3/$5.fits EXPTIME "${VALUE} / total Exposure Time" REPLACE


EXPID=${3##${cluster}_}
value ${EXPID}
#adam-SHNT# check that this is the right test
if [ -n "${EXPID}" ]; then
	writekey /$1/$2/coadd_$3/$5.fits EXPID "${VALUE} / kind of coadd" REPLACE
fi
#adam-SHNT# make a MYSEEING (with comment) and put the default get_seeing calculation in there as SEEING
echo "EXPID=$EXPID MYSEEING=$MYSEEING SEEING=$SEEING"

# the following expression for the GAIN is only valid if the unit of the co-added
# inage is ADU/sec and if a mean (weighted mean) co-addition was performed.
value ${GAINEFF}
writekey /$1/$2/coadd_$3/$5.fits GAIN "${VALUE} / effective GAIN for SExtractor" REPLACE

value $6
writekey /$1/$2/coadd_$3/$5.fits MAGZP "${VALUE} / $7 Magnitude Zeropoint" REPLACE

echo  "update_coadd_header.sh: SEEING=" $SEEING
value ${SEEING}
writekey /$1/$2/coadd_$3/$5.fits GSEEING "${VALUE} / measured image Seeing (arcsec)" REPLACE
#adam# don't write these since they might not be the actual MYSEEING values gotten with BartStar.py
#writekey /$1/$2/coadd_$3/$5.fits SEEINGSE "${VALUE} / measured image Seeing (arcsec)" REPLACE
#writekey /$1/$2/coadd_$3/$5.fits MYSEEING "${VALUE} / measured image Seeing (arcsec)" REPLACE

#
# add information on the condition on the input images
# to enter the stacking process.
writecommhis /$1/$2/coadd_$3/$5.fits COMMENT ""
writecommhis /$1/$2/coadd_$3/$5.fits COMMENT "Conditions on the input images:"
#
# split the coaddition condition in strings of length 20 if necessary
echo ${COADDCONDITION}
echo ${COADDCONDITION} | ${P_GAWK} 'BEGIN {len=20} 
                      {
                          if((n=length($1)/len)-(int(length($1)/len))>0.001)
                          { 
                              n=n+1; 
                          }
                          pos=1; 
                          for(i=1; i<=n; i++) 
                          {
                              print substr($1,pos,len); 
                              pos+=len;
                          }
                      }' > ${TEMPDIR}/coaddcondition_$$.txt

j=1
while read string
do
  writekey /$1/$2/coadd_$3/$5.fits COND${j} "'${string}'" REPLACE
  j=$(( $j + 1 ))
done < ${TEMPDIR}/coaddcondition_$$.txt

rm -f ${TEMPDIR}/coaddcondition_$$.txt
 
#
# add information about the photometric solutions entering the
# coadded image
if [ -f /$1/$2/cat/chips_phot.cat5 ]; then
	${P_LDACTESTEXIST} -i /$1/$2/cat/chips_phot.cat5 -t SOLPHOTOM
	if [ "$?" -eq "0" ]; then
	  ${P_LDACTOASC} -i /$1/$2/cat/chips_phot.cat5 -b -t SOLPHOTOM | \
	  ${P_GAWK} '{printf $0"; "}' | \
	  ${P_GAWK} 'BEGIN {len=69} 
		     {
			 if((n=length($0)/len)-(int(length($0)/len))>0.001) 
			 { 
			     n=n+1; 
			 } 
			 pos=1; 
			 for(i=1; i<=n; i++) 
			 {
			     print substr($0,pos,len); 
			     pos+=len;
			 }
		     }' > ${TEMPDIR}/nights_$$.txt
	  j=1
	  while read string
	  do
	    writekey /$1/$2/coadd_$3/$5.fits SOLPH${j} "'${string}'" REPLACE
	    j=$(( $j + 1 ))
	  done < ${TEMPDIR}/nights_$$.txt

	  rm -f ${TEMPDIR}/nights_$$.txt
	fi
fi

./adam_quicktools_fix_header_verify.py /$1/$2/coadd_$3/$5.fits
. ~/wtgpipeline/progs.ini
. ~/wtgpipeline/SUBARU.ini
./SeeingClearly_for_coadds.py /$1/$2/coadd_$3/$5.fits
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	echo "adam-Error (update_coadd_header.sh seeing calc failed): ./SeeingClearly_for_coadds.py /$1/$2/coadd_$3/$5.fits"
fi

echo "ds9e /$1/$2/coadd_$3/$5.fits -catalog import tsv $1/$2/coadd_$3/$5.get_seeing.filtered.tsv -catalog import tsv $1/$2/coadd_$3/$5.get_seeing.unfiltered.tsv &"
