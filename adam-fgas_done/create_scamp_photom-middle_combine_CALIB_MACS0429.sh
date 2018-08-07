#!/bin/bash
set -xv
#adam-example# ./create_scamp_photom-middle_combine_dirs.sh RXJ2129 W-J-B W-J-B
cluster=MACS0429-02
astrom_filt_new="W-J-B"
astrom_filt_old="W-J-V"

newdir=/gpfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}
olddir=/nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}

## combine the astrom directories first:

for filt in "W-J-V_2009-01-23_CALIB" "W-C-RC_2009-01-23_CALIB" "W-C-IC_2006-12-21_CALIB"
do
	if [ -d ${olddir}/${filt} ]; then
		if [ ! -d ${newdir}/${filt} ]; then
			## what about for distinct filters in the old, but not in the new?
			mkdir -p ${newdir}/${filt}/SCIENCE/headers_scamp_PANSTARRS/
			#mkdir -p ${newdir}/${filt}/SCIENCE/headers_scamp_photom_PANSTARRS/
			mkdir -p ${newdir}/${filt}/SCIENCE/cat_scampIC
			mkdir -p ${newdir}/${filt}/SCIENCE/cat_scamp
			mkdir -p ${newdir}/${filt}/WEIGHTS

		fi
		cp /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${filt}/WEIGHTS/SUPA*_*I.weight.fits ${newdir}/${filt}/WEIGHTS/
		cp /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${filt}/WEIGHTS/SUPA*_*I.flag.fits ${newdir}/${filt}/WEIGHTS/
		cp /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${filt}/SCIENCE/SUPA*I.fits ${newdir}/${filt}/SCIENCE/
		cp /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${filt}/SCIENCE/SUPA*I.sub.fits ${newdir}/${filt}/SCIENCE/
		cp /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${filt}/SCIENCE/headers_scamp_2MASS/SUPA*.head ${newdir}/${filt}/SCIENCE/headers_scamp_PANSTARRS/
		ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${filt}/SCIENCE/cat_scampIC/SUPA*I.cat ${newdir}/${filt}/SCIENCE/cat_scampIC/
		ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${filt}/SCIENCE/cat_scamp/SUPA*.cat ${newdir}/${filt}/SCIENCE/cat_scamp/
	fi
done
