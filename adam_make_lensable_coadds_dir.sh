#!/bin/bash
set -xv
#adam-example# ./adam_make_lensable_coadds_dir.sh MACS1115+01
#adam-example# ./adam_make_lensable_coadds_dir.sh ${cluster}

. SUBARU.ini > /tmp/prog.out 2>&1

##################################

export cluster=$1
# possible coaddition modes:
# - "all" : all images, needs to be run first!
# - "good" : only chips with not too elliptical PSF
# - "rotation" : split by rotation
# - "exposure" : one coadd per exposure
# - "3s" : coadds the SDSS 3s exposure
# - "pretty" : coadds the deep and 3s cluster exposure
# - "gabodsid"


for filter in W-J-V W-C-RC W-C-IC W-S-I+
do
	if [ ! -d ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/ ]; then
		continue
	fi
	if [ ! -d ${SUBARUDIR}/${cluster}/coadds_lensable_${cluster} ]; then
		mkdir ${SUBARUDIR}/${cluster}/coadds_lensable_${cluster}
		mkdir ${SUBARUDIR}/${cluster}/coadds_lensable_${cluster}/flags
		mkdir ${SUBARUDIR}/${cluster}/coadds_lensable_${cluster}/weights
	fi

	for coadd_dir in `\ls -d ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_g*/`
	do
		coadd_name=`basename ${coadd_dir} `
		ln -s ${coadd_dir}/coadd.fits ${SUBARUDIR}/${cluster}/coadds_lensable_${cluster}/${coadd_name}.${filter}.fits
		ln -s ${coadd_dir}/coadd.flag.fits ${SUBARUDIR}/${cluster}/coadds_lensable_${cluster}/flags/${coadd_name}.${filter}.flag.fits
		ln -s ${coadd_dir}/coadd.weight.fits ${SUBARUDIR}/${cluster}/coadds_lensable_${cluster}/weights/${coadd_name}.${filter}.weight.fits
	done

	echo "adam-look: ds9e ${SUBARUDIR}/${cluster}/coadds_lensable_${cluster}/coadd_${cluster}_*.fits &"
done
dfits /gpfs/slac/kipac/fs1/u/awright/SUBARU//${cluster}/coadds_lensable_${cluster}/coadd_${cluster}_*.fits | fitsort SEEING EXPTIME > /gpfs/slac/kipac/fs1/u/awright/SUBARU//${cluster}/coadds_lensable_${cluster}/SEEING_EXPTIME.txt
