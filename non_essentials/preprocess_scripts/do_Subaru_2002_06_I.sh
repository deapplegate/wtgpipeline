#! /bin/bash -xv

### superscript to reduce the 2002-06-04_W-C-IC dataset
### $Id: do_Subaru_2002_06_I.sh,v 1.7 2008-08-01 22:31:46 pkelly Exp $

. progs.ini

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki02/xoc/anja/SUBARU

run=2002-06-04
filter="W-C-IC"

FLAT=SKYFLAT        # SKYFLAT or DOMEFLAT
SKYBACK=16          # in case of SKYFLAT: size of background mesh for superflat
                    # illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?)
                    # 16 (or 32) if lots of blobs

FRINGE=FRINGE       # FRINGE if fringing correction necessary; NOFRINGE otherwise

if [ ${FRINGE} == "FRINGE" ]; then
    ending="OFCSF"
elif [ ${FRINGE} == "NOFRINGE" ]; then
    ending="OFCS"
else
    echo "You need to specify FRINGE or NOFRINGE for the fringing correction!"
    exit 2;
fi

##################################################################
### create and load the SUBARU.ini file
### !!! DO NOT COMMENT THIS BLOCK !!!
##################################################################

./setup_SUBARU.sh ${SUBARUDIR}/${run}_*/SCIENCE/ORIGINALS
export INSTRUMENT=SUBARU

##################################################################
# if needed: cp auxiliary data
##################################################################

#./cp_aux_data.sh ${SUBARUDIR} ${run}_${filter} ${SUBARUDIR}/auxiliary/${run}_${filter}/SCIENCE
#
###################################################################
## process the BIAS frames (per chip)
## only needs to be done once per run!
###################################################################
#
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_BIAS BIAS
#
#### first quality check: run  imstats  , if necessary, reject files:
# ./check_files.sh  ${SUBARUDIR}/${run}_BIAS BIAS "" 8000 12000
#
#### overscan-correct BIAS frames, OC+BIAS correct flats
#./parallel_manager.sh ./process_bias_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS
#
#
#
#####################################################################
## pre-processing of individual chips,
## per filter
#####################################################################
#
#
#### if necessary, rename the STANDARD directory
##mv ${SUBARUDIR}/${run}_${filter}/STANDARD_STAR ${SUBARUDIR}/${run}_${filter}/STANDARD
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
#
#### overscan+bias correct the FLAT fields
#./parallel_manager.sh ./process_flat_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT}
#
#### OC+flat SCIENCE frames, create superflat
#./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE NORESCALE ${FRINGE}
#
#### masking
#./maskBadOverscans.py ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA
#./maskAutotracker.py ${SUBARUDIR}/${run}_${filter} SCIENCE
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
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA ${ending} 8 -32
#
##### at this stage: inspect SCIENCE/BINNED frames; if necessary, reject individual frames (bright stars, etc.)
##### by listing them in file  superflat_exclusion
##### ---> repeat previous step
#
##### also at this stage: mask artefacts in individual frames: satellite tracks, etc.
##### transform ds9-region file into ww-readable file:
### ./transform_ds9_reg_alt.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
#
#./splitoff_aux_data.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending} ${SUBARUDIR}/SUBARU.list
#
#./parallel_manager.sh ./spikefinder_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA ${ending}
#
#### create weight images
#./parallel_manager.sh ./create_norm_para.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}
#./parallel_manager.sh ./create_norm_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
#./parallel_manager.sh ./create_global_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}_norm 0.6 1.3 BIAS -9 9 SCIENCE_norm 0.9 1.1

### create_global_weights_para.sh: first 2 numbers are acceptable range of pixels in normalized flat file. .6 - 1.3 includes corners (may cause problems in the future, just keep an eye out.   If you have a dark frame, substitue for BIAS.  basiaclly, tell it all things that you want to feed in to make global file with the acceptable ranges. first input forms the basis, any subsequent inputs just flag pixels

### note: I've modified create_global_weights_para.sh so that it looks for reg
### files in a reg-directory

#./parallel_manager.sh ./create_weights_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending}
### note: I've changed the saturation level to 30000 in weights.ww
### (was:62000)

#./parallel_manager.sh ./create_science_weighted.sh ${SUBARUDIR}/${run}_${filter} SCIENCE WEIGHTS ${ending}

#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} WEIGHTS SUPA ${ending}.weight 8 -32


################################################################################
### ignore for now
################################################################################

### process STANDARD frames  ---  ignore for now


#./parallel_manager.sh ./process_standard_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE STANDARD NORESCALE

#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} STANDARD SUPA OFC 8 -32

#./maskBadOverscans.py ${SUBARUDIR}/${run}_${filter} STANDARD SUPA
#./maskAutotracker.py ${SUBARUDIR}/${run}_${filter} STANDARD

#if [ ${FRINGE} == "NOFRINGE" ]; then
#  ./parallel_manager.sh ./create_illumfringe_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD
#  ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD RESCALE ILLUM
#else
#  ./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD 16
#  ./parallel_manager.sh ./process_science_illum_fringe_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD RESCALE
#fi

#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} STANDARD SUPA ${ending} 8 -32
#./parallel_manager.sh ./create_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${ending} WEIGHTS_FLAGS 
#./parallel_manager.sh ./create_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${ending} WEIGHTS_FLAGS 
#./parallel_manager.sh ./create_astrom_std_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD \
#    ${ending} default
##./create_abs_photo_info.sh ${MD} STANDARD_${FILTER} SCIENCE_${FILTER} \
##    OFCS${FRINGING} ${FILTER} ${FILTER} ${COLOR} ${EXT} ${COLCOEFF}
##./create_abs_photo_info.sh ${SUBARUDIR}/${run}_${filter} STANDARD SCIENCE \
##    ${ending} ${FILTER} ${FILTER} ${COLOR} ${EXT} ${COLCOEFF}

./create_abs_photo_info.sh ${SUBARUDIR}/${run}_${filter} STANDARD SCIENCE \
    ${ending} ${filter} I RmI -0.10 -0.11 #${COLCOEFF}
./create_zp_correct_header.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending}
exit 0
=======
#
<<<<<<< do_Subaru_2002_06_I.sh
#./parallel_manager.sh ./create_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${ending} WEIGHTS_FLAGS 
exit 0;
=======
#./parallel_manager.sh ./create_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${ending} WEIGHTS_FLAGS 
>>>>>>> 1.5
#
##./parallel_manager.sh ./create_astrom_std_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD \
##    ${ending} default
#
####./create_abs_photo_info.sh ${MD} STANDARD_${FILTER} SCIENCE_${FILTER} \
####    OFCS${FRINGING} ${FILTER} ${FILTER} ${COLOR} ${EXT} ${COLCOEFF}
####./create_abs_photo_info.sh ${SUBARUDIR}/${run}_${filter} STANDARD SCIENCE \
####    ${ending} ${FILTER} ${FILTER} ${COLOR} ${EXT} ${COLCOEFF}
##
##./create_abs_photo_info.sh ${SUBARUDIR}/${run}_${filter} STANDARD SCIENCE \
##    ${ending} ${filter} I RmI -0.10 ${COLCOEFF}
##exit 0;
##./create_zp_correct_header.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending}
##
##exit 0;

#################################################################################


#################################################################################
### set-specific processing
#################################################################################

###groups together cluster pointings from one run
./distribute_sets_subaru.sh ${SUBARUDIR} ${run}_${filter}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list


###  script for the coaddition:
###  do_Subaru_coadd_template.sh
