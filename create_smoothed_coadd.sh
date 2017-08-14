#!/bin/bash -xv
######################
# $Id: create_smoothed_coadd.sh,v 1.2 2009-04-23 19:10:25 dapple Exp $
#
# Adapted from doall_science_MEGAPRIME.sh by T. Erben
######################

# $1 Main directory
# $2 Coadd List of filters
# $3 Science directory
# $4 coadd identifier directory
# $5 coadd image

. progs.ini


MD=$1
FILTERS=$2
SCIENCE=$3
COADDIDENT=$4
IMAGE=$5

IMAGEBASE=`basename $IMAGE .fits`

# first determine the seeing in all images
# and also provide the maxium seeing measures:
MAXSEEING=0
SEEINGS=""
for FILTER in ${FILTERS}
do

    
  IMDIR=${MD}/${FILTER}/${SCIENCE}/coadd_${COADDIDENT}/

  SEEINGCURR=`./determine_seeing.sh ${IMDIR} \
      ${IMAGEBASE}.fits \
      ${IMAGEBASE}.weight.fits \
      ${IMAGEBASE}.flag.fits \
      "4000 4000" \
      ${IMDIR}/../seeing_${COADDIDENT} \
      ${IMAGEBASE}.seeing.fits\
      ${IMAGEBASE}.seeing.weight.fits \
      ${IMAGEBASE}.seeing.flag.fits | \
      awk 'END{print $NF}'`

  if [ "${SEEINGCURR}" = "ERROR" ]; then
      echo "Problem Measuring Seeing for ${FILTER}!!!!!"
      exit 1
  fi

  MAXSEEING=`awk 'BEGIN { if('${MAXSEEING}' < '${SEEINGCURR}') {
                            print '${SEEINGCURR}'
                          } else {
                            print '${MAXSEEING}'
                          }}'`

  SEEINGS="${SEEINGS} ${SEEINGCURR}"
done

## filter the small subimages we generated to inspect
## the seeing:
#i=1
#SEEINGFILTEREDMAX=0
#SEEINGFILTEREDMIN=10
#
#for FILTER in ${FILTERS}
#do
#
#
#  IMDIR=${MD}/${FILTER}/${SCIENCE}/seeing_${COADDIDENT}
#
#  # to know where the seeing summary files goes:
#  if [ $i -eq 1 ]; then
#    IMDIRREF=${IMDIR}  
#
#    test -f ${IMDIRREF}/${FIELD}_seeings_small_`echo ${FILTERS} |\
#            awk 'BEGIN {FS = " "; OFS = ""} {$1 = $1; print $0}'`.asc && \
#            rm ${IMDIRREF}/${FIELD}_seeings_small_`echo ${FILTERS} |\
#            awk 'BEGIN {FS = " "; OFS = ""} {$1 = $1; print $0}'`.asc
#  fi
#
#  SEEINGCURR=`echo ${SEEINGS} | awk '{print $'$i'}'`
#
#  # we do not need to apply any filtering on the worst seeing image:
#  APPLYFILTER=`awk 'BEGIN {
#               if(('${MAXSEEING}' - '${SEEINGCURR}') > 1.0e-03) {
#                 print 1;
#               } else {
#                 print 0;
#               }}'`
#
#  if [ ${APPLYFILTER} -eq 1 ]; then
#    ./create_gaussfiltered_image.sh ${IMDIR}\
#       ${IMAGEBASE}.seeing.fits \
#       ${IMAGEBASE}.seeing.weight.fits \
#       ${SEEINGCURR} ${MAXSEEING} \
#       ${IMAGEBASE}.seeing.filtered.fits
#  else
#    cp ${IMDIR}/${IMAGEBASE}.seeing.fits \
#       ${IMDIR}/${IMAGEBASE}.seeing.filtered.fits
#  fi
#
#  SEEINGFILTERED=`./determine_seeing.sh ${IMDIR} \
#      ${IMAGEBASE}.seeing.filtered.fits\
#      ${IMAGEBASE}.seeing.weight.fits\
#      ${IMAGEBASE}.seeing.flag.fits\
#      '6000 6000' | awk 'END {print $NF}'`
#
#  SEEINGFILTEREDMAX=`awk 'BEGIN {
#                        if ('${SEEINGFILTEREDMAX}' < '${SEEINGFILTERED}') {
#                          print '${SEEINGFILTERED}'
#                        } else {
#                          print '${SEEINGFILTEREDMAX}'
#                        }}'`
#
#  SEEINGFILTEREDMIN=`awk 'BEGIN {
#                        if ('${SEEINGFILTEREDMIN}' > '${SEEINGFILTERED}') {
#                          print '${SEEINGFILTERED}'
#                        } else {
#                          print '${SEEINGFILTEREDMIN}'
#                        }}'`
#
#  echo "${FIELD} ${FILTER} ${SEEINGCURR} ${SEEINGFILTERED}" >> \
#    ${IMDIRREF}/${FIELD}_seeings_small_`echo ${FILTERS} |\
#    awk 'BEGIN {FS=" "; OFS=""} {$1 = $1; print $0}'`.asc
#
#  i=$(( $i + 1 ))
#
#done
#
#
#
## check if we continue; we do if the maximum and minimum seeing
## of the filtered images do not differ by more than 0.1 arcsec:
#CONTINUE=`awk 'BEGIN { 
#               if('${SEEINGFILTEREDMAX}' - '${SEEINGFILTEREDMIN}' < 0.2) {
#                 print 1;
#               }
#               else {
#                 print 0;
#               }}'`
#
SEEINGFILTEREDMAX=0
SEEINGFILTEREDMIN=10
i=1
for FILTER in ${FILTERS}
do


    IMDIR=${MD}/${FILTER}/${SCIENCE}/coadd_${COADDIDENT}
    IMDIRDEST=${IMDIR}

    # to know where the seeing summary files goes:
    if [ $i -eq 1 ]; then
      IMDIRDESTREF=${IMDIRDEST}  

      test -f ${IMDIRDESTREF}/${FIELD}_seeings_`echo ${FILTERS} |\
           awk 'BEGIN {FS = " "; OFS = ""} {$1 = $1; print $0}'`.asc && \
           rm ${IMDIRDESTREF}/${FIELD}_seeings_`echo ${FILTERS} |\
           awk 'BEGIN {FS = " "; OFS = ""} {$1 = $1; print $0}'`.asc 
    fi
   
    test -d ${IMDIRDEST} || mkdir ${IMDIRDEST}

    SEEINGCURR=`echo ${SEEINGS} | awk '{print $'$i'}'`

    # we do not need to apply any filtering on the worst seeing image:
    APPLYFILTER=`awk 'BEGIN {
                 if (('${MAXSEEING}' - '${SEEINGCURR}') > 1.0e-03) {
                   print 1;
                 } else {
                   print 0;
                 }}'`

    if [ ${APPLYFILTER} -eq 1 ]; then
      ./create_gaussfiltered_image.sh ${IMDIRDEST}\
         ${IMAGEBASE}.fits \
         ${IMAGEBASE}.weight.fits \
         ${SEEINGCURR} ${MAXSEEING} \
         ${IMAGEBASE}.smooth.fits
    else
      cp ${IMDIRDEST}/${IMAGEBASE}.fits \
      ${IMDIRDEST}/${IMAGEBASE}.smooth.fits
    fi       

    SEEINGFILTERED=`./determine_seeing.sh ${IMDIRDEST} \
      ${IMAGEBASE}.smooth.fits \
      ${IMAGEBASE}.weight.fits \
      ${IMAGEBASE}.flag.fits \
      '8000 8000' | awk 'END{print $NF}'`

    if [ "${SEEINGFILTERED}" = "ERROR" ]; then
	echo "Problem Measuring Seeing for ${FILTER}!!!!!"
	exit 1
    fi

    # update the SEEING header keyword in the filtered image:
    replacekey \
      ${IMDIRDEST}/${IMAGEBASE}.smooth.fits\
      "SEEING  = ${SEEINGFILTERED}" SEEING  

    SEEINGFILTEREDMAX=`awk 'BEGIN {
                        if ('${SEEINGFILTEREDMAX}' < '${SEEINGFILTERED}') {
                          print '${SEEINGFILTERED}'
                        } else {
                          print '${SEEINGFILTEREDMAX}'
                        }}'`

    SEEINGFILTEREDMIN=`awk 'BEGIN {
                        if ('${SEEINGFILTEREDMIN}' > '${SEEINGFILTERED}') {
                          print '${SEEINGFILTERED}'
                        } else {
                          print '${SEEINGFILTEREDMIN}'
                        }}'`


        # security touch to force update of image access times
    # (problems with heavy I/O when NFS might not update images
    # properly!)
    touch \
      ${IMDIRDEST}/${IMAGEBASE}.smooth.fits

    echo "${FIELD} ${FILTER} ${SEEINGFILTERED}" >> \
      ${IMDIRDESTREF}/${FIELD}_seeings_`echo ${FILTERS} |\
    awk 'BEGIN {FS = " "; OFS = ""} {$1 = $1; print $0}'`.asc

    i=$(( $i + 1 ))
  done  

awk 'BEGIN { 
       if('${SEEINGFILTEREDMAX}' - '${SEEINGFILTEREDMIN}' < 0.2) {
                 print "All Set";
       }
       else {
                 print "!!!!!!!!WARNING! BAD CONVOLUTION!!!!!!!!!!!!!!!!!!!";
       }}'


