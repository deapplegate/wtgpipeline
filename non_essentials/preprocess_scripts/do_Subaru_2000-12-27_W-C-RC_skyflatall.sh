#! /bin/bash -xv

### superscript template to do the preprocessing
### $Id: do_Subaru_2000-12-27_W-C-RC_skyflatall.sh,v 1.1 2010-02-04 19:55:00 anja Exp $

. progs.ini

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki05/anja/SUBARU

run=2000-12-27
filter="W-C-RC"

export BONN_TARGET=${run}
export BONN_FILTER=${filter}

FLAT=SKYFLATALL        # SKYFLAT or DOMEFLAT
SKYBACK=256          # in case of SKYFLAT: size of background mesh for superflat
                    # illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?)
                    # 16 (or 32) if lots of blobs

FRINGE=NOFRINGE       # FRINGE if fringing correction necessary; NOFRINGE otherwise
STANDARDSTARS=0     # process the STANDARD frames, too  (1 if yes; 0 if no)

SCIENCEDIR=SCIENCE_${FLAT}

if [ ${FRINGE} == "FRINGE" ]; then
    ending="OCFSF"
elif [ ${FRINGE} == "NOFRINGE" ]; then
    ending="OCFS"
else
    echo "You need to specify FRINGE or NOFRINGE for the fringing correction!"
    exit 2;
fi

### NOTES:
### I've checked the BIAS frames for the 2000-11, 2000-12, and 2001-01.
### There are differences between all three periods. This is most obvious
### in Chip 6, where the BIAS level can change by 300 counts (!!!).
### Differences in the other chips are less dramatic, but since they
### apparently changed the electronics, I feel it is safer not to
### mix runs.
### This makes the construction of a good FLAT very difficult. The
### SKYFLAT is of no use (6 frames).
### Even the 3 DOMEFLAT frames are crap (one very different).
### At least for R-band, I can try to construct a FLATfield from
### just the SCIENCE data

### datasets: 2000-12-27 ( 51 images)
###           2001-01-20 (169 images)
###           2001-02-20 (127 images)

### errrm, I didn't use the non-MACS 2000-12 observations???
### split things into two sets:
###           2001-01-20 (169 images)
###           2001-02-20 (127 images)
### and
###           2000-12-27 (118 images)
###           2000-11-?? ( 59 images)

### Main interests:
### MACS clusters  2000-12-27
### MS0451         2001-01-20
### HDF            2001-02-20

### BAD FLATS:
### 2001-02-20_W-C-RC  SKYFLAT

### 2000-11-24_W-C-RC/SKYFLAT    BAD
### 2001-03-17        SKYFLAT    maybe with some tweaking
### 2001-01-20_W-C-RC/DOMEFLAT   maybe with some tweaking
### 2001-01-20_W-C-RC/SKYFLAT    stars...

#Comment out the lines as you progress through the script

./BonnLogger.py clear

##################################################################
### create and load the SUBARU.ini file
### !!! DO NOT COMMENT THIS BLOCK !!!
##################################################################

#./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
./setup_SUBARU.sh ${SUBARUDIR}/${run}_BIAS/BIAS/ORIGINALS
export INSTRUMENT=SUBARU

. ${INSTRUMENT:?}.ini

###################################################################
## if needed: cp auxiliary data
###################################################################
#
##./cp_aux_data.sh ${SUBARUDIR} ${run}_BIAS ${SUBARUDIR}/auxiliary/${run}_BIAS
#./cp_aux_data.sh ${SUBARUDIR} ${run}_${filter} ${SUBARUDIR}/auxiliary/${run}_${filter}/SKYFLAT
#
###################################################################
## process the BIAS frames (per chip)
## only needs to be done once per run!
###################################################################

./BonnLogger.py clear
#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_BIAS BIAS

### first quality check: run  imstats  , if necessary, reject files:
##./check_files.sh  ${SUBARUDIR}/${run}_BIAS BIAS "" 0 10000
## overscan-correct BIAS frames, OC+BIAS correct flats

#./parallel_manager.sh ./process_bias_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS BIAS "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS SUP "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_BIAS BIAS SUP "OC" 8 -32

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

## copy the master BIAS
#mkdir ${SUBARUDIR}/${run}_${filter}/BIAS
#cp ${SUBARUDIR}/${run}_BIAS/BIAS/BIAS_*.fits ${SUBARUDIR}/${run}_${filter}/BIAS

### copy master DARK ###
#mkdir ${SUBARUDIR}/${run}_${filter}/DARK_master
#cp ${SUBARUDIR}/${INSTRUMENT}_${config}_DARK/DARK_master/DARK_master_*.fits ${SUBARUDIR}/${run}_${filter}/DARK_master

### overscan+bias correct the FLAT fields
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} SUP "" 8 -32

cd ${SUBARUDIR}/${run}_${filter}/${FLAT}
rm SUPA0004860_*.fits \
SUPA0004801_*.fits \
SUPA0004799_*.fits \
SUPA0004798_*.fits \
SUPA0004737_*.fits \
SUPA0004736_*.fits \
SUPA0004735_*.fits \
SUPA0004296_*.fits \
SUPA0004295_*.fits \
SUPA0004294_*.fits \
SUPA0003922_*.fits \
SUPA0003854_*.fits \
SUPA0003852_*.fits \
SUPA0003629_*.fits \
SUPA0003628_*.fits \
SUPA0003559_*.fits \
SUPA0003558_*.fits \
SUPA0003228_*.fits \
SUPA0003165_*.fits \
SUPA0003164_*.fits \
SUPA0003163_*.fits \
SUPA0002529_*.fits \
SUPA0002528_*.fits \
SUPA0002527_*.fits \
SUPA0002473_*.fits \
SUPA0002472_*.fits \
SUPA0002469_*.fits \
SUPA0002468_*.fits \
SUPA0002467_*.fits \
SUPA0002466_*.fits \
SUPA0002465_*.fits #\
#BADMODE

cd BINNED
rm SUPA0004860_*.fits \
SUPA0004801_*.fits \
SUPA0004799_*.fits \
SUPA0004798_*.fits \
SUPA0004737_*.fits \
SUPA0004736_*.fits \
SUPA0004735_*.fits \
SUPA0004296_*.fits \
SUPA0004295_*.fits \
SUPA0004294_*.fits \
SUPA0003922_*.fits \
SUPA0003854_*.fits \
SUPA0003852_*.fits \
SUPA0003629_*.fits \
SUPA0003628_*.fits \
SUPA0003559_*.fits \
SUPA0003558_*.fits \
SUPA0003228_*.fits \
SUPA0003165_*.fits \
SUPA0003164_*.fits \
SUPA0003163_*.fits \
SUPA0002529_*.fits \
SUPA0002528_*.fits \
SUPA0002527_*.fits \
SUPA0002473_*.fits \
SUPA0002472_*.fits \
SUPA0002469_*.fits \
SUPA0002468_*.fits \
SUPA0002467_*.fits \
SUPA0002466_*.fits \
SUPA0002465_*.fits #\
#BADMODE

cd ${REDDIR}

#./check_files.sh  ${SUBARUDIR}/${run}_${filter} ${FLAT} "" 10000 32000

###./parallel_manager.sh ./process_flat_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT}
#./parallel_manager.sh ./process_makeflat_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT}
#./create_binnedmosaics_empty.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} ${FLAT} "" 8 -32
#./create_binnedmosaics_empty.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} SUP "OC" 8 -32

ic -m 10000 '%1' ${SUBARUDIR}/${run}_${filter}/${FLAT}/${FLAT}_1.fits > ${SUBARUDIR}/${run}_${filter}/${FLAT}/blub.fits
mv ${SUBARUDIR}/${run}_${filter}/${FLAT}/blub.fits ${SUBARUDIR}/${run}_${filter}/${FLAT}/${FLAT}_1.fits

if [ ! -f ${SUBARUDIR}/${run}_${filter}/${FLAT}_${FLAT} ]; then
    mkdir ${SUBARUDIR}/${run}_${filter}/${FLAT}_${FLAT}
fi
#cp ${SUBARUDIR}/${run}_${filter}/${FLAT}/SUP*[0-9]OC.fits ${SUBARUDIR}/${run}_${filter}/TEST_${FLAT}/

#./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} TEST_${FLAT} RESCALE NOFRINGE
./parallel_manager.sh ./process_sub_images_para.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} ${FLAT} NOFRINGE

./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}_${FLAT} SUP OCF
rm  ${SUBARUDIR}/${run}_${filter}/${FLAT}_${FLAT}_norm/SUP*_1OCFN.fits
./create_binnedmosaics_empty.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}_${FLAT}_norm SUP "OCFN" 8 -32

exit 0;

if [ ${FLAT} == "FAKEFLAT" ]; then
    ./parallel_manager.sh ./create_fakeflat_para.sh ${SUBARUDIR}/${run}_${filter}
fi


##### OC SCIENCE frames
#./parallel_manager.sh prep_science_para.sh ${SUBARUDIR}/${run}_${filter} BIAS SCIENCE

#./test_run_prep.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} SCIENCE
#
###################################################################

./BonnLogger.py comment "A: Process Superflat"

### OCF SCIENCE frames + superflat (allows for easy tryout of diff flat fields)
if [ ! -d ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR ]; then
    mkdir ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR
fi
./parallel_manager.sh process_sub_images_para.sh ${SUBARUDIR}/${run}_${filter} ${FLAT} SCIENCE NOFRINGE

### A: PROCESS SUPERFLAT ###
./parallel_manager.sh process_superflat_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_${FLAT}

# Create Illum/Fringe Corrections
 ./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR ${SKYBACK}

#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "_fringe${SKYBACK}" 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR $SCIENCEDIR "_illum${SKYBACK}" 8 -32

./create_norm.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}
./create_norm_illum_fringe.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} $SKYBACK
./make_residuals.sh ${SUBARUDIR}/${run}_${filter} $SCIENCEDIR ${SKYBACK}
./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "" 8 -32
./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "_illum${SKYBACK}" 8 -32
./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm ${SCIENCEDIR} "_fringe${SKYBACK}" 8 -32

echo "Todo: Inspect SCIENCE/BINNED frames for bright stars, autotracker shadows, etc.
Create maindir/superflat_exclusion, which is a list of the SUPAxxx_CHIP frames to exclude. 
createExclusion.py may help in making the list."
echo "Goto A: Process SUPERFLAT"

echo "Finally, settle on a blasted Flat field, will you!?"

#exit 0;

# Apply Corrections to Science Data
if [ ${FRINGE} == "NOFRINGE" ]; then
  ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm RESCALE SUPER ${SKYBACK} ${SCIENCEDIR}
else
  ./parallel_manager.sh ./process_science_illum_fringe_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm RESCALE ${SKYBACK} ${SCIENCEDIR}
fi

sleep 60

./create_norm_many.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} SUP ${ending}

./create_binnedmosaics_empty.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm SUP ${ending}N 8 -32

exit 0;

##########################################################

./BonnLogger.py comment "Transfering Winning Flatfield"


cd ${SUBARUDIR}/${run}_${filter}/SCIENCE

### link science data back into SCIENCE
if [ ! -d OC_IMAGES ]; then
    mkdir OC_IMAGES
fi
mv SUPA*OC.fits OC_IMAGES/


ln -s ../$SCIENCEDIR/SUPA*${ending}.fits .

if [ ! -d ../${FLAT} ]; then
    mkdir ../${FLAT}
fi



for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
do

    rm SCIENCE_${CHIP}.fits
    rm SCIENCE_${CHIP}_illum.fits
    rm SCIENCE_${CHIP}_fringe.fits

    ln -s ../$SCIENCEDIR/${SCIENCEDIR}_${CHIP}.fits SCIENCE_${CHIP}.fits
    ln -s ../$SCIENCEDIR/${SCIENCEDIR}_${CHIP}_illum${SKYBACK}.fits SCIENCE_${CHIP}_illum.fits
    ln -s ../$SCIENCEDIR/${SCIENCEDIR}_${CHIP}_fringe${SKYBACK}.fits SCIENCE_${CHIP}_fringe.fits

#    ln -s ../${FLAT}_${SET}/${FLAT}_${SET}_${CHIP}.fits ../${FLAT}/${FLAT}_${CHIP}.fits

done

cd ${REDDIR}

### create normalized weight images

./create_norm.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
./create_norm_illum_fringe.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
./create_norm.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}

./create_globalweight_base.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}_norm SCIENCE_norm
########################################################


exit 0;



























###########  OLD SCRIPT VERSION ######################


####################################################################
#
### A: PROCESS SUPERFLAT ###

### OC+flat SCIENCE frames, create superflat
./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE NOFRINGE
./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUP OFC 8 -32


if [ ${FLAT} == "DOMEFLAT" ]; then
  ./parallel_manager.sh ./create_illumfringe_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
else
  ./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${SKYBACK}
fi

if [ ${FRINGE} == "NOFRINGE" ]; then
  ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE RESCALE ILLUM
else
  ./parallel_manager.sh ./process_science_illum_fringe_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE RESCALE
fi

./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SCIENCE "" 8 -32
./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SCIENCE "_fringe" 8 -32
./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SCIENCE "_illum" 8 -32
./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUP ${ending} 8 -32


echo "Todo: Inspect SCIENCE/BINNED frames for bright stars, autotracker shadows, etc.
Create maindir/superflat_exclusion, which is a list of the SUPAxxx_CHIP frames to exclude. 
createExclusion.py may help in making the list."
echo "Goto A: Process SUPERFLAT"

exit 0;

##########################################################

#### create normalized weight images
./create_norm.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}
./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${FLAT}_norm ${FLAT}_norm "" 8 -32
exit 0;
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

./splitoff_aux_data.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending} ${SUBARUDIR}/SUBARU.list

##########################################################

### Processing for each Ind Image ###


./maskBadOverscans.py ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA
./maskAutotracker.py ${SUBARUDIR}/${run}_${filter} SCIENCE
./parallel_manager.sh ./spikefinder_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA ${ending}

  #### transform ds9-region file into ww-readable file:
./convertBox2Poly.py ${SUBARUDIR}/${run}_${filter} SCIENCE
./transform_ds9_reg_alt.sh ${SUBARUDIR}/${run}_${filter} SCIENCE

### C: CHIP PROCESSING ###

if [ -d ${SUBARUDIR}/${run}_${filter}/SCIENCE_weighted ]; then
    ./convertBox2Poly.py ${SUBARUDIR}/${run}_${filter} SCIENCE_weighted
    ./transform_ds9_reg_alt.sh ${SUBARUDIR}/${run}_${filter} SCIENCE_weighted

    mkdir ${SUBARUDIR}/${run}_${filter}/SCIENCE/reg/OLD

    mv ${SUBARUDIR}/${run}_${filter}/SCIENCE/reg/*.reg ${SUBARUDIR}/${run}_${filter}/SCIENCE/reg/OLD

    cp ${SUBARUDIR}/${run}_${filter}/SCIENCE_weighted/reg/*.reg ${SUBARUDIR}/${run}_${filter}/SCIENCE/reg

    ./parallel_manager.sh ./create_weights_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending}
fi

./parallel_manager.sh ./create_weights_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending}
## note: I've changed the saturation level to 30000 in weights.ww
## (was:62000)

./parallel_manager.sh ./create_science_weighted.sh ${SUBARUDIR}/${run}_${filter} SCIENCE WEIGHTS ${ending}

./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} WEIGHTS SUPA ${ending}.weight 8 -32

echo "Todo: Mask images by hand for remaining defects (satelite trails, blobs, etc).
Use the images in SCIENCE_weighted for masking.
maskImages.pl may be useful for managing region files."
echo "Goto C: Chip Processing"

exit 0;


################################################################################
### STANDARD star processing
################################################################################

if [ ! -d  ${SUBARUDIR}/${run}_${filter}/STANDARD ] && [ ${STANDARDSTARS} -eq 1 ]; then

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
  
  ./parallel_manager.sh ./process_standard_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE STANDARD NORESCALE
  
  ./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} STANDARD SUPA OFC 8 -32
  
  ./maskBadOverscans.py ${SUBARUDIR}/${run}_${filter} STANDARD SUPA
  #./maskAutotracker.py ${SUBARUDIR}/${run}_${filter} STANDARD
  
  if [ ${FLAT} == "DOMEFLAT" ]; then
    ./parallel_manager.sh ./create_illumfringe_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD
  else
    ./parallel_manager.sh ./create_illumfringe_stars_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${SKYBACK}
  fi
  
  if [ ${FRINGE} == "NOFRINGE" ]; then
    ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD RESCALE ILLUM
  else
    ./parallel_manager.sh ./process_science_illum_fringe_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD RESCALE
  fi
  
  ./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} STANDARD SUPA ${ending} 8 -32
  
  ./parallel_manager.sh ./create_weights_flags_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD ${ending} WEIGHTS_FLAGS 
  
  ./parallel_manager.sh ./create_astrom_std_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD \
      ${ending} default
  
  ./create_abs_photo_info.sh ${SUBARUDIR}/${run}_${filter} STANDARD SCIENCE \
      ${ending} ${filter} ${photfilter} ${photcolor} ${EXTCOEFF} ${COLCOEFF}
  
  ./create_zp_correct_header.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending}

fi



#################################################################################
### set-specific processing
#################################################################################

###groups together cluster pointings from one run
./distribute_sets_subaru.sh ${SUBARUDIR} ${run}_${filter}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list


#################################################################################
###  script for the coaddition:
###  do_Subaru_coadd_template.sh
#################################################################################
