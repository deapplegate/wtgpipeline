#!/bin/bash -xv
. BonnLogger.sh
. log_start
# 15.01.03:
# - included correct treatment of link structure
# - more robust conversion from ASCII Astrometrix header
#   to FITS tables if the Astrometrix header contains
#   comments
# - additional argument to indicate LDAC or SWARP header update 
# - substituted the inclusion of WFI.ini by progs.ini
#   as no instrument specific data are used in this script
#
# 30.05.04:
# tempaorary files go to a TEMPDIR directory 

# script to write Astrometrix polynomials into
# image headers ready for use with drizzle.
# The images to that this script is applied
# have to be gone through add_image_calibs
# already. The astrometrix header files
# have to reside in ../sciencedir/headers
# and have to be created from the (..FF.fits)
# images.

#$1: main directory
#$2: science directory
#$3: old image extension (ext) on  ..._iext.fits (i is the chip number)
#$4: new image extension
#$5: polynom type (LDAC or SWARP)
#$6: chips to work on

. progs.ini

for CHIP in $6
do
  ls -1 /$1/$2/*_${CHIP}$3.fits > ${TEMPDIR}/astrometriximages_$$

  FILE=`${P_GAWK} '(NR==1) {print $0}' ${TEMPDIR}/astrometriximages_$$`

  if [ -L ${FILE} ]; then
    LINK=`${P_READLINK} ${FILE}`
    RESULTDIR=`dirname ${LINK}`
  else
    RESULTDIR="/$1/$2"
  fi
  
  cat ${TEMPDIR}/astrometriximages_$$ |\
  {
    while read file
    do
      BASE=`basename ${file} $3.fits`

      # create an LDAC catalog from the astrometrix header

      ${P_GAWK} 'BEGIN {FS = "[=/]"; string="" } 
      		{if($1 ~ /^[PC][DRV]/) 
      		 { string = string $2 "";
      		   printf("COL_NAME = %s\n", $1) >  "'${TEMPDIR}/asctoldac.asc_$$'"; 
      		   print "COL_TTYPE= DOUBLE"     >> "'${TEMPDIR}/asctoldac.asc_$$'";
      		   print "COL_HTYPE= FLOAT"      >> "'${TEMPDIR}/asctoldac.asc_$$'";
      		   print "COL_COMM = \"\""       >> "'${TEMPDIR}/asctoldac.asc_$$'";
      		   print "COL_UNIT = \"\""       >> "'${TEMPDIR}/asctoldac.asc_$$'";
      		   print "COL_DEPTH= 1"          >> "'${TEMPDIR}/asctoldac.asc_$$'" }
      		} END { print string > "'${TEMPDIR}/astrometrixtmp.asc_$$'" }' /$1/$2/headers/${BASE}.head
      
	 ${P_ASCTOLDAC} -i ${TEMPDIR}/astrometrixtmp.asc_$$ \
                        -c ${TEMPDIR}/asctoldac.asc_$$ -o /$1/$2/headers/${BASE}.cat\
			-t DISTORTIONS -b 1 -n "test"

	 if [ "$5" != "SWARP" ]; then
	   ${P_ASTROMETRIXCONVERT} -i /$1/$2/headers/${BASE}.cat -f\
				   /$1/$2/${BASE}$3.fits -o\
				   ${RESULTDIR}/${BASE}$4.fits
	 else
	   ${P_ASTROMETRIXCONVERT} -i /$1/$2/headers/${BASE}.cat -f\
				   /$1/$2/${BASE}$3.fits -o\
				   ${RESULTDIR}/${BASE}$4.fits\
	                           -t SWARP
	 fi    

	 if [ "${RESULTDIR}" != "/$1/$2" ]; then
	   ln -s ${RESULTDIR}/${BASE}$4.fits /$1/$2/${BASE}$4.fits
	 fi
    done
  }
done







log_status $?
