#!/bin/bash
set -uxv
#########################

cluster=$1
filters=$2

subarudir=/nfs/slac/g/ki/ki18/anja/SUBARU

IMAGE=coadd

export LENSCONF=lensconf

. progs.ini

#########################

for filter in ${filters}; do

    calibnight=`ls ${subarudir}/${cluster} | grep ${filter} | grep CALIB`

    if [ -z "${calibnight}" ]; then
	continue
    fi

    calib_dir=${subarudir}/${cluster}/${calibnight}


    sdss_coadd_dir=${calib_dir}/SCIENCE/coadd_${cluster}_3s/

    photometry_dir=${calib_dir}/PHOTOMETRY_3sec

    if [ ! -d ${photometry_dir} ]; then
	mkdir ${photometry_dir}
    fi

    lensing_workdir=${calib_dir}/LENSING_3sec
    if [ ! -d ${lensing_workdir} ]; then
	mkdir ${lensing_workdir}
    fi
       
    gain=`dfits ${sdss_coadd_dir}/coadd.fits | fitsort -d GAIN | awk '{print $2}'`
    NAXIS1=`dfits ${sdss_coadd_dir}/coadd.fits | fitsort -d NAXIS1 | awk '{print $2}'`
    NAXIS2=`dfits ${sdss_coadd_dir}/coadd.fits | fitsort -d NAXIS2 | awk '{print $2}'`

    ${P_SEX} ${sdss_coadd_dir}/coadd.fits \
        -c photconf/phot.conf.sex \
        -PARAMETERS_NAME photconf/phot.param.short.sex \
        -CATALOG_NAME ${photometry_dir}/coadd.3sec.cat \
        -FILTER_NAME ${DATACONF}/default.conv \
        -FILTER  Y \
        -DETECT_MINAREA 4 -DETECT_THRESH 5 -ANALYSIS_THRESH 5 \
        -MAG_ZEROPOINT 0 \
        -FLAG_TYPE OR \
        -FLAG_IMAGE ${sdss_coadd_dir}/coadd.flag.fits \
        -GAIN ${gain} \
        -CHECKIMAGE_TYPE NONE \
        -WEIGHT_IMAGE ${sdss_coadd_dir}/coadd.weight.fits \
        -WEIGHT_TYPE MAP_WEIGHT
    if [ $? -ne 0 ]; then
	echo "Failure in Source Extractor"
	exit 1
    fi
    
    ${P_LDACCONV} -b 1 -c "sex" -i ${photometry_dir}/coadd.3sec.cat  -o ${photometry_dir}/${cluster}.3sec.cat0 -f $filter
    if [ $? -ne 0 ]; then
	echo "Failure in LDACCONV"
	exit 2
    fi

    if [ ! -s ${photometry_dir}/${cluster}.3sec.cat0 ]; then
	echo 3sec Exposure Catalog not found!
	exit 3
    fi

    ${P_LDACRENKEY} -i ${photometry_dir}/${cluster}.3sec.cat0 -o ${photometry_dir}/${cluster}.3sec.cat -k MAG_APER MAG_APER-${filter} MAGERR_APER MAGERR_APER-${filter}

    ./measure_shapes.sh ${sdss_coadd_dir}/coadd.fits  ${photometry_dir}/${cluster}.3sec.cat0 $lensing_workdir/${IMAGE}_ell.cat $lensing_workdir

### i've decreased the stepsize (to locate the stellar sequence better)
### and account for it by increasing the box to 4*STEPSIZE
STEPSIZE=0.05

${P_PREANISOTROPY} -i $lensing_workdir/${IMAGE}_ell.cat -t OBJECTS \
                   -k rh mag -s 0.05 -c rh 1.0 10.0 snratio 20.0 10000.0 >& ${TEMPDIR}/tmp1.asc_$$

### make check plots

MINRH=`awk '($2=="propose") { print $8-'${STEPSIZE}'}' ${TEMPDIR}/tmp1.asc_$$`
MAXRH=`awk '($2=="propose") { print $12+'${STEPSIZE}'}' ${TEMPDIR}/tmp1.asc_$$`
MAXMAG=`awk '($2=="propose") { print $14}' ${TEMPDIR}/tmp1.asc_$$`
MINMAG=`awk '($2=="propose") { print $18}' ${TEMPDIR}/tmp1.asc_$$`
LINE="rh $MINRH $MAXRH MAG_AUTO $MAXMAG $MINMAG"

${P_LDACTOASC} -i $lensing_workdir/${IMAGE}_ell.cat \
	       -t OBJECTS \
	       -b -k rh mag \
	       > $lensing_workdir/rh_mag_$$.dat

ANISOLINE=`${P_GAWK} '($2=="propose") { print $10,'${MINRH}','${MAXRH}',$16,'${MAXMAG}','${MINMAG}'}' ${TEMPDIR}/tmp1.asc_$$`

${P_ANISOTROPY} -i $lensing_workdir/${IMAGE}_ell.cat -c ${ANISOLINE} \
                -o $lensing_workdir/${IMAGE}_anisocorr.cat -j 5.0 -e 2.0

${P_LDACFILTER} -i  $lensing_workdir/${IMAGE}_anisocorr.cat\
                -o $lensing_workdir/${IMAGE}_stars.cat -c "(cl=2);"

### make star / reference catalog

${P_LDACTOASC} -i $lensing_workdir/${IMAGE}_stars.cat \
               -t OBJECTS -b -k ALPHA_J2000 \
               > tmp_rad_$$.dat

${P_LDACTOASC} -i $lensing_workdir/${IMAGE}_stars.cat \
               -t OBJECTS -b -k DELTA_J2000 \
               > tmp_decd_$$.dat

${P_LDACTOASC} -i $lensing_workdir/${IMAGE}_stars.cat \
               -t OBJECTS -b -k MAG_AUTO \
               > tmp_mag_$$.dat

${P_DECIMALTOHMS} -f tmp_rad_$$.dat > tmp_ras_$$.dat
${P_DECIMALTODMS} -f tmp_decd_$$.dat > tmp_decs_$$.dat

paste tmp_ras_$$.dat tmp_decs_$$.dat tmp_mag_$$.dat > $lensing_workdir/${IMAGE}_stars.dat

${P_LDACTOASC} -i $lensing_workdir/${IMAGE}_stars.cat \
               -t OBJECTS -b -k \
               rh mag \
               > tmp_stars_$$.dat

{
echo 'device "postencap '$lensing_workdir/${IMAGE}'_rh_mag.eps"'
#
echo "ctype black"
echo "lweight 4"
echo 'data "'$lensing_workdir'/rh_mag_'$$'.dat"'
echo "read { rh 1 mag 2 }"
echo "limits rh mag"
echo "limits 0.5 5 30 20"
echo "box"
echo "expand 1.3"
echo "xlabel r_h"
echo "ylabel MAG_AUTO"
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


${P_LDACTOASC} -i $lensing_workdir/${IMAGE}_stars.cat -b -t OBJECTS\
               -k Xpos Ypos e1 e2 > ${TEMPDIR}/${IMAGE}_PSFplot.asc_$$


${P_GAWK} '{print $3, $4}' ${TEMPDIR}/${IMAGE}_PSFplot.asc_$$ > \
          ${TEMPDIR}/${IMAGE}_PSF_allellip.asc_$$ 

{
  echo 'macro read "'${SMMACROS}'/shearfield.sm"'
  echo 'device "postencap '$lensing_workdir'/'${IMAGE}'.psf.ps"'
  echo "relocate (17600 32500)"
  echo "putlabel 5 '${IMAGE}'"
  echo "limits 0 ${NAXIS1} 0 ${NAXIS2}"      
  echo "lweight 1.5"
  echo "expand 0.5"
  echo "box"
  echo 'shearfield "'${TEMPDIR}'/'${IMAGE}'_PSFplot.asc_'$$'" 2000'
  # global statistics on the PSF ellipticity      
  # distribution:
  echo "expand 0.7"
  echo 'data "'${TEMPDIR}'/'${IMAGE}'_PSF_allellip.asc_'$$'"'
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
} > ${TEMPDIR}/${IMAGE}_PSFplot.sm_$$
cat ${TEMPDIR}/${IMAGE}_PSFplot.sm_$$ | ${P_SM}


rm -f ${TEMPDIR}/tmp1.asc_$$ tmp_ras_$$.dat tmp_decs_$$.dat tmp_mag_$$.dat tmp_stars_$$.dat ${TEMPDIR}/${IMAGE}_PSFplot.asc_$$ ${TEMPDIR}/${IMAGE}_PSF_allellip.asc_$$ ${TEMPDIR}/${IMAGE}_PSFplot.sm_$$

#####################################

./extract_catalog_subset.py $lensing_workdir/${IMAGE}_stars.cat ${photometry_dir}/$cluster.3sec.cat ${photometry_dir}/$cluster.stars.cat

if [ ! -s ${photometry_dir}/$cluster.stars.cat ]; then
    echo "Star cat not found!"
    exit 4
fi


done

