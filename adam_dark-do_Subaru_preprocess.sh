#! /bin/bash
set -xv

### superscript template to do the preprocessing
. progs.ini > /tmp/progs.out 2>&1
REDDIR=`pwd`

####################################################
### the following need to be specified for each run
####################################################

export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
export BONN_TARGET=${run}
export BONN_FILTER=DARK

#FLAT=        # SKYFLAT or DOMEFLAT
SET=SET1            # sets time period of flat to use
SKYBACK=256          # in case of SKYFLAT: size of background mesh for superflat
                    # illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?)
                    # 16 (or 32) if lots of blobs

#adam# fringing correction for Z band only
FRINGE=NOFRINGE       # FRINGE if fringing correction necessary; NOFRINGE otherwise
SCIENCEDIR=SCIENCE_${FLAT}_${SET}

####################################################
###
####################################################
if [ ${FRINGE} == "FRINGE" ]; then
    ending="OCFSF"
elif [ ${FRINGE} == "NOFRINGE" ]; then
    ending="OCFS"
else
    echo "You need to specify FRINGE or NOFRINGE for the fringing correction!"
    exit 2;
fi

##################################################################
### create and load the SUBARU.ini file
### !!! DO NOT COMMENT THIS BLOCK !!!
###
### well, this only works after some data has been adapted to
### THELI format. otherwise, make sure that SUBARU.ini has the
### right configuration (10_3)
##################################################################

export INSTRUMENT=SUBARU
##################################################################
config="10_3"

###################################################################
##If needed: process the DARK frames (per chip)
##   before: DARK Step (1) - cp_aux_data - once ever
##   here: DARK Step (2) - process DARK frames - once per run
##   later (always needed): DARK Step (3) - copy DARK frames to run_filter/DARK - once per filter
###################################################################
#DARK Step (2)# step #1-3 equivalent, but for darks
#for run in 2012 2013
for run in 2015-12-15
do
	./setup_SUBARU.sh ${SUBARUDIR}/${run}_DARK/DARK/ORIGINALS
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	. ${INSTRUMENT:?}.ini
	./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_DARK DARK
	./parallel_manager.sh ./process_bias_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_DARK DARK
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	./create_binnedmosaics.sh ${SUBARUDIR}/${run}_DARK DARK DARK "" 8 -32
	./create_binnedmosaics.sh ${SUBARUDIR}/${run}_DARK DARK SUP "" 8 -32
	./create_binnedmosaics.sh ${SUBARUDIR}/${run}_DARK DARK SUP "OC" 8 -32
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	#adam-DO check# after it creates the mosaics, look at the filter_DARK/DARK/BINNED/*_mosOC.fits folder and see if any of the frames are bad. delete them (in the /DARK/BINNED, /DARK/ORIGINALS, and /DARK/ folders), then delete, in the /DARK/ folder, the DARK_*.fits files, and re-run the process_bias_4channel_eclipse_para.sh file so that the final averaged flats dont have these bad frames included (see #STARTOVER-BAD DARK FRAMES REMOVED)
	echo "#adam-look# ds9 ${SUBARUDIR}/${run}_DARK/DARK/BINNED/*_mosOC.fits &"
	#echo "check: do any of the bias frames look like light is leaking in?"
	./parallel_manager.sh ./create_norm_para.sh ${SUBARUDIR}/${run}_DARK DARK
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
done
exit 0; #DARK Step (2)
#adam-SHNT# If I do need to check it out, then look here: do_Subaru_DARK_Template.sh
#adam-SHNT# check things out here:/u/ki/awright/data/10_3_DARK/DARK/darks_2yr2mo_change
