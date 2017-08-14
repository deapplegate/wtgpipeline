setup_SUBARU.sh: makes the SUBARU.ini file which is specific to the telescope setup your images come from (for example 10_3)

process_split_Subaru_eclipse.sh: 10 files from concatenated files

parallel_manager.sh: handles multiple ccds

process_bias_4channels_eclipse_para.sh: correct the bias frames for overscan

#DARK STEPS
########### DARK Step (1) #########################################
#adam# Dark step (1) is to do this, use optional run directory=10_3 for darks since you only take darks very infrequently
#adam# instead of this I ran ./cp_aux_data.sh /nfs/slac/g/ki/ki18/anja/SUBARU 10_3_DARK /nfs/slac/g/ki/ki18/anja/SUBARU/from_archive/darks

########### DARK Step (2) #########################################
## process the DARK frames (per chip)
## only needs to be done once per run!
###################################################################
##./BonnLogger.py clear
#### "process_split" splits the multi-extension files into one file
#### per CCD, i.e. SUPA*_${chip}.fits
#adam# put DARK in for bias here ${run}=10_3
##./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_DARK DARK 

#### overscan-correct DARK frames, OC+DARK correct flats
#### processed files are called  SUPA*_${chip}OC.fits
##./parallel_manager.sh ./process_bias_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_DARK DARK

##### creates overview mosaics; use these to identify bad frames
##./create_binnedmosaics.sh ${SUBARUDIR}/${run}_DARK DARK DARK "" 8 -32
##./create_binnedmosaics.sh ${SUBARUDIR}/${run}_DARK DARK SUP "" 8 -32
##./create_binnedmosaics.sh ${SUBARUDIR}/${run}_DARK DARK SUP "OC" 8 -32

########### DARK Step (3) #########################################
##### copy master DARK (3) #### (I DID THIS FOR ALL OF THE !0_3 runs already)
#adam# instead of this I just ran:
#adam# mkdir 2010-02-12_W-C-IC/DARK
#adam# ln -s ~/data/10_3_DARK/DARK/DARK_*.fits ~/data/2010-02-12_W-C-IC/DARK
##if [ ! -d ${SUBARUDIR}/${run}_${filter}/DARK_master ]; then
##    mkdir ${SUBARUDIR}/${run}_${filter}/DARK_master
##fi
##ln -s ${SUBARUDIR}/${INSTRUMENT}_${config}_DARK/DARK/DARK_*.fits ${SUBARUDIR}/${run}_${filter}/DARK

#########################OLD MASKS#######################################################
#adam-notes# find removed USELESS BLOCK and stuff about how I used to do the limits and regions before WeightMasker in do_Subaru_preprocess_notes.sh search #OLD MASKS

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
##      ${SUBARUDIR}/${run}_${filter} \
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

#########################By Eye Limits#################################################
#adam-notes# find "By Eye" limits for old filters/runs in do_Subaru_preprocess_notes.sh
#for 2010-02-12_W-C-IC
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.48 0.91 DARK -1.73 4.15 1
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.82 1.01 DARK -1.88 4.6 2
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.87 1.05 DARK -1.88 4.9 3
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.82 1.02 DARK -1.88 5.35 4
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.48 0.97 DARK -2.94 5.95 5
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.43 0.99 DARK -1.88 5.5 6
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.83 1.05 DARK -1.73 4.75 7
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.89 1.08 DARK -2.04 4.75 8
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.7 0.99 DARK -1.43 4.6 9
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.5 0.95 DARK -1.58 4.75 10

#for 2010-02-12_W-C-RC
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.48 0.91 DARK -1.73 4.15 1
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.82 1.01 DARK -1.88 4.6 2
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.86 1.06 DARK -1.88 4.9 3
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.81 1.02 DARK -1.88 5.35 4
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.47 1.01 DARK -2.94 5.95 5
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.42 0.99 DARK -1.88 5.5 6
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.8 1.05 DARK -1.73 4.75 7
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.9 1.09 DARK -2.04 4.75 8
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.71 0.97 DARK -1.43 4.6 9
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.5 0.95 DARK -1.58 4.75 10

#for 2010-02-12_W-J-B
# ./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.47 0.93 DARK -1.73 4.15 1
# ./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.81 1.03 DARK -1.88 4.6 2
# ./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.84 1.07 DARK -1.88 4.9 3
# ./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.73 1.04 DARK -1.88 5.35 4
# ./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.45 1.02 DARK -2.94 5.95 5
# ./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.41 1.03 DARK -1.88 5.5 6
# ./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.78 1.06 DARK -1.73 4.75 7
# ./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.85 1.11 DARK -2.04 4.75 8
# ./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.69 1.01 DARK -1.43 4.6 9
# ./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.5 0.99 DARK -1.58 4.75 10

#for 2010-02-12_W-J-V
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.49 0.91 DARK -1.73 4.15 1
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.82 1.02 DARK -1.88 4.6 2
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.85 1.06 DARK -1.88 4.9 3
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.81 1.02 DARK -1.88 5.35 4
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.47 0.98 DARK -2.94 5.95 5
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.44 0.99 DARK -1.88 5.5 6
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.85 1.05 DARK -1.73 4.75 7
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.9 1.1 DARK -2.04 4.75 8
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.72 1.0 DARK -1.43 4.6 9
#./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.51 0.97 DARK -1.58 4.75 10

#for 2010-04-15_W-S-G+
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.46 0.94 DARK -1.73 4.15 1
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.81 1.01 DARK -1.88 4.6 2
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.83 1.06 DARK -1.88 4.9 3
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.8 1.03 DARK -1.88 5.35 4
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.43 0.99 DARK -2.94 5.95 5
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.42 1.01 DARK -1.88 5.5 6
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.82 1.05 DARK -1.73 4.75 7
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.9 1.1 DARK -2.04 4.75 8
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.68 0.98 DARK -1.43 4.6 9
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.47 0.98 DARK -1.58 4.75 10

#for 2010-04-15_W-S-I+
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.5 0.93 DARK -1.73 4.15 1
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.83 1.01 DARK -1.88 4.6 2
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.87 1.05 DARK -1.88 4.9 3
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.82 1.0 DARK -1.88 5.35 4
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.46 0.97 DARK -2.94 5.95 5
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.45 1.0 DARK -1.88 5.5 6
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.84 1.04 DARK -1.73 4.75 7
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.89 1.07 DARK -2.04 4.75 8
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.69 0.95 DARK -1.43 4.6 9
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.49 0.95 DARK -1.58 4.75 10

#for 2011-01-06_W-C-IC
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.58 0.96 DARK -1.73 4.15 1
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.78 1.0 DARK -1.88 4.6 2
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.86 1.04 DARK -1.88 4.9 3
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.78 1.01 DARK -1.88 5.35 4
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.36 0.94 DARK -2.94 5.95 5
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.55 1.03 DARK -1.88 5.5 6
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.85 1.05 DARK -1.73 4.75 7
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.9 1.07 DARK -2.04 4.75 8
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.65 0.95 DARK -1.43 4.6 9
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.38 0.92 DARK -1.58 4.75 10

#for 2011-01-06_W-S-Z+
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.58 0.91 DARK -1.73 4.15 1
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.78 1.01 DARK -1.88 4.6 2
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.86 1.04 DARK -1.88 4.9 3
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.8 1.02 DARK -1.88 5.35 4
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.42 0.95 DARK -2.94 5.95 5
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.41 0.98 DARK -1.88 5.5 6
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.8 1.05 DARK -1.73 4.75 7
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.86 1.07 DARK -2.04 4.75 8
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.63 0.94 DARK -1.43 4.6 9
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.34 0.93 DARK -1.58 4.75 10

###########################SUPER WIDE LIMITS##########################################
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

#10_2-old# use these ultra-wide limits for 10_2 where CCD #6 has super low counts. Also, there are no DARK frames for this config
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.12 1.34 1
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.44 1.41 2
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.49 1.45 3
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.39 1.42 4
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.02 1.40 5
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.00 1.41 6 #was .07 lower limit
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.44 1.44 7
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.51 1.49 8
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.29 1.39 9
./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.00 1.37 10 # 13

