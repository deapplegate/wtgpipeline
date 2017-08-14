#! /bin/bash -xv

. progs.ini

cluster=$1
filter=$2
lensext=$3

SUBARUDIR=/nfs/slac/g/ki/ki05/anja/SUBARU
LENSDIR=${SUBARUDIR}/${cluster}/LENSING_${filter}_${filter}_aper/${lensext}
PHOTDIR=${SUBARUDIR}/${cluster}/PHOTOMETRY_${filter}_aper

lensimage=${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${lensext}/coadd.fits
detectimage=${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits
inputcat=${LENSDIR}/lensing.cat
outputcat=${LENSDIR}/coadd_ell.cat


if [ -f ${inputcat} ]; then

  ./measure_shapes.sh ${lensimage} ${detectimage} ${inputcat} ${outputcat}

else

  ./produce_catalogs.sh ${SUBARUDIR} ${PHOTDIR} ${LENSDIR} ${cluster} ${detectimage} ${lensimage}

fi
