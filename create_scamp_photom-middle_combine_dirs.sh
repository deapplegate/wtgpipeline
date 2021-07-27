#!/bin/bash
set -xv
#adam-example# ./create_scamp_photom-middle_combine_dirs.sh RXJ2129 W-J-B W-J-B
cluster=$1
astrom_filt_new=$2
astrom_filt_old=$3

newdir=/gpfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}
olddir=/nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}

## combine the astrom directories first:
astrom_newdir=/gpfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}/${astrom_filt_new}/SCIENCE/astrom_photom_scamp_SDSS-R6/
astrom_olddir=/nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${astrom_filt_old}/SCIENCE/astrom_photom_scamp_SDSS-R6/
if [ ! -d ${astrom_newdir} ]; then
	exit 1
fi
if [ ! -d ${astrom_newdir}/cat_photom/ ]; then
	exit 1
fi
if [ ! -d ${astrom_newdir}/headers/ ]; then
	exit 1
fi
if [ ! -d ${astrom_olddir} ]; then
	exit 1
fi
ln -s ${astrom_olddir}/cat_photom/SUPA* ${astrom_newdir}/cat_photom/
ln -s ${astrom_olddir}/cat/SUPA*.ahead ${astrom_newdir}/cat/
ln -s ${astrom_olddir}/headers/SUPA* ${astrom_newdir}/headers/

for filt in "W-J-B" "W-J-V" "W-C-RC" "W-S-I+" "W-C-IC" "W-S-Z+"
do
	if [ -d ${olddir}/${filt} ]; then
		if [ ! -d ${newdir}/${filt} ]; then
			## what about for distinct filters in the old, but not in the new?
			mkdir -p ${newdir}/${filt}/SCIENCE/headers_scamp_SDSS-R6/
			#mkdir -p ${newdir}/${filt}/SCIENCE/headers_scamp_photom_SDSS-R6/
			mkdir -p ${newdir}/${filt}/SCIENCE/cat_scampIC
			mkdir -p ${newdir}/${filt}/WEIGHTS

		fi
		cp /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${filt}/WEIGHTS/SUPA*_*I.weight.fits ${newdir}/${filt}/WEIGHTS/
		cp /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${filt}/WEIGHTS/SUPA*_*I.flag.fits ${newdir}/${filt}/WEIGHTS/
		ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${filt}/SCIENCE/SUPA*I.fits ${newdir}/${filt}/SCIENCE/
		ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${filt}/SCIENCE/SUPA*I.sub.fits ${newdir}/${filt}/SCIENCE/
		cp /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${filt}/SCIENCE/headers_scamp_SDSS-R6/SUPA*.head ${newdir}/${filt}/SCIENCE/headers_scamp_SDSS-R6/
		ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${filt}/SCIENCE/cat_scampIC/SUPA*I.cat ${newdir}/${filt}/SCIENCE/cat_scampIC/
	fi
done


## OLD example:
#rename 's/OCFSI/OCFSRI/g' SUPA0019*.cat
#cd ../headers_scamp_SDSS-R6/
#cp /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/W-C-RC/SCIENCE/headers_scamp_SDSS-R6/SUPA*.head .
## now combine the astrom_photom_scamp_SDSS-R6 stuff!
#find . -name "astrom_photom_scamp_SDSS-R6"
#ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/W-J-V/SCIENCE/astrom_photom_scamp_SDSS-R6/cat_photom/SUPA* ~/data/${cluster}/W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6
#ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/W-J-V/SCIENCE/astrom_photom_scamp_SDSS-R6/headers/SUPA* ~/data/${cluster}/W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6

#mkdir -p /u/ki/awright/data/${cluster}/W-C-IC/SCIENCE/headers_scamp_SDSS-R6/
#mkdir -p /u/ki/awright/data/${cluster}/W-C-IC/SCIENCE/headers_scamp_photom_SDSS-R6/
#mkdir -p /u/ki/awright/data/${cluster}/W-C-IC/SCIENCE/cat_scampIC
#mkdir -p /u/ki/awright/data/${cluster}/W-C-IC/WEIGHTS
#cp /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/W-C-IC/WEIGHTS/SUPA*_*I.weight.fits /u/ki/awright/data/${cluster}/W-C-IC/WEIGHTS/
#cp /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/W-C-IC/WEIGHTS/SUPA*_*I.flag.fits /u/ki/awright/data/${cluster}/W-C-IC/WEIGHTS/
#ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/W-C-IC/SCIENCE/SUPA*I.fits /u/ki/awright/data/${cluster}/W-C-IC/SCIENCE/
#ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/W-C-IC/SCIENCE/SUPA*I.sub.fits /u/ki/awright/data/${cluster}/W-C-IC/SCIENCE/
#cp /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/W-C-IC/SCIENCE/headers_scamp_SDSS-R6/SUPA*.head /u/ki/awright/data/${cluster}/W-C-IC/SCIENCE/headers_scamp_SDSS-R6/
#ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/W-C-IC/SCIENCE/cat_scampIC/SUPA*I.cat /u/ki/awright/data/${cluster}/W-C-IC/SCIENCE/cat_scampIC/
