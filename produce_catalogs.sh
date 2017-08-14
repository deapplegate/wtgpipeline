#!/bin/bash -uxv
########################
# Run photometry on all available filters,
#   and run shape measurement code.
# Produces a photometry catalog, a star catalog, and a shape catalog
########################

clusterdir=$1
phot_workdir=$2
lensing_workdir=$3
cluster=$4
detection_image=$5

lensing_image=${detection_image}
if [ $# -gt 5 ]; then
    lensing_image=$6
fi

#adam#  Got rid of the redo_starselect option.
# 	It makes preanisotropy fail later, and all it does is skip a step that takes a few seconds

. progs.ini > scratch/progs.out 2>&1

export LENSCONF=lensconf

IMAGE=`basename ${lensing_image} .fits`

if [ ! -d $phot_workdir ]; then
    mkdir $phot_workdir
fi

if [ ! -d ${lensing_workdir} ]; then
    mkdir ${lensing_workdir}
fi


NAXIS1=`${P_DFITS} ${detection_image} | ${P_FITSORT} NAXIS1 | ${P_GAWK} '($1!="FILE") {print $2}'`
NAXIS2=`${P_DFITS} ${detection_image} | ${P_FITSORT} NAXIS2 | ${P_GAWK} '($1!="FILE") {print $2}'`


#####################################

inputcat=${phot_workdir}/$cluster.unstacked.cat
if [ ${detection_image} != ${lensing_image} ]; then

    detect_dir=`dirname ${detection_image}`
    detect_base=`basename ${detection_image} .fits`
    detect_weight=${detect_dir}/${detect_base}.weight.fits

    lensing_dir=`dirname ${lensing_image}`
    lensing_base=`basename ${lensing_image} .fits`
    lensing_weight=${lensing_dir}/${lensing_base}.weight.fits
    lensing_flag=${lensing_dir}/${lensing_base}.flag.fits


    ./extract_object_cats.py --di ${detection_image} --dw $detect_weight \
	--pi ${lensing_image} --pw $lensing_weight --pf $lensing_flag \
	-o ${lensing_workdir}/lensing.cat --noarea
    if [ $? -ne 0 ]; then
	echo "Failure in extract_object_cats"
	exit 1
    fi
    
    inputcat=${lensing_workdir}/lensing.cat

fi

./measure_shapes.sh ${lensing_image} ${inputcat} ${lensing_workdir}/${IMAGE}_ell.cat ${lensing_workdir}
if [ $? -ne 0 ]; then
    echo "Failure in measure_shapes.sh"
    exit 2
fi

## i've decreased the stepsize (to locate the stellar sequence better)
## and account for it by increasing the box to 4*STEPSIZE
STEPSIZE=0.05

starselect_file=${lensing_workdir}/starselection



${P_PREANISOTROPY} -i ${lensing_workdir}/${IMAGE}_ell.cat -t OBJECTS \
-k rh mag -s 0.05 -c rh 1.0 10.0 snratio 20.0 10000.0 >& tmp1.asc_$$

### make check plots

MINRH=`awk '($2=="propose") { print $8-'${STEPSIZE}'}' tmp1.asc_$$`
MAXRH=`awk '($2=="propose") { print $12+'${STEPSIZE}'}' tmp1.asc_$$`
MAXMAG=`awk '($2=="propose") { print $14}' tmp1.asc_$$`
MINMAG=`awk '($2=="propose") { print $18}' tmp1.asc_$$`

LINE="rh $MINRH $MAXRH MAG_AUTO $MAXMAG $MINMAG"
echo $LINE > $starselect_file


${P_LDACTOASC} -i ${lensing_workdir}/${IMAGE}_ell.cat \
	       -t OBJECTS \
	       -b -k rh mag \
	       > ${lensing_workdir}/rh_mag_$$.dat

ANISOLINE=`${P_GAWK} '($2=="propose") { print $10,'${MINRH}','${MAXRH}',$16,'${MAXMAG}','${MINMAG}'}' tmp1.asc_$$`

${P_ANISOTROPY} -i ${lensing_workdir}/${IMAGE}_ell.cat -c ${ANISOLINE} \
                -o ${lensing_workdir}/${IMAGE}_anisocorr.cat -j 5.0 -e 2.0

${P_LDACFILTER} -i  ${lensing_workdir}/${IMAGE}_anisocorr.cat\
                -o ${lensing_workdir}/${IMAGE}_stars.cat -c "(cl=2);"

### make star / reference catalog

${P_LDACTOASC} -i ${lensing_workdir}/${IMAGE}_stars.cat \
               -t OBJECTS -b -k ALPHA_J2000 \
               > tmp_rad_$$.dat

${P_LDACTOASC} -i ${lensing_workdir}/${IMAGE}_stars.cat \
               -t OBJECTS -b -k DELTA_J2000 \
               > tmp_decd_$$.dat

${P_LDACTOASC} -i ${lensing_workdir}/${IMAGE}_stars.cat \
               -t OBJECTS -b -k MAG_AUTO \
               > tmp_mag_$$.dat

${P_DECIMALTOHMS} -f tmp_rad_$$.dat > tmp_ras_$$.dat
${P_DECIMALTODMS} -f tmp_decd_$$.dat > tmp_decs_$$.dat

paste tmp_ras_$$.dat tmp_decs_$$.dat tmp_mag_$$.dat > ${lensing_workdir}/${IMAGE}_stars.dat

${P_LDACTOASC} -i ${lensing_workdir}/${IMAGE}_stars.cat \
               -t OBJECTS -b -k \
               rh mag \
               > tmp_stars_$$.dat

{
echo 'device "postencap '${lensing_workdir}/${IMAGE}'_rh_mag.eps"'
#
echo "ctype black"
echo "lweight 4"
echo 'data "'${lensing_workdir}'/rh_mag_'$$'.dat"'
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


${P_LDACTOASC} -i ${lensing_workdir}/${IMAGE}_stars.cat -b -t OBJECTS\
               -k Xpos Ypos e1 e2 > ${TEMPDIR}/${IMAGE}_PSFplot.asc_$$


${P_GAWK} '{print $3, $4}' ${TEMPDIR}/${IMAGE}_PSFplot.asc_$$ > \
          ${TEMPDIR}/${IMAGE}_PSF_allellip.asc_$$ 

{
  echo 'macro read "'${SMMACROS}'/shearfield.sm"'
  echo 'device "postencap '${lensing_workdir}'/'${IMAGE}'.psf.ps"'
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


rm tmp1.asc_$$ tmp_ras_$$.dat tmp_decs_$$.dat tmp_mag_$$.dat tmp_stars_$$.dat ${TEMPDIR}/${IMAGE}_PSFplot.asc_$$ ${TEMPDIR}/${IMAGE}_PSF_allellip.asc_$$ ${TEMPDIR}/${IMAGE}_PSFplot.sm_$$

#####################################

./extract_catalog_subset.py ${lensing_workdir}/${IMAGE}_stars.cat ${phot_workdir}/$cluster.unstacked.cat ${phot_workdir}/$cluster.stars.cat
if [ $? -ne 0 ]; then
    echo "Failure in extract_catalog_subset.py"
    exit 3
fi
