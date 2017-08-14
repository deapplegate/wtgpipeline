#! /bin/bash -xv

### superscript template to do the preprocessing
. progs.ini
REDDIR=`pwd`

####################################################
### the following need to be specified for each run
####################################################

export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
#DONE COMBINATIONS
#run=10_3 #use this for processing DARK
#(dont use) run=2010-02-12 ; filter="W-C-IC" ; FLAT=SKYFLAT
#(dont use) run=2010-02-12 ; filter="W-C-RC" ; FLAT=SKYFLAT
#(dont use) run=2010-04-15 ; filter="W-S-I+" ; FLAT=SKYFLAT #DIV3
#run=2010-02-12 ; filter="W-C-IC" ; FLAT=DOMEFLAT
#run=2010-02-12 ; filter="W-C-RC" ; FLAT=DOMEFLAT
#run=2010-02-12 ; filter="W-J-B" ; FLAT=DOMEFLAT
#run=2010-02-12 ; filter="W-J-V" ; FLAT=DOMEFLAT
#run=2010-04-15 ; filter="W-S-G+" ; FLAT=SKYFLAT #DIV1
#run=2010-04-15 ; filter="W-S-I+" ; FLAT=DOMEFLAT #DIV2
#run=2011-01-06 ; filter="W-C-IC" ; FLAT=DOMEFLAT #DIV4
#run=2011-01-06 ; filter="W-S-Z+" ; FLAT=DOMEFLAT #DIV5

#WORKING ON IT COMBINATIONS
#10_2
run=2006-03-04 ; filter="W-C-RC" ; FLAT=DOMEFLAT

export BONN_TARGET=${run}
export BONN_FILTER=${filter}

#FLAT=        # SKYFLAT or DOMEFLAT
SET=SET1            # sets time period of flat to use
SKYBACK=256          # in case of SKYFLAT: size of background mesh for superflat
                    # illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?)
                    # 16 (or 32) if lots of blobs

FRINGE=NOFRINGE       # FRINGE if fringing correction necessary; NOFRINGE otherwise

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
./BonnLogger.py clear
##################################################################
# if needed: cp auxiliary data
##################################################################
#adam# use this to sort the downloaded data
########### DARK Step (1) #########################################
###./cp_aux_data.sh ${SUBARUDIR} [optional run directory] ${SUBARUDIR}/${run}_RAWDATA

##################################################################
### create and load the SUBARU.ini file
### !!! DO NOT COMMENT THIS BLOCK !!!
###
### well, this only works after some data has been adapted to
### THELI format. otherwise, make sure that SUBARU.ini has the
### right configuration (10_3)
##################################################################

#adam# this isn't a directory
./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS #RAWDATA folder
#./setup_SUBARU.sh /nfs/slac/g/ki/ki18/anja/SUBARU/2006-03-04_W-C-RC/SCIENCE/ORIGINALS/
export INSTRUMENT=SUBARU

. ${INSTRUMENT:?}.ini
#exit 0;

##################################################################
### Capture Variables
./BonnLogger.py config \
    run=${run} \
    filter=${filter} \
    FLAT=${FLAT} \
    SET=${SET} \
    SKYBACK=${SKYBACK} \
    FRINGE=${FRINGE} \
    STANDARDSTARS=${STANDARDSTARS} \
    config=${config}

###################################################################
## process the BIAS frames (per chip)
## only needs to be done once per run!
###################################################################
./BonnLogger.py clear

#BLOCK1-PER RUN# BIAS frames are filter indep. so do this once per run
#STARTOVER-BEGIN NEW RUN#
#### "process_split" splits the multi-extension files into one file per CCD, i.e. SUPA*_${chip}.fits
#adam# splits BIAS files SUPA#.fits into SUPA#_1.fits, SUPA#_2.fits, ...
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_BIAS BIAS #1
#exit 0; #1
#STARTOVER-BAD BIAS FRAMES REMOVED
#### overscan-correct BIAS frames, OC+BIAS correct flats
#### processed files are called  SUPA*_${chip}OC.fits
#adam# does and makes (in ~/data/2010-02-12_BIAS/BIAS/):
##       1.) does overscan correct (O) & cuts the images (C) to make SUPA#_1OC.fits, SUPA#_2OC.fits, ...
##       2.) makes the master bias files BIAS_1.fits - BIAS_10.fits
##       3.) and makes new dir /BINNED/ with BIAS_mos.fits and SUPA#_mosOC.fits
#10_3#./parallel_manager.sh ./process_bias_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS #2
#./parallel_manager.sh ./process_bias_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS #2
#exit 0; #2
#### creates overview mosaics; use these to identify bad frames
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS BIAS "" 8 -32 #3
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS SUP "" 8 -32 #3
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS SUP "OC" 8 -32 #3
#adam-DO check# after it creates the mosaics, look at the filter_BIAS/BIAS/BINNED/*_mosOC.fits folder and see if any of the frames are bad. delete them (in the /BIAS/BINNED, /BIAS/ORIGINALS, and /BIAS/ folders), then delete, in the /BIAS/ folder, the BIAS_*.fits files, and re-run the process_bias_4channel_eclipse_para.sh file so that the final averaged flats dont have these bad frames included (see #STARTOVER-BAD BIAS FRAMES REMOVED)
#ds9 ${SUBARUDIR}/${run}_BIAS/BIAS/BINNED/*_mosOC.fits
#echo "check: do any of the bias frames look like light is leaking in?"
#exit 0; #3

########### DARK Step (2) #########################################

####################################################################
# pre-processing of individual chips,
# PER FILTER (and per FLAT)
####################################################################

#BLOCK2-PER RFF# per Run per Filter and per Flat
#STARTOVER-OTHER FLAT CHOSEN (make sure you change the FLAT up above!)
#### re-split the flat files, write THELI headers  -->  SUPA*_${chip}.fits
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} #4
#adam-DO check skyflats# if you are doing sky flats, then stop here, run imstats ${SUBARUDIR}/${run}_${filter}/${FLAT}/SUPA*3.fits and see if the counts are comparable, not too high, not too low, etc. If you throw any out, delete every occurance of it (including in ORIGINALS, BINNED, from_archive, etc.).
#imstats ${SUBARUDIR}/${run}_${filter}/${FLAT}/SUPA*3.fits
#echo "check: doing " ${FLAT} " if this is SKYFLAT, make sure the median counts are pretty close"
#exit 0; #4

#BLOCK3-PER RF# per Run and per Filter (i.e. dont run if processing SKYFLAT after already having processed DOMEFLAT)
#adam# re-split the science files, write SUPA*_${chip}.fits
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} SCIENCE #5
#### copy the master BIAS to run_filter/BIAS
#if [ ! -d ${SUBARUDIR}/${run}_${filter}/BIAS ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/BIAS
#    cp ${SUBARUDIR}/${run}_BIAS/BIAS/BIAS_*.fits ${SUBARUDIR}/${run}_${filter}/BIAS
#fi
#exit 0; #5
########## DARK Step (3) #########################################

#BLOCK4-PER RFF# per Run per Filter and per Flat
#STARTOVER-BAD FLAT FRAMES REMOVED (really could do this in terminal using only the CCDs that were removed)
#### overscan+bias correct the FLAT fields then average the flats to create the masterFLAT
#adam# corrects for overscan (O), cuts the images (C), subtracts the master bias, averages the flat fields. Make the files SUPA#_1OC.fits
#10_3#./parallel_manager.sh ./process_flat_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} #6
#./parallel_manager.sh ./process_flat_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} #6
#exit 0; #6
#### creates overview mosaics; use these to identify bad frames
#adam# makes little images from the *_#OC.fits files
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} ${FLAT} "" 8 -32 #7
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} SUP "OC" 8 -32 #7
#adam-DO check# go to ${SUBARUDIR}/${run}_${filter}/${FLAT}/BINNED and ds9 *_mosOC.fits and see if any images have large gradients (only remove if really bad):
#	* ds9 -zscale ~data/2011-01-06_W-S-Z+/DOMEFLAT/BINNED/SUPA*mosOC.fits -geometry 2000x2000 -zoom to fit
#	*Then, for example if 5 and 8 are bad do "rm -f *8OC.fits *5OC.fits *CHallOC.fits SKYFLAT_5.fits SKYFLAT_8.fits".
#	* Then re-run process_flat_4channels_eclipse_para.sh on those frames:
#		* see #STARTOVER-BAD FLAT FRAMES REMOVED
#		* for example "./process_flat_4channels_eclipse_para.sh ~/data/2010-02-12_W-C-IC BIAS SKYFLAT 8" and the same thing with 5
#	* Then re-run #7 and check again
#ds9 -zscale -geometry 2000x2000 -zoom to fit ${SUBARUDIR}/${run}_${filter}/${FLAT}/BINNED/*mosOC.fits &
#echo "check: do any of the flats look like they have large gradients?"
#exit 0; #7

#BLOCK5-PER RFF# per Run per Filter and per Flat
#### processes SCIENCE frames:
#### overscan, bias, flat -->  SUPA*_${chip}OCF.fits
#adam# process the SCIENCE images result=(science-bias)/(flat-bias)
#THIS TAKES ~15 min#
#10_3#./parallel_manager.sh ./process_science_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE} #8
#./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE} #8
#10_3# this is where process_science_4channels_eclipse_para.sh calls things OCF and process_science_eclipse_para.sh calls things OFC, so you gotta change that in this code (tried changing process_science_eclipse_para.sh, but it won't work)
#exit 0; #8
#adam# normalize the science images
#10_3#./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUP OCF #9
#10_3#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_norm SUP "OCFN" 8 -32 #9
#10_2#./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUP OFC #9
#10_2#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_norm SUP "OFCN" 8 -32 #9
#adam-DO# if there is another type of flat (which hasn't been processed yet), change which flat you're using and start over at #STARTOVER-OTHER FLAT CHOSEN
#	*mv ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm_${FLAT}
#adam-DO check# choose which FLAT is better by comparing science images
#10_3#ds9 -zscale -geometry 2000x2000 -zoom to fit ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm/BINNED/*mosOCFN.fits &
#10_2#ds9 -zscale -geometry 2000x2000 -zoom to fit ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm/BINNED/*mosOFCN.fits &
#	echo "if there are two flats available and you still have to process the other one, then start over here"
#	echo "check: the normalized science images from which type of flat looks better?"
#adam-DO pick/restart# determine which flat is better and continue on from here using only one flat (change beginning of script to make sure you have the right one, then go to #STARTOVER-OTHER FLAT CHOSEN)
#exit 0; #9
#### this is it if we assume we don't need a fringing correction...

##########################################################
#### WEIGHT creation
##########################################################

#adam-USELESS BLOCK#
#### create normalized weight images
##./create_norm.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
##./create_norm_illum_fringe.sh ${SUBARUDIR}/${run}_${filter} SCIENCE

#BLOCK6-PER RF# per Run and per Filter (flat chosen already)
#adam# normalizes the flat field: makes flat_norm directory and FLAT_norm/FLAT_norm_1-10.fits
#./create_norm.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} #10
#exit 0; #10

#adam-USELESS BLOCK#
#adam# no superflat, so don't use this next line
##./create_globalweight_base.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}_norm SCIENCE_norm

#BLOCK7-PER RF# per Run and per Filter (flat chosen already)
#adam# make the directory myself instead of doing the thing with the superflat
#if [ ! -d ${SUBARUDIR}/${run}_${filter}/BASE_WEIGHT ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/BASE_WEIGHT
#fi #11a
#cp ${SUBARUDIR}/${run}_${filter}/${FLAT}_norm/${FLAT}_norm*.fits ${SUBARUDIR}/${run}_${filter}/BASE_WEIGHT
#rename "s/${FLAT}_norm/BASE_WEIGHT/g" ${SUBARUDIR}/${run}_${filter}/BASE_WEIGHT/${FLAT}_norm_*.fits #11a

########################################################t#
#### B: GLOBAL WEIGHT CREATION ###
##########################################################
./BonnLogger.py comment "B: Global Weight Creation"

#BLOCK8#
#adam-DO# copy over the region files to the /reg/ directory in ${run}_${filter} (COPY, DON'T LINK!)
#STARTOVER-REGION CHANGE# IF YOU MESS WITH REGION FILES YOU MUST START OVER AT THIS POINT!
for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
do
    if [ -e ${SUBARUDIR}/${run}_${filter}/reg/globalweight_${CHIP}.reg ]; then
	cp ${SUBARUDIR}/${run}_${filter}/reg/globalweight_${CHIP}.reg ${SUBARUDIR}/${run}_${filter}/reg/SUBARU_${CHIP}.reg
    fi
done
#exit 0; #11
#adam# these two lines are needed if you have region files. these make the region files consistent with the current distribution of ds9
#convertRegion2Poly.py just backs up the directory1G
./convertRegion2Poly.py ${SUBARUDIR} ${run}_${filter} #12
./transform_ds9_reg_alt.sh ${SUBARUDIR} ${run}_${filter} #12
#exit 0; #12

#adam-notes# find removed USELESS BLOCK and stuff about how I used to do the limits and regions before WeightMasker in do_Subaru_preprocess_notes.sh search #OLD MASKS

#BLOCK9#
#adam# this will use the flats and darks to make run_filter/WEIGHTS/global*.fits
#adam# this uses the tools I've developed, it applies the SUPER WIDE uniform cuts, then uses WeightMasker and region files to mask out bad pixels in globalweights_1.fits
#############SUPER WIDE BASE_WEIGHT LIMITS USED HERE!########################
#adam# The DARK limits are the same unless config changes (these were fit by eye)
#adam#super wide limits that I just use because this doesn't matter much at this point (this is found by taking the min of the lower limits and max of the upper limits for all "by eye" limits for each filter, then taking min-.04 and max+.08 so that I'm sure this will cut almost nothing out)
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.42 1.04 DARK -1.73 4.15 1
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.74 1.11 DARK -1.88 4.6 2
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.79 1.15 DARK -1.88 4.9 3
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.69 1.12 DARK -1.88 5.35 4
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.32 1.1 DARK -2.94 5.95 5
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.37 1.11 DARK -1.88 5.5 6
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.74 1.14 DARK -1.73 4.75 7
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.81 1.19 DARK -2.04 4.75 8
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.59 1.09 DARK -1.43 4.6 9
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.3 1.07 DARK -1.58 4.75 10 # 13
#10_2# use these ultra-wide limits for 10_2 where CCD #6 has super low counts so we don't use it. Also, I've copied over DARK frames and have fit limits for them.
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.22 1.24 DARK -4.43 10.06 1
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.54 1.31 DARK -4.43 9.06 2
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.59 1.35 DARK -4.43 8.45 3
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.49 1.32 DARK -4.43 6.84 4
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.12 1.3 DARK -4.63 7.04 5
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.17 1.31 DARK -4.43 6.84 6
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.54 1.34 DARK -4.43 13.29 7
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.61 1.39 DARK -4.43 6.84 8
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.39 1.29 DARK -4.43 6.84 9
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.1 1.27 DARK -4.43 6.64 10


#adam-notes# find "By Eye" limits for old filters/runs in do_Subaru_preprocess_notes.sh search #BY EYE LIMITS
#exit 0; #13
#adam# make weighted science images
./create_global_science_weighted.sh ${SUBARUDIR}/${run}_${filter} SCIENCE WEIGHTS #14
#exit 0; #14
#echo "Todo: Mask SCIENCE Flats for dust grains, missed hot pixels, etc.
#Use the images in the SCIENCE_weighted directory for masking.
#Region files should be saved in $maindir/reg.
#For precision masking, using mark_badpixel_regions.pl."
#echo "Goto B: Global Weight Creation"
#adam-DO check# MAKE SURE BAD THINGS (hot pixels, etc.) ARE COVERED BY REGION FILES:
#	ds9 ${run}_${filter}/WEIGHTS/globalweight_*.fits
./WeightMasker.py ${SUBARUDIR}/${run}_${filter}/WEIGHTS #15

#adam-USELESS BLOCK# (i think so at least, i don't need that #?# command do I?
##########################################################
###./splitoff_aux_data.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending} ${SUBARUDIR}/SUBARU.list
##########################################################
###groups together cluster pointings from one run
#?#./distribute_sets_subaru.sh ${SUBARUDIR} ${run}_${filter}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list
### note: this script now also copies globalweight*.fits and globalflag*fits
### to ${SUBARUDIR}/${cluster}/${filter}/WEIGHTS

####################################
##CHECKPOINT
####################################
./BonnLogger.py checkpoint Preprocess
exit 0; #15
