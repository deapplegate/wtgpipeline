#!/bin/bash
set -uxv
########################
# Process Photometry, from masked, coadded images through photo-zs
#
# Makes some assumptions. Custom jobs should be run manually.
#######################

. progs.ini > /tmp/progs.out 2>&1



cluster=$1
detect_filter=$2
mode=$3

export BONN_TARGET=$cluster
export BONN_FILTER=$detect_filter

#adam-BL#./BonnLogger.py clear

#SDSS CALIB or blank for all


########################
# Parse Command Line

sdss=0
fit_calibration=0

for ((i=3;i<=$#;i=i+1)); do
    
    command=${!i}
    case "$command" in
	SDSS)
	    sdss=1;
	    ;;
	CALIB)
	    fit_calibration=1;
	    ;;
    esac
done    




########################

subarudir=/nfs/slac/g/ki/ki18/anja/SUBARU
export subarudir
SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
export SUBARUDIR

#adam#photrepo=/nfs/slac/g/ki/ki06/anja/SUBARU/photometry
#adam#lensingrepo=/nfs/slac/g/ki/ki06/anja/SUBARU/lensing
photrepo=/nfs/slac/kipac/fs1/u/awright/SUBARU/photometry
lensingrepo=/nfs/slac/kipac/fs1/u/awright/SUBARU/lensing

queue=kipac-xocq



photrepo=/nfs/slac/g/ki/ki06/anja/SUBARU/photometry
photdirname=PHOTOMETRY_${detect_filter}
photdir=${photrepo}/${cluster}/${photdirname}




filters=W-C-RC

photdirname=PHOTOMETRY_${detect_filter}_${mode}
photdir=${photrepo}/${cluster}/${photdirname}

if [ ! -d ${photdir} ]; then
    mkdir -p ${photdir}
fi

if [ ! -e ${subarudir}/${cluster}/${photdirname} ]; then
    ln -s ${photdir} ${subarudir}/${cluster}/${photdirname}
fi


############################

############################
### Mode specific flags
############################
spec_flag="--spec mode=${mode}"

#######################################


all_phot_cat=${photdir}/${cluster}.unstacked.cat
star_cat=${photdir}/${cluster}.stars.cat


filters=W-C-RC


for filter in $filters; do
echo -----------------------------------
echo ${filter}
echo -----------------------------------


    export BONN_FILTER=${filter}

    isSpecial=`grep $filter specialfilters.list`
    matched_catalog=''
    calibnight=''

    echo "is special  = $isSpecial"

    if [ -z "$isSpecial" ]; then
	

	calibnight=`ls ${subarudir}/${cluster} | grep ${filter} | grep CALIB`
	
	if [ -z "${calibnight}" ]; then
	    continue
	fi
	
	calib_dir=${subarudir}/${cluster}/${calibnight}
	
	sdss_coadd_dir=${calib_dir}/SCIENCE/coadd_${cluster}_3s
	cluster_coadd_dir=${calib_dir}/SCIENCE/coadd_${cluster}_all
	
	photometry_3sec=${calib_dir}/PHOTOMETRY_3sec
	if [ ! -d ${photometry_3sec} ]; then
	    mkdir ${photometry_3sec}
	fi
	

	matched_catalog=${photometry_3sec}/${cluster}.sdss.matched.cat

	
        ###########################################
        # Get SDSS Stars
        ###########################################
    
    
	if [ $sdss -eq 1 ]; then

	    star_3sec_cat=${sdss_coadd_dir}/coadd.stars.cat
	    if [ ! -e ${star_3sec_cat} ]; then
		echo "Starcat does not exist! ${star_3sec_cat}"
		exit 4
	    fi
	    
	    ready=`ldacdesc -i ${star_3sec_cat} -t OBJECTS | grep name | grep BackGr | wc | awk '{print $1}'`
	    if [ ${ready} -eq 0 ]; then
		echo "Need to run "
		echo "     check_psf_3s_vis.sh ${sdss_coadd_dir} "
		exit 9
	    fi


	    sdss_cat=${photometry_3sec}/sdssstar.cat
	    
	    python retrieve_test.py ${sdss_coadd_dir}/coadd.fits ${sdss_cat}
	    if [ $? -ne 0 ]; then
		echo "Failure in retrieve_test.py!"
		exit 4
	    fi
	    if [ ! -s $sdss_cat ]; then
		echo "SDSS star cat not found!"
		exit 5
	    fi
	
	    
	    ./convert_aper.py ${star_3sec_cat} ${sdss_coadd_dir}/coadd.stars.conv.cat
	    ./match_simple.sh ${sdss_coadd_dir}/coadd.stars.conv.cat ${sdss_cat} ${matched_catalog}

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

	rm -f ${photdir}/calibration_plots/*

	if [ -z "${isSpecial}" ]; then
	
	    ./fit_phot.py \
		-c ${cluster} \
		-i ${matched_catalog} \
		-f ${filter} \
		-p ${photdir}/calibration_plots \
		-t SUBARU-10_2-1 \
		-3 ${spec_flag}
		#--free-color \
		#-3
	    exit_code=$?
	    if [ "${exit_code}" != "0" ]; then
		echo "Failure in fit_phot.py!"
		exit 6
	    fi
	    
	    #old#longfilters=`./dump_cat_filters.py ${star_cat} | grep ${filter}`
	    longfilters=`./dump_cat_filters.py -a ${star_cat} | grep ${filter}`
	    
	    ./transfer_photocalibration.py -c ${cluster} -f SUBARU-10_2-1-${filter}_3sec ${longfilters} ${spec_flag}
	    
	else

	    #old#longfilters=`./dump_cat_filters.py ${star_cat} | grep ${filter}`
	    longfilters=`./dump_cat_filters.py -a ${star_cat} | grep ${filter}`

	    ./fit_phot.py \
		-c ${cluster} \
		-f ${longfilter} \
		-p ${photdir}/calibration_plots \
		-m ${subarudir} \
		-s ${spec_flag}

       	    exit_code=$?
	    if [ "${exit_code}" != "0" ]; then
		echo "Failure in fit_phot.py!"
		exit 6
	    fi
	    
	    #old#longfilters=`./dump_cat_filters.py ${star_cat} | grep ${filter}`
	    longfilters=`./dump_cat_filters.py -a ${star_cat} | grep ${filter}`
	    
	    ./transfer_photocalibration.py ${cluster} ${longfilter} ${longfilters}

	    
	fi
	
    fi
done
