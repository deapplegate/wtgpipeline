#!/bin/bash
set -xv
########################
# Process Photometry, from masked, coadded images through photo-zs
#
# Makes some assumptions. Custom jobs should be run manually.
#######################

cluster=$1
detect_filter=$2
lensing_filter=$3
mode=$4  #aper or iso
#PHOTO MERGE STARS SDSS CALIB APPLY SLR
export BONN_TARGET=$cluster
export BONN_FILTER='all'

#./BonnLogger.py clear

########################
# Parse Command Line

measure_photometry=0
merge_filters=0
find_stars=0
sdss=0
fit_calibration=0
apply_calibrations=0
slr=0

for ((i=5;i<=$#;i=i+1)); do

    operation=${!i}
    case "$operation" in
	PHOTO)
	    measure_photometry=1;
	    ;;
	MERGE)
	    merge_filters=1;
	    ;;
	STARS)
	    find_stars=1;
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
	SLR)
	    slr=1;
	    ;;
    esac


done

########################
export subarudir=/nfs/slac/g/ki/ki18/anja/SUBARU
export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU

#adam#photrepo=/nfs/slac/g/ki/ki06/anja/SUBARU/photometry_2010
#adam#lensingrepo=/nfs/slac/g/ki/ki06/anja/SUBARU/lensing_2010
photrepo=/nfs/slac/kipac/fs1/u/awright/SUBARU/photometry
lensingrepo=/nfs/slac/kipac/fs1/u/awright/SUBARU/lensing
if [ ! -d "${photrepo}/${cluster}" ]; then
    mkdir -p ${photrepo}/${cluster}
fi
if [ ! -d "${lensingrepo}/${cluster}" ]; then
    mkdir -p ${lensingrepo}/${cluster}
fi

queue=long

#filters=`grep "${cluster}" cluster.status | awk -v ORS=' ' '($1 !~ /#/){print $2}'`
filters=`grep "${cluster}" cluster_cat_filters.dat | awk -v ORS=' ' '{for(i=3;i<=NF;i++){if($i!~"CALIB" && $i!="K") print $i}}'`
echo "filters=" $filters

photdirname=PHOTOMETRY_${detect_filter}_${mode}
photdir=${photrepo}/${cluster}/${photdirname}

lensingdirname=LENSING_${detect_filter}_${lensing_filter}_${mode}
lensingdir=${lensingrepo}/${cluster}/${lensingdirname}


if [ ! -d "${photdir}" ]; then
    mkdir -p ${photdir}
fi

if [ ! -e "${subarudir}/${cluster}/${photdirname}" ]; then
    ln -s ${photdir} ${subarudir}/${cluster}/${photdirname}
fi

if [ ! -d "${lensingdir}" ]; then
    mkdir -p ${lensingdir}
fi

if [ ! -e "${subarudir}/${cluster}/${lensingdirname}" ]; then
    ln -s ${lensingdir} ${subarudir}/${cluster}/${lensingdirname}
fi

############################
### Mode specific flags
############################
spec_flag="--spec mode=${mode}"

if [ "${mode}" == "aper" ]; then
    fit_phot_flag="--fluxtype APER1 ${spec_flag}"
    slr_flag=APER1
elif [ "${mode}" == "iso" ]; then
    fit_phot_flag="--fluxtype ISO ${spec_flag}"
    slr_flag=APER1
fi

photocalibrate_cat_flag=${spec_flag}
save_slr_flag="${spec_flag} --fluxtype $slr_flag"

#################################################
# Measuring photometry
#################################################

############# Run From Command Line & Separate from other commands ############################


all_phot_cat=${photdir}/${cluster}.unstacked.cat
star_cat=${photdir}/${cluster}.stars.cat

detect_image=${subarudir}/${cluster}/${detect_filter}/SCIENCE/coadd_${cluster}_all/coadd.fits
lensing_image=${subarudir}/${cluster}/${lensing_filter}/SCIENCE/coadd_${cluster}_good/coadd.fits

if [ ! -e "${lensing_image}" ]; then
    echo "!!!!!!!!!!!!!!!!!WARNING: USING ALL IMAGE IN LENSING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    lensing_image=${subarudir}/${cluster}/${lensing_filter}/SCIENCE/coadd_${cluster}_all/coadd.fits
fi


#adam-look# PHOTO (a)
if [ $measure_photometry -eq 1 ]; then

    ./create_seeing_file.sh ${cluster}

    worstseeing=`sort -n -k2 seeing_${cluster}.cat | tail -n1 | awk '{print $2}'`
    detectseeing=`dfits $detect_image | fitsort -d SEEING | awk '{print $2}'`
    convolve=`echo "worst=${worstseeing}; maxconvolve=${detectseeing}+.3; if (maxconvolve < worst) {maxconvolve} else {worst}" | bc`

    detect_dir=`dirname $detect_image`
    echo "detect_dir=" $detect_dir
    detect_base=`basename $detect_image .fits`
    detect_weight=${detect_dir}/${detect_base}.weight.fits
    detect_flag=${detect_dir}/${detect_base}.flag.fits
    seeing=`dfits ${lensing_image} | fitsort -d SEEING | awk '{print $2}'`

    ./extract_object_cats.py --di $detect_image --dw $detect_weight \
       --pi $detect_image --pw $detect_weight --pf $detect_flag \
       --fwhm ${seeing} --new-fwhm ${convolve} \
       -o ${detect_dir}/detection.cat
    if [ $? -ne 0 ]; then
	echo "Failure in extract_object_cats.py"
	exit 1
    fi

    if [ "${mode}" == "iso" ]; then

	detect_image=${detect_dir}/detection.filtered.fits
	if [ ! -e "${detect_dir}/detection.filtered.weight.fits" ]; then
	    ln -s $detect_weight ${detect_dir}/detection.filtered.weight.fits
	fi
	if [ ! -e "${detect_dir}/detection.filtered.flag.fits" ]; then
	    ln -s $detect_flag ${detect_dir}/detection.filtered.flag.fits
	fi

	./extract_object_cats.py --di $detect_image --dw $detect_weight \
	    --pi $detect_image --pw $detect_weight --pf $detect_flag \
	    -o ${detect_dir}/detection.filtered.cat
	if [ $? -ne 0 ]; then
	    echo "Failure in extract_object_cats.py"
	    exit 2
	fi

    fi


    for filter in $filters; do

	jobid=${cluster}.${detect_filter}.${filter}.${mode}.cats

	bsub -q ${queue} -o $subarudir/photlogs/$jobid.log -e $subarudir/photlogs/$jobid.err ./run_unstacked_photometry.sh ${subarudir}/${cluster} ${photdir} ${cluster} ${filter} ${detect_image} ${convolve}
	#adam# How do I get the code to wait here until this job is done running on the batchq?

	#need to make 2 calls; need to modify run_unstacked_photometry to handle two seperate calls.

    done

fi

if [ "${mode}" == "iso" ]; then
    detect_dir=`dirname $detect_image`
    detect_image=${detect_dir}/detection.filtered.fits
fi


##################################################
# MERGING FILTERS
##################################################


#adam-look# MERGE (b)
if [ $merge_filters -eq 1 ]; then

    MERGE_LINE=""
    for filter in $filters; do

	if [ "${filter}" == "B-WHT" ]; then
	    shortfilter=B
	elif [ "${filter}" == "U-WHT" ]; then
	    shortfilter=U
	else
	    shortfilter=$filter
	fi


	if [ ! -e "${photdir}/${filter}/unstacked/$cluster.$shortfilter.unstacked.cat" ]; then
	    echo "Failure in run_unstacked_photometry.sh: ${filter}"
	    exit 11
	fi


	if [ "${filter}" = "${detect_filter}" ]; then
	    MERGE_LINE="${photdir}/${filter}/unstacked/all.filtered.cat ${photdir}/${filter}/unstacked/$cluster.$shortfilter.unstacked.cat $shortfilter ${MERGE_LINE}"
	else

	    MERGE_LINE="${MERGE_LINE} ${photdir}/${filter}/unstacked/$cluster.$shortfilter.unstacked.cat $shortfilter"
	fi
    done


    ./merge_filters.py ${all_phot_cat} ${MERGE_LINE}
    if [ $? -ne 0 ]; then
	echo "Failure in merge_filters.py"
	exit 12
    fi


    if [ ! -s "${all_phot_cat}" ]; then
	echo "Photometry catalog not found!"
	exit 13
    fi



fi

#####################################################
# Find Stars
#####################################################

#adam-look# STARS (c)
if [ $find_stars -eq 1 ]; then

    #adam-SHNT# I think everything up to this point is ok
    ./produce_catalogs.sh ${subarudir}/${cluster} ${photdir} ${lensingdir} ${cluster} ${detect_image} ${lensing_image}
    exit_code=$?
    if [ "${exit_code}" != "0" ]; then
	echo "Failure in produce_catalogs.sh!"
	exit 21
    fi

    if [ ! -s "${star_cat}" ]; then
	echo "Star catalog not found!"
	exit 23
    fi



fi

matched_catalog=${photdir}/${cluster}.sdss.matched.cat

###########################################
# Get SDSS Stars
###########################################

#############  RUN ON TERMINAL, not COMA OR BATCH  ###########################

#adam-look# SDSS (d)
if [ $sdss -eq 1 ]; then

    sdss_cat=${photdir}/sdssstar.cat

    python retrieve_test.py ${detect_image} ${sdss_cat}
    if [ $? -ne 0 ]; then
	echo "Failure in retrieve_test.py!"
	exit 31
    fi
    if [ ! -s "${sdss_cat}" ]; then
	echo "SDSS star cat not found!"
	exit 32
    fi
    ./convert_aper.py ${star_cat} ${photdir}/${cluster}.stars.converted.cat
    ./match_simple.sh ${photdir}/${cluster}.stars.converted.cat ${sdss_cat} ${matched_catalog}
    if [ $? -ne 0 ]; then
	echo "Failure in match_simple.py!"
	exit 33
    fi
    if [ ! -s "${matched_catalog}" ]; then
	echo "Matched catalog not found!"
	exit 34
    fi
fi

################################################
# Photometric calibration
################################################

#adam-look# CALIB (e)
if [ $fit_calibration -eq 1 ]; then
    rm -f ${photdir}/calibration_plots/*
    #old#longfilters=`./dump_cat_filters.py ${star_cat}`
    longfilters=`./dump_cat_filters.py -a ${star_cat}`
    for longfilter in $longfilters; do
	instrum=`echo $longfilter | awk -F'-' '{print $1}'`
	if [ "${instrum}" == "SPECIAL" ] || [ "${instrum}" == "MEGAPRIME" ] || [ "${instrum}" == "CFH12K" ]; then
	    ./fit_phot.py \
		-c ${cluster} \
		-f ${longfilter} \
		-p ${photdir}/calibration_plots \
		-m ${subarudir} \
		-s  \
		${fit_phot_flag}
	    if [ $? -ne "0" ]; then
		echo "Failure in fit_phot.py!"
		exit 41
	    fi
	else
	    ./fit_phot.py \
		-c ${cluster} \
		-i ${matched_catalog} \
		-f ${longfilter} \
		-p ${photdir}/calibration_plots \
		${fit_phot_flag}
	    if [ $? -ne "0" ]; then
		echo "Failure in fit_phot.py!"
		exit 42
	    fi
	fi
    done

    exit_code=$?
    if [ "${exit_code}" != "0" ]; then
	echo "Failure in fit_phot.py!"
	exit 43
    fi

fi

##################################################
# Apply Photometric Calibration
##################################################

#adam-look# APPLY (f)
if [ $apply_calibrations -eq 1 ]; then

    calibrated_cat=${photdir}/${cluster}.calibrated.cat

    ./photocalibrate_cat.py -i ${all_phot_cat} -c ${cluster} -o ${calibrated_cat} ${photocalibrate_cat_flag}
    exit_code=$?
    if [ "${exit_code}" != "0" ]; then
	echo "Failure in photocalibrate_cat.py!"
	exit 51
    fi

    if [ ! -s "${calibrated_cat}" ]; then
	echo "Calibrated Photometry not found!"
	exit 52
    fi

    ./photocalibrate_cat.py -i ${star_cat} -c ${cluster} -o ${photdir}/${cluster}.stars.calibrated.cat ${photocalibrate_cat_flag}

    exit_code=$?
    if [ "${exit_code}" != "0" ]; then
	echo "Failure in photocalibrate_cat.py!"
	exit 53
    fi

    if [ ! -s "${calibrated_cat}" ]; then
	echo "Calibrated Photometry not found!"
	exit 54
    fi

fi

####################################################
# SLR
####################################################

#adam-look# SLR (g)
if [ $slr -eq 1 ]; then

    ./phot_slr.sh ${photdir} ${cluster}.stars.calibrated.cat $slr_flag
    exit_code=$?
    if [ "${exit_code}" != "0" ]; then
	echo "Failure in phot_slr.sh!"
	exit 61
    fi
    ./save_slr.py -c ${cluster} -i ${photdir}/${cluster}.stars.calibrated.cat -o ${photdir}/slr.offsets.list ${save_slr_flag}
    exit_code=$?
    if [ "${exit_code}" != "0" ]; then
	echo "Failure in save_slr.py!"
	exit 62
    fi

    ./photocalibrate_cat.py -i ${all_phot_cat} -c $cluster -o ${photdir}/${cluster}.slr.cat -t slr ${photocalibrate_cat_flag}
    exit_code=$?
    if [ "${exit_code}" != "0" ]; then
	echo "Failre in photocalibrate_cat - slr edition!"
	exit 63
    fi

fi
