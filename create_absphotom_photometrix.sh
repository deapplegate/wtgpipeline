#!/bin/bash
set -xv
# SCRIPT: create_absphotom_photometrix.sh
#adam-BL#. BonnLogger.sh
#adam-BL#. log_start
# The script estimates an absolute photometric zeropoint for the
# coadded image of a set. It relies on presence of information on
# relative photometry (PHOTOMETRIX) and photometric zeropoints.  If
# the script is called with the first two arguments only it uses the
# default zeropoints to estimate the zeropoint of a stacked image.

# 29.01.2006:
# The table in which to find info. on the abolute photometry
# is now called STATS instead of IMAGES.
#
# 25.05.2007:
# The calculation of the final zeropoint has been refined.
# If more than 20 images contribte to the final zeropoint calculation
# we now perform a sigmaclipping on the sample before estimating the
# final zeropoint. This was done because in CFHTLS Deep processings
# we noted photometrically marked frames that falsified the result.
# The reason in the actual case was a wrong listed exposure time in
# an image header.
#
# TODO:
# - The sigmaclipping on the zeropoint calculation (introduced
#   on (25.05.2007) might be refined. It is now a simple rejection
#   of points deviating three sigmas from the mean. This rejection
#   is done three times at most.
# - Better checking of catalogues entering this script. For instance
#   we should react on cases where relative zeropoints are not found
#   in the input 'chips.cat5' catalogue.

. ${INSTRUMENT:?}.ini  > /tmp/SUBARU.out 2>&1

# $1: main dir.
# $2: science dir. (the cat dir is a subdirectory of this)
# $3-$#: pairs of GABODSID and photometric solution that should
#        be considered in the photometric solution

#
# check consistency of command line arguments
if [ $# -gt 2 ] && [ $(( ($# - 2) % 2 )) -ne 0 ]; then
    comment="wrong command line syntax !!"
  echo $comment
  #adam-BL#log_status 1 $comment
  exit 1
fi

#
# Generate a catalog containing the photometric information
# requested by the user.

if [ -f "/$1/$2/cat/absphot.asc" ]; then
  rm -f /$1/$2/cat/absphot.asc
fi

if [ -f "${TEMPDIR}/nights_$$.asc" ]; then
  rm -f ${TEMPDIR}/nights_$$.asc
fi
# if we have nights to calibrate on the command line take this info,
# otherwise calibrate with all preselected photometric information
if [ $# -gt 2 ]; then
  NAME=""
  NIGHT=3
  CHOICE=4

  while [ ${NIGHT} -le $(( $# - 1 )) ]
  do
    ${P_LDACFILTER} -i /$1/$2/cat/chips.cat5 -o ${TEMPDIR}/zp_$$.cat \
                    -t STATS -c "(GABODSID=${!NIGHT});"
    ${P_LDACTOASC} -b -i ${TEMPDIR}/zp_$$.cat -s -t STATS \
                   -k IMAGENAME ZP${!CHOICE} COEFF${!CHOICE} AIRMASS RZP | \
                   ${P_GAWK} '{if ($1!="#" && $2!="-1") print $1, $2, $3, $4, $5}' >\
                             ${TEMPDIR}/zp_$$.asc

    if [ -s "${TEMPDIR}/zp_$$.asc" ]; then
	cat ${TEMPDIR}/zp_$$.asc >> /$1/$2/cat/absphot.asc
        echo ${!NIGHT} ${!CHOICE} >> ${TEMPDIR}/nights_$$.asc
    else
	comment="problem with night ${!NIGHT} and solution ${!CHOICE}; aborting !!"
	echo ${comment}
	#adam-BL#log_status 1 ${comment}
	exit 1
    fi
    NAME="${NAME}_${!NIGHT}_${!CHOICE}"
    NIGHT=$(( ${NIGHT} + 2 ))
    CHOICE=$(( ${CHOICE} + 2 ))
  done
else
  ${P_LDACTOASC} -b -i /$1/$2/cat/chips.cat5 -s -t STATS -k IMAGENAME ZP COEFF AIRMASS RZP | \
      ${P_GAWK} '{if ($1!="#" && $2!="-1") print $1, $2, $3, $4, $5}' > /$1/$2/cat/absphot.asc
  if [ ! -s "/$1/$2/cat/absphot.asc" ]; then
      comment="No default zeropoints and extinction coefficients available !! Exiting !!"
      echo ${comment}
      #adam-BL#log_status 1 ${comment}
      exit 1
  fi
  ${P_LDACTOASC} -b -i /$1/$2/cat/chips.cat5 -t STATS -k GABODSID ZPCHOICE |\
                 ${P_SORT} -g | uniq | ${P_GAWK} '($2>0) {print $0}' > ${TEMPDIR}/nights_$$.asc
fi

# now estimate the absolute photometric zeropoint. If more than
# 20 photometric images are available we perform a sigmaclipping
# algorithm before estimating the zeropoint by a straight mean.
${P_GAWK} '{oldline[NR] = $0;
            newline[NR] = $0;
            oldzp[NR]   = $2+$3*$4-$5;
            newzp[NR]   = $2+$3*$4-$5;}
           END {if(NR>20) {maxiter = 3} else {maxiter=0}
                oldnelem = 0;
                newnelem = NR;
                actuiter = 0;
                while (actuiter <= maxiter && oldnelem != newnelem) {
                  zpmean = 0.0; zpsdev = 0.0;
                  for(i = 1; i <= newnelem; i++) {
                    zpmean += newzp[i];
                    zpsdev += newzp[i]*newzp[i];
                  } zpmean /= newnelem;
                  if(newnelem > 2) {
                    zpsdev = sqrt(zpsdev/newnelem-zpmean*zpmean)
                  } else {
                    zpsdev = 0.0
                  }

                  oldnelem = newnelem;
                  if(zpsdev > 0.0 && actuiter < maxiter)
                  {
                    newnelem = 0;
                    for(i = 1; i <= oldnelem; i++) {
                      oldzp[i]   = newzp[i];
                      oldline[i] = newline[i];
                    }
                    for(i = 1; i <= oldnelem; i++) {
                      if(sqrt((oldzp[i]-zpmean)*(oldzp[i]-zpmean)) < 3.0*zpsdev)
                      {
                        newzp[++newnelem] = oldzp[i];
                        newline[newnelem] = oldline[i];
                      }
                    }
                  }
                  actuiter++;
                }
                for(i=1; i<=oldnelem; i++) {
                  print newline[i], newzp[i], zpmean, zpsdev
                }
               }' /$1/$2/cat/absphot.asc > ${TEMPDIR}/phottmp_$$.asc

#
# create tables SOLPHOTOM and ABSPHOTOM containing info on the nights and
# solutions that finally went into the photometric calibration.
if [ -s "${TEMPDIR}/nights_$$.asc" ] && [ -s "${TEMPDIR}/phottmp_$$.asc" ]; then
  ${P_ASCTOLDAC} -a ${TEMPDIR}/nights_$$.asc -o ${TEMPDIR}/nights_$$.cat \
                 -t SOLPHOTOM -c ${DATACONF}/asctoldac_solphotom.conf

  ${P_ASCTOLDAC} -a ${TEMPDIR}/phottmp_$$.asc -o ${TEMPDIR}/phottmp_$$.cat \
                 -t ABSPHOTOM -c ${DATACONF}/asctoldac_absphotom.conf

  ${P_LDACADDTAB} -i /$1/$2/cat/chips.cat5 -o /$1/$2/cat/chips_tmp.cat5 \
                  -p ${TEMPDIR}/nights_$$.cat -t SOLPHOTOM

  ${P_LDACADDTAB} -i /$1/$2/cat/chips_tmp.cat5 -o /$1/$2/cat/chips_phot.cat5 \
                  -p ${TEMPDIR}/phottmp_$$.cat -t ABSPHOTOM

  rm -f /$1/$2/cat/chips_tmp.cat5
  rm -f ${TEMPDIR}/nights_$$.asc
  rm -f ${TEMPDIR}/phottmp_$$.asc
fi

rm -f /$1/$2/cat/absphot.asc
#adam-BL#log_status $?
