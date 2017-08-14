#! /bin/bash -xv

### superscript template to do the preprocessing
### $Id: do_Subaru_preprocess_config8.sh,v 1.6 2010-02-02 23:04:24 dapple Exp $


. progs.ini

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki05/anja/SUBARU

run=2000-08-06
filter="W-C-RC"

export BONN_TARGET=${run}
export BONN_FILTER=${filter}

FLAT=SKYFLAT        # SKYFLAT or DOMEFLAT
SET=SET0            # sets time period of flat to use
SKYBACK=256          # in case of SKYFLAT: size of background mesh for superflat
                    # illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?)
                    # 16 (or 32) if lots of blobs

FRINGE=NOFRINGE       # FRINGE if fringing correction necessary; NOFRINGE otherwise
STANDARDSTARS=0     # process the STANDARD frames, too  (1 if yes; 0 if no)

if [ ${FRINGE} == "FRINGE" ]; then
    ending="OCFSF"
elif [ ${FRINGE} == "NOFRINGE" ]; then
    ending="OCFS"
else
    echo "You need to specify FRINGE or NOFRINGE for the fringing correction!"
    exit 2;
fi

SCIENCEDIR=SCIENCE_${FLAT}_${SET}

export TEMPDIR='.'
#Comment out the lines as you progress through the script

#######################################
## Reset Logger
./BonnLogger.py clear

##################################################################
### create and load the SUBARU.ini file
### !!! DO NOT COMMENT THIS BLOCK !!!
##################################################################

./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
export INSTRUMENT=SUBARU

. ${INSTRUMENT:?}.ini

#################################################################
## Capture Variables
./BonnLogger.py config \
    run=${run} \
    filter=${filter} \
    FLAT=${FLAT} \
    SET=${SET} \
    SKYBACK=${SKYBACK} \
    FRINGE=${FRINGE} \
    STANDARDSTARS=${STANDARDSTARS} \
    config=${config}


##################################################################
# if needed: cp auxiliary data
##################################################################

#./cp_aux_data.sh ${SUBARUDIR} ${run}_BIAS ${SUBARUDIR}/auxiliary/${run}_BIAS
#./cp_aux_data.sh ${SUBARUDIR} ${run}_DARK /nfs/slac/g/ki/ki03/xoc/anja/SUBARU/auxiliary/${run}_DARK
#./cp_aux_data.sh ${SUBARUDIR} ${run}_${filter} /nfs/slac/g/ki/ki03/xoc/anja/SUBARU/auxiliary/${run}_${filter}
#./cp_aux_data.sh ${SUBARUDIR} ${run}_${filter} ${SUBARUDIR}/auxiliary/${run}_${filter}/SCIENCE

##################################################################
# process the BIAS frames (per chip)
# only needs to be done once per run!
##################################################################

#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_BIAS BIAS

### first quality check: run  imstats  , if necessary, reject files:
# ./check_files.sh  ${SUBARUDIR}/${run}_BIAS BIAS "" 500 9000

### overscan-correct BIAS frames, OC+BIAS correct flats
#./parallel_manager.sh ./process_bias_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS


##################################################################
# process the DARK frames (per chip)
# only needs to be done once per run!
##################################################################

#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_DARK DARK
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_DARK DARK SUP "" 8 -32

### first quality check: run  imstats  , if necessary, reject files:
# ./check_files.sh  ${SUBARUDIR}/${run}_BIAS BIAS "" 500 9000

### overscan-correct BIAS frames, OC+BIAS correct flats
#./parallel_manager.sh ./process_bias_eclipse_para.sh ${SUBARUDIR}/${run}_DARK DARK
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_DARK DARK SUP "OC" 8 -32

### note: I am doing this the old way of using DARKs. the DARKs show
### varying levels, hence, i will adjust the threshold when doing the
### globalweights.
### manual masking of the DARKs will be done as part of masking the
### global weights


####################################################################
# pre-processing of individual chips,
# per filter
####################################################################


#### if necessary, rename the STANDARD directory
#if [ -d ${SUBARUDIR}/${run}_${filter}/STANDARD_STAR ]; then
#    mv ${SUBARUDIR}/${run}_${filter}/STANDARD_STAR ${SUBARUDIR}/${run}_${filter}/STANDARD
#fi
#
### re-split the files, overwrite headers

#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
##./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} STANDARD
#
### copy the master BIAS
#if [ ! -d ${SUBARUDIR}/${run}_${filter}/BIAS ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/BIAS
#fi
#ln -s ${SUBARUDIR}/${run}_BIAS/BIAS/BIAS_*.fits ${SUBARUDIR}/${run}_${filter}/BIAS
#
#
## copy the master DARK
#if [ ! -d ${SUBARUDIR}/${run}_${filter}/DARK ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/DARK
#fi
#ln -s ${SUBARUDIR}/${run}_DARK/DARK/DARK_*.fits ${SUBARUDIR}/${run}_${filter}/DARK
#
#
#
#exit 0;
#
#####################################################
##### PROCESS FLATFIELD
#
###./check_files_1chip.sh  ${SUBARUDIR}/${run}_${filter} ${FLAT} "" 10000 32000 2
##
###cd ${SUBARUDIR}/${run}_${filter}/${FLAT}
###mv SUPA0001983_*.fits SUPA0002133_*.fits SUPA0002294_*.fits BADMODE
###cd ${REDDIR}

#./parallel_manager.sh ./process_flat_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT}
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} ${FLAT} "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} SUP "OC" 8 -32
#
#if [ ! -f ${SUBARUDIR}/${run}_${filter}/TEST_${FLAT} ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/TEST_${FLAT}
#fi
#cp ${SUBARUDIR}/${run}_${filter}/${FLAT}/SUP*[0-9].fits ${SUBARUDIR}/${run}_${filter}/TEST_${FLAT}/
#
#./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} TEST_${FLAT} RESCALE NOFRINGE
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} TEST_${FLAT} SUP "OFC" 8 -32
#
#
### OC SCIENCE frames
#./parallel_manager.sh prep_science_para.sh ${SUBARUDIR}/${run}_${filter} BIAS SCIENCE
#
#if [ ! -d ${SUBARUDIR}/${run}_${filter}/${FLAT}_${SET} ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/${FLAT}_${SET}
#fi
#
#i=1
#while [ "${i}" -le "${NCHIPS}" ]
#do
# ln -s ${SUBARUDIR}/${run}_${filter}/${FLAT}/${FLAT}_${i}.fits ${SUBARUDIR}/${run}_${filter}/${FLAT}_${SET}/${FLAT}_${SET}_${i}.fits
# i=$(( $i + 1 ))
#done
#
#./test_run_prep.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}_${SET} SCIENCE
#
##################################################################

## A: PROCESS SUPERFLAT ###

#./BonnLogger.py comment "A: Process Superflat"
#
#### OCF SCIENCE frames + superflat (allows for easy tryout of diff flat fields)
#if [ ! -d ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR
#fi
#./parallel_manager.sh process_sub_images_para.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}_${SET} SCIENCE NOFRINGE
#
## A: PROCESS SUPERFLAT ###
#./parallel_manager.sh process_superflat_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_${FLAT}_${SET}

### Create Illum/Fringe Corrections
#./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR ${SKYBACK}
#
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "_fringe${SKYBACK}" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "_illum${SKYBACK}" 8 -32
#
#./create_norm.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}
#./create_norm_illum_fringe.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} $SKYBACK
#./make_residuals.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR ${SKYBACK}
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "_illum${SKYBACK}" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "_fringe${SKYBACK}" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "_res${SKYBACK}" 8 -32
#
#echo "Todo: Inspect SCIENCE/BINNED frames for bright stars, autotracker shadows, etc.
#Create maindir/superflat_exclusion, which is a list of the SUPAxxx_CHIP frames to exclude. 
#createExclusion.py may help in making the list."
#echo "Goto A: Process SUPERFLAT"
#
#echo "Finally, settle on a blasted Flat field, will you!?"
#
#### Apply Corrections to Science Data
#if [ ${FRINGE} == "NOFRINGE" ]; then
#  ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm RESCALE ILLUM ${SKYBACK} ${SCIENCEDIR}
#else
#  ./parallel_manager.sh ./process_science_illum_fringe_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm RESCALE ${SKYBACK} ${SCIENCEDIR}
#fi
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}/OCF_IMAGES SUP OCF 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} SUP ${ending} 8 -32
#exit 0;
###########################################################

#./BonnLogger.py comment "Transfering Winning Flatfield"
#
#### link science data back into SCIENCE
#if [ ! -d ${SUBARUDIR}/${run}_${filter}/SCIENCE/OC_IMAGES ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/SCIENCE/OC_IMAGES
#fi
#mv ${SUBARUDIR}/${run}_${filter}/SCIENCE/SUPA*OC.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/OC_IMAGES
#
#ln -s ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR/SUPA*${ending}.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/
#
#for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
#do
#    ln -s ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR/${SCIENCEDIR}_${CHIP}.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}.fits
#    ln -s ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR/${SCIENCEDIR}_${CHIP}_illum${SKYBACK}.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}_illum.fits
#    ln -s ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR/${SCIENCEDIR}_${CHIP}_fringe${SKYBACK}.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}_fringe.fits
#done
#
#ln -s ${SUBARUDIR}/${run}_${filter}/${FLAT}_${SET} ${SUBARUDIR}/${run}_${filter}/${FLAT}
#
#### create normalized weight images
#
#./create_norm.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
#./create_norm_illum_fringe.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
#./create_norm.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}
#
#./create_globalweight_base.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}_norm SCIENCE_norm
########################################################

### B: GLOBAL WEIGHT CREATION ###
#./BonnLogger.py comment "B: Global Weight Creation"
#
##if [ ! -d ${SUBARUDIR}/${run}_${filter}/reg ]; then
##    mkdir ${SUBARUDIR}/${run}_${filter}/reg
##fi
#
#./convertRegion2Poly.py ${SUBARUDIR} ${run}_${filter}
#./transform_ds9_reg_alt.sh ${SUBARUDIR} ${run}_${filter}
#
#####Create Masks from SCIENCE images### 
##for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
##do
##    cp ${SUBARUDIR}/${run}_${filter}/SCIENCE_weighted/SCIENCE_${CHIP}.weighted.imask ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}.imask
##done
#
##./create_badpixel_mask.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
#
#### create_global_weights_para.sh: first 2 numbers are acceptable range of pixels in normalized flat file. .6 - 1.3 includes corners (may cause problems in the future, just keep an eye out.   If you have a dark frame, substitue for BIAS.  basiaclly, tell it all things that you want to feed in to make global file with the acceptable ranges. first input forms the basis, any subsequent inputs just flag pixels
##
#./parallel_manager.sh ./create_global_weights_flags_raw_para.sh \
#	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.4 1.3 BIAS -20 20 \
#	SCIENCE_norm 0.9 1.1
#exit 0;
#### W-C-RC
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.5 0.9 BIAS -2 2 \
###	DARK -3 5 SCIENCE_norm 0.9 1.1 SCIENCE_mask -0.5 0.5 1
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.96 1.06 BIAS -2 2 \
###	DARK -4 3 SCIENCE_norm 0.9 1.1 SCIENCE_mask -0.5 0.5 2
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.53 0.63 BIAS -9 9 \
###	DARK -15 15 SCIENCE_norm 0.9 1.1 SCIENCE_mask -0.5 0.5 3
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.53 0.63 BIAS -9 9 \
###	DARK -15 15 SCIENCE_norm 0.9 1.1 SCIENCE_mask -0.5 0.5 4
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.55 1.07 BIAS -3 9 \
###	DARK -2 3 SCIENCE_norm 0.9 1.1 SCIENCE_mask -0.5 0.5 5
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.92 1.02 BIAS -3 4 \
###	DARK -3 3 SCIENCE_norm 0.9 1.1 SCIENCE_mask -0.5 0.5 6
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.66 0.76 BIAS -20 20 \
###	DARK -15 20 SCIENCE_norm 0.9 1.1 SCIENCE_mask -0.5 0.5 7
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.54 0.69 BIAS -15 15 \
###	DARK -25 30 SCIENCE_norm 0.9 1.1 SCIENCE_mask -0.5 0.5 8
###
##### W-C-IC
##### note: these are very tight constraints!
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.46 0.78 BIAS -2 2 \
###	DARK -3 5 SCIENCE_norm 0.9 1.1 1
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.7 0.85 BIAS -2 2 \
###	DARK -4 3 SCIENCE_norm 0.9 1.1 2
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.48 0.55 BIAS -9 9 \
###	DARK -15 15 SCIENCE_norm 0.9 1.1 3
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.46 1.3 BIAS -9 9 \
###	DARK -15 15 SCIENCE_norm 0.9 1.1 4
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.6 1.1 BIAS -3 9 \
###	DARK -2 3 SCIENCE_norm 0.9 1.1 5
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.68 0.81 BIAS -3 4 \
###	DARK -3 3 SCIENCE_norm 0.9 1.1 6
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.58 0.68 BIAS -20 20 \
###	DARK -15 20 SCIENCE_norm 0.9 1.1 7
###./create_global_weights_flags_para.sh \
###	${SUBARUDIR}/${run}_${filter} BASE_WEIGHT 0.5 0.61 BIAS -15 15 \
###	DARK -25 30 SCIENCE_norm 0.9 1.1 8
#
#./create_global_science_weighted.sh ${SUBARUDIR}/${run}_${filter} SCIENCE WEIGHTS
#./create_global_science_weighted.sh ${SUBARUDIR}/${run}_${filter} DARK WEIGHTS
#
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} WEIGHTS globalweight "" 8 -32
#
#
#echo "Todo: Mask SCIENCE Flats for dust grains, missed hot pixels, etc.
#Use the images in the SCIENCE_weighted directory for masking.
#Region files should be saved in $maindir/reg.
#For precision masking, using mark_badpixel_regions.pl."
#echo "Goto B: Global Weight Creation"

##########################################################

#./BonnLogger.py clear
#
#./splitoff_aux_data.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending} ${SUBARUDIR}/SUBARU.list
#
#exit 0;
#################################################################################
#### STANDARD star processing
#################################################################################
#
#
#if [ ! -d  ${SUBARUDIR}/${run}_${filter}/STANDARD ] && [ ${STANDARDSTARS} -eq 1 ]; then
#
#    ./BonnLogger.py clear
#    ./BonnLogger.py comment "STANDARD star processing"
#
#  case ${filter} in
#      "W-J-B" )
#  	photfilter=B          # corresponding Johnson filter
#  	photcolor=BmV         # color to use
#  	EXTCOEFF=-0.2104      # guess for the extinction coefficient
#  	COLCOEFF=0.0          # guess for the color coefficient
#  	;;
#      "W-J-V" )
#  	photfilter=V
#  	photcolor=VmR
#  	EXTCOEFF=-0.1202
#  	COLCOEFF=0.0
#  	;;
#      "W-C-RC" )
#  	photfilter=R
#  	photcolor=VmR
#  	EXTCOEFF=-0.0925
#  	COLCOEFF=0.0
#  	;;
#      "W-C-IC" | "W-S-I+" )
#  	photfilter=I
#  	photcolor=RmI
#  	EXTCOEFF=-0.02728
#  	COLCOEFF=0.0
#  	;;
#      "W-S-Z+" )
#  	photfilter=I
#  	photcolor=RmI
#  	EXTCOEFF=0.0
#  	COLCOEFF=0.0
#  	;;
#  esac
#  
#  ./parallel_manager.sh ./process_standard_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE STANDARD NORESCALE
#  
#  ./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} STANDARD SUPA OFC 8 -32
#  
#  ./maskBadOverscans.py ${SUBARUDIR}/${run}_${filter} STANDARD SUPA
#  #./maskAutotracker.py ${SUBARUDIR}/${run}_${filter} STANDARD
#  
#  ./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${SKYBACK}
#
#  if [ ${FRINGE} == "NOFRINGE" ]; then
#    ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD RESCALE ILLUM
#  else
#    ./parallel_manager.sh ./process_science_illum_fringe_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD RESCALE
#  fi
#  
#  ./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} STANDARD SUPA ${ending} 8 -32
#  
#  ./parallel_manager.sh ./create_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${ending} WEIGHTS_FLAGS 
#  
#  ./parallel_manager.sh ./create_astrom_std_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${ending} default
#  
#  ./create_abs_photo_info.sh ${SUBARUDIR}/${run}_${filter} STANDARD SCIENCE \
#      ${ending} ${filter} ${photfilter} ${photcolor} ${EXTCOEFF} ${COLCOEFF}
#  
#  ./create_zp_correct_header.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending}
#
#fi



#################################################################################
### set-specific processing
#################################################################################

###groups together cluster pointings from one run
./distribute_sets_subaru.sh ${SUBARUDIR} ${run}_${filter}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list WEIGHTS

### note: this script now also copies globalweight*.fits and globalflag*fits
### to ${SUBARUDIR}/${cluster}/${filter}/WEIGHTS

####################################
##CHECKPOINT
####################################
exit 0;
./BonnLogger.py checkpoint Preprocess

#################################################################################
###  script for the coaddition:
###  do_Subaru_coadd_template.sh
#################################################################################
