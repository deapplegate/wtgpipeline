#!/bin/bash
set -xvu
#adam-BL#. BonnLogger.sh
#adam-BL#. log_start
# the script runs analyseldac over the objects previously
# used in the singleastrom step.

# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 21.11.2006:
# - The script is more general and can be used also
#   in cases where a .cat1 catalogue is not yet present
#   (e.g. if we use only ASTROMETRIX for astrometric calibration
#   and hence do not create all intermediate catalogues
#   of the LDAC pipeline).
# - 'analyseldac' runs with the option '-p' which uses the SExtractor
#   centre for shape estimation instead of determining a new one.
#   For PSF checkplots this is good enough and it speeds up the
#   script tremendously.
#
# 16.03.2007:
# I delete some temporary files
#
# 01.08.2007:
# some more deletion of temporary files

# $1: main directory
# $2: science dir.
# $3: image extension (ext) on ..._iext.fits (i is the chip number)
# $4: chips to be processed

. progs.ini > /tmp/progs.out 2>&1
{
echo "VERBOSE = DEBUG"   
echo "COL_NAME  = cl" 
echo "COL_TTYPE = SHORT"
echo "COL_HTYPE = INT"
echo 'COL_COMM = ""'     
echo 'COL_UNIT = ""'
} > ${TEMPDIR}/asctoldac_stars_tmp.conf_$$

for CHIP in $4
do
  ls -1 /$1/$2/*_${CHIP}$3.fits > ${TEMPDIR}/psfimages_${CHIP}_$$
  
  cat ${TEMPDIR}/psfimages_${CHIP}_$$ |\
  {
    while read file
    do
      BASE=`basename ${file} .fits`
      #
      # now convert the SExtractor cat to one readable by analyseldac:
      if [ -f "/$1/$2/cat/${BASE}.cat" ]; then
	  ${P_LDACCONV} -b 1 -c R -i /$1/$2/cat/${BASE}.cat -o /$1/$2/cat/${BASE}.cat0 

      else
	  continue
      fi 

      if [ ! -f "/$1/$2/cat/${BASE}.cat0" ]; then 
	  echo "no catalog /$1/$2/cat/${BASE}.cat0 present; exiting"
	  #adam-BL#log_status 1 "no catalog /$1/$2/cat/${BASE}.cat0 present; exiting"
	  exit 1
      fi 

      ${P_LDACADDKEY} -i /$1/$2/cat/${BASE}.cat0 -o ${TEMPDIR}/tmp11.cat_$$ \
                            -t OBJECTS -k nu 1.0 FLOAT ""

      ${P_LDACCALC} -i ${TEMPDIR}/tmp11.cat_$$ -o ${TEMPDIR}/tmp12.cat_$$ -t OBJECTS \
                    -c "(FLUX_RADIUS);" -n "rg" "" -k FLOAT \
                    -c "(Xpos-1.0);" -n "x" "" -k LONG \
                    -c "(Ypos-1.0);" -n "y" "" -k LONG \
                    -c "(Xpos);" -n "xbad" "" -k FLOAT \
                    -c "(Ypos);" -n "ybad" "" -k FLOAT

      ${P_LDACTOASC} -i ${TEMPDIR}/tmp12.cat_$$ -b -t FIELDS \
                    -k FITSFILE SEXBKGND SEXBKDEV -s > ${TEMPDIR}/tmp.asc_$$

      # create a config file for asctoldac on the fly
      
      echo "VERBOSE = DEBUG"       >  ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo "COL_NAME  = IMAGE"     >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo "COL_TTYPE = STRING"    >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo "COL_HTYPE = STRING"    >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo 'COL_COMM = ""'         >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo 'COL_UNIT = ""'         >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo 'COL_DEPTH = 128'       >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo "COL_NAME  = SKY_MODE"  >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo "COL_TTYPE = FLOAT"     >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo "COL_HTYPE = FLOAT"     >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo 'COL_COMM = ""'         >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo 'COL_UNIT = ""'         >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo 'COL_DEPTH = 1'         >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo "COL_NAME  = SKY_SIGMA" >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo "COL_TTYPE = FLOAT"     >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo "COL_HTYPE = FLOAT"     >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo 'COL_COMM = ""'         >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo 'COL_UNIT = ""'         >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      echo 'COL_DEPTH = 1'         >> ${TEMPDIR}/asctoldac_tmp.conf_$$
      
      ${P_ASCTOLDAC} -i ${TEMPDIR}/tmp.asc_$$ -c ${TEMPDIR}/asctoldac_tmp.conf_$$ -t HFINDPEAKS \
 		     -o ${TEMPDIR}/hfind.cat_$$ -b 1 -n "KSB"
      exit_stat=$?
      if [ "${exit_stat}" -gt "0" ]; then
	      exit ${exit_stat};
      fi
      rm -f ${TEMPDIR}/asctoldac_tmp.conf_$$
      
      # now transfer the HFINDPEAKS table to the SEX catalog
      ${P_LDACADDTAB} -i ${TEMPDIR}/tmp12.cat_$$ -o /$1/$2/cat/${BASE}_tmp1.cat1 \
                      -t HFINDPEAKS -p ${TEMPDIR}/hfind.cat_$$

      ${P_LDACFILTER} -i /$1/$2/cat/${BASE}_tmp1.cat1 \
                      -o /$1/$2/cat/${BASE}_tmp.cat1 \
                      -c "(IMAFLAGS_ISO=0)AND((rg>0.0)AND(rg<20.0));"

      # now run analyseldac
      ${P_ANALYSELDAC} -i /$1/$2/cat/${BASE}_tmp.cat1 \
                       -o /$1/$2/cat/${BASE}_tmp2.cat1 \
                       -p -x 1 -r -3 -f ${file}

      ${P_LDACJOINKEY} -i /$1/$2/cat/${BASE}_tmp2.cat1 \
		 -t OBJECTS \
		 -o /$1/$2/cat/${BASE}_ksb.cat1 \
		 -p /$1/$2/cat/${BASE}_tmp.cat1 \
                 -k MAG_AUTO \
                    MAGERR_AUTO	\
                    ALPHA_J2000 \
                    DELTA_J2000 \
                    FWHM_IMAGE

      STEPSIZE=0.05
      ${P_PREANISOTROPY} -i /$1/$2/cat/${BASE}_ksb.cat1 -t OBJECTS \
                         -k rh mag -s ${STEPSIZE} -c rh 1.0 10.0 snratio 20.0 10000.0 >& ${TEMPDIR}/tmp1.asc_$$
      MINRH=`awk '($2=="propose") { print $8-'${STEPSIZE}'}' ${TEMPDIR}/tmp1.asc_$$`
      MAXRH=`awk '($2=="propose") { print $12+'${STEPSIZE}'}' ${TEMPDIR}/tmp1.asc_$$`
      MAXMAG=`awk '($2=="propose") { print $14}' ${TEMPDIR}/tmp1.asc_$$`
      MINMAG=`awk '($2=="propose") { print $18}' ${TEMPDIR}/tmp1.asc_$$`
      LINE="rh $MINRH $MAXRH MAG_AUTO $MAXMAG $MINMAG"

      magdiff=`awk 'BEGIN{print '${MAXMAG}'-'${MINMAG}'}'`

      MAXMAG=`awk 'BEGIN{print ('${magdiff}'>0.5 ? '${MAXMAG}' : '${MAXMAG}'-2.0)}'`
      MINMAG=`awk 'BEGIN{print ('${magdiff}'>0.5 ? '${MINMAG}' : '${MINMAG}'+2.0)}'`

      ANISOLINE=`${P_GAWK} '($2=="propose") { print $10,'${MINRH}','${MAXRH}',$16,'${MAXMAG}','${MINMAG}'}' ${TEMPDIR}/tmp1.asc_$$`

###      ANISOLINE=`${P_GAWK} '($2=="propose") { print $10,$8,$12,$16,$14,$18}' ${TEMPDIR}/tmp1.asc_$$`
      ${P_ANISOTROPY} -i /$1/$2/cat/${BASE}_ksb.cat1 -c ${ANISOLINE} \
                      -o /$1/$2/cat/${BASE}_ksb_tmp.cat2 -j 5.0 -e 2.0

      if [ ! -f "/$1/$2/cat/${BASE}_ksb_tmp.cat2" ]; then
	      echo "adam-look inconsequential error: no biggie if you got an error just now that looks like 'ERROR(anisotropy): not enough stars after preselection'"

	  ${P_LDACTOASC} -i /$1/$2/cat/${BASE}_ksb.cat1 \
                         -t OBJECTS -b -k rh mag cl snratio |\
                         ${P_GAWK} '{if($1>='${MINRH}' && $1<='${MAXRH}' && $2>='${MAXMAG}' && $2<='${MINMAG}') print 2, $4; else print $3, $4}' \
                         > ${TEMPDIR}/${BASE}_stars.tmp

	  ${P_ASCTOLDAC} -i ${TEMPDIR}/${BASE}_stars.tmp -o ${TEMPDIR}/${BASE}_stars.fake.cat -t OBJECTS \
                         -c ${TEMPDIR}/asctoldac_stars_tmp.conf_$$
	  
	  ${P_LDACDELKEY} -i /$1/$2/cat/${BASE}_ksb.cat1 \
                          -o ${TEMPDIR}/${BASE}_ksb.cat1 \
	                  -t OBJECTS -k cl
	  
	  ${P_LDACJOINKEY} -i ${TEMPDIR}/${BASE}_ksb.cat1 \
	                   -o /$1/$2/cat/${BASE}_ksb_tmp.cat2 \
	                   -p ${TEMPDIR}/${BASE}_stars.fake.cat \
                           -t OBJECTS -k cl
      fi

      ${P_LDACFILTER} -i /$1/$2/cat/${BASE}_ksb_tmp.cat2 \
                      -o /$1/$2/cat/${BASE}_ksb.cat2 -c "(cl=2);"

      if [ ! -s "/$1/$2/cat/${BASE}_ksb.cat2" ]; then
	  #adam-BL#log_status 3 "Catalog ${BASE}_ksb.cat2 not produced!"
	  exit 3
      fi

    ${P_LDACTOASC} -i /$1/$2/cat/${BASE}_ksb.cat1 \
	       -t OBJECTS \
	       -b -k rh mag \
	       > ${TEMPDIR}/rh_mag_$$.dat
    
    ${P_LDACTOASC} -i /$1/$2/cat/${BASE}_ksb.cat2 \
                   -t OBJECTS -b -k \
                   rh mag \
                   > ${TEMPDIR}/tmp_stars_$$.dat
    
    {
    echo 'device "postencap /'$1'/'$2'/cat/'${BASE}'_rh_mag.eps"'
    #
    echo "ctype black"
    echo "lweight 4"
    echo 'data "'${TEMPDIR}'/rh_mag_'$$'.dat"'
    echo "read { rh 1 mag 2 }"
    echo "limits rh mag"
    echo "limits 0.5 5 22 14"
    echo "box"
    echo "expand 1.3"
    echo "xlabel r_h"
    echo "ylabel MAG_AUTO"
      echo "relocate (17600 32000)"
    echo "putlabel 5 '${BASE}'"
    echo "expand 0.4"
    echo "ptype 20 3"
    echo "lweight 3"
    #
    echo "points rh mag"
    #
    echo "ctype green"
    echo 'data "'${TEMPDIR}'/tmp_stars_'$$'.dat"'
    echo "read { rh 1 mag 2 }"
    echo "points rh mag"
    #
    echo "ctype red"
    echo "relocate ${MINRH} ${MAXMAG}"
    echo "draw ${MINRH} ${MINMAG}"
    echo "draw ${MAXRH} ${MINMAG}"
    echo "draw ${MAXRH} ${MAXMAG}"
    echo "draw ${MINRH} ${MAXMAG}"
    #
    echo "hardcopy"
    } | sm

    done
  }
  rm -f ${TEMPDIR}/psfimages_${CHIP}_$$
done

rm -f ${TEMPDIR}/*_ksb.cat1
rm -f ${TEMPDIR}/*_stars.fake.cat
rm -f ${TEMPDIR}/asctoldac_stars_tmp.conf_$$
rm -f ${TEMPDIR}/tmp*cat_$$
rm -f ${TEMPDIR}/tmp*asc_$$
rm -f ${TEMPDIR}/hfind.cat_$$

#adam-BL#log_status 0
