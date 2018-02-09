##!/bin/bash
#set -xv
#
##################################################################
### create and load the SUBARU.ini file
### !!! DO NOT COMMENT THIS BLOCK !!!
###
### well, this only works after some data has been adapted to
### THELI format. otherwise, make sure that SUBARU.ini has the
### right configuration (10_3)
##################################################################

export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU/ ; export INSTRUMENT=SUBARU
export bonn=/u/ki/awright/wtgpipeline/
export subdir=/nfs/slac/g/ki/ki18/anja/SUBARU/

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

#BLOCK1-PER RUN# BIAS frames are filter indep. so do this once per run
#STARTOVER-BEGIN NEW RUN#
for run in "2013-06-10"
do
	./setup_SUBARU.sh ${SUBARUDIR}/${run}_BIAS/BIAS/ORIGINALS
	exit_stat=$?
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	. ${INSTRUMENT:?}.ini
	#### "process_split" splits the multi-extension files into one file per CCD, i.e. SUPA*_${chip}.fits
	#adam# splits BIAS files SUPA#.fits into SUPA#_1.fits, SUPA#_2.fits, ...
	#makes: SUPA0046882_1.fits
	./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_BIAS BIAS #1

	#STARTOVER-BAD BIAS FRAMES REMOVED
	#### overscan-cut BIAS frames, OC+BIAS correct flats
	#### processed files are called  SUPA*_${chip}OC.fits
	#adam# does and makes (in ~/data/2010-02-12_BIAS/BIAS/):
	##       1.) does overscan correct (O) & cuts the images (C) to make SUPA#_1OC.fits, SUPA#_2OC.fits, ...
	##       2.) makes the master bias files BIAS_1.fits - BIAS_10.fits
	##       (next line) 3.) and makes new dir /BINNED/ with BIAS_mos.fits and SUPA#_mosOC.fits
	#makes: SUPA0046882_1OC.fits, SUPA0046882_1OC_CH1.fits, BIAS_1.fits
	if [ "$config" == "10_3" ] ; then
		./parallel_manager.sh ./process_bias_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS #2
	elif [ "$config" == "10_2" ] ; then
		./parallel_manager.sh ./process_bias_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS #2
	else
		echo "problem with config"
		exit 1
	fi

	#### creates overview mosaics; use these to identify bad frames
	#makes: BIAS/BINNED, BIAS/BINNED/BIAS_mos.fits, BIAS/BINNED/SUPA0046882_mosOC.fits
	./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS BIAS "" 8 -32 #3
	#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS SUP "" 8 -32 #3
	#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS SUP "OC" 8 -32 #3
	#adam-DO check# after it creates the mosaics, look at the filter_BIAS/BIAS/BINNED/*_mosOC.fits folder and see if any of the frames are bad. delete them (in the /BIAS/BINNED, /BIAS/ORIGINALS, and /BIAS/ folders), then delete, in the /BIAS/ folder, the BIAS_*.fits files, and re-run the process_bias_4channel_eclipse_para.sh file so that the final averaged flats dont have these bad frames included (see #STARTOVER-BAD BIAS FRAMES REMOVED)
	#echo "#adam-look# ds9 ${SUBARUDIR}/${run}_BIAS/BIAS/BINNED/*_mosOC.fits &"
	#echo "check: do any of the bias frames look like light is leaking in?"
done


#BLOCK2 and 3 and 4 combined-PER RFF# per Run per Filter and per Flat
#STARTOVER-OTHER FLAT CHOSEN (make sure you change the FLAT up above!)
for pprun in 2013-06-10_W-S-Z+
do
	filter=${pprun#2*_}
	run=${pprun%_*}
	for FLAT in "DOMEFLAT" "SKYFLAT"
	do
		if [ -d ${SUBARUDIR}/${run}_${filter}/${FLAT} ]; then
			echo "START: processing flat   ${SUBARUDIR}/${run}_${filter}/${FLAT}" >> adam-look-postH_preprocess.log2
			./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/${FLAT}/ORIGINALS/
			exit_stat=$?
			if [ "${exit_stat}" -gt "0" ]; then
				exit ${exit_stat};
			fi
			. ${INSTRUMENT:?}.ini

			#### re-split the flat files, write THELI headers  -->  SUPA*_${chip}.fits
			#makes: DOMEFLAT/SUPA0120759_1.fits
			./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} #4
			exit_stat=$?
			if [ "${exit_stat}" -gt "0" ]; then
				exit ${exit_stat};
			fi

			#adam-DO check skyflats# if you are doing sky flats, then stop here, run imstats ${SUBARUDIR}/${run}_${filter}/${FLAT}/SUPA*3.fits and see if the counts are comparable, not too high, not too low, etc. If you throw any out, delete every occurance of it (including in ORIGINALS, BINNED, from_archive, etc.).
			#echo "check: doing " ${run}_${filter}/${FLAT} " if this is SKYFLAT, make sure the median counts are pretty close"
			echo ""  >> adam-look-postH_flatcheck.log2
			echo "${run}_${filter} ${FLAT}"  >> adam-look-postH_flatcheck.log2
			imstats ${SUBARUDIR}/${run}_${filter}/${FLAT}/SUPA*3.fits >> adam-look-postH_flatcheck.log2
			imstats ${SUBARUDIR}/${run}_${filter}/${FLAT}/SUPA*8.fits >> adam-look-postH_flatcheck.log2

			### copy the master BIAS to run_filter/BIAS
			if [ ! -d ${SUBARUDIR}/${run}_${filter}/BIAS ]; then
			    mkdir ${SUBARUDIR}/${run}_${filter}/BIAS
			    cp ${SUBARUDIR}/${run}_BIAS/BIAS/BIAS_*.fits ${SUBARUDIR}/${run}_${filter}/BIAS
			fi

			### copy the master DARK to run_filter/DARK
			#if [ "$config" == "10_3" ] ; then
			#	ln -s ${SUBARUDIR}/10_3_DARK/DARK/DARK_*.fits ${SUBARUDIR}/${run}_${filter}/DARK/
			#elif [ "$config" == "10_2" ] ; then
			#	ln -s ${SUBARUDIR}/2006-03-04_W-C-RC/DARK/DARK_*.fits ${SUBARUDIR}/${run}_${filter}/DARK/
			#else
			#	echo "problem with config";exit 1
			#fi

			#### overscan+bias correct the FLAT fields then average the flats to create the masterFLAT
			#adam# corrects for overscan (O), cuts the images (C), subtracts the master bias, averages the flat fields. Make the files SUPA#_1OC.fits
			if [ "$config" == "10_3" ] ; then
				./parallel_manager.sh ./process_flat_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} #6
			elif [ "$config" == "10_2" ] ; then
				./parallel_manager.sh ./process_flat_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} #6
			else
				echo "problem with config";exit 1
			fi
			exit_stat=$?
			if [ "${exit_stat}" -gt "0" ]; then
				exit ${exit_stat};
			fi

			#### creates overview mosaics; use these to identify bad frames
			#adam# makes little images from the *_#OC.fits files
			./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} ${FLAT} "" 8 -32 #7
			./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} SUP "OC" 8 -32 #7
			exit_stat=$?
			if [ "${exit_stat}" -gt "0" ]; then
				exit ${exit_stat};
			fi

			#adam-DO check# go to ${SUBARUDIR}/${run}_${filter}/${FLAT}/BINNED and ds9 *_mosOC.fits and see if any images have large gradients (only remove if really bad):
			#	* ds9 -zscale ~data/2011-01-06_W-S-Z+/DOMEFLAT/BINNED/SUPA*mosOC.fits -geometry 2000x2000 -zoom to fit
			#	*Then, for example if 5 and 8 are bad do "rm -f *8OC.fits *5OC.fits *CHallOC.fits SKYFLAT_5.fits SKYFLAT_8.fits".
			#	* Then re-run process_flat_4channels_eclipse_para.sh on those frames:
			#		* see #STARTOVER-BAD FLAT FRAMES REMOVED
			#		* for example "./process_flat_4channels_eclipse_para.sh ~/data/2010-02-12_W-C-IC BIAS SKYFLAT 8" and the same thing with 5
			#	* Then re-run #7 and check again
			echo "ds9 -zscale -geometry 2000x2000 ${SUBARUDIR}/${run}_${filter}/${FLAT}/BINNED/*mosOC.fits -zoom to fit " >> adam-look-postH_flatcheck.log2
			echo "adam-look| check: do any of the flats look like they have large gradients?"

			echo "DONE : processing flat   ${SUBARUDIR}/${run}_${filter}/${FLAT}" >> adam-look-postH_preprocess.log2
		else
			echo "DOESNT EXIST: ${SUBARUDIR}/${run}_${filter}/${FLAT}" >> adam-look-postH_preprocess.log2
		fi
	done
	if [ -d ${SUBARUDIR}/${run}_${filter}/ ]; then
	        echo "START: splitting science ${SUBARUDIR}/${run}_${filter}/" >> adam-look-postH_preprocess.log2
		./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS/
		exit_stat=$?
		if [ "${exit_stat}" -gt "0" ]; then
			exit ${exit_stat};
		fi
		. ${INSTRUMENT:?}.ini
		#adam# re-split the science files, write SUPA*_${chip}.fits
		./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} SCIENCE #5
		exit_stat=$?
		if [ "${exit_stat}" -gt "0" ]; then
			exit ${exit_stat};
		fi
	        echo "DONE : splitting science ${SUBARUDIR}/${run}_${filter}/" >> adam-look-postH_preprocess.log2
	else
	        echo "ERROR DOESNT EXIST: ${SUBARUDIR}/${run}_${filter}/" >> adam-look-postH_preprocess.log2
	fi
done
echo "check out: adam-look-postH_flatcheck.log2"
echo "check out: adam-look-postH_preprocess.log2"
exit 0; #5
