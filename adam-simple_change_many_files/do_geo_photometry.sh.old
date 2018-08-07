#!/bin/bash -u
######################
# 20 Mar 2012 - Run through relevant steps of photometry
#  to propagate geocor to slr catalogs
######################


cluster=$1
detect_filter=$2
mode=aper

#####################


subarudir=/nfs/slac/g/ki/ki18/anja/SUBARU
export subarudir
SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
export SUBARUDIR
#adam#photrepo=/nfs/slac/g/ki/ki06/anja/SUBARU/photometry
photrepo=/nfs/slac/kipac/fs1/u/awright/SUBARU/photometry

filters=`grep "${cluster}" cluster_cat_filters.dat | awk -v ORS=' ' '{for(i=3;i<=NF;i++){if($i!~"CALIB" && $i!="K") print $i}}'`

photdirname=PHOTOMETRY_${detect_filter}_${mode}
photdir=${photrepo}/${cluster}/${photdirname}


############################
### Mode specific flags
############################
spec_flag="--spec mode=${mode}"

if [ "${mode}" == "aper" ]; then
    fit_phot_flag="--fluxtype APER1 ${spec_flag}"
    slr_flag=APER
elif [ "${mode}" == "iso" ]; then
    fit_phot_flag="--fluxtype ISO ${spec_flag}"
    slr_flag=ISO
fi

photocalibrate_cat_flag=${spec_flag}
save_slr_flag=${spec_flag}


##########################

all_phot_cat=${photdir}/${cluster}.unstacked.geocor.cat
star_cat=${photdir}/${cluster}.stars.cat

detect_image=${subarudir}/${cluster}/${detect_filter}/SCIENCE/coadd_${cluster}_all/coadd.fits




########################


MERGE_LINE=""
for filter in $filters; do

    if [ "${filter}" == "B-WHT" ]; then
	shortfilter=B
    elif [ "${filter}" == "U-WHT" ]; then
	shortfilter=U
    else
	shortfilter=$filter
    fi
    
    
    if [ ! -e ${photdir}/${filter}/unstacked/$cluster.$shortfilter.unstacked.cor.cat ]; then
	echo "Failure in run_unstacked_photometry.sh: ${filter}"
	exit 11
    fi
    
    
    if [ "${filter}" = "${detect_filter}" ]; then
	MERGE_LINE="${photdir}/${filter}/unstacked/all.filtered.cat ${photdir}/${filter}/unstacked/$cluster.$shortfilter.unstacked.cor.cat $shortfilter ${MERGE_LINE}"
    else
	
	MERGE_LINE="${MERGE_LINE} ${photdir}/${filter}/unstacked/$cluster.$shortfilter.unstacked.cor.cat $shortfilter"
    fi
done


./merge_filters.py ${all_phot_cat} ${MERGE_LINE}
if [ $? -ne 0 ]; then
    echo "Failure in merge_filters.py"
    exit 12
fi


if [ ! -s ${all_phot_cat} ]; then
    echo "Photometry catalog not found!"
    exit 13
fi

###########################




./photocalibrate_cat.py -i ${all_phot_cat} -c $cluster -o ${photdir}/${cluster}.slr.geocor.cat -t slr ${photocalibrate_cat_flag}
exit_code=$?
if [ "${exit_code}" != "0" ]; then
    echo "Failre in photocalibrate_cat - slr edition!"
    exit 63
fi
    
