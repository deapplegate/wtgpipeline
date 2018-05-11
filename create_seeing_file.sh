#!/bin/bash
set -uxv

#
# inspect all images in a cluster to compile their seeing values
#

cluster=$1


subarudir=/gpfs/slac/kipac/fs1/u/awright/SUBARU/

special_filters="I K"

special_filter_shell_key=`echo $special_filters | sed -e 's/ //g'`

if [  -e seeing_${cluster}.cat ]; then
    rm -f seeing_${cluster}.cat
fi


files="$subarudir/$cluster/W-?-??/SCIENCE/coadd_${cluster}_SUP*/coadd.fits
           $subarudir/$cluster/W-?-?/SCIENCE/coadd_${cluster}_SUP*/coadd.fits
           $subarudir/$cluster/W-?-??/SCIENCE/coadd_${cluster}_all/coadd.fits
           $subarudir/$cluster/W-?-?/SCIENCE/coadd_${cluster}_all/coadd.fits
           $subarudir/$cluster/?/SCIENCE/coadd_${cluster}_*[op]/coadd.fits
           $subarudir/$cluster/?/SCIENCE/coadd_${cluster}_all/coadd.fits
           $subarudir/$cluster/[$special_filter_shell_key]/SCIENCE/coadd_${cluster}_all/coadd.fits
           $subarudir/$cluster/[UB]-WHT/SCIENCE/coadd_${cluster}_*/coadd.fits"

for file in $files; do
    
    if [ -e $file ]; then
	
	seeing=`dfits $file | fitsort -d SEEING | awk '{print $2}'`
	echo $file $seeing >> seeing_${cluster}.cat
    fi
    
done


