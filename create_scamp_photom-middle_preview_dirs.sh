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
find $olddir -type d -name "astrom_photom_scamp_*"
astrom_olddir=`find $olddir -type d -name "astrom_photom_scamp_*"`
echo "ln -s ${astrom_olddir}/cat_photom/SUPA* ${astrom_newdir}/cat_photom/"
echo "ln -s ${astrom_olddir}/cat/SUPA*.ahead ${astrom_newdir}/cat/"
echo "ln -s ${astrom_olddir}/headers/SUPA* ${astrom_newdir}/headers/"

for filt in "W-J-B" "W-J-V" "W-C-RC" "W-S-I+" "W-C-IC" "W-S-Z+"
do
	filtstr="${filt}: "
	if [ -d ${olddir}/${filt} ]; then
		filtstr="${filtstr} : SCIENCE in OLD"
	fi
	if [ -d ${newdir}/${filt} ]; then
		filtstr="${filtstr} : SCIENCE in NEW"
	fi
	oldcalib=`\ls -d ${olddir}/${filt}*CALIB/`
	newcalib=`\ls -d ${newdir}/${filt}*CALIB/`
	if [ -d ${oldcalib} ]; then
		filtstr="${filtstr} : CALIB in OLD"
	fi
	if [ -d ${newcalib} ]; then
		filtstr="${filtstr} : CALIB in NEW"
	fi
done
