#! /bin/bash -xv

### superscript template to do the preprocessing
. progs.ini
REDDIR=`pwd`

####################################################
### the following need to be specified for each run
####################################################

export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
run=2006-03-04 ; filter="W-C-RC" ; FLAT=DOMEFLAT #10_2 config

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

./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS/
export INSTRUMENT=SUBARU

. ${INSTRUMENT:?}.ini

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

#STARTOVER-BEGIN#

#BLOCK1-PER RUN# BIAS frames are filter indep. so do this once per run
#### "process_split" splits the multi-extension files into one file
#### per CCD, i.e. SUPA*_${chip}.fits
#adam# splits BIAS files SUPA#.fits into SUPA#_1.fits, SUPA#_2.fits, ...
#adam# this step takes a while
./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_BIAS BIAS
#### overscan-correct BIAS frames, OC+BIAS correct flats
#### processed files are called  SUPA*_${chip}OC.fits
#adam# handles multiple ccds, does overscan correct, and makes the master bias files (in ~/data/2010-02-12_BIAS/BIAS/ makes:
##       1.) SUPA#_1OC.fits, SUPA#_2OC.fits, ...
##       2.) BIAS_1.fits - BIAS_10.fits which are the master bias files copied to ~/data/2010-02-12_W-C-IC/BIAS
##       3.) new dir /BINNED/ with BIAS_mos.fits and SUPA#_mosOC.fits
#STARTOVER-BAD BIAS FRAMES REMOVED
./parallel_manager.sh ./process_bias_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS
#### creates overview mosaics; use these to identify bad frames
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS BIAS "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS SUP "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS SUP "OC" 8 -32
#adam-check# after it creates the mosaics, look at the filter_BIAS/BIAS/BINNED/*_mosOC.fits folder and see if any of the frames are bad. delete them (in the /BIAS/BINNED, /BIAS/ORIGINALS, and /BIAS/ folders), then delete, in the /BIAS/ folder, the BIAS_*.fits files, and re-run the process_bias_4channel_eclipse_para.sh file so that the final averaged flats dont have these bad frames included (see #STARTOVER-BAD BIAS FRAMES REMOVED)
exit
########### DARK Step (2) #########################################

####################################################################
# pre-processing of individual chips,
# PER FILTER (and per FLAT)
####################################################################

#BLOCK2-PER RFF# per Run per Filter and per Flat
#### re-split the files, write THELI headers  -->  SUPA*_${chip}.fits
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}
#adam-check# if you are doing sky flats, then stop here, run imstats SUPA*3.fits and see if the counts are comparable, not too high, not too low, etc. There might be some bad ones you want to throw out. If you throw any out, delete every occurance of it (including in ORIGINALS, BINNED, from_archive, etc.).

#BLOCK3-PER RF# per Run and per Filter (i.e. dont run if processing SKYFLAT after already having processed DOMEFLAT)
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
#### copy the master BIAS to run_filter/BIAS
#if [ ! -d ${SUBARUDIR}/${run}_${filter}/BIAS ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/BIAS
#    cp ${SUBARUDIR}/${run}_BIAS/BIAS/BIAS_*.fits ${SUBARUDIR}/${run}_${filter}/BIAS
#fi

########### DARK Step (3) #########################################

#BLOCK4-PER RFF# per Run per Filter and per Flat
#### overscan+bias correct the FLAT fields then average the flats to create the masterFLAT
#adam# corrects for overscan (O), cuts the images (C), subtracts the master bias, averages the flat fields. Make the files SUPA#_1OC.fits
#STARTOVER-BAD FLAT FRAMES REMOVED
#./parallel_manager.sh ./process_flat_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT}
#### creates overview mosaics; use these to identify bad frames
#adam# makes little images from the *_#OC.fits files
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} ${FLAT} "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} SUP "OC" 8 -32
#adam-check# at this point, go to BINNED dir and ds9 *.fits (ds9 -zscale ./2011-01-06_W-S-Z+/DOMEFLAT/BINNED/SUPA*mosOC.fits -geometry 2000x2000 -zoom to fit), see if any of the frames are bad. If they are, then, for example if 5 and 8 are bad do "rm -f *8OC.fits *5OC.fits *CHallOC.fits SKYFLAT_5.fits SKYFLAT_8.fits". Then re-run process_flat_eclipse_para.sh on those frames (for example "./process_flat_eclipse_para.sh ~/data/2010-02-12_W-C-IC BIAS SKYFLAT 8" and the same thing with 5) (see #STARTOVER-BAD FLAT FRAMES REMOVED) ONLY REMOVE IF REALLY BAD

#BLOCK5-PER RFF# per Run per Filter and per Flat
#### processes SCIENCE frames:
#### overscan, bias, flat -->  SUPA*_${chip}OCF.fits
#adam# process the SCIENCE images result=(science-bias)/(flat-bias)
#THIS TAKES A WHILE!#
#./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE}
#adam# normalize the flat fields
#./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUP OCF
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_norm SUP "OCFN" 8 -32
#### this is it if we assume we don't need a fringing correction...
#adam-check# choose which FLAT is better
#adam-restart#determine which flat is better and continue on from here using only one flat (change beginning of script to make sure you have the right one)

##########################################################
#### WEIGHT creation
##########################################################

#adam-USELESS BLOCK#
#### create normalized weight images
##./create_norm.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
##./create_norm_illum_fringe.sh ${SUBARUDIR}/${run}_${filter} SCIENCE

#BLOCK6-PER RF# per Run and per Filter (flat chosen already)
#adam# normalizes the flat field
#adam# this makes flat_norm directory and files
#./create_norm.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}

#adam-USELESS BLOCK#
#adam# no superflat, so don't use this next line
##./create_globalweight_base.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}_norm SCIENCE_norm

#BLOCK7-PER RF# per Run and per Filter (flat chosen already)
#adam# make the directory myself instead of doing the thing with the superflat
#if [ ! -d ${SUBARUDIR}/${run}_${filter}/BASE_WEIGHT ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/BASE_WEIGHT
#fi
#cp ${SUBARUDIR}/${run}_${filter}/${FLAT}_norm/${FLAT}_norm*.fits ${SUBARUDIR}/${run}_${filter}/BASE_WEIGHT
#rename "s/${FLAT}_norm/BASE_WEIGHT/g" ${SUBARUDIR}/${run}_${filter}/BASE_WEIGHT/${FLAT}_norm_*.fits
########################################################t#
#### B: GLOBAL WEIGHT CREATION ###
##########################################################
./BonnLogger.py comment "B: Global Weight Creation"

#BLOCK8#
#adam-DO# copy over the region files to the /reg/ directory in ${run}_${filter} (COPY, DON'T LINK!)
#STARTOVER-REGION CHANGE# IF YOU MESS WITH REGION FILES YOU MUST START OVER AT THIS POINT!
#adam# this loop is needed if you have region files
for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
do
    if [ -e ${SUBARUDIR}/${run}_${filter}/reg/globalweight_${CHIP}.reg ]; then
	cp ${SUBARUDIR}/${run}_${filter}/reg/globalweight_${CHIP}.reg ${SUBARUDIR}/${run}_${filter}/reg/SUBARU_${CHIP}.reg
    fi
done
#adam# these two lines are needed if you have region files. these make the region files consistent with the current distribution of ds9
./convertRegion2Poly.py ${SUBARUDIR} ${run}_${filter}
./transform_ds9_reg_alt.sh ${SUBARUDIR} ${run}_${filter}

#adam-USELESS BLOCK#
####Create Masks from SCIENCE images### 
##for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
##do
##    cp ${SUBARUDIR}/${run}_${filter}/SCIENCE_weighted/SCIENCE_${CHIP}.weighted.imask ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}.imask
##done
##./create_badpixel_mask.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
#### create_global_weights_para.sh: first 2 numbers are acceptable range of pixels in normalized flat file (don't want to exclude corners and stuff!).  Basically, tell it all things that you want to feed in to make global file with the acceptable ranges. first input forms the basis, any subsequent inputs (such as the DARK # #) just flag pixels
#adam# Dont use this command, this treats all CCDs the same (below: everything with an amount of light below .4 & above 1.1 is given 0 weight)
##./parallel_manager.sh ./create_global_weights_flags_para.sh \
##	${SUBARUDIR}/${run}_${filter} \
##        BASE_WEIGHT 0.4 1.1 \
##        DARK -3 4
#adam# Instead of the above command, I select the limits (on flat (BASE_WEIGHT) & dark (DARK) frames) for each CCD individually

#BLOCK9#
#adam# this will use the flats and darks to make run_filter/WEIGHTS/global*.fits
#adam# the flat (BASE_WEIGHT) limits I define here will change for the different filters within a run
#adam-tool# use python script I wrote that outputs pictures at limits as well as the histograms.
#adam-help# ds9 BASE_WEIGHT_1.fits -zscale -view layout vertical -geometry 2000x2000 -zoom to fit &
#adam-help# paste in a bunch of lines that look like
## ./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.48 0.91 DARK -1.73 4.15 1
## use the python code 1st guesses & ds9 to perfect them. The DARK limits are the same unless config changes

#############SUPER WIDE LIMITS USED HERE!########################
#adam#super wide limits that I just use because this doesn't matter much at this point (this is found by taking the min of the lower limits and max of the upper limits for all "by eye" limits for each filter, then taking min-.04 and max+.08 so that I'm sure this will cut almost nothing out)
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.42 1.04 DARK -1.73 4.15 1
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.74 1.11 DARK -1.88 4.6 2
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.79 1.15 DARK -1.88 4.9 3
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.69 1.12 DARK -1.88 5.35 4
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.32 1.1 DARK -2.94 5.95 5
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.37 1.11 DARK -1.88 5.5 6
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.74 1.14 DARK -1.73 4.75 7
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.81 1.19 DARK -2.04 4.75 8
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.59 1.09 DARK -1.43 4.6 9
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.3 1.07 DARK -1.58 4.75 10

#adam-archived#find limits for old filters/runs in do_Subaru_preprocess_notes.sh
#adam# make weighted science images
./create_global_science_weighted.sh ${SUBARUDIR}/${run}_${filter} SCIENCE WEIGHTS
#echo "Todo: Mask SCIENCE Flats for dust grains, missed hot pixels, etc.
#Use the images in the SCIENCE_weighted directory for masking.
#Region files should be saved in $maindir/reg.
#For precision masking, using mark_badpixel_regions.pl."
#echo "Goto B: Global Weight Creation"
#adam-check# MAKE SURE THE BAD THINGS (hot pixels, etc.) ARE COVERED BY REGION FILES:
#	ds9 ${run}_${filter}/WEIGHTS/globalweight_*.fits
./WeightMasker.py ${SUBARUDIR}/${run}_${filter}/WEIGHTS
exit 0;
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

./BonnLogger.py checkpoint Preprocess

#exit 0;
