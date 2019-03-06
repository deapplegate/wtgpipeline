#!/bin/bash
set -xv
#example: lensext='good' ; filter="W-C-RC" ; cluster="MACS0416-24"
#adam-example# ./measure_shapes_wrapper.sh ${cluster} ${filter} ${lensext}


. progs.ini > /tmp/progs.out 2>&1 

cluster=$1
filter=$2
lensext=$3

SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
LENSDIR=${SUBARUDIR}/${cluster}/LENSING_${filter}_${filter}_aper/${lensext}
PHOTDIR=${SUBARUDIR}/${cluster}/PHOTOMETRY_${filter}_aper

lensimage=${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${lensext}/coadd.fits
detectimage=${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits
inputcat=${LENSDIR}/lensing.cat
outputcat=${LENSDIR}/coadd_ell.cat


if [ -f ${inputcat} ]; then

  #adam-old#./measure_shapes.sh ${lensimage} ${detectimage} ${inputcat} ${outputcat}
  ./measure_shapes.sh ${lensimage} ${inputcat} ${outputcat} ${TEMPDIR}

else

  ./produce_catalogs.sh ${SUBARUDIR} ${PHOTDIR} ${LENSDIR} ${cluster} ${detectimage} ${lensimage}

fi
