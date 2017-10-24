#! /bin/bash
set -xv

#adam-does# this is contains all of the preliminaries that you need to start with in order to do the preprocessing steps.
#	primary script to pull from to peg onto the end is from adam_MACS1115-do_Subaru_preprocess.sh
#	search for #adam-CHANGE# for the things you may need to change in certain circumstances
pprun=2010-03-12_W-J-B
filter=${pprun#2*_}
run=${pprun%_*}
ending=`grep "$pprun" ~/wtgpipeline/fgas_pprun_endings.txt | awk '{print $2}'`
export BONN_TARGET=${run}
export BONN_FILTER=${filter}

####################################################
### the following need to be specified for each run
####################################################
. progs.ini > /tmp/progs.out 2>&1
REDDIR=`pwd`
export INSTRUMENT=SUBARU
export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
#run="2010-03-12" ; filter="W-S-I+";FLAT=SKYFLAT  #Z2701   10_3 2010-03-12_W-S-I+
SET=SET1            # sets time period of flat to use
SKYBACK=256         # in case of SKYFLAT: size of background mesh for superflat illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?) 16 (or 32) if lots of blobs
####################################################
### set FLAT, FRINGE, and ENDING ( fringing correction for Z band only )
####################################################

if [ -d ${SUBARUDIR}/${run}_${filter}/DOMEFLAT ]; then
	FLAT=DOMEFLAT
elif [ -d ${SUBARUDIR}/${run}_${filter}/SKYFLAT ]; then
	FLAT=SKYFLAT
else
    echo "You need flats!"
    exit 2;
fi
FRINGE=NOFRINGE # FRINGE if fringing correction necessary; NOFRINGE otherwise
if [ "${filter}" == "W-S-Z+" ] ; then
	FRINGE="FRINGE"
	if [ ${ending} != "OCFSF" ]; then
		exit 1
	fi
fi
SCIENCEDIR=SCIENCE_${FLAT}_${SET}

####################################################
### set config, can make this changable if you like
####################################################
config="10_3"
#adam-CHANGE# change this if I'm working with multiple configs!
#./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
#exit_stat=$?
#if [ "${exit_stat}" -gt "0" ]; then
#	exit ${exit_stat};
#fi
. ${INSTRUMENT:?}.ini > /tmp/instrum.out 2>&1

####################################################
### a quick example
####################################################
#if [ "$config" == "10_3" ] ; then
#	./parallel_manager.sh ./process_science_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE} #8
#elif [ "$config" == "10_2" ] ; then
#	./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE} #8
#else
#	echo "problem with config";exit 1
#fi
#exit_stat=$?
#if [ "${exit_stat}" -gt "0" ]; then
#	exit ${exit_stat};
#fi

####################################################
### START pasting in new stuff below here!
####################################################

########################################################t#
#### #weights: GLOBAL WEIGHT CREATION
##########################################################
#see postH_preprocess_template-weights.sh

#BLOCK8#

if [ ! -d ${SUBARUDIR}/${run}_${filter}/reg/ ] ; then
	mkdir ${SUBARUDIR}/${run}_${filter}/reg/
fi
if [ ! -d ${SUBARUDIR}/${run}_${filter}/DARK/ ] ; then
	mkdir ${SUBARUDIR}/${run}_${filter}/DARK/
fi


#adam-DO# copy over the region files to the /reg/ directory in ${run}_${filter} (COPY, DON'T LINK!)
#STARTOVER-REGION CHANGE# IF YOU MESS WITH REGION FILES YOU MUST START OVER AT THIS POINT!
for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
do
    if [ ! -e ${SUBARUDIR}/${run}_${filter}/DARK/DARK_${CHIP}.fits ]; then
	cp ${SUBARUDIR}/${config}_DARK/DARK/DARK_${CHIP}.fits ${SUBARUDIR}/${run}_${filter}/DARK/
    fi

    if [ ! -e ${SUBARUDIR}/${run}_${filter}/reg/globalweight_${CHIP}.reg ]; then
	cp ${SUBARUDIR}/${config}_reg/globalweight_${CHIP}.reg ${SUBARUDIR}/${run}_${filter}/reg/globalweight_${CHIP}.reg
    fi

    if [ -e ${SUBARUDIR}/${run}_${filter}/reg/globalweight_${CHIP}.reg ]; then
	cp ${SUBARUDIR}/${run}_${filter}/reg/globalweight_${CHIP}.reg ${SUBARUDIR}/${run}_${filter}/reg/SUBARU_${CHIP}.reg
    fi
done
#exit 0; #11
#adam# these two lines are needed if you have region files. these make the region files consistent with the current distribution of ds9
#convertRegion2Poly.py just backs up the directory
./convertRegion2Poly.py ${SUBARUDIR} ${run}_${filter} #12
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi
./transform_ds9_reg_alt.sh ${SUBARUDIR} ${run}_${filter} #12
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi
#exit 0; #12

#adam-notes# find removed USELESS BLOCK and stuff about how I used to do the limits and regions before WeightMasker in do_Subaru_preprocess_notes.sh search #OLD MASKS

#BLOCK9#
#adam# this will use the flats and darks to make run_filter/WEIGHTS/global*.fits
#adam# this uses the tools I've developed, it applies the SUPER WIDE uniform cuts, then uses WeightMasker and region files to mask out bad pixels in globalweights_1.fits
#nisius############SUPER WIDE BASE_WEIGHT LIMITS USED HERE!########################
#adam# The DARK limits are the same unless config changes (these were fit by eye)
#10_3#super wide limits that I just use because this doesn't matter much at this point (this is found by taking the min of the lower limits and max of the upper limits for all "by eye" limits for each filter, then taking min-.04 and max+.08 so that I'm sure this will cut almost nothing out)
#STARTOVER-CHANGE DARK LIMS or CHANGE WeightMasker#
#adam# to mess with limits, see ~/thiswork/scripts/Plot_Light_Cutter.py
#adam# The DARK limits are the same unless config changes (these were fit by eye)
#adam# The FLAT limits may not be the same

#adam-notes# find "By Eye" limits for old filters/runs in do_Subaru_preprocess_notes.sh search #BY EYE LIMITS
if [ "$config" == "10_3" ] ; then
	#10_3#super wide limits that I just use because this doesn't matter much at this point (this is found by taking the min of the lower limits and max of the upper limits for all "by eye" limits for each filter, then taking min-.04 and max+.04 so that I'm sure this will cut almost nothing out)
	#10_3# DARKs play a very minor role in 10_3 cuts, as they should, because they're basically gaussians
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.42 1.04 DARK -1.73 4.15 1
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.74 1.11 DARK -1.88 4.6 2
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.79 1.15 DARK -1.88 4.9 3
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.69 1.12 DARK -1.88 5.35 4
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.32 1.1 DARK -2.94 5.95 5
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.37 1.11 DARK -1.88 5.5 6
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.74 1.14 DARK -1.73 4.75 7
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.81 1.19 DARK -2.04 4.75 8
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.59 1.09 DARK -1.43 4.6 9
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.3 1.07 DARK -1.58 4.75 10 # 13

elif [ "$config" == "10_2" ] ; then
	#10_2-new# use these ultra-wide BASE_WEIGHT limits for 10_2 where CCD #6 has super low counts so we don't use it. Also, I've copied over DARK frames and have fit limits for them.
	#10_2-new# CCD #7 has a very real feature along one edge in the darks that makes it so very little is cut out in the other CCDs, but in #7 more pixels are outside the limits
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.22 1.24 DARK -4.20 9.56 1
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.54 1.31 DARK -4.20 8.56 2
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.59 1.35 DARK -4.20 7.95 3
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.49 1.32 DARK -4.20 7.03 4
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.12 1.30 DARK -4.20 7.22 5
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.17 1.31 DARK -4.20 7.06 6
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.54 1.34 DARK -4.20 9.56 7
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.61 1.39 DARK -4.20 6.99 8
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.39 1.29 DARK -4.20 6.84 9
	./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.10 1.27 DARK -4.20 7.08 10

	#10_2-old# use these ultra-wide BASE_WEIGHT limits for 10_2 where CCD #6 has super low counts so we don't use it. Also, I've copied over DARK frames and have fit limits for them.
	#10_2-old#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.22 1.24 DARK -5.00 10.06 1
	#10_2-old#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.54 1.31 DARK -5.00 9.06 2
	#10_2-old#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.59 1.35 DARK -5.00 8.45 3
	#10_2-old#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.49 1.32 DARK -5.00 6.84 4
	#10_2-old#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.12 1.30 DARK -5.00 7.04 5
	#10_2-old#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.17 1.31 DARK -5.00 6.84 6
	#10_2-old#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.54 1.34 DARK -5.00 13.29 7
	#10_2-old#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.61 1.39 DARK -5.00 6.84 8
	#10_2-old#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.39 1.29 DARK -5.00 6.84 9
	#10_2-old#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.10 1.27 DARK -5.00 6.64 10
else
	echo "problem with config";exit 1
fi
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi

#adam# make weighted science images
./create_global_science_weighted.sh ${SUBARUDIR}/${run}_${filter} SCIENCE WEIGHTS #14
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi
./parallel_manager.sh WeightMasker.py ${SUBARUDIR}/${run}_${filter}/WEIGHTS #15
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi
exit 0; #13
echo "Todo: Mask SCIENCE Flats for dust grains, missed hot pixels, etc.
Use the images in the SCIENCE_weighted directory for masking.
Region files should be saved in $maindir/reg.
For precision masking, using mark_badpixel_regions.pl."

#adam-DO check# MAKE SURE BAD THINGS (hot pixels, etc.) ARE COVERED BY REGION FILES:
#	ds9 ${run}_${filter}/WEIGHTS/globalweight_*.fits

##########################################################
###./splitoff_aux_data.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending} ${SUBARUDIR}/SUBARU.list
##########################################################
###groups together cluster pointings from one run
#./distribute_sets_subaru.sh ${SUBARUDIR} ${run}_${filter}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list
### note: this script now also copies globalweight*.fits and globalflag*fits
### to ${SUBARUDIR}/${cluster}/${filter}/WEIGHTS
#15 made: all of the plots DefectMasker makes and backup files and changed globalweights_#.fits
exit 0; #15
