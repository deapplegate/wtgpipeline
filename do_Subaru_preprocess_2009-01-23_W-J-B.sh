#! /bin/bash -xv

### superscript template to do the preprocessing
### $Id: do_Subaru_preprocess_2009-01-23_W-J-B.sh,v 1.3 2010-02-02 23:04:24 dapple Exp $


. progs.ini

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki05/anja/SUBARU

run=2009-01-23
filter="W-J-B"

export BONN_TARGET=${run}
export BONN_FILTER=${filter}

FLAT=DOMEFLAT        # SKYFLAT or DOMEFLAT
SET=SET1            # sets time period of flat to use
SKYBACK=256          # in case of SKYFLAT: size of background mesh for superflat
                    # illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?)
                    # 16 (or 32) if lots of blobs

FRINGE=NOFRINGE       # FRINGE if fringing correction necessary; NOFRINGE otherwise
STANDARDSTARS=1     # process the STANDARD frames, too  (1 if yes; 0 if no)

if [ ${FRINGE} == "FRINGE" ]; then
    ending="OCFSF"
elif [ ${FRINGE} == "NOFRINGE" ]; then
    ending="OCFS"
else
    echo "You need to specify FRINGE or NOFRINGE for the fringing correction!"
    exit 2;
fi

SCIENCEDIR=SCIENCE_${FLAT}

# New CCDs, new luck...
# The new CCDs are read out via four ports. The resulting image
# comes in four long, narrow stripes, with the overscan region
# between the physical chip area. (Whoever came up with this?)
# The four "channels" have slightly different gains, too...
# For now, I'll take approach of splitting by channel for the
# BIAS correction, and then piecing back together the physical
# chips - otherwise, background fitting and the astrometric
# solution will be compromised.
# If this does not work, I will need to consider the different
# channels to be discrete chips...

# The CCDs show an extreme susceptibility to cosmic rays. For
# simple color images, this should be ok, it just means we really
# have to do a MEDIAN coaddition.
# If we ever have to do lensing with these (where we want a
# weighted mean coaddtion), we will need to consider training
# Eye for these.
# Right now, I don't know how the cosmics will affect the 3s
# exposures...
# Also, some chips exhibit CTE problems, although on a very
# low level.

# There are no flatfields for the 3s-only exposures...
# I will try with the flats from the other bands.

#export TEMPDIR='.'
#Comment out the lines as you progress through the script



########################################
### Reset Logger
./BonnLogger.py clear

##################################################################
# if needed: cp auxiliary data
##################################################################

#./cp_aux_data.sh ${SUBARUDIR} ${SUBARUDIR}/${run}_RAWDATA

##################################################################
### create and load the SUBARU.ini file
### !!! DO NOT COMMENT THIS BLOCK !!!
##################################################################

./setup_SUBARU.sh ${SUBARUDIR}/${run}_RAWDATA
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
#
./BonnLogger.py clear
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_BIAS BIAS
#
### first quality check: run  imstats  , if necessary, reject files:
##./check_files.sh  ${SUBARUDIR}/${run}_BIAS BIAS "" 0 10000

## overscan-correct BIAS frames, OC+BIAS correct flats
#./parallel_manager.sh ./process_bias_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS
##./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS BIAS "" 8 -32
###./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS SUP "" 8 -32
##./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS SUP "OC" 8 -32

####################################################################
# pre-processing of individual chips,
# per filter
####################################################################

###### if necessary, rename the STANDARD directory
#if [ -d ${SUBARUDIR}/${run}_${filter}/STANDARD_STAR ]; then
#    mv ${SUBARUDIR}/${run}_${filter}/STANDARD_STAR ${SUBARUDIR}/${run}_${filter}/STANDARD
#fi
##
##### re-split the files, overwrite headers
##
##./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}
##./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} STANDARD
##
### copy the master BIAS
#if [ ! -d ${SUBARUDIR}/${run}_${filter}/BIAS ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/BIAS
#    cp ${SUBARUDIR}/${run}_BIAS/BIAS/BIAS_*.fits ${SUBARUDIR}/${run}_${filter}/BIAS
#fi

##### copy master DARK ###
##if [ ! -d ${SUBARUDIR}/${run}_${filter}/DARK_master ]; then
##    mkdir ${SUBARUDIR}/${run}_${filter}/DARK_master
##fi
##ln -s ${SUBARUDIR}/${INSTRUMENT}_${config}_DARK/DARK_master/DARK_master_*.fits ${SUBARUDIR}/${run}_${filter}/DARK_master
#
#
#### overscan+bias correct the FLAT fields
#
###./check_files_1chip.sh  ${SUBARUDIR}/${run}_${filter} ${FLAT} "" 10000 32000 2
#
#./parallel_manager.sh ./process_flat_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT}
#
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} ${FLAT} "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} SUP "OC" 8 -32
#
#if [ ! -f ${SUBARUDIR}/${run}_${filter}/TEST_${FLAT} ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/TEST_${FLAT}
#fi
#cp ${SUBARUDIR}/${run}_${filter}/${FLAT}/SUP*[0-9].fits ${SUBARUDIR}/${run}_${filter}/TEST_${FLAT}/
#
#./parallel_manager.sh ./process_science_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} TEST_${FLAT} RESCALE NOFRINGE
#sleep 60
#
#./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} TEST_${FLAT} SUP OCF
#
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} TEST_${FLAT}_norm SUP "OCFN" 8 -32
#
#exit 0;
#
#
#
#
#### OC SCIENCE frames
#./parallel_manager.sh ./prep_science_4channels_para.sh ${SUBARUDIR}/${run}_${filter} BIAS SCIENCE
#exit 0;
#./test_run_prep.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} SCIENCE
#
####################################################################
#
#./BonnLogger.py comment "A: Process Superflat"
#
#### OCF SCIENCE frames + superflat (allows for easy tryout of diff flat fields)
#if [ ! -d ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR
#fi
#./parallel_manager.sh process_sub_images_para.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} SCIENCE NOFRINGE
#
#### A: PROCESS SUPERFLAT ###
#./parallel_manager.sh process_superflat_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_${FLAT}
#
### Create Illum/Fringe Corrections
# ./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR ${SKYBACK}
#
#
##./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "" 8 -32
##./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "_fringe${SKYBACK}" 8 -32
##./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "_illum${SKYBACK}" 8 -32
#
#
#./create_norm.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}
#./create_norm_illum_fringe.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} $SKYBACK
#./make_residuals.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR ${SKYBACK}
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "_illum${SKYBACK}" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "_fringe${SKYBACK}" 8 -32
#
#./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} SUP OCF
#./create_binnedmosaics_empty.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm SUP OCFN 8 -32
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
#
#sleep 60
#
#./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} SUP ${ending}
#
#./create_binnedmosaics_empty.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm SUP ${ending}N 8 -32
#
#
#exit 0;
#
###########################################################

###########################################################
#
#./BonnLogger.py comment "Transfering Winning Flatfield"
#
#
#cd ${SUBARUDIR}/${run}_${filter}/SCIENCE
#
#### link science data back into SCIENCE
#if [ ! -d OC_IMAGES ]; then
#    mkdir OC_IMAGES
#fi
#mv SUPA*OC.fits OC_IMAGES/
#
#
#ln -s ../$SCIENCEDIR/SUPA*${ending}.fits .
#
#if [ ! -d ../${FLAT} ]; then
#    mkdir ../${FLAT}
#fi
#
#
#
#for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
#do
#
#    rm SCIENCE_${CHIP}.fits
#    rm SCIENCE_${CHIP}_illum.fits
#    rm SCIENCE_${CHIP}_fringe.fits
#
#    ln -s ../$SCIENCEDIR/${SCIENCEDIR}_${CHIP}.fits SCIENCE_${CHIP}.fits
#    ln -s ../$SCIENCEDIR/${SCIENCEDIR}_${CHIP}_illum${SKYBACK}.fits SCIENCE_${CHIP}_illum.fits
#    ln -s ../$SCIENCEDIR/${SCIENCEDIR}_${CHIP}_fringe${SKYBACK}.fits SCIENCE_${CHIP}_fringe.fits
#
#done
#
#cd ${REDDIR}
#
#### create normalized weight images
#
#./create_norm.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
#./create_norm_illum_fringe.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
#./create_norm.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}
#
#./create_globalweight_base.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}_norm SCIENCE_norm
##########################################################
#exit 0;

#### B: GLOBAL WEIGHT CREATION ###
#./BonnLogger.py comment "B: Global Weight Creation"
#
#if [ ! -d ${SUBARUDIR}/${run}_${filter}/SCIENCE_FRINGE ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/SCIENCE_FRINGE
#fi
#
#cd ${SUBARUDIR}/${run}_${filter}
#for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
#do
#    ln -s ../SCIENCE_norm/SCIENCE_norm_${CHIP}_fringe.fits SCIENCE_FRINGE/SCIENCE_FRINGE_${CHIP}.fits
#done
#cd ${REDDIR}
#
#if [ ! -d ${SUBARUDIR}/${run}_${filter}/reg ]; then
#    mkdir ${SUBARUDIR}/${run}_${filter}/reg
#fi
#
#for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
#do
#    if [ -e ${SUBARUDIR}/${run}_${filter}/reg/globalweight_${CHIP}.reg ]; then
#	cp ${SUBARUDIR}/${run}_${filter}/reg/globalweight_${CHIP}.reg ${SUBARUDIR}/${run}_${filter}/reg/SUBARU_${CHIP}.reg
#    fi
#done
#
#./convertRegion2Poly.py ${SUBARUDIR} ${run}_${filter}
#./transform_ds9_reg_alt.sh ${SUBARUDIR} ${run}_${filter}
#
######Create Masks from SCIENCE images### 
##for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
##do
##    cp ${SUBARUDIR}/${run}_${filter}/SCIENCE_weighted/SCIENCE_${CHIP}.weighted.imask ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}.imask
##done
##
##./create_badpixel_mask.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
##
#### create_global_weights_para.sh: first 2 numbers are acceptable range of pixels in normalized flat file. .6 - 1.3 includes corners (may cause problems in the future, just keep an eye out.   If you have a dark frame, substitue for BIAS.  basiaclly, tell it all things that you want to feed in to make global file with the acceptable ranges. first input forms the basis, any subsequent inputs just flag pixels
#
#./parallel_manager.sh ./create_global_weights_flags_para.sh \
#	${SUBARUDIR}/${run}_${filter} \
#        BASE_WEIGHT 0.4 1.1 \
#        BIAS -3 4 \
#	SCIENCE_FRINGE -0.03 0.03
#
#exit 0;
#
#./create_global_science_weighted.sh ${SUBARUDIR}/${run}_${filter} SCIENCE WEIGHTS
#
#echo "Todo: Mask SCIENCE Flats for dust grains, missed hot pixels, etc.
#Use the images in the SCIENCE_weighted directory for masking.
#Region files should be saved in $maindir/reg.
#For precision masking, using mark_badpixel_regions.pl."
#echo "Goto B: Global Weight Creation"


##########################################################



#./splitoff_aux_data.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending} ${SUBARUDIR}/SUBARU.list


##########################################################


###groups together cluster pointings from one run
#./distribute_sets_subaru.sh ${SUBARUDIR} ${run}_${filter}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list

### note: this script now also copies globalweight*.fits and globalflag*fits
### to ${SUBARUDIR}/${cluster}/${filter}/WEIGHTS


####################################
##CHECKPOINT
####################################

#./BonnLogger.py checkpoint Preprocess

#exit 0;


################################################################################
### STANDARD star processing
################################################################################


if [ -d  ${SUBARUDIR}/${run}_${filter}/STANDARD ] && [ ${STANDARDSTARS} -eq 1 ]; then

    ./BonnLogger.py comment "STANDARD star processing"

  case ${filter} in
      "W-J-B" )
  	photfilter=B          # corresponding Johnson filter
  	photcolor=BmV         # color to use
  	EXTCOEFF=-0.2104      # guess for the extinction coefficient
  	COLCOEFF=0.0          # guess for the color coefficient
  	;;
      "W-J-V" )
  	photfilter=V
  	photcolor=VmR
  	EXTCOEFF=-0.1202
  	COLCOEFF=0.0
  	;;
      "W-C-RC" )
  	photfilter=R
  	photcolor=VmR
  	EXTCOEFF=-0.0925
  	COLCOEFF=0.0
  	;;
      "W-C-IC" | "W-S-I+" )
  	photfilter=I
  	photcolor=RmI
  	EXTCOEFF=-0.02728
  	COLCOEFF=0.0
  	;;
      "W-S-Z+" )
  	photfilter=I
  	photcolor=RmI
  	EXTCOEFF=0.0
  	COLCOEFF=0.0
  	;;
  esac

  
  ./BonnLogger.py config \
      photfilter=${photfilter} \
      photcolor=${photcolor} \
      EXTCOEFF=${EXTCOEFF} \
      COLCOEFF=${COLCOEFF}
  
  
# ./parallel_manager.sh ./process_standard_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT}_norm STANDARD RESCALE

  ./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} STANDARD SUP OCF 8 -32

  if [ ${FRINGE} == "NOFRINGE" ]; then
    ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_norm RESCALE ILLUM '' STANDARD
  else
    ./parallel_manager.sh ./process_science_illum_fringe_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_norm RESCALE '' STANDARD
  fi
  
  ./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} STANDARD SUP ${ending} 8 -32
exit 0;  
  ./parallel_manager.sh ./create_weights_raw_delink_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${ending} WEIGHTS

  ./distribute_standards_subaru.sh ${SUBARUDIR} ${run}_${filter}/STANDARD ${ending} 1000 ${SUBARUDIR}/SUBARU.list

#TO BE REPLACED 9/3/2008
#  
#  ./parallel_manager.sh ./create_astrom_std_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${ending} default
#  
#  ./create_abs_photo_info.sh ${SUBARUDIR}/${run}_${filter} STANDARD SCIENCE \
#      ${ending} ${filter} ${photfilter} ${photcolor} ${EXTCOEFF} ${COLCOEFF}
#  
#  ./create_zp_correct_header.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending}
#

  
   ####################################
   ##CHECKPOINT 
   ####################################

#  ./BonnLogger.py checkpoint Photometry


fi


