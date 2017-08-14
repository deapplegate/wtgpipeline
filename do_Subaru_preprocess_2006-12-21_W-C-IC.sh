#! /bin/bash -xv

### superscript template to do the preprocessing
### $Id: do_Subaru_preprocess_2006-12-21_W-C-IC.sh,v 1.1 2010-02-04 19:55:00 anja Exp $

. progs.ini

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki02/xoc/anja/SUBARU

run=2006-12-21
filter="W-C-IC"

FLAT=DOMEFLAT        # SKYFLAT or DOMEFLAT
SKYBACK=256          # in case of SKYFLAT: size of background mesh for superflat
                    # illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?)
                    # 16 (or 32) if lots of blobs

FRINGE=FRINGE       # FRINGE if fringing correction necessary; NOFRINGE otherwise
STANDARDSTARS=0     # process the STANDARD frames, too  (1 if yes; 0 if no)

if [ ${FRINGE} == "FRINGE" ]; then
    ending="OFCSF"
elif [ ${FRINGE} == "NOFRINGE" ]; then
    ending="OFCS"
else
    echo "You need to specify FRINGE or NOFRINGE for the fringing correction!"
    exit 2;
fi

#Comment out the lines as you progress through the script

##################################################################
### create and load the SUBARU.ini file
### !!! DO NOT COMMENT THIS BLOCK !!!
##################################################################

./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
export INSTRUMENT=SUBARU

. ${INSTRUMENT:?}.ini

##################################################################
# if needed: cp auxiliary data
##################################################################

#./cp_aux_data.sh ${SUBARUDIR} ${run}_BIAS ${SUBARUDIR}/auxiliary/${run}_BIAS
#./cp_aux_data.sh ${SUBARUDIR} ${run}_${filter} ${SUBARUDIR}/auxiliary/${run}_${filter}


##################################################################
# process the BIAS frames (per chip)
# only needs to be done once per run!
##################################################################

#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_BIAS BIAS

#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS SUP "" 8 -32

#### first quality check: run  imstats  , if necessary, reject files:
# ./check_files_disp.sh  ${SUBARUDIR}/${run}_BIAS BIAS "" 8000 10500 7

#### overscan-correct BIAS frames, OC+BIAS correct flats
#./parallel_manager.sh ./process_bias_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS BIAS "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS SUP "OC" 8 -32

#
#
#####################################################################
## pre-processing of individual chips,
## per filter
#####################################################################
#
#
#### if necessary, rename the STANDARD directory
#mv ${SUBARUDIR}/${run}_${filter}/STANDARD_STAR ${SUBARUDIR}/${run}_${filter}/STANDARD
#
#
#### re-split the files, overwrite headers
#
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} STANDARD
#
#
#### copy the master BIAS
#mkdir ${SUBARUDIR}/${run}_${filter}/BIAS
#cp ${SUBARUDIR}/${run}_BIAS/BIAS/BIAS_*.fits ${SUBARUDIR}/${run}_${filter}/BIAS

#### copy master DARK ###
#mkdir ${SUBARUDIR}/${run}_${filter}/DARK_master
#cp ${SUBARUDIR}/${INSTRUMENT}_${config}_DARK/DARK_master/DARK_master_*.fits ${SUBARUDIR}/${run}_${filter}/DARK_master

#### overscan+bias correct the FLAT fields
#./check_files.sh  ${SUBARUDIR}/${run}_${filter} ${FLAT} "" 8000 30000
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} SUP "" 8 -32

#./parallel_manager.sh ./process_flat_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT}
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} SUP "OC" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} ${FLAT} "" 8 -32


####################################################################
#
#### A: PROCESS SUPERFLAT ###
#
#### OC+flat SCIENCE frames, create superflat
#./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE NOFRINGE
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUP OFC 8 -32
#
#
#if [ ${FLAT} == "DOMEFLAT" ]; then
#  ./parallel_manager.sh ./create_illumfringe_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
#else
#  ./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${SKYBACK}
#fi
#
#if [ ${FRINGE} == "NOFRINGE" ]; then
#  ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE RESCALE ILLUM
#else
#  ./parallel_manager.sh ./process_science_illum_fringe_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE RESCALE
#fi
#
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SCIENCE "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SCIENCE "_fringe" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SCIENCE "_illum" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUP ${ending} 8 -32
#
#
#echo "Todo: Inspect SCIENCE/BINNED frames for bright stars, autotracker shadows, etc.
#Create maindir/superflat_exclusion, which is a list of the SUPAxxx_CHIP frames to exclude. 
#createExclusion.py may help in making the list."
#echo "Goto A: Process SUPERFLAT"
#
#exit 0;
#
##########################################################

#### create normalized weight images
#./parallel_manager.sh ./create_norm_para.sh \
#    ${SUBARUDIR}/${run}_${filter} ${FLAT}
#
#./parallel_manager.sh ./create_norm_para.sh \
#    ${SUBARUDIR}/${run}_${filter} SCIENCE
#
#########################################################
#
### B: GLOBAL WEIGHT CREATION ###
#
#./convertBox2Poly.py ${SUBARUDIR} ${run}_${filter}
#./transform_ds9_reg_alt.sh ${SUBARUDIR} ${run}_${filter}
#
#####Create Masks from SCIENCE images### 
#for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
#do
#    cp ${SUBARUDIR}/${run}_${filter}/SCIENCE_weighted/SCIENCE_${CHIP}.weighted.imask ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}.imask
#done
#
#./create_badpixel_mask.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
#
### create_global_weights_para.sh: first 2 numbers are acceptable range of pixels in normalized flat file. .6 - 1.3 includes corners (may cause problems in the future, just keep an eye out.   If you have a dark frame, substitue for BIAS.  basiaclly, tell it all things that you want to feed in to make global file with the acceptable ranges. first input forms the basis, any subsequent inputs just flag pixels
#
#./parallel_manager.sh ./create_global_weights_flags_para.sh \
#	${SUBARUDIR}/${run}_${filter} ${FLAT}_norm 0.6 1.3 BIAS -9 9 \
#	SCIENCE_norm 0.9 1.1 DARK_master .5 1.5 SCIENCE_mask -.5 .5
#
#./create_global_science_weighted.sh ${SUBARUDIR}/${run}_${filter} SCIENCE WEIGHTS
#
#echo "Todo: Mask SCIENCE Flats for dust grains, missed hot pixels, etc.
#Use the images in the SCIENCE_weighted directory for masking.
#Region files should be saved in $maindir/reg.
#For precision masking, using mark_badpixel_regions.pl."
#echo "Goto B: Global Weight Creation"
#
#exit 0;

##########################################################

#./splitoff_aux_data.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending} ${SUBARUDIR}/SUBARU.list

##########################################################

### Processing for each Ind Image ###


#./maskBadOverscans.py ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA
#./maskAutotracker.py ${SUBARUDIR}/${run}_${filter} SCIENCE
#./parallel_manager.sh ./spikefinder_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA ${ending}
#
##### transform ds9-region file into ww-readable file:
#./convertBox2Poly.py ${SUBARUDIR}/${run}_${filter} SCIENCE
#./transform_ds9_reg_alt.sh ${SUBARUDIR}/${run}_${filter} SCIENCE

### C: CHIP PROCESSING ###

#if [ -d ${SUBARUDIR}/${run}_${filter}/SCIENCE_weighted ]; then
#    ./convertBox2Poly.py ${SUBARUDIR}/${run}_${filter} SCIENCE_weighted
#    ./transform_ds9_reg_alt.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_weighted
#
#    mkdir ${SUBARUDIR}/${run}_${filter}/SCIENCE/reg/OLD
#
#    mv ${SUBARUDIR}/${run}_${filter}/SCIENCE/reg/*.reg ${SUBARUDIR}/${run}_${filter}/SCIENCE/reg/OLD
#
#    cp ${SUBARUDIR}/${run}_${filter}/SCIENCE_weighted/reg/*.reg ${SUBARUDIR}/${run}_${filter}/SCIENCE/reg
#
#fi
#
#./parallel_manager.sh ./create_weights_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending}
### note: I've changed the saturation level to 30000 in weights.ww
### (was:62000)
#
#./parallel_manager.sh ./create_science_weighted.sh ${SUBARUDIR}/${run}_${filter} SCIENCE WEIGHTS ${ending}
#
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_weighted SUP ${ending}.weighted 8 -32
#
#echo "Todo: Mask images by hand for remaining defects (satelite trails, blobs, etc).
#Use the images in SCIENCE_weighted for masking.
#maskImages.pl may be useful for managing region files."
#echo "Goto C: Chip Processing"
#
#exit 0;
#
#
#################################################################################
#### STANDARD star processing
#################################################################################
#
#if [ -d  ${SUBARUDIR}/${run}_${filter}/STANDARD ] && [ ${STANDARDSTARS} -eq 1 ]; then
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
#  if [ ${FLAT} == "DOMEFLAT" ]; then
#    ./parallel_manager.sh ./create_illumfringe_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD
#  else
#    ./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${SKYBACK}
#  fi
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
#  ./parallel_manager.sh ./create_astrom_std_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD \
#      ${ending} default
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
./distribute_sets_subaru.sh ${SUBARUDIR} ${run}_${filter}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list


#################################################################################
###  script for the coaddition:
###  do_Subaru_coadd_template.sh
#################################################################################
