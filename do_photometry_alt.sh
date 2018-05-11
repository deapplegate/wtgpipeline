#!/bin/bash
set -uxv
########################
# Process Photometry, from masked, coadded images through photo-zs
#
# Makes some assumptions. Custom jobs should be run manually.
#
# This runs on SDSS fields, but detects stars independently in each exposure
#######################

. progs.ini > /tmp/progs.out 2>&1

cluster=$1
#PHOTO SDSS CALIB APPLY SLR or blank for ALL

########################
# Parse Command Line

measure_photometry=0
sdss=0
fit_calibration=0
apply_calibrations=0
photoz=0
slr=0

if [ $# -eq 1 ]; then
    measure_photometry=1
    sdss=1
    fit_calibration=1
    apply_calibration=1
    photoz=1
    slr=1
elif [ $# -gt 1 ]; then
    for ((i=2;i<=$#;i=i+1)); do

	mode=${!i}
	case "$mode" in
	    PHOTO)
		measure_photometry=1;
		;;
	    SDSS)
		sdss=1;
		;;
	    CALIB)
		fit_calibration=1;
		;;
	    APPLY)
		apply_calibrations=1;
		;;
	    PHOTOZ)
		photoz=1;
		;;
	    SLR)
		slr=1;
		;;

	esac
	

    done
fi


########################

subarudir=/gpfs/slac/kipac/fs1/u/awright/SUBARU

#filters=`grep "${cluster}" cluster.status | awk -v ORS=' ' '($1 !~ /#/){print $2}'`
filters=`grep "${cluster}" cluster_cat_filters.dat | awk -v ORS=' ' '{for(i=3;i<=NF;i++){if($i!~"CALIB" && $i!="K") print $i}}'`

filters=W-C-RC

#################################################
# Catalog production, measuring photometry
#################################################

all_phot_cat=${subarudir}/${cluster}/PHOTOMETRY/${cluster}.unstacked.cat
star_cat=${subarudir}/${cluster}/PHOTOMETRY/${cluster}.stars.cat

lensing_filter=`grep "${cluster}" ${subarudir}/lensing.bands | awk '(NR==1){print $2}'`
if [ -z "$lensing_filter" ]; then
    echo "Cannot Find Lensing Filter!"
    exit 1
fi

detect_image=${subarudir}/${cluster}/${lensing_filter}/SCIENCE/coadd_${cluster}_all/coadd.fits
lensing_image=${subarudir}/${cluster}/${lensing_filter}/SCIENCE/coadd_${cluster}_good/coadd.fits

if [ $measure_photometry -eq 1 ]; then
    
# This is a wrapper around a bunch of steps, and may need to exploded for custom use
    ./produce_catalogs.sh $cluster "$filters" ${lensing_filter} ${detect_image} ${lensing_image}
    exit_code=$?
    if [ "${exit_code}" != "0" ]; then
	echo "Failure in produce_catalogs.sh!"
	exit 1
    fi


    if [ ! -s ${all_phot_cat} ]; then
	echo "Photometry catalog not found!"
	exit 2
    fi


    if [ ! -s ${star_cat} ]; then
	echo "Star catalog not found!"
	exit 3
    fi

fi




for filter in $filters; do

    isSpecial=`grep $filter specialfilters.list`
    matched_catalog=''
    if [ -z "$isSpecial" ]; then
	

	filter_dir=${subarudir}/${cluster}/${filter}
	
	cluster_coadd_dir=${filter_dir}/SCIENCE/coadd_${cluster}_all
	
	photometry=${filter_dir}/PHOTOMETRY
	if [ ! -d ${photometry} ]; then
	    mkdir ${photometry}
	fi
	
	star_calib_cat=${cluster_coadd_dir}/coadd.stars.cat
	if [ ! -e ${star_calib_cat} ]; then
	    echo "Starcat does not exist! ${star_calib_cat}"
	    exit 4
	fi

	
	matched_catalog=${photometry}/${cluster}.sdss.matched.cat

	
        ###########################################
        # Get SDSS Stars
        ###########################################
    
    
	if [ $sdss -eq 1 ]; then

	    sdss_cat=${photometry}/sdssstar.cat
	    
	    python retrieve_test.py ${cluster_coadd_dir}/coadd.fits ${sdss_cat}
	    if [ $? -ne 0 ]; then
		echo "Failure in retrieve_test.py!"
		exit 4
	    fi
	    if [ ! -s $sdss_cat ]; then
		echo "SDSS star cat not found!"
		exit 5
	    fi
	
	    ./convert_aper.py ${star_calib_cat} ${cluster_coadd_dir}/coadd.stars.conv.cat
	    ./match_simple.sh ${cluster_coadd_dir}/coadd.stars.conv.cat ${sdss_cat} ${matched_catalog}
	    if [ $? -ne 0 ]; then
		echo "Failure in match_simple.py!"
		exit 4
	    fi
	    if [ ! -s $matched_catalog ]; then
		echo "Matched catalog not found!"
		exit 5
	    fi
	    
	    
	fi

    fi
    ################################################
    # Photometric calibration
    ################################################

    if [ $fit_calibration -eq 1 ]; then

	rm -f ${subarudir}/${cluster}/PHOTOMETRY/calibration_plots/*

	if [ -z "${isSpecial}" ]; then

	    #old#ftype=`./dump_cat_filters.py ${star_cat} | grep ${filter} | awk -v ORS=' ' '($1 !~ /COADD/){print}' | awk -F'-' '{print $1"-"$2"-"$3}'`
	    ftype=`./dump_cat_filters.py -a ${star_cat} | grep ${filter} | awk -v ORS=' ' '($1 !~ /COADD/){print}' | awk -F'-' '{print $1"-"$2"-"$3}'`

	    ./fit_phot.py \
		-c ${cluster} \
		-i ${matched_catalog} \
		-f ${filter} \
		-t $ftype \
	        -3 \
		-p ${subarudir}/${cluster}/PHOTOMETRY/calibration_plots \
		    
		exit_code=$?
		if [ "${exit_code}" != "0" ]; then
		    echo "Failure in fit_phot.py!"
		    exit 6
		fi

	    #old#longfilters=`./dump_cat_filters.py ${star_cat} | grep ${filter} | awk -v ORS=' ' '{print}'`
	    longfilters=`./dump_cat_filters.py -a ${star_cat} | grep ${filter} | awk -v ORS=' ' '{print}'`
	    
	    ./transfer_photocalibration.py ${cluster} ${ftype}-${filter}_3sec ${longfilters}



	    
	else

	    #old#longfilter=`./dump_cat_filters.py ${star_cat}| awk -v ORS=' ' -F'-' '($4 ~ /^'${filter}'/){print}'`
	    longfilter=`./dump_cat_filters.py -a ${star_cat}| awk -v ORS=' ' -F'-' '($4 ~ /^'${filter}'/){print}'`

	    ./fit_phot.py \
		-c ${cluster} \
		-f ${longfilter} \
		-m ${subarudir} \
		-s \
		-p ${subarudir}/${cluster}/PHOTOMETRY/calibration_plots \

       	    exit_code=$?
	    if [ "${exit_code}" != "0" ]; then
		echo "Failure in fit_phot.py!"
		exit 6
	    fi
	    
	    #old#longfilters=`./dump_cat_filters.py ${star_cat} | awk -v ORS=' ' -F'-' '($4 ~ /^'${filter}'/){print}'`
	    longfilters=`./dump_cat_filters.py -a ${star_cat} | awk -v ORS=' ' -F'-' '($4 ~ /^'${filter}'/){print}'`
	    
	    ./transfer_photocalibration.py ${cluster} ${longfilter} ${longfilters}

	    
	fi
	
    fi
done

##################################################
# Apply Photometric Calibration
##################################################

if [ $apply_calibrations -eq 1 ]; then

    calibrated_cat=${subarudir}/${cluster}/PHOTOMETRY/${cluster}.calibrated.cat

    ./photocalibrate_cat.py -i ${all_phot_cat} -c ${cluster} -o ${calibrated_cat}
    exit_code=$?
    if [ "${exit_code}" != "0" ]; then
	echo "Failure in photocalibrate_cat.py!"
	exit 7
    fi

    if [ ! -s ${calibrated_cat} ]; then
	echo "Calibrated Photometry not found!"
	exit 8
    fi

    ./photocalibrate_cat.py -i ${star_cat} -c ${cluster} -o ${subarudir}/${cluster}/PHOTOMETRY/${cluster}.stars.calibrated.cat
    exit_code=$?
    if [ "${exit_code}" != "0" ]; then
	echo "Failure in photocalibrate_cat.py!"
	exit 7
    fi

    if [ ! -s ${calibrated_cat} ]; then
	echo "Calibrated Photometry not found!"
	exit 8
    fi

fi


####################################################
# SLR
####################################################

if [ $slr -eq 1 ]; then

    ./phot_slr.sh ${subarudir}/${cluster}/PHOTOMETRY ${cluster}.stars.calibrated.cat
    exit_code=$?
    if [ "${exit_code}" != "0" ]; then
	echo "Failure in phot_slr.sh!"
	exit 9
    fi
    ./save_zp.py ${cluster} ${cluster}.stars.calibrated.cat slr.offsets.list slr
    exit_code=$?
    if [ "${exit_code}" != "0" ]; then
	echo "Failure in save_zp.py!"
	exit 10
    fi
    

fi
