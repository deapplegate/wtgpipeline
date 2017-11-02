#!/bin/bash
set -xv
#adam-does# this is like do_photometry.sh, but it runs the bigmacs version of the SLR (currently the absolute calibration comes from SDSS by way of the -s option in bigmacs, this will need to be changed to 2MASS for non-SDSS clusters).
# 	It also has these features:
# 	1.) It uses the *_APER1-* keyword (second component of the *_APER-* vector in the ldac catalogs)
# 	2.) It writes the ZP and ZP_ERR into image headers (all coadd.fits files) in addition to applying them to the catalogs
# 	3.) It doesn't utilize the photometry_db at all and ignores the lephare_zp entirely
#adam-example# #use next two lines instead# ./adam_do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO MERGE STARS BIGMACSCALIB BIGMACSAPPLY
#adam-example# ./adam_do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO 2>&1 | tee -a OUT-adam_do_photometry-PHOTO.log
#adam-example# ./adam_do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper MERGE STARS BIGMACSCALIB BIGMACSAPPLY 2>&1 | tee -a OUT-adam_do_photometry-MERGE_STARS_BIGMACSCALIB_BIGMACSAPPLY.log
########################
# Process Photometry, from masked, coadded images through photo-zs
#
# Makes some assumptions. Custom jobs should be run manually.
#######################

cluster=$1
detect_filter=$2
lensing_filter=$3
mode=$4  #aper or iso
#PHOTO MERGE STARS SDSS BIGMACSCALIB BIGMACSAPPLY
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
	BIGMACSCALIB)
	    fit_calibration=1;
	    ;;
	BIGMACSAPPLY)
	    apply_calibrations=1;
	    ;;
    esac


done

########################
export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
export subarudir=${SUBARUDIR}
export subdir=${SUBARUDIR}

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

queue="long -W 7000 -R rhel60 "

#filters=`grep "${cluster}" cluster.status | awk -v ORS=' ' '($1 !~ /#/){print $2}'`
filters=`grep "${cluster}" cluster_cat_filters.dat | awk -v ORS=' ' '{for(i=3;i<=NF;i++){if($i!~"CALIB" && $i!="K") print $i}}'`
echo "filters=" $filters

photdirname=PHOTOMETRY_${detect_filter}_${mode}
photdir=${photrepo}/${cluster}/${photdirname}

lensingdirname=LENSING_${detect_filter}_${lensing_filter}_${mode}
lensingdir=${lensingrepo}/${cluster}/${lensingdirname}
#adam-new# so, this determines which type of coadd is used for the lensing image and where to write the lensing cats to (i.e. writes to ${lensingdir}/${lensing_coadd_type})

#adam-tmp#
lensing_coadd_type="gabodsid1554" #adam: default is to use "good" coadd for lensing
#adam-tmp# lensing_coadd_type="good" #adam: default is to use "good" coadd for lensing

#default: lensing_image=${subarudir}/${cluster}/${lensing_filter}/SCIENCE/coadd_${cluster}_good/coadd.fits and cats go to LENSING_${detect_filter}_${lensing_filter}_${mode}/good/
#but, for MACS1226+21 for example, used lensing_coadd_type="gab4060-rot1" 


if [ ! -d "${photdir}" ]; then
    mkdir -p ${photdir}
fi

if [ ! -e "${subarudir}/${cluster}/${photdirname}" ]; then
    ln -s ${photdir} ${subarudir}/${cluster}/${photdirname}
fi

if [ ! -d "${lensingdir}" ]; then
    mkdir -p ${lensingdir}
fi

if [ ! -d "${lensingdir}/${lensing_coadd_type}" ]; then
    mkdir -p ${lensingdir}/${lensing_coadd_type}
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
lensing_image=${subarudir}/${cluster}/${detect_filter}/SCIENCE/coadd_${cluster}_${lensing_coadd_type}/coadd.fits

if [ ! -e "${lensing_image}" ]; then
    echo "!!!!!!!!!!!!!!!!!WARNING: USING ALL IMAGE IN LENSING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    lensing_image=${subarudir}/${cluster}/${lensing_filter}/SCIENCE/coadd_${cluster}_all/coadd.fits
    exit 1; #adam: This should kill the program!
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
	#adam-tmp#
	#if [ "${filter}" == "W-C-IC" ]; then
	#	continue
	#elif [ "${filter}" == "W-C-RC" ]; then 
	#	continue
	#fi

	rm $subarudir/photlogs/$jobid.log $subarudir/photlogs/$jobid.err
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
    ./produce_catalogs.sh ${subarudir}/${cluster} ${photdir} ${lensingdir}/${lensing_coadd_type} ${cluster} ${detect_image} ${lensing_image}
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
# Run BIGMACS to get the Photometric Calibration (i.e. get the zeropoints)
################################################

#adam-look# BIGMACSCALIB (e)
if [ $fit_calibration -eq 1 ]; then
	#adam_bigmacs-make_input_columns.py makes these files:
	#	/nfs/slac/g/ki/ki18/anja/SUBARU//${cluster}/PHOTOMETRY_W-C-RC_aper/${cluster}.sdss.columns
	#	/nfs/slac/g/ki/ki18/anja/SUBARU//${cluster}/PHOTOMETRY_W-C-RC_aper/${cluster}.qc.columns 
	# adam_bigmacs-make_input_columns.py: make the cluster.qc.columns and cluster.sdss.columns files needed to run bigmacs.
	python adam_bigmacs-make_input_columns.py $cluster detect=${detect_filter} aptype=${mode}
	if [ "${exit_code}" != "0" ]; then echo "Failure in BIGMACSCALIB" ; exit 40 ; fi
	# adam_bigmacs-cat_array_splitter.py: split the APER- cat objects in two and save APER1- scalar object, which is the only useful one
	python adam_bigmacs-cat_array_splitter.py -i ${photdir}/${cluster}.unstacked.cat -o ${photdir}/${cluster}.unstacked.split_apers.cat
	if [ "${exit_code}" != "0" ]; then echo "Failure in BIGMACSCALIB" ; exit 41 ; fi
	python adam_bigmacs-cat_array_splitter.py -i ${photdir}/${cluster}.stars.cat -o ${photdir}/${cluster}.stars.split_apers.cat
	exit_code=$?
	if [ "${exit_code}" != "0" ]; then echo "Failure in BIGMACSCALIB" ; exit 42 ; fi
	# makes the MACS1226+21.unstacked.split_apers.cat file
	# makes the MACS1226+21.stars.split_apers.cat file
	export BIGMACS=/nfs/slac/kipac/fs1/u/awright/InstallingSoftware_extension/big-macs-calibrate
	PYTHONPATH_old=$PYTHONPATH
	PYTHONPATH=${BIGMACS}:${PYTHONPATH_old}
	export PYTHONPATH
	cd $BIGMACS
	mkdir ${photdir}/BIGMACS_output/

	#adam-note# use -j for 2MASS and -s for SDSS
	#2MASS# fit zps with 2MASS, bootstrap=5
	#2MASS# python fit_locus.py --file ${photdir}/${cluster}.stars.split_apers.cat --columns ${photdir}/${cluster}.qc.columns --extension 1 --bootstrap 5 --l -j --output ${photdir}/BIGMACS_output/ 2>&1 | tee -a OUT-bigmacs-fit_locus.log
	#SDSS# fit zps with SDSS, bootstrap=5
	python fit_locus.py --file ${photdir}/${cluster}.stars.split_apers.cat --columns ${photdir}/${cluster}.qc.columns --extension 1 --bootstrap 5 --l -s --output ${photdir}/BIGMACS_output/ 2>&1 | tee -a OUT-bigmacs-fit_locus.log
	exit_code=${PIPESTATUS[0]}
	if [ "${exit_code}" != "0" ]; then
		echo "Failure in BIGMACSCALIB"
		exit 43
	fi

	#2MASS# ## fit zps with 2MASS, bootstrap=5
	#2MASS# python fit_locus.py --file /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/PHOTOMETRY_W-C-RC_aper/${cluster}.stars.calibrated.cat --columns /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/PHOTOMETRY_W-C-RC_aper/${cluster}.qc.columns --extension 1 --bootstrap 5 -l -j --output /nfs/slac/g/ki/ki18/anja/SUBARU//${cluster}/PHOTOMETRY_W-C-RC_aper/BIGMACS_output_2MASS-no_unit_test/ -p /nfs/slac/g/ki/ki18/anja/SUBARU//${cluster}/PHOTOMETRY_W-C-RC_aper/BIGMACS_output_2MASS-no_unit_test/PLOTS 2>&1 | tee -a OUT-fit_locus-2MASS-no_unit_test-bootstrap5.log
	cd $bonn
	export PYTHONPATH=$PYTHONPATH_old
	grep -v "^#\|^psfPogCorr" ${photdir}/BIGMACS_output/${cluster}.stars.split_apers.cat.offsets.list | sed 's/\ +-//g;s/\ REDDER//g' >${photdir}/${cluster}.bigmacs_cleaned_offsets.list
	exit_code=`wc -l ${photdir}/${cluster}.bigmacs_cleaned_offsets.list`
	if [ "${exit_code}" -eq  "0" ]; then
		echo "Failure in BIGMACSCALIB"
		exit 43
	fi

fi

##################################################
# Apply the BIGMACS Photometric Calibration (i.e. add the zeropoints to the catalogs and put them in the image headers)
##################################################

#adam-look# BIGMACSAPPLY (f)
if [ $apply_calibrations -eq 1 ]; then

	#apply ZPs in ${photdir}/${cluster}.bigmacs_cleaned_offsets.list, save to cat headers, and save them to images (coadd.fits)
	#example:./adam_bigmacs-apply_zps.py -i /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.unstacked.split_apers.cat -o /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.cat -z /nfs/slac/kipac/fs1/u/awright/SUBARU/photometry/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.bigmacs_cleaned_offsets.list
	./adam_bigmacs-apply_zps.py -i ${photdir}/${cluster}.stars.split_apers.cat -o ${photdir}/${cluster}.stars.calibrated.cat -z ${photdir}/${cluster}.bigmacs_cleaned_offsets.list
	exit_code=$?
	if [ "${exit_code}" != "0" ]; then
	    echo "Failure in adam_bigmacs-apply_zps.py!"
	    exit 51
	fi
	./adam_bigmacs-apply_zps.py -i ${photdir}/${cluster}.unstacked.split_apers.cat -o ${photdir}/${cluster}.calibrated.cat -z ${photdir}/${cluster}.bigmacs_cleaned_offsets.list

	exit_code=$?
	if [ "${exit_code}" != "0" ]; then
	    echo "Failure in adam_bigmacs-apply_zps.py!"
	    exit 53
	fi

	if [ ! -s "${photdir}/${cluster}.calibrated.cat" ]; then
	    echo "Calibrated Photometry not found!"
	    exit 52
	fi
	
	
	if [ ! -s "${photdir}/${cluster}.stars.calibrated.cat" ]; then
	    echo "Calibrated Photometry not found!"
	    exit 54
	fi
	
fi
