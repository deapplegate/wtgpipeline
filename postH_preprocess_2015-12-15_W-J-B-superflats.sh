#! /bin/bash
set -xv

### superscript template to do the preprocessing
. progs.ini > /tmp/progs.out 2>&1
REDDIR=`pwd`

####################################################
### the following need to be specified for each run
####################################################

export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
export BONN_TARGET=${run}
export BONN_FILTER=${filter}
export INSTRUMENT=SUBARU

SKYBACK=256          # in case of SKYFLAT: size of background mesh for superflat
                    # illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?)
                    # 16 (or 32) if lots of blobs

pprun="2015-12-15_W-J-B"
#in 2015-12-15_W-J-B  2015-12-15_W-S-Z+  2015-12-15_W-J-B  2013-06-10_W-S-Z+ 2012-07-23_W-C-RC 2010-11-04_W-J-B 2010-11-04_W-S-Z+ 2010-03-12_W-C-RC 2010-03-12_W-J-B 2010-03-12_W-S-Z+ 2009-09-19_W-J-V 2009-04-29_W-J-B 2009-04-29_W-S-Z+ 2009-03-28_W-J-V
filter=${pprun#2*_}
run=${pprun%_*}
SET=SET3            # sets time period of flat to use

#this sets: FLAT=        # SKYFLAT or DOMEFLAT
if [ -d ${SUBARUDIR}/${run}_${filter}/DOMEFLAT ]; then                                                                                                                                                                                
	FLAT=DOMEFLAT
elif [ -d ${SUBARUDIR}/${run}_${filter}/SKYFLAT ]; then
	FLAT=SKYFLAT
else
	continue
fi

SCIENCEDIR=SCIENCE_${FLAT}_${SET}
./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
. ${INSTRUMENT:?}.ini > /tmp/instrum.out 2>&1
# this sets: config="10_3"

#adam# fringing correction for Z band only
FRINGE=NOFRINGE
if [ "${filter}" == "W-S-Z+" ] ; then
	FRINGE="FRINGE"
fi

#adam# have to copy SCIENCE/SUPA*OCF.fits files over to ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR
if [ ! -d ${SUBARUDIR}/${run}_${filter}/${SCIENCEDIR} ]; then
    mkdir ${SUBARUDIR}/${run}_${filter}/${SCIENCEDIR}
    cp ${SUBARUDIR}/${run}_${filter}/SCIENCE/SUPA*OCF.fits ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR
fi

if [ ${FRINGE} == "FRINGE" ]; then
    ending="OCFSF"
elif [ ${FRINGE} == "NOFRINGE" ]; then
    ending="OCFS"
else
    echo "You need to specify FRINGE or NOFRINGE for the fringing correction!"
    exit 2;
fi

#questions#
# 	* what is eclipse anyway? -> this is the software that messes with stuff (does the Overscan, Cut/Trim, Flat-fielding, Renormalizing, etc.)
# 	* what is RESCALE? (In process_sub_images_para.sh it determines FLAT properties) -> it's just the renormalizing thing
# 	* should I even run lines like "./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "_fringe${SKYBACK}" 8 -32" if there is no fringing correction? -> No, you don't have to run them
# 	* illum isn't the IC, so what is it? -> Its the superflat
# 	* is the superflat correction supposed to be run only on the OC.fits, not OCF.fits? -> run it on the OCF files
#for other example see: ~/thiswork/preprocess_scripts/do_Subaru_preprocess_2007-07-18_W-J-V.sh #

#./parallel_manager.sh ./process_sub_images_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} $FRINGE
#exit_stat=$?
#if [ "${exit_stat}" -gt "0" ]; then
#	exit ${exit_stat};
#fi

### A: PROCESS SUPERFLAT ###
#adam# makes individual chip superflats: SCIENCE_SKYFLAT_SET2_${CHIP}.fits
#./process_superflat_rescale_obj_subs.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}
./parallel_manager.sh ./process_superflat_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} > OUT-process_superflat_para-${pprun}.log 2>&1
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi

### Create Illum/Fringe Corrections (both of them, then you can choose not to use the fringe stuff if you don't want to)
#adam# makes fringe/illum from individual chip superflats: SCIENCE_SKYFLAT_SET2_${CHIP}_illum${SKYBACK}.fits SCIENCE_SKYFLAT_SET2_${CHIP}_fringe${SKYBACK}.fits
./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR ${SKYBACK} > OUT-create_illumfringe_stars_para-${pprun}.log 2>&1
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi

./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "" 8 -32
./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "_illum${SKYBACK}" 8 -32
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi
##
if [ ${FRINGE} == "FRINGE" ]; then
  ./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "_fringe${SKYBACK}" 8 -32
fi

##
# Set normalization to the highest mode value AND Set threshold to 20% of the smallest mode value.
#create_norm.sh: from $1/$2/${2}_${i}${3}.fits it makes /$1/$2_norm//$2_norm_${i}${3}.fits NORM and THRESH by CHIP max(modes)
#makes: ${SUBARUDIR}/${run}_${filter}/${SCIENCEDIR}_norm/SCIENCE_SKYFLAT_SET2_norm_1.fits
./create_norm.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} > OUT-create_norm-${pprun}.log 2>&1
\ls -lrth ${SUBARUDIR}/${run}_${filter}/${SCIENCEDIR}_norm > FILES-create_norm-${pprun}.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi
# Set normalization to the highest mode value AND NO threshold
#adam# does this all get overwritten and never used? (${RESULTDIR}/$2_norm_${i}_fringe${3}.fits) (${RESULTDIR}/$2_norm_${i}_illum${3}.fits)
#./create_norm_illum_fringe.sh: NORM from $1/$2/${2}_${i}_illum${3}.fits, used to make /$1/$2_norm/$2_norm_${i}_illum${3}.fits and /$1/$2_norm/$2_norm_${i}_fringe${3}.fits
# from: /$1/$2/$2_${i}_illum${3}.fits and /$1/$2/$2_${i}_fringe${3}.fits
./create_norm_illum_fringe.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} $SKYBACK > OUT-create_norm_illum_fringe-${pprun}.log 2>&1
\ls -lrth ${SUBARUDIR}/${run}_${filter}/${SCIENCEDIR}_norm > FILES-create_norm_illum_fringe-${pprun}.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi

#adam# this makes final superflats: ${RESULTDIR}/$2_norm_${i}_illum$3.fits with NORM and THRESH  AND makes:${RESULTDIR}/$2_res${3}_${i}.fits
#make_residuals.sh: from $1/$2/${2}_${i}_illum$3.fits make $1/$2_norm/$2_norm_${i}_illum$3.fits and $1/$2_norm/$2_res${3}_${i}.fits
./make_residuals.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR ${SKYBACK} > OUT-make_residuals-${pprun}.log 2>&1
\ls -lrth ${SUBARUDIR}/${run}_${filter}/${SCIENCEDIR}_norm > FILES-make_residuals-${pprun}.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi

## try ./make_residuals.sh first this time! ./create_norm_illum_fringe.sh

./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "" 8 -32
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi
./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "_illum${SKYBACK}" 8 -32
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi

if [ ${FRINGE} == "FRINGE" ]; then
  ./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "_fringe${SKYBACK}" 8 -32
fi

#tmp#./make_binned_sets.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm/BINNED > OUT-make_binned_sets-${pprun}.log 2>&1
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi

echo "adam-look| Todo: Inspect ${SCIENCEDIR}/BINNED frames for bright stars, autotracker shadows, etc.
Create maindir/superflat_exclusion, which is a list of the SUPAxxx_CHIP frames to exclude. 
createExclusion.py may help in making the list."

#adam# to make exclusion list, do this: ./createExclusion.py ${SUBARUDIR}/${run}_${filter}/...
echo "Goto A: Process SUPERFLAT"
echo "Finally, settle on a blasted Flat field, will you!?"


### Apply Corrections to Science Data
if [ ${FRINGE} == "NOFRINGE" ]; then
  #adam: this only does the superflat (aka the "illum")
  ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm RESCALE ILLUM ${SKYBACK} ${SCIENCEDIR} > OUT-process_science_illum_eclipse_para-${pprun}.log 2>&1
else
  ./parallel_manager.sh ./process_science_illum_fringe_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm RESCALE ${SKYBACK} ${SCIENCEDIR} > OUT-process_science_illum_fringe_eclipse_para-${pprun}.log 2>&1
fi
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi

./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} SUP ${ending} 8 -32 > OUT-create_binnedmosaics-${pprun}.log 2>&1
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi

imstats -d 3 /nfs/slac/g/ki/ki18/anja/SUBARU/${pprun}/${SCIENCEDIR}/${SCIENCEDIR}_{1,2,3,4,5,6,7,8,9,10}.fits > stats_${SCIENCEDIR}.log
imstats -d 3 /nfs/slac/g/ki/ki18/anja/SUBARU/${pprun}/${SCIENCEDIR}/${SCIENCEDIR}_{1,2,3,4,5,6,7,8,9,10}_illum256.fits > stats_${SCIENCEDIR}_illum256.log
imstats -d 3 /nfs/slac/g/ki/ki18/anja/SUBARU/${pprun}/${SCIENCEDIR}/${SCIENCEDIR}_{1,2,3,4,5,6,7,8,9,10}_fringe256.fits > stats_${SCIENCEDIR}_fringe256.log

imstats -d 3 /nfs/slac/g/ki/ki18/anja/SUBARU/${pprun}/${SCIENCEDIR}_norm/${SCIENCEDIR}_norm_{1,2,3,4,5,6,7,8,9,10}.fits > stats_${SCIENCEDIR}_norm.log
imstats -d 3 /nfs/slac/g/ki/ki18/anja/SUBARU/${pprun}/${SCIENCEDIR}_norm/${SCIENCEDIR}_norm_{1,2,3,4,5,6,7,8,9,10}_illum256.fits > stats_${SCIENCEDIR}_norm_illum256.log
imstats -d 3 /nfs/slac/g/ki/ki18/anja/SUBARU/${pprun}/${SCIENCEDIR}_norm/${SCIENCEDIR}_norm_{1,2,3,4,5,6,7,8,9,10}_fringe256.fits > stats_${SCIENCEDIR}_norm_fringe256.log

exit 0;
