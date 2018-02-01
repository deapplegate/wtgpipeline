#! /bin/bash
set -xv
#adam-does# this is a template for how to catch new data up to speed. Mainly this will be useful for catching new superflat data I want to add.

####################################################
### the following need to be specified for each run
####################################################
pprun="2010-12-05_W-J-V"
FLAT="DOMEFLAT"
config="10_3"
filter=${pprun#2*_}
run=${pprun%_*}
SET=SET1            # sets time period of flat to use
SKYBACK=256          # in case of SKYFLAT: size of background mesh for superflat
                    # illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?)
                    # 16 (or 32) if lots of blobs
SCIENCEDIR=SCIENCE_${FLAT}_${SET}

export INSTRUMENT=SUBARU
export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
##################################################################

### superscript template to do the preprocessing
. progs.ini > /tmp/progs.out 2>&1
REDDIR=`pwd`

./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
. ${INSTRUMENT:?}.ini > /tmp/instr.out 2>&1

#adam# fringing correction for Z band only
FRINGE=NOFRINGE
if [ "${filter}" == "W-S-Z+" ] ; then
	FRINGE="FRINGE"
fi

if [ ${FRINGE} == "FRINGE" ]; then
    ending="OCFSF"
elif [ ${FRINGE} == "NOFRINGE" ]; then
    ending="OCFS"
else
    echo "You need to specify FRINGE or NOFRINGE for the fringing correction!"
    exit 2;
fi


BeforeSuperflat="NOTDONE"
AfterSuperflat="DONE"
if [ "${BeforeSuperflat}" != "DONE" ] ; then
	./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter}/ SCIENCE
	#### processes SCIENCE frames:
	#### overscan, bias, flat -->  SUPA*_${chip}OCF.fits
	#adam# process the SCIENCE images result=(science-bias)/(flat-bias)
	#makes (in undo form): rm SUPA*OCF.fits ; rm SUPA*OCF_sub.fits ; rm SCIENCE_*.fits ; mv SPLIT_IMAGES/SUPA*.fits . ; rm -r SUB_IMAGES/ ; rm -r SPLIT_IMAGES/
	## also sets up superflat stuff, to exclude things from superflat, put them here:
	#    # modify the input list of images
	# in case we have to reject files for the superflat: ${SUBARUDIR}/${run}_${filter}/superflat_exclusion
	#THIS TAKES ~15 min#
	if [ "$config" == "10_3" ] ; then
		./parallel_manager.sh ./process_science_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE} #8
	elif [ "$config" == "10_2" ] ; then
		./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE} #8
	else
		echo "problem with config";exit 1
	fi
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	#./parallel_manager.sh ./spikefinder_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA OCF ${filter}
	#adam-del# #10_2 & 10_3# this is where process_science_4channels_eclipse_para.sh calls things OCF and process_science_eclipse_para.sh calls things OFC, so you gotta change that in this code (tried changing process_science_eclipse_para.sh, but it won't work)
	#adam# normalize the science images
	#./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUP OCF #9
	#exit_stat=$?
	#if [ "${exit_stat}" -gt "0" ]; then
	#	exit ${exit_stat};
	#fi
	#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_norm SUP "OCFN" 8 -32 #9
	#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_norm SUP "OCFN" 8 -32 > OUT-create_binnedmosaics.log 2>&1
	#exit_stat=$?
	#if [ "${exit_stat}" -gt "0" ]; then
	#	exit ${exit_stat};
	#fi

	#adam-new#
	####################################################################
	#
	#./BonnLogger.py comment "A: Process Superflat"
	#
	#### OCF SCIENCE frames + superflat (allows for easy tryout of diff flat fields)

	#run="2010-12-05" ; filter="W-J-V"; FLAT=DOMEFLAT #Z2701   10_3 2010-12-05_W-J-V
	#"2010-12-05"
	#SCIENCEDIR=SCIENCE_${FLAT}_${SET}
	#echo "SCIENCEDIR=" ${SCIENCEDIR}
	#ls ${SUBARUDIR}/${run}_${filter}/${SCIENCEDIR}/SUPA*OCF.fits | wc -l
	#ls ${SUBARUDIR}/${run}_${filter}/SCIENCE/SUPA*OCF.fits | wc -l

	#adam# have to copy SCIENCE/SUPA*OCF.fits files over to ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR
	#if [ ! -d ${SUBARUDIR}/${run}_${filter}/${SCIENCEDIR} ]; then
	#    mkdir ${SUBARUDIR}/${run}_${filter}/${SCIENCEDIR}
	#    cp ${SUBARUDIR}/${run}_${filter}/SCIENCE/SUPA*OCF.fits ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR
	#fi
fi

#questions#
# 	* what is eclipse anyway? -> this is the software that messes with stuff (does the Overscan, Cut/Trim, Flat-fielding, Renormalizing, etc.)
# 	* what is RESCALE? (In process_sub_images_para.sh it determines FLAT properties) -> it's just the renormalizing thing
# 	* should I even run lines like "./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "_fringe${SKYBACK}" 8 -32" if there is no fringing correction? -> No, you don't have to run them
# 	* illum isn't the IC, so what is it? -> Its the superflat
# 	* is the superflat correction supposed to be run only on the OC.fits, not OCF.fits? -> run it on the OCF files
#for other example see: ~/thiswork/preprocess_scripts/do_Subaru_preprocess_2007-07-18_W-J-V.sh #
SCIENCEDIR=SCIENCE_${FLAT}_${SET}
echo "SCIENCEDIR=" ${SCIENCEDIR}

if [ "${AfterSuperflat}" != "DONE" ] ; then
	#adam# have to copy SCIENCE/SUPA*OCF.fits files over to ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR
	if [ ! -d ${SUBARUDIR}/${run}_${filter}/${SCIENCEDIR} ]; then
	    mkdir ${SUBARUDIR}/${run}_${filter}/${SCIENCEDIR}
	    cp ${SUBARUDIR}/${run}_${filter}/SCIENCE/SUPA*OCF.fits ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR
	fi
	#delA# ./parallel_manager.sh ./process_sub_images_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} NOFRINGE
	./parallel_manager.sh ./process_sub_images_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} NOFRINGE
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	#delB# ./parallel_manager.sh ./process_sub_images_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} NOFRINGE

	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi

	### A: PROCESS SUPERFLAT ###
	#delA#./parallel_manager.sh process_superflat_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_${FLAT}_${SET}
	./parallel_manager.sh ./process_superflat_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	#delB#./parallel_manager.sh process_superflat_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_${FLAT}_${SET}

	### Create Illum/Fringe Corrections (both of them, then you can choose not to use the fringe stuff if you don't want to)
	#delA#./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR ${SKYBACK}
	./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR ${SKYBACK}
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	#delB#./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR ${SKYBACK}


	./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "" 8 -32
	./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "_illum${SKYBACK}" 8 -32
	##./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "_fringe${SKYBACK}" 8 -32

	./create_norm.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	./create_norm_illum_fringe.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} $SKYBACK
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	./make_residuals.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR ${SKYBACK}
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "" 8 -32
	./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "_illum${SKYBACK}" 8 -32
	#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "_fringe${SKYBACK}" 8 -32

	echo "adam-look| Todo: Inspect ${SCIENCEDIR}/BINNED frames for bright stars, autotracker shadows, etc.
	Create maindir/superflat_exclusion, which is a list of the SUPAxxx_CHIP frames to exclude. 
	createExclusion.py may help in making the list."
	./make_binned_sets.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm/BINNED
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	#adam# to make exclusion list, do this: ./createExclusion.py ${SUBARUDIR}/${run}_${filter}/...
	echo "Goto A: Process SUPERFLAT"

	echo "Finally, settle on a blasted Flat field, will you!?"


	### Apply Corrections to Science Data
	if [ ${FRINGE} == "NOFRINGE" ]; then
	  #adam: this only does the superflat (aka the "illum")
	  ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm RESCALE ILLUM ${SKYBACK} ${SCIENCEDIR}
	else
	  ./parallel_manager.sh ./process_science_illum_fringe_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm RESCALE ${SKYBACK} ${SCIENCEDIR}
	fi
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} SUP ${ending} 8 -32
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi

	./bad_shadow_remover.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/diffmask
fi

exit 0;
