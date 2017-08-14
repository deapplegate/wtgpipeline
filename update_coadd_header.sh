#!/bin/bash -xv
. BonnLogger.sh
. log_start
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

#$1: main dir
#$2: science dir
#$3: coadd identifier
#$4: table in coaddidentifier.cat where to find EXPTIME
#$5: name of coadded image (without .fits extension)
#    we assume that the weight has the name $4.weight.fits
#$6: Mag Zeropoint
#$7: 'AB' or 'Vega'. The type of the mnagnitude zeropoint.
#    It is used for the comment of the MAGZP header keyword.
#$8: coaddition condition

. ${INSTRUMENT:?}.ini
. bash_functions.include

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
if [ -f /$1/$2/$3.cat ]; then
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

  rm ${TEMPDIR}/tmp_$$.cat
fi

#
# determine the seeing in the coadded image:
#
# first create a simple SExtractor parameter file. It
# only contains three entries and is very special for
# this script. Hence we do not create a new pipeline
# config file:
{
    echo "NUMBER"
    echo "FWHM_IMAGE"
    echo "IMAFLAGS_ISO"
} > ${TEMPDIR}/seeing_sexparam.asc_$$

${P_SEX} /$1/$2/coadd_$3/$5.fits -c ${CONF}/postcoadd.conf.sex \
           -CATALOG_NAME ${TEMPDIR}/seeing_$$.cat \
           -FILTER_NAME ${DATACONF}/default.conv\
           -WEIGHT_IMAGE /$1/$2/coadd_$3/$5.weight.fits \
           -WEIGHT_TYPE MAP_WEIGHT -FLAG_IMAGE /$1/$2/coadd_$3/$5.flag.fits \
           -FLAG_TYPE MAX \
           -DETECT_THRESH 10 -DETECT_MINAREA 10 \
           -ANALYSIS_THRESH 15\
           -PARAMETERS_NAME ${TEMPDIR}/seeing_sexparam.asc_$$

${P_LDACCONV}  -i ${TEMPDIR}/seeing_$$.cat -o ${TEMPDIR}/seeing_ldac.cat_$$\
               -b 1 -c "sex" -f R

${P_LDACFILTER} -i ${TEMPDIR}/seeing_ldac.cat_$$ \
                -o ${TEMPDIR}/seeing_ldac_filt.cat_$$ -c "(IMAFLAGS_ISO<16);"

${P_LDACTOASC} -b -i ${TEMPDIR}/seeing_ldac_filt.cat_$$ -t OBJECTS\
               -k FWHM_IMAGE > ${TEMPDIR}/seeing_$$.asc

CDELT2=`${P_DFITS} /$1/$2/coadd_$3/$5.fits | ${P_FITSORT} -d CDELT2 | awk '{print $2}'`
CD22=`${P_DFITS} /$1/$2/coadd_$3/$5.fits | ${P_FITSORT} -d CD2_2 | awk '{print $2}'`

if [ "${CDELT2}" != "KEY_N/A" ]; then
	PXSCALE=`${P_GAWK} 'BEGIN{print '${CDELT2}'*3600.}'`
elif [ "${CD22}" != "KEY_N/A" ]; then
	PXSCALE=`${P_GAWK} 'BEGIN{print '${CD22}'*3600.}'`
fi

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


rm ${TEMPDIR}/seeing_sexparam.asc_$$
rm ${TEMPDIR}/seeing_$$.cat
rm ${TEMPDIR}/seeing_$$.asc
rm ${TEMPDIR}/seeing_ldac.cat_$$
rm ${TEMPDIR}/seeing_ldac_filt.cat_$$

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

# the following expression for the GAIN is only valid if the unit of the co-added
# inage is ADU/sec and if a mean (weighted mean) co-addition was performed.
value ${GAINEFF}
writekey /$1/$2/coadd_$3/$5.fits GAIN "${VALUE} / effective GAIN for SExtractor" REPLACE

value $6
writekey /$1/$2/coadd_$3/$5.fits MAGZP "${VALUE} / $7 Magnitude Zeropoint" REPLACE

value ${SEEING}
writekey /$1/$2/coadd_$3/$5.fits SEEING "${VALUE} / measured image Seeing (arcsec)" REPLACE
writekey /$1/$2/coadd_$3/$5.fits SEEINGSE "${VALUE} / measured image Seeing (arcsec)" REPLACE

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

#rm ${TEMPDIR}/coaddcondition_$$.txt
 
#
# add information about the photometric solutions entering the
# coadded image
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

  rm ${TEMPDIR}/nights_$$.txt
fi



log_status $?
