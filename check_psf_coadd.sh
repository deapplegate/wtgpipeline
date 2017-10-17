#!/bin/bash
set -xv
#adam-BL#. BonnLogger.sh
#adam-BL#. log_start
# CVSId: $Id: check_psf_coadd.sh,v 1.12 2010-02-02 20:18:35 dapple Exp $

# $1: directory
# $2: image name
# $3 : NAXIS1
# $4 : NAXIS2

. progs.ini > /tmp/progs.out 2>&1
. bash_functions.include > /tmp/bash_functions.out 2>&1

image=$2
BASE=`basename ${image} .fits`
wimage=${BASE}.weight.fits
fimage=${BASE}.flag.fits

NAXIS1=`dfits $1/$image | fitsort -d NAXIS1 | awk '{print $2}'`
NAXIS2=`dfits $1/$image | fitsort -d NAXIS2 | awk '{print $2}'`

# set SM postscript device
SMPSDEVICE="postencap"

REDDIR=`pwd`

cd $1/

cluster=`basename $1 | awk 'BEGIN{FS="_"}{print $2}'`
mode=`basename $1 | awk 'BEGIN{FS="_"}{print $3}'`

# run sextractor to determine the seeing:

PXSCALE=`${P_DFITS} ${image} | ${P_FITSORT} -d CD2_2 | awk '{print $2*3600.}'`
px0=$(echo "${PXSCALE}>0" | bc) #px0=0 <==> PXSCALE -eq 0
if [ ${px0} -eq 0 ]; then
	PXSCALE=`${P_DFITS} ${image} | ${P_FITSORT} -d CDELT2 | awk '{print $2*3600.}'`
fi

fwhm=`${P_DFITS} ${image} | ${P_FITSORT} -d SEEING | awk '{print $2}'`
fwhmSE=`${P_DFITS} ${image} | ${P_FITSORT} -d SEEINGSE | awk '{print $2}'`
MYfwhm=`${P_DFITS} ${image} | ${P_FITSORT} -d MYSEEING | awk '{print $2}'`
fwhm_gt_test=$(echo "${MYfwhm}>0.1" | bc)
fwhm_lt_test=$(echo "${MYfwhm}<1.9" | bc)                                                                                    
fwhm_test=$(echo "${fwhm_lt_test}*${fwhm_gt_test}" | bc)
echo "fwhm_test=" $fwhm_test
#adam-SEEING# if not 0.1<MYSEEING<1.9 or Nelements!=4 then use the crappy method!
if [ "${fwhm_test}" = "1" ]; then
	fwhm=$MYfwhm
	fwhmSE=$MYfwhm
fi

if [ ${fwhm} == "KEY_N/A" ] || [ ${fwhm} == "KEY_EMPTY" ] && [ ${fwhmSE} != "KEY_N/A" ]; then
    fwhm=${fwhmSE}
fi

if [ ${fwhm} == "KEY_N/A" ] || [ ${fwhm} == "KEY_EMPTY" ]; then

  ${P_SEX} ${image} -c ${DATACONF}/singleastrom.conf.sex \
  		 -CATALOG_NAME ${TEMPDIR}/seeing_$$.cat \
                   -FILTER_NAME ${DATACONF}/default.conv\
  		 -CATALOG_TYPE "ASCII" \
  		 -DETECT_MINAREA 5 -DETECT_THRESH 5.\
  		 -ANALYSIS_THRESH 1.2 \
  		 -PARAMETERS_NAME ${DATACONF}/singleastrom.ascii.param.sex\
                   -WEIGHT_IMAGE ${wimage} \
                   -WEIGHT_TYPE MAP_WEIGHT \
                   -FLAG_IMAGE ${fimage} \
                   -FLAG_TYPE MAX

  NLINES=`wc ${TEMPDIR}/seeing_$$.cat | ${P_GAWK} '{print $1}'`
  fwhm=`${P_GAWK} 'BEGIN {binsize=10./'${NLINES}'; 
  		  nbins=int(((3.0-0.3)/binsize)+0.5);
  		  for(i=1; i<=nbins; i++) bin[i]=0}
  		 { if(($3*'${PXSCALE}' > 0.3) && ($3*'${PXSCALE}' < 3.0)) 
                     {
  		     actubin=int(($3*'${PXSCALE}'-0.3)/binsize);
  		     bin[actubin]+=1; 
                     }
                   }
  	         END {max=0; k=0 
  		 for(i=1;i<=nbins; i++)
  		 {
  		   if(bin[i]>max)
  		   { 
  		     max=bin[i];
  		     k=i;
  		   }
  		 }
  		 print 0.3+k*binsize}' ${TEMPDIR}/seeing_$$.cat`

fi

if [ "A${fwhm}" = "A0.0" ]; then
  fwhm=1.0
fi

#fwhm=`${P_DFITS} ${image} | fitsort -d SEEING | awk '{print $2}'`

ZEROPOINT=""
MAGZP=`${P_DFITS} ${image} | ${P_FITSORT} -d MAGZP | awk '{print $2}'`
if [ ${MAGZP} != "KEY_N/A" ] && [ ${MAGZP} != "-1.0" ]; then
    ZEROPOINT="-MAG_ZEROPOINT ${MAGZP}"
fi

#now run sextractor to extract the objects
sex ${image} -c ${DATACONF}/singleastrom.conf.sex\
	       -CATALOG_NAME ${BASE}.cat ${ZEROPOINT} \
	       -DETECT_MINAREA 1 -DETECT_THRESH 10.\
               -SEEING_FWHM ${fwhm} \
               -FLAG_IMAGE ${fimage} -FLAG_TYPE MAX \
               -WEIGHT_IMAGE ${wimage} \
               -WEIGHT_TYPE MAP_WEIGHT \
               -PARAMETERS_NAME ${REDDIR}/photconf/checkpsf.params.sex

if [ ! -f ${BASE}.cat0 ] && [ -f ${BASE}.cat ]; then
	  ${P_LDACCONV} -b 1 -c R -i ${BASE}.cat -o ${BASE}.cat0 
fi 

${P_LDACADDKEY} -i ${BASE}.cat0 -o ${TEMPDIR}/tmp11.cat_$$ \
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
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi

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

echo "adam: not really a problem, I just want to verify that this conf file has nothing wrong with it"
wc -l ${TEMPDIR}/asctoldac_tmp.conf_$$

if [ -f "${TEMPDIR}/asctoldac_tmp.conf_$$" ]; then
	rm -f ${TEMPDIR}/asctoldac_tmp.conf_$$
fi
# now transfer the HFINDPEAKS table to the SEX catalog
${P_LDACADDTAB} -i ${TEMPDIR}/tmp12.cat_$$ -o ${BASE}_tmp1.cat1 \
                -t HFINDPEAKS -p ${TEMPDIR}/hfind.cat_$$

${P_LDACFILTER} -i ${BASE}_tmp1.cat1 \
                -o ${BASE}_tmp.cat1 \
                -c "(rg>0.0)AND(rg<10.0);"

# now run analyseldac
${P_ANALYSELDAC} -i ${BASE}_tmp.cat1 \
                 -o ${BASE}_tmp2.cat1 \
                 -p -x 1 -r -3 -f ${image}

${P_LDACJOINKEY} -i ${BASE}_tmp2.cat1 \
		 -t OBJECTS \
		 -o ${BASE}_ksb.cat1 \
		 -p ${BASE}_tmp.cat1 \
                 -k MAG_AUTO \
                    MAGERR_AUTO	\
                    ALPHA_J2000 \
                    DELTA_J2000 \
                    FWHM_IMAGE \
                    BackGr \
                    MaxVal \
                    Flag

# i've decreased the stepsize (to locate the stellar sequence better)
# and account for it by increasing the box to 4*STEPSIZE
STEPSIZE=0.05

${P_PREANISOTROPY} -i ${BASE}_ksb.cat1 -t OBJECTS \
                   -k rh mag -s ${STEPSIZE} -c rh 0.5 8.0 snratio 30.0 100000.0 >& ${TEMPDIR}/tmp1.asc_$$

### make check plot

MINRH=`awk '($2=="propose") { print $8-'${STEPSIZE}'}' ${TEMPDIR}/tmp1.asc_$$`
MAXRH=`awk '($2=="propose") { print $12+5*'${STEPSIZE}'}' ${TEMPDIR}/tmp1.asc_$$`
MAXMAG=`awk '($2=="propose") { print $14}' ${TEMPDIR}/tmp1.asc_$$`
MINMAG=`awk '($2=="propose") { print $18}' ${TEMPDIR}/tmp1.asc_$$`
LINE="rh $MINRH $MAXRH MAG_AUTO $MAXMAG $MINMAG"

${P_LDACTOASC} -i ${BASE}_ksb.cat1 \
	       -t OBJECTS \
	       -b -k rh mag \
	       > rh_mag_$$.dat

ANISOLINE=`${P_GAWK} '($2=="propose") { print $10,'${MINRH}','${MAXRH}',$16,'${MAXMAG}','${MINMAG}'}' ${TEMPDIR}/tmp1.asc_$$`

${P_ANISOTROPY} -i ${BASE}_ksb.cat1 -c ${ANISOLINE} \
                -o ${BASE}_ksb_tmp.cat2 -j 5.0 -e 2.0

${P_LDACFILTER} -i ${BASE}_ksb_tmp.cat2 \
                -o ${BASE}_ksb.cat2 -c "(cl=2);"

### make star / reference catalog

cp ${BASE}_ksb.cat2 ${BASE}.stars.cat

${P_LDACRENKEY} -i ${BASE}_ksb.cat2 \
                -o ${BASE}_stars.cat \
                -t OBJECTS \
                -k SeqNr Nr ALPHA_J2000 Ra DELTA_J2000 Dec

SEEING=`${P_LDACTOASC} -i ${BASE}_stars.cat -t OBJECTS -b -k FWHM_IMAGE | ${P_GAWK} 'BEGIN{n=0;sum=0}{sum=sum+$1;n++}END{printf "%.3f\n", sum/n*'${PXSCALE}'}'`

value ${SEEING}
writekey ${image} SEEING "${VALUE} / analyseldac Seeing (arcsec)" REPLACE

echo "in order of most trusted to least (remember SEEING is from fwhm of stars it picks out in this code (i.e. check_psf_coadd.sh) )" 
echo "SEEING=" ${SEEING} "MYfwhm=" ${MYfwhm} "fwhm=" ${fwhm} "fwhmSE=" ${fwhmSE}

${P_LDACTOSKYCAT} -i ${BASE}_stars.cat \
                  -t OBJECTS \
                  -k Nr Ra Dec MAG_AUTO \
                  -l id_col Nr ra_col Ra dec_col Dec mag_col MAG_AUTO \
                  > ${BASE}.skycat

${P_LDACTOASC} -i ${BASE}_stars.cat \
               -t OBJECTS -b -k Ra \
               > tmp_rad_$$.dat

${P_LDACTOASC} -i ${BASE}_stars.cat \
               -t OBJECTS -b -k Dec \
               > tmp_decd_$$.dat

${P_LDACTOASC} -i ${BASE}_stars.cat \
               -t OBJECTS -b -k MAG_AUTO \
               > tmp_mag_$$.dat

${P_DECIMALTOHMS} -f tmp_rad_$$.dat > tmp_ras_$$.dat
${P_DECIMALTODMS} -f tmp_decd_$$.dat > tmp_decs_$$.dat

paste tmp_ras_$$.dat tmp_decs_$$.dat tmp_mag_$$.dat > ${BASE}_stars.dat

${P_LDACTOASC} -i ${BASE}_stars.cat \
               -t OBJECTS -b -k \
               rh mag \
               > tmp_stars_$$.dat

{
echo 'device "postencap '${BASE}'_rh_mag.eps"'
#
echo "ctype black"
echo "lweight 4"
echo 'data "rh_mag_'$$'.dat"'
echo "read { rh 1 mag 2 }"
echo "limits rh mag"
echo "limits 0.5 5 30 20"
echo "box"
echo "expand 1.3"
echo "xlabel r_h"
echo "ylabel MAG_AUTO"
  echo "relocate (17600 32000)"
echo "putlabel 5 '${cluster}' '${mode}'"
echo "expand 0.4"
echo "ptype 20 3"
echo "lweight 3"
#
echo "points rh mag"
#
echo "ctype green"
echo 'data "tmp_stars_'$$'.dat"'
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


# The file for global ellipticity statistics:
test -f  ${TEMPDIR}/${BASE}_PSF_allellip.asc_$$ && \
      rm -f ${TEMPDIR}/${BASE}_PSF_allellip.asc_$$ 


${P_LDACTOASC} -i ${BASE}_ksb.cat2 -b -t OBJECTS \
               -k Xpos Ypos e1 e2 > ${TEMPDIR}/${BASE}_PSFplot.asc_$$

${P_GAWK} '{print $3, $4}' ${TEMPDIR}/${BASE}_PSFplot.asc_$$ > \
          ${TEMPDIR}/${BASE}_PSF_allellip.asc_$$ 

{
  echo 'macro read "'${SMMACROS}'/shearfield.sm"'
  echo 'device "'${SMPSDEVICE}' /'$1'/'${BASE}'.psf.ps"'
  echo "relocate (17600 32500)"
#  echo "putlabel 5 '${BASE}'"
  echo "putlabel 5 '${cluster}' '${mode}'"
  echo "limits 0 ${NAXIS1} 0 ${NAXIS2}"      
  echo "lweight 1.5"
  echo "expand 0.5"
  echo "box"
  echo 'shearfield "'${TEMPDIR}'/'${BASE}'_PSFplot.asc_'$$'" 2000'
  # global statistics on the PSF ellipticity      
  # distribution:
  echo "expand 0.7"
  echo 'data "'${TEMPDIR}'/'${BASE}'_PSF_allellip.asc_'$$'"'
  echo "read { e1 1 e2 2 }"
  echo "stats e1 m1 s1 k1"
  echo "stats e2 m2 s2 k2"
  echo "relocate ( 2000 1500 )"
  echo "define s (sprintf('<e1>: %.2f +/- ', \$m1))"
  echo 'label $s'
  echo "define s (sprintf('%.2f;', \$s1))"
  echo 'label $s'
  echo "relocate ( 8000 1500 ) "
  echo "define s (sprintf('<e2>: %.2f +/- ', \$m2))"
  echo 'label $s'
  echo "define s (sprintf('%.2f;', \$s2))"
  echo 'label $s'
  echo "set eabs=sqrt(e1*e1+e2*e2)"
  echo "sort {eabs}"
  echo "relocate ( 15000 1500 )"
  echo "define s (sprintf('|e| min = %.2f;', \$(eabs[0])))"
  echo 'label $s'
  echo "relocate ( 20000 1500 )"
  echo "define n (dimen(eabs)-1)"
  echo "define s (sprintf('|e| max = %.2f', \$(eabs[\$n])))"
  echo 'label $s'

  echo "sort {e1}"
  echo "relocate ( 2000 1000 )"
  echo "define s (sprintf('e1 min = %.2f;', \$(e1[0])))"
  echo 'label $s'
  echo "relocate ( 8000 1000 )"
  echo "define n (dimen(e1)-1)"
  echo "define s (sprintf('e1 max = %.2f', \$(e1[\$n])))"
  echo 'label $s'

  echo "sort {e2}"
  echo "relocate ( 15000 1000 )"
  echo "define s (sprintf('e2 min = %.2f;', \$(e2[0])))"
  echo 'label $s'
  echo "relocate ( 20000 1000 )"
  echo "define n (dimen(e2)-1)"
  echo "define s (sprintf('e2 max = %.2f', \$(e2[\$n])))"
  echo 'label $s'

  echo "expand 1.0"
  echo "lweight 1.0"
  echo "hardcopy"      
} > ${TEMPDIR}/${BASE}_PSFplot.sm_$$
cat ${TEMPDIR}/${BASE}_PSFplot.sm_$$ | ${P_SM}


rm -f tmp_*_$$.dat
rm -f rh_mag_$$.dat
rm -f ${TEMPDIR}/tmp1.asc_$$
rm -f ${BASE}_tmp*.cat1
rm -f ${BASE}_ksb*.cat*
rm -f ${BASE}.cat0
rm -f ${BASE}.cat
rm -f ${BASE}_ref.cat


rm -f ${TEMPDIR}/tmp*cat_$$
rm -f ${TEMPDIR}/tmp*asc_$$
rm -f ${TEMPDIR}/hfind.cat_$$
rm -f ${TEMPDIR}/seeing_$$.cat

rm -f ${TEMPDIR}/psfimages_plot_$$
find ${TEMPDIR} -maxdepth 1 -name \*PSF_allellip.asc_$$ -exec rm -f {} \;
find ${TEMPDIR} -maxdepth 1 -name \*PSFplot.asc_$$      -exec rm -f {} \;
find ${TEMPDIR} -maxdepth 1 -name \*PSF_allellip.asc_$$ -exec rm -f {} \;
find ${TEMPDIR} -maxdepth 1 -name \*PSFplot.sm_$$       -exec rm -f {} \;
