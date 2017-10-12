#!/bin/bash
set -xv
#adam-example# ./adam_make_coadds_dir.sh MACS1115+01 W-J-B 
#adam-example# ./adam_make_coadds_dir.sh ${cluster} ${filter}

. SUBARU.ini > /tmp/prog.out 2>&1

##################################

export cluster=$1
export filter=$2
# possible coaddition modes:
# - "all" : all images, needs to be run first!
# - "good" : only chips with not too elliptical PSF
# - "rotation" : split by rotation
# - "exposure" : one coadd per exposure
# - "3s" : coadds the SDSS 3s exposure
# - "pretty" : coadds the deep and 3s cluster exposure
# - "gabodsid"


if [ ! -d ${SUBARUDIR}/${cluster}/coadds_together_${cluster} ]; then
	mkdir ${SUBARUDIR}/${cluster}/coadds_together_${cluster}
	mkdir ${SUBARUDIR}/${cluster}/coadds_together_${cluster}/flags
	mkdir ${SUBARUDIR}/${cluster}/coadds_together_${cluster}/weights
fi

for coadd_dir in `\ls -d ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_*/`
do
	coadd_name=`basename ${coadd_dir} `
	ln -s ${coadd_dir}/coadd.fits ${SUBARUDIR}/${cluster}/coadds_together_${cluster}/${coadd_name}.${filter}.fits
	ln -s ${coadd_dir}/coadd.flag.fits ${SUBARUDIR}/${cluster}/coadds_together_${cluster}/flags/${coadd_name}.${filter}.flag.fits
	ln -s ${coadd_dir}/coadd.weight.fits ${SUBARUDIR}/${cluster}/coadds_together_${cluster}/weights/${coadd_name}.${filter}.weight.fits
done

echo "adam-look: ds9e ${SUBARUDIR}/${cluster}/coadds_together_${cluster}/coadd_${cluster}_*.fits &"
