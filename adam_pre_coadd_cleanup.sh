#!/bin/bash
set -xvu
cluster=$1
filter=$2
rm -rf ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/plots
rm -rf ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat
rm -rf ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_OLD_OLD_*
rename 's/coadd_/coadd_OLD_/g' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_*
rm ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}*.cat
rm ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/SUPA*.sub.fits


RESULTDIR=${SUBARUDIR}/${cluster}/${filter}/SCIENCE/
find ${RESULTDIR} \
          -name SUPA\*_weighted.fits    -exec rm -f {} \;
find ${RESULTDIR} \
          -name SUPA\*_backsub.fits    -exec rm -f {} \;
find ${RESULTDIR} \
          -name SUPA\*_noobj.fits      -exec rm -f {} \;
find ${RESULTDIR} \
          -name SUPA\*_noobj_mode.fits -exec rm -f {} \;
find ${RESULTDIR} \
          -name SUPA\*_skyback.fits    -exec rm -f {} \;
find ${RESULTDIR} \
          -name SUPA\*_backsub1.fits    -exec rm -f {} \;
find ${RESULTDIR} \
          -name SUPA\*_skyback1.fits    -exec rm -f {} \;
find ${RESULTDIR} \
          -name SUPA\*_backsub_noobj.fits    -exec rm -f {} \;
