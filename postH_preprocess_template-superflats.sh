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

pprun="CHANGEIT"
#in 2015-12-15_W-J-B  2015-12-15_W-S-Z+  2015-12-15_W-C-RC  2013-06-10_W-S-Z+ 2012-07-23_W-C-RC 2010-11-04_W-J-B 2010-11-04_W-S-Z+ 2010-03-12_W-C-RC 2010-03-12_W-J-B 2010-03-12_W-S-Z+ 2009-09-19_W-J-V 2009-04-29_W-J-B 2009-04-29_W-S-Z+ 2009-03-28_W-J-V
filter=${pprun#2*_}
run=${pprun%_*}
SET=SET1            # sets time period of flat to use

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

SCIENCEDIR=SCIENCE_${FLAT}_${SET}
echo "SCIENCEDIR=" ${SCIENCEDIR}
ls ${SUBARUDIR}/${run}_${filter}/${SCIENCEDIR}/SUPA*OCF.fits | wc -l
ls ${SUBARUDIR}/${run}_${filter}/SCIENCE/SUPA*OCF.fits | wc -l

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

./parallel_manager.sh ./process_sub_images_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} $FRINGE
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi

### A: PROCESS SUPERFLAT ###
./parallel_manager.sh ./process_superflat_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
	exit ${exit_stat};
fi

### Create Illum/Fringe Corrections (both of them, then you can choose not to use the fringe stuff if you don't want to)
./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR ${SKYBACK}
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

exit 0;
