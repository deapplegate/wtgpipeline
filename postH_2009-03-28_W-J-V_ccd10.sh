#! /bin/bash
set -xv

### superscript template to do the preprocessing
. progs.ini > /tmp/progs.out 2>&1
REDDIR=`pwd`

####################################################
### the following need to be specified for each run
####################################################

export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
#run="2010-03-12" ; filter="W-S-I+";FLAT=SKYFLAT  #Z2701   10_3 2010-03-12_W-S-I+
export BONN_TARGET=${run}
export BONN_FILTER=${filter}

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
#./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
#. ${INSTRUMENT:?}.ini
##################################################################
config="10_3"

###################################################################
##If needed: process the DARK frames (per chip)
##   before: DARK Step (1) - cp_aux_data - once ever
##   here: DARK Step (2) - process DARK frames - once per run
##   later (always needed): DARK Step (3) - copy DARK frames to run_filter/DARK - once per filter
###################################################################
#DARK Step (2)# step #1-3 equivalent, but for darks
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_DARK DARK
#./parallel_manager.sh ./process_bias_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_DARK DARK
#10_2#./parallel_manager.sh ./process_bias_eclipse_para.sh ${SUBARUDIR}/${run}_DARK DARK #2
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_DARK DARK DARK "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_DARK DARK SUP "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_DARK DARK SUP "OC" 8 -32
#exit 0; #DARK Step (2)
###################################################################
## process the BIAS frames (per chip)
## only needs to be done once per run!
###################################################################
#adam-BL# ./BonnLogger.py clear

#BLOCK5-PER RFF# per Run per Filter and per Flat
pprun=2009-03-28_W-J-V
#in 2015-12-15_W-J-B  2015-12-15_W-S-Z+  2015-12-15_W-C-RC  2013-06-10_W-S-Z+ 2012-07-23_W-C-RC 2010-11-04_W-J-B 2010-11-04_W-S-Z+ 2010-03-12_W-C-RC 2010-03-12_W-J-B 2010-03-12_W-S-Z+ 2009-09-19_W-J-V 2009-04-29_W-J-B 2009-04-29_W-S-Z+ 2009-03-28_W-J-V
filter=${pprun#2*_}
run=${pprun%_*}
for FLAT in "SKYFLAT"
do
	if [ -d ${SUBARUDIR}/${run}_${filter}/${FLAT} ]; then
		#./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/${FLAT}/ORIGINALS/
		#exit_stat=$?
		#if [ "${exit_stat}" -gt "0" ]; then
		#	exit ${exit_stat};
		#fi
		. ${INSTRUMENT:?}.ini

		#adam-FRINGE#
		FRINGE=NOFRINGE
		if [ "${filter}" == "W-S-Z+" ] ; then
			FRINGE="FRINGE"
		fi

		#### processes SCIENCE frames:
		#### overscan, bias, flat -->  SUPA*_${chip}OCF.fits
		#adam# process the SCIENCE images result=(science-bias)/(flat-bias)
		#makes (in undo form): rm SUPA*OCF.fits ; rm SUPA*OCF_sub.fits ; rm SCIENCE_*.fits ; mv SUB_IMAGES/SUPA*.fits . ; rm -r SUB_IMAGES/
		## also sets up superflat stuff, to exclude things from superflat, put them here:
		#    # modify the input list of images
		# in case we have to reject files for the superflat: ${SUBARUDIR}/${run}_${filter}/superflat_exclusion
		#THIS TAKES ~15 min#
		if [ "$config" == "10_3" ] ; then
			./process_science_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE} '10'
		elif [ "$config" == "10_2" ] ; then
			./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE} #8
		else
			echo "problem with config";exit 1
		fi
		exit_stat=$?
		if [ "${exit_stat}" -gt "0" ]; then
			exit ${exit_stat};
		fi
		#adam-del# #10_2 & 10_3# this is where process_science_4channels_eclipse_para.sh calls things OCF and process_science_eclipse_para.sh calls things OFC, so you gotta change that in this code (tried changing process_science_eclipse_para.sh, but it won't work)
	fi
done
exit 0; #8-9
