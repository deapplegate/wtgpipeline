#! /bin/bash
set -xv

### superscript template to do the preprocessing
. progs.ini > /tmp/progs.out 2>&1
REDDIR=`pwd`

####################################################
### the following need to be specified for each run
####################################################

export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU

## adam notes: fgas_Zclusters_doubled_datasets.log
#1# all Z2089 biases are Z2701 biases!
#2# some Z2089 Flats are Z2701 FLATs (the ones in W-J-V from 2010-03-15 and 2010-12-05)
###    Z2089 Flats from (below) actually in Z2701/FLAT right now
###    *SKYFLAT        2010-03-15      W-J-V
###    *DOMEFLAT       2010-12-05      W-J-V
#3# all SUPERFLATs and SUPERFLAT2s from (Z2089 2010-12-05_W-J-V) should be used for (Z2701 2010-12-05 W-J-V)
###    /u/ki/awright/data/from_archive/f_gas_clusters/Z2089/SUPERFLAT_2010-12-05_W-J-V
###    Z2701   2010-12-05      W-J-V
#4# all SUPERFLATs and SUPERFLAT2s  from (Z2089 2010-03-15 W-J-V) should be used for (Z2701 2010-03-15 W-J-V)

## adam notes: adam_group2_process_now.txt
### 2007-02-13_W-J-V 	DOMEFLAT #Z2089   10_2	FLAT
### 2007-02-13_W-J-V 	SKYFLAT  #Z2089   10_2	FLAT
### 2007-02-13_W-S-I+	DOMEFLAT #Z2089   10_2	FLAT
### #2007-02-13_W-S-I+	SCIENCE  #Z2089   10_2	SCIENCE
### #2007-02-13_W-S-I+	SCIENCE  #Z2089   10_2	SUPERFLAT2_2007-02-13_W-S-I+
### #2007-02-13_W-S-I+	SCIENCE  #Z2089   10_2	SUPERFLAT_2007-02-13_W-S-I+
### 2009-03-28_W-S-I+	DOMEFLAT #Z2089   10_3	FLAT
### #2009-03-28_W-S-I+	SCIENCE  #Z2089   10_3	SCIENCE
### #2009-03-28_W-S-I+	SCIENCE  #Z2089   10_3	SUPERFLAT2_2009-03-28_W-S-I+
### #2009-03-28_W-S-I+	SCIENCE  #Z2089   10_3	SUPERFLAT_2009-03-28_W-S-I+
### 2009-03-28_W-S-I+	SKYFLAT  #Z2089   10_3	FLAT
### 2010-03-12_W-J-V 	DOMEFLAT #Z2701   10_3	FLAT
### #2010-03-12_W-J-V 	SCIENCE  #Z2701   10_3	SCIENCE
### #2010-03-12_W-J-V 	SCIENCE  #Z2089   10_3	SUPERFLAT2_2010-03-15_W-J-V
### #2010-03-12_W-J-V 	SCIENCE  #Z2089   10_3	SUPERFLAT_2010-03-15_W-J-V
### 2010-03-12_W-J-V 	SKYFLAT  #Z2701   10_3	FLAT
### #2010-03-12_W-S-I+	SCIENCE  #Z2701   10_3	SCIENCE
### #2010-03-12_W-S-I+	SCIENCE  #Z2701   10_3	SUPERFLAT2_2010-03-15_W-S-I+
### #2010-03-12_W-S-I+	SCIENCE  #Z2701   10_3	SUPERFLAT_2010-03-15_W-S-I+
### 2010-03-12_W-S-I+	SKYFLAT  #Z2701   10_3	FLAT
### #adam-SHNT#2010-11-07_W-J-V (process with 2010-12-05)	SCIENCE  #Z2089   10_3	SUPERFLAT2_2010-12-05_W-J-V ##hopefully I don't need this at all
### 2010-12-05_W-J-V	DOMEFLAT #Z2701   10_3	FLAT
### #2010-12-05_W-J-V	SCIENCE  #Z2089   10_3	SCIENCE
### #2010-12-05_W-J-V	SCIENCE  #Z2701   10_3	SCIENCE
### #2010-12-05_W-J-V	SCIENCE  #Z2089   10_3	SUPERFLAT_2010-12-05_W-J-V

#adam# maybe helpful to copy later
#for run in "2007-02-13" "2009-03-28" "2010-03-12" "2010-12-05"
#do
#	for filter in "W-J-V" "W-S-I+"
#	do
#		if [ -d ${SUBARUDIR}/${run}_${filter}/ ]; then
#			echo "${run}_${filter} exists"
#		else
#			echo "${run}_${filter} NOT REAL"
#		fi
#	done

## define run/filter/flat (ex. run=2010-11-04 ; filter="W-C-RC" ; FLAT=SKYFLAT)
##adam-pprun-PPRUN-list
#done on ki05# run="2007-02-13" ; filter="W-J-V"; FLAT=DOMEFLAT #Z2089   10_2 2007-02-13_W-J-V
#done on ki05# see /nfs/slac/g/ki/ki05/anja/SUBARU/2006-12-21_W-J-V/SCIENCE_DOMEFLAT_SET4
#done on ki05# run="2007-02-13" ; filter="W-J-V"; FLAT=SKYFLAT  #Z2089   10_2 2007-02-13_W-J-V
run="2007-02-13" ; filter="W-S-I+";FLAT=DOMEFLAT #Z2089   10_2 2007-02-13_W-S-I+
run="2009-03-28" ; filter="W-S-I+";FLAT=DOMEFLAT #Z2089   10_3 2009-03-28_W-S-I+
#run="2009-03-28" ; filter="W-S-I+";FLAT=SKYFLAT  #Z2089   10_3 2009-03-28_W-S-I+
run="2010-03-12" ; filter="W-J-V"; FLAT=DOMEFLAT #Z2701   10_3 2010-03-12_W-J-V
#run="2010-03-12" ; filter="W-J-V"; FLAT=SKYFLAT  #Z2701   10_3 2010-03-12_W-J-V
run="2010-03-12" ; filter="W-S-I+";FLAT=SKYFLAT  #Z2701   10_3 2010-03-12_W-S-I+
run="2010-12-05" ; filter="W-J-V"; FLAT=DOMEFLAT #Z2701   10_3 2010-12-05_W-J-V

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
########################################
### Reset Logger
#adam-BL# ./BonnLogger.py clear
##################################################################
# if needed: cp auxiliary data
##################################################################
#adam# use this to sort the downloaded data
###DARK Step (1)# make DARK dir if I haven't already
###./cp_aux_data.sh /u/ki/awright/data 10_3_DARK /u/ki/awright/data/from_archive/darks
###./cp_aux_data.sh ${SUBARUDIR} [optional run directory] ${SUBARUDIR}/${run}_RAWDATA

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
### Capture Variables
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

#BLOCK1-PER RUN# BIAS frames are filter indep. so do this once per run
#STARTOVER-BEGIN NEW RUN#
######## for run in "2007-02-13" "2009-03-28" "2010-03-12" "2010-12-05"
######## do
######## 	./setup_SUBARU.sh ${SUBARUDIR}/${run}_BIAS/BIAS/ORIGINALS
######## 	exit_stat=$?
######## 	if [ "${exit_stat}" -gt "0" ]; then
######## 		exit ${exit_stat};
######## 	fi
######## 	. ${INSTRUMENT:?}.ini
######## 	#### "process_split" splits the multi-extension files into one file per CCD, i.e. SUPA*_${chip}.fits
######## 	#adam# splits BIAS files SUPA#.fits into SUPA#_1.fits, SUPA#_2.fits, ...
######## 	#makes: SUPA0046882_1.fits
######## 	./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_BIAS BIAS #1
########
######## 	#STARTOVER-BAD BIAS FRAMES REMOVED
######## 	#### overscan-cut BIAS frames, OC+BIAS correct flats
######## 	#### processed files are called  SUPA*_${chip}OC.fits
######## 	#adam# does and makes (in ~/data/2010-02-12_BIAS/BIAS/):
######## 	##       1.) does overscan correct (O) & cuts the images (C) to make SUPA#_1OC.fits, SUPA#_2OC.fits, ...
######## 	##       2.) makes the master bias files BIAS_1.fits - BIAS_10.fits
######## 	##       (next line) 3.) and makes new dir /BINNED/ with BIAS_mos.fits and SUPA#_mosOC.fits
######## 	#makes: SUPA0046882_1OC.fits, SUPA0046882_1OC_CH1.fits, BIAS_1.fits
######## 	if [ "$config" == "10_3" ] ; then
######## 		./parallel_manager.sh ./process_bias_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS #2
######## 	elif [ "$config" == "10_2" ] ; then
######## 		./parallel_manager.sh ./process_bias_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS #2
######## 	else
######## 		echo "problem with config"
######## 		exit 1
######## 	fi
########
######## 	#### creates overview mosaics; use these to identify bad frames
######## 	#makes: BIAS/BINNED, BIAS/BINNED/BIAS_mos.fits, BIAS/BINNED/SUPA0046882_mosOC.fits
######## 	./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS BIAS "" 8 -32 #3
######## 	./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS SUP "" 8 -32 #3
######## 	./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS SUP "OC" 8 -32 #3
######## 	#adam-DO check# after it creates the mosaics, look at the filter_BIAS/BIAS/BINNED/*_mosOC.fits folder and see if any of the frames are bad. delete them (in the /BIAS/BINNED, /BIAS/ORIGINALS, and /BIAS/ folders), then delete, in the /BIAS/ folder, the BIAS_*.fits files, and re-run the process_bias_4channel_eclipse_para.sh file so that the final averaged flats dont have these bad frames included (see #STARTOVER-BAD BIAS FRAMES REMOVED)
######## 	#ds9 ${SUBARUDIR}/${run}_BIAS/BIAS/BINNED/*_mosOC.fits
######## 	#echo "check: do any of the bias frames look like light is leaking in?"
######## done
#exit 0; #3

####################################################################
# pre-processing of individual chips,
# PER FILTER (and per FLAT)
####################################################################

#BLOCK2 and 3 and 4 combined-PER RFF# per Run per Filter and per Flat
#STARTOVER-OTHER FLAT CHOSEN (make sure you change the FLAT up above!)
########for pprun in 2016-12-15_W-J-B  2015-12-15_W-S-Z+  2015-12-15_W-C-RC 2013-06-10_W-S-Z+ 2012-07-23_W-C-RC 2010-03-12_W-C-RC 2010-03-12_W-J-B 2010-03-12_W-S-Z+ 2009-09-19_W-J-V 2009-04-29_W-J-B 2009-04-29_W-S-Z+ 2009-03-28_W-J-V
########do
########	filter=${pprun#2*_}
########	run=${pprun%_*}
########	for FLAT in "DOMEFLAT" "SKYFLAT"
########	do
########		if [ -d ${SUBARUDIR}/${run}_${filter}/${FLAT} ]; then
########			echo "START: processing flat   ${SUBARUDIR}/${run}_${filter}/${FLAT}" >> adam-look-postH_preprocess.log2
########			./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/${FLAT}/ORIGINALS/
########			exit_stat=$?
########			if [ "${exit_stat}" -gt "0" ]; then
########				exit ${exit_stat};
########			fi
########			. ${INSTRUMENT:?}.ini
########
########			#### re-split the flat files, write THELI headers  -->  SUPA*_${chip}.fits
########			#makes: DOMEFLAT/SUPA0120759_1.fits
########			#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} #4
########			exit_stat=$?
########			if [ "${exit_stat}" -gt "0" ]; then
########				exit ${exit_stat};
########			fi
########
########			#adam-DO check skyflats# if you are doing sky flats, then stop here, run imstats ${SUBARUDIR}/${run}_${filter}/${FLAT}/SUPA*3.fits and see if the counts are comparable, not too high, not too low, etc. If you throw any out, delete every occurance of it (including in ORIGINALS, BINNED, from_archive, etc.).
########			#echo "check: doing " ${run}_${filter}/${FLAT} " if this is SKYFLAT, make sure the median counts are pretty close"
########
########			#echo ""  >> adam-look-postH_flatcheck.log
########			#echo "${run}_${filter} ${FLAT}"  >> adam-look-postH_flatcheck.log
########			#imstats ${SUBARUDIR}/${run}_${filter}/${FLAT}/SUPA*3.fits >> adam-look-postH_flatcheck.log
########			#imstats ${SUBARUDIR}/${run}_${filter}/${FLAT}/SUPA*8.fits >> adam-look-postH_flatcheck.log
########
########			### copy the master BIAS to run_filter/BIAS
########			if [ ! -d ${SUBARUDIR}/${run}_${filter}/BIAS ]; then
########			    mkdir ${SUBARUDIR}/${run}_${filter}/BIAS
########			    cp ${SUBARUDIR}/${run}_BIAS/BIAS/BIAS_*.fits ${SUBARUDIR}/${run}_${filter}/BIAS
########			fi
########
########			### copy the master DARK to run_filter/DARK
########			#if [ "$config" == "10_3" ] ; then
########			#	ln -s ${SUBARUDIR}/10_3_DARK/DARK/DARK_*.fits ${SUBARUDIR}/${run}_${filter}/DARK/
########			#elif [ "$config" == "10_2" ] ; then
########			#	ln -s ${SUBARUDIR}/2006-03-04_W-C-RC/DARK/DARK_*.fits ${SUBARUDIR}/${run}_${filter}/DARK/
########			#else
########			#	echo "problem with config";exit 1
########			#fi
########
########			#### overscan+bias correct the FLAT fields then average the flats to create the masterFLAT
########			#adam# corrects for overscan (O), cuts the images (C), subtracts the master bias, averages the flat fields. Make the files SUPA#_1OC.fits
########			if [ "$config" == "10_3" ] ; then
########				./parallel_manager.sh ./process_flat_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} #6
########			elif [ "$config" == "10_2" ] ; then
########				./parallel_manager.sh ./process_flat_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} #6
########			else
########				echo "problem with config";exit 1
########			fi
########			exit_stat=$?
########			if [ "${exit_stat}" -gt "0" ]; then
########				exit ${exit_stat};
########			fi
########
########			#### creates overview mosaics; use these to identify bad frames
########			#adam# makes little images from the *_#OC.fits files
########			#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} ${FLAT} "" 8 -32 #7
########			#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} SUP "OC" 8 -32 #7
########
########			#adam-DO check# go to ${SUBARUDIR}/${run}_${filter}/${FLAT}/BINNED and ds9 *_mosOC.fits and see if any images have large gradients (only remove if really bad):
########			#	* ds9 -zscale ~data/2011-01-06_W-S-Z+/DOMEFLAT/BINNED/SUPA*mosOC.fits -geometry 2000x2000 -zoom to fit
########			#	*Then, for example if 5 and 8 are bad do "rm -f *8OC.fits *5OC.fits *CHallOC.fits SKYFLAT_5.fits SKYFLAT_8.fits".
########			#	* Then re-run process_flat_4channels_eclipse_para.sh on those frames:
########			#		* see #STARTOVER-BAD FLAT FRAMES REMOVED
########			#		* for example "./process_flat_4channels_eclipse_para.sh ~/data/2010-02-12_W-C-IC BIAS SKYFLAT 8" and the same thing with 5
########			#	* Then re-run #7 and check again
########			#echo "ds9 -zscale -geometry 2000x2000 ${SUBARUDIR}/${run}_${filter}/${FLAT}/BINNED/*mosOC.fits -zoom to fit " >> adam-look-postH_flatcheck.log
########			#echo "adam-look| check: do any of the flats look like they have large gradients?"
########
########			echo "DONE : processing flat   ${SUBARUDIR}/${run}_${filter}/${FLAT}" >> adam-look-postH_preprocess.log2
########		else
########			echo "DOESNT EXIST: ${SUBARUDIR}/${run}_${filter}/${FLAT}" >> adam-look-postH_preprocess.log2
########		fi
########	done
########	#if [ -d ${SUBARUDIR}/${run}_${filter}/ ]; then
########	#        echo "START: splitting science ${SUBARUDIR}/${run}_${filter}/" >> adam-look-postH_preprocess.log
########	#	./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS/
########	#	exit_stat=$?
########	#	if [ "${exit_stat}" -gt "0" ]; then
########	#		exit ${exit_stat};
########	#	fi
########	#	. ${INSTRUMENT:?}.ini
########	#	#adam# re-split the science files, write SUPA*_${chip}.fits
########	#	./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} SCIENCE #5
########	#	exit_stat=$?
########	#	if [ "${exit_stat}" -gt "0" ]; then
########	#		exit ${exit_stat};
########	#	fi
########	#        echo "DONE : splitting science ${SUBARUDIR}/${run}_${filter}/" >> adam-look-postH_preprocess.log
########	#else
########	#        echo "ERROR DOESNT EXIST: ${SUBARUDIR}/${run}_${filter}/" >> adam-look-postH_preprocess.log
########	#fi
########done
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/2010-11-04_W-J-B SCIENCE
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/2010-11-04_W-S-Z+ SCIENCE
#echo "check out: adam-look-postH_flatcheck.log"
#echo "check out: adam-look-postH_preprocess.log"
#exit 0; #5

#adam-DO# make sure that I have DARKs now.
#DARK Step (3)# copy things from run_DARK/ to run_filter/DARK/
#adam# DARKs are done and copied over right now!
########for run in "2007-02-13" "2009-03-28" "2010-03-12" "2010-12-05"
########do
########	for filter in "W-J-V" "W-S-I+"
########	do
########		if [ -d ${SUBARUDIR}/${run}_${filter}/ ]; then
########			./setup_SUBARU.sh ${SUBARUDIR}/${run}_BIAS/BIAS/ORIGINALS
########			exit_stat=$?
########			if [ "${exit_stat}" -gt "0" ]; then
########				exit ${exit_stat};
########			fi
########			. ${INSTRUMENT:?}.ini
########			if [ ! -d ${SUBARUDIR}/${run}_${filter}/DARK ]; then
########			    mkdir ${SUBARUDIR}/${run}_${filter}/DARK
########			fi
########			if [ "$config" == "10_3" ] ; then
########				ln -s ${SUBARUDIR}/10_3_DARK/DARK/DARK_*.fits ${SUBARUDIR}/${run}_${filter}/DARK/
########			elif [ "$config" == "10_2" ] ; then
########				ln -s ${SUBARUDIR}/2006-03-04_W-C-RC/DARK/DARK_*.fits ${SUBARUDIR}/${run}_${filter}/DARK/
########			else
########				echo "problem with config";exit 1
########			fi
########			##ln -s ${SUBARUDIR}/${run}_DARK/DARK/DARK_*.fits ${SUBARUDIR}/${run}_${filter}/DARK/
########		fi
########	done
########done
#exit 0; #dark3

#BLOCK4-PER RFF# per Run per Filter and per Flat
#STARTOVER-BAD FLAT FRAMES REMOVED (really could do this in terminal using only the CCDs that were removed)
########for run in "2007-02-13" "2009-03-28" "2010-03-12" "2010-12-05"
########do
########	for filter in "W-J-V" "W-S-I+"
########	do
########		for FLAT in "DOMEFLAT" "SKYFLAT"
########		do
########			if [ -d ${SUBARUDIR}/${run}_${filter}/${FLAT} ]; then
########				./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/${FLAT}/ORIGINALS/
########				exit_stat=$?
########				if [ "${exit_stat}" -gt "0" ]; then
########					exit ${exit_stat};
########				fi
########				. ${INSTRUMENT:?}.ini
########
########			fi
########		done
########	done
########done
#exit 0; #6-7

####################################################################
### #step9 : apply flats, make $SCIENCEDIR stuff for evaluating superflat targets
####################################################################
#see postH_preprocess_template-step9.sh

#BLOCK5-PER RFF# per Run per Filter and per Flat
for pprun in 2015-12-15_W-J-B  2015-12-15_W-S-Z+  2015-12-15_W-C-RC  2013-06-10_W-S-Z+ 2012-07-23_W-C-RC 2010-11-04_W-J-B 2010-11-04_W-S-Z+ 2010-03-12_W-C-RC 2010-03-12_W-J-B 2010-03-12_W-S-Z+ 2009-09-19_W-J-V 2009-04-29_W-J-B 2009-04-29_W-S-Z+ 2009-03-28_W-J-V
do
	filter=${pprun#2*_}
	run=${pprun%_*}
	for FLAT in "DOMEFLAT" "SKYFLAT"
	do
		if [ -d ${SUBARUDIR}/${run}_${filter}/${FLAT} ]; then
			./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/${FLAT}/ORIGINALS/
			exit_stat=$?
			if [ "${exit_stat}" -gt "0" ]; then
				exit ${exit_stat};
			fi
			. ${INSTRUMENT:?}.ini

			#adam-FRINGE#
			FRINGE=NOFRINGE
			if [ "${filter}" == "W-S-Z+" ] ; then
				FRINGE="FRINGE"
			fi

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
			#adam-del# #10_2 & 10_3# this is where process_science_4channels_eclipse_para.sh calls things OCF and process_science_eclipse_para.sh calls things OFC, so you gotta change that in this code (tried changing process_science_eclipse_para.sh, but it won't work)
			#adam# normalize the science images
			./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUP OCF #9
			exit_stat=$?
			if [ "${exit_stat}" -gt "0" ]; then
				exit ${exit_stat};
			fi
			./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_norm SUP "OCFN" 8 -32 #9
			#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_norm SUP "OCFN" 8 -32 > OUT-create_binnedmosaics.log 2>&1
			exit_stat=$?
			if [ "${exit_stat}" -gt "0" ]; then
				exit ${exit_stat};
			fi
			#adam-del# #10_2#./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUP OFC #9
			#adam-del# #10_2#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_norm SUP "OFCN" 8 -32 #9
			#adam-DO# if there is another type of flat (which hasn't been processed yet), change which flat you're using and start over at #STARTOVER-OTHER FLAT CHOSEN
			if [ -d ${SUBARUDIR}/${run}_${filter}/SKYFLAT ]; then
				if [ -d ${SUBARUDIR}/${run}_${filter}/DOMEFLAT ]; then
					mv ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm_${FLAT}
					echo "adam-look| mv ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm_${FLAT}"
					if [ ! -d ${SUBARUDIR}/${run}_${filter}/SCIENCE_${FLAT} ]; then
					    mv ${SUBARUDIR}/${run}_${filter}/SCIENCE ${SUBARUDIR}/${run}_${filter}/SCIENCE_${FLAT}
					    mkdir -p ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
					    cp -r ${SUBARUDIR}/${run}_${filter}/SCIENCE_${FLAT}/SPLIT_IMAGES/SUPA*.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/
					    cp -r ${SUBARUDIR}/${run}_${filter}/SCIENCE_${FLAT}/ORIGINALS/SUPA*.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS/
					    echo "adam-look| #BEFORE moving on to the next step, I'll have to rm SCIENCE and replace it with either SCIENCE_DOMEFLAT or SCIENCE_SKYFLAT!"
					    echo "adam-look| rm -r ${SUBARUDIR}/${run}_${filter}/SCIENCE/"
					    echo "adam-look| mv ${SUBARUDIR}/${run}_${filter}/SCIENCE_DOMEFLAT/ ${SUBARUDIR}/${run}_${filter}/SCIENCE/"
					    echo "adam-look| OR"
					    echo "adam-look| mv ${SUBARUDIR}/${run}_${filter}/SCIENCE_SKYFLAT/ ${SUBARUDIR}/${run}_${filter}/SCIENCE/"
					fi
				fi
			fi
			#adam-DO check# choose which FLAT is better by comparing science images
			#ds9 -zscale -geometry 2000x2000 ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm/BINNED/*mosOCFN.fits -zoom to fit &
			echo "if there are two flats available and you still have to process the other one, then start over here"
			echo "check: the normalized science images from which type of flat looks better?"
			#adam-DO pick/restart# determine which flat is better and continue on from here using only one flat (change beginning of script to make sure you have the right one, then go to #STARTOVER-OTHER FLAT CHOSEN)
			#ds9 -zscale -geometry 2000x2000 ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm_${FLAT}/BINNED/*mosOCFN.fits -zoom to fit &
			#ds9 -zscale -geometry 2000x2000 ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm_DOMEFLAT/BINNED/*mosOCFN.fits -zoom to fit &
			#ds9 -zscale -geometry 2000x2000 ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm_SKYFLAT/BINNED/*mosOCFN.fits -zoom to fit &
			#### this is it if we assume we don't need a fringing correction...
		fi
	done
done

exit 0; #8-9

####################################################################
### #superflat : Process Superflat
####################################################################
#see postH_preprocess_template-superflats.sh

#### OCF SCIENCE frames + superflat (allows for easy tryout of diff flat fields)

#also this one later on: "2007-02-13_W-J-V"
for pprun in "2007-02-13_W-S-I+" "2009-03-28_W-S-I+" "2010-03-12_W-J-V" "2010-03-12_W-S-I+"
do
	filter=${pprun#2*_}
	run=${pprun%_*}
	if [ -d ${SUBARUDIR}/${run}_${filter}/DOMEFLAT ]; then
		FLAT=DOMEFLAT
	elif [ -d ${SUBARUDIR}/${run}_${filter}/SKYFLAT ]; then
		FLAT=SKYFLAT
	else
		continue
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
	./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
	. ${INSTRUMENT:?}.ini > /tmp/instrum.out 2>&1

	#questions#
	# 	* what is eclipse anyway? -> this is the software that messes with stuff (does the Overscan, Cut/Trim, Flat-fielding, Renormalizing, etc.)
	# 	* what is RESCALE? (In process_sub_images_para.sh it determines FLAT properties) -> it's just the renormalizing thing
	# 	* should I even run lines like "./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "_fringe${SKYBACK}" 8 -32" if there is no fringing correction? -> No, you don't have to run them
	# 	* illum isn't the IC, so what is it? -> Its the superflat
	# 	* is the superflat correction supposed to be run only on the OC.fits, not OCF.fits? -> run it on the OCF files
	#for other example see: ~/thiswork/preprocess_scripts/do_Subaru_preprocess_2007-07-18_W-J-V.sh #

	#delA# ./parallel_manager.sh ./process_sub_images_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} NOFRINGE
	./parallel_manager.sh ./process_sub_images_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} NOFRINGE
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	#delB# ./parallel_manager.sh ./process_sub_images_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} NOFRINGE

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
	./create_norm_illum_fringe.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} $SKYBACK
	./make_residuals.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR ${SKYBACK}
	./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "" 8 -32
	./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "_illum${SKYBACK}" 8 -32
	#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "_fringe${SKYBACK}" 8 -32

	echo "adam-look| Todo: Inspect ${SCIENCEDIR}/BINNED frames for bright stars, autotracker shadows, etc.
	Create maindir/superflat_exclusion, which is a list of the SUPAxxx_CHIP frames to exclude. 
	createExclusion.py may help in making the list."
	./make_binned_sets.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm/BINNED
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
done

exit
####################################################################
### #start_weights : BASE_WEIGHT begins
####################################################################
# see postH_preprocess_template-start_weights.sh

if [ -d ${SUBARUDIR}/${run}_${filter}/BASE_WEIGHT ]; then
	rm -r ${SUBARUDIR}/${run}_${filter}/BASE_WEIGHT
fi
#adam-SUPERFLAT BLOCK#
#### create normalized weight images
./create_norm.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
./create_norm.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}
#new:stacks all of the images from that run (with objects removed)
#BLOCK7-PER RF# per Run and per Filter (flat chosen already)
if [[ ${ending} == *"S"* ]];then
	echo "adam-look: Make superflat stuff directly. S in this ending=${ending}"
	ln -s ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR/SUPA*${ending}.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/

	for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
	do

	    rm ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}.fits
	    rm ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}_illum.fits
	    rm ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}_fringe.fits

	    ln -s ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR/${SCIENCEDIR}_${CHIP}.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}.fits
	    ln -s ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR/${SCIENCEDIR}_${CHIP}_illum${SKYBACK}.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}_illum.fits
	    if [ ${FRINGE} == "FRINGE" ]; then
		ln -s ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR/${SCIENCEDIR}_${CHIP}_fringe${SKYBACK}.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}_fringe.fits
	    fi
	    #ln -s ${SUBARUDIR}/${run}_${filter}/${FLAT}_${SET}/${FLAT}_${SET}_${CHIP}.fits ${SUBARUDIR}/${run}_${filter}/${FLAT}/${FLAT}_${CHIP}.fits

	done
	./create_norm_illum_fringe.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
	./create_globalweight_base.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}_norm SCIENCE_norm
else
	#adam# no superflat, so don't use this next line
	echo "adam-look: Copy FLAT_norm stuff over. no S in ending=${ending}."
	#adam# make the directory myself instead of doing the thing with the superflat
	if [ ! -d ${SUBARUDIR}/${run}_${filter}/BASE_WEIGHT ]; then
	    mkdir ${SUBARUDIR}/${run}_${filter}/BASE_WEIGHT
	fi #11a
	cp ${SUBARUDIR}/${run}_${filter}/${FLAT}_norm/${FLAT}_norm*.fits ${SUBARUDIR}/${run}_${filter}/BASE_WEIGHT
	rename "s/${FLAT}_norm/BASE_WEIGHT/g" ${SUBARUDIR}/${run}_${filter}/BASE_WEIGHT/${FLAT}_norm_*.fits #11a
fi

########################################################t#
#### #weights: GLOBAL WEIGHT CREATION
##########################################################
#see postH_preprocess_template-weights.sh

#BLOCK8#
#adam-DO# copy over the region files to the /reg/ directory in ${run}_${filter} (COPY, DON'T LINK!)
#STARTOVER-REGION CHANGE# IF YOU MESS WITH REGION FILES YOU MUST START OVER AT THIS POINT!
#for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
#do
#    if [ -e ${SUBARUDIR}/${run}_${filter}/reg/globalweight_${CHIP}.reg ]; then
#	cp ${SUBARUDIR}/${run}_${filter}/reg/globalweight_${CHIP}.reg ${SUBARUDIR}/${run}_${filter}/reg/SUBARU_${CHIP}.reg
#    fi
#done
#exit 0; #11
#adam# these two lines are needed if you have region files. these make the region files consistent with the current distribution of ds9
#convertRegion2Poly.py just backs up the directory1G
#./convertRegion2Poly.py ${SUBARUDIR} ${run}_${filter} #12
#./transform_ds9_reg_alt.sh ${SUBARUDIR} ${run}_${filter} #12
#exit 0; #12

#adam-notes# find removed USELESS BLOCK and stuff about how I used to do the limits and regions before WeightMasker in do_Subaru_preprocess_notes.sh search #OLD MASKS

#BLOCK9#
#adam# this will use the flats and darks to make run_filter/WEIGHTS/global*.fits
#adam# this uses the tools I've developed, it applies the SUPER WIDE uniform cuts, then uses WeightMasker and region files to mask out bad pixels in globalweights_1.fits
#############SUPER WIDE BASE_WEIGHT LIMITS USED HERE!########################
#adam# The DARK limits are the same unless config changes (these were fit by eye)
#10_3#super wide limits that I just use because this doesn't matter much at this point (this is found by taking the min of the lower limits and max of the upper limits for all "by eye" limits for each filter, then taking min-.04 and max+.08 so that I'm sure this will cut almost nothing out)
#STARTOVER-CHANGE DARK LIMS or CHANGE WeightMasker#
# 2007-02-13_W-J-V/DOMEFLAT
# 2007-02-13_W-S-I+/DOMEFLAT
# 2009-03-28_W-S-I+/DOMEFLAT
# 2010-03-12_W-J-V/DOMEFLAT
# 2010-12-05_W-J-V/DOMEFLAT
# 2010-03-12_W-S-I+/SKYFLAT
for run in "2007-02-13" "2009-03-28" "2010-03-12" "2010-12-05"
do
	for filter in "W-J-V" "W-S-I+"
	do
		if [ -d ${SUBARUDIR}/${run}_${filter}/DOMEFLAT ]; then
			FLAT=DOMEFLAT
		elif [ -d ${SUBARUDIR}/${run}_${filter}/SKYFLAT ]; then
			FLAT=SKYFLAT
		else
			continue
		fi
		./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/${FLAT}/ORIGINALS/
		. ${INSTRUMENT:?}.ini > /tmp/INSTRUMENT.log 2>&1

		#adam# to mess with limits, see Plot_Light_Cutter.py
		#adam# The DARK limits are the same unless config changes (these were fit by eye)
		#adam# The FLAT limits may not be the same

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

		#adam-notes# find "By Eye" limits for old filters/runs in do_Subaru_preprocess_notes.sh search #BY EYE LIMITS
		#./create_global_science_weighted.sh ${SUBARUDIR}/${run}_${filter} SCIENCE WEIGHTS #14
		#./parallel_manager.sh WeightMasker.py ${SUBARUDIR}/${run}_${filter}/WEIGHTS #15
		###groups together cluster pointings from one run
		./distribute_sets_subaru.sh ${SUBARUDIR} ${run}_${filter}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list
		exit_stat=$?
		if [ "${exit_stat}" -gt "0" ]; then
			exit ${exit_stat};
		fi
	done
done
exit 0; #13
#adam# make weighted science images
#./create_global_science_weighted.sh ${SUBARUDIR}/${run}_${filter} SCIENCE WEIGHTS #14
#exit 0; #14
#echo "Todo: Mask SCIENCE Flats for dust grains, missed hot pixels, etc.
#Use the images in the SCIENCE_weighted directory for masking.
#Region files should be saved in $maindir/reg.
#For precision masking, using mark_badpixel_regions.pl."
#echo "Goto B: Global Weight Creation"
#./parallel_manager.sh WeightMasker.py ${SUBARUDIR}/${run}_${filter}/WEIGHTS #15
#adam-DO check# MAKE SURE BAD THINGS (hot pixels, etc.) ARE COVERED BY REGION FILES:
#	ds9 ${run}_${filter}/WEIGHTS/globalweight_*.fits

#adam-USELESS BLOCK# (i think so at least, i don't need that #?# command do I?
##########################################################
###./splitoff_aux_data.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending} ${SUBARUDIR}/SUBARU.list
##########################################################
###groups together cluster pointings from one run
#./distribute_sets_subaru.sh ${SUBARUDIR} ${run}_${filter}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list
### note: this script now also copies globalweight*.fits and globalflag*fits
### to ${SUBARUDIR}/${cluster}/${filter}/WEIGHTS

####################################
##CHECKPOINT
####################################
#./BonnLogger.py checkpoint Preprocess
#15 made: all of the plots DefectMasker makes and backup files and changed globalweights_#.fits
exit 0; #15
