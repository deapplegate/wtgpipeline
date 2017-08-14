#!/bin/bash

# This script illustrates the basic usage of the THELI pipeline.
# The commands below process a WFI test data set from raw image
# to a final co-added image.

# It also serves an an example for possible 'superscripts'
# collecting various pipeline tasks.

# Note that the script does NOT react intelligently 
# on errors in one of the reduction steps!!!!

#
# Edit the following two lines to point to
# the MD of your data and your reduction directory:
export MD=/aibn85_d/terben/TESTDATA_MASTER
export REDDIR=/aibn85_d/terben/reduce

export INSTRUMENT=WFI
export FILTER=R

# Do astrometric calibration with SCAMP or ASTROMETRIX?
ASTROMMETHOD=ASTROMETRIX

ASTROMADD=""
if [ ${ASTROMMETHOD} = "SCAMP" ]
then
  ASTROMADD="_scamp"
fi
 
#
# split data and update headers
./process_split_WFI_eclipse.sh ${MD}/ BIAS
./process_split_WFI_eclipse.sh ${MD}/ DARK
./process_split_WFI_eclipse.sh ${MD}/ SKYFLAT_${FILTER}
./process_split_WFI_eclipse.sh ${MD}/ SCIENCE_${FILTER}
./process_split_WFI_eclipse.sh ${MD}/ STANDARD_${FILTER}
#
# Here you could do a first data checking and
# verify that the modes of raw images are within
# predefined values. A typical script call would look
# like:
# ./check_files.sh ${MD}/ SKYFLAT_${FILTER} 5000 40000
#
# we omit this step as the data were chosen to be good !!

# 
# Here, RUN processing is performed:
#
# process BIAS frames
./parallel_manager.sh ./process_bias_eclipse_para.sh ${MD}/ BIAS
#
# process DARK frames
./parallel_manager.sh ./process_bias_eclipse_para.sh ${MD}/ DARK
#
# process FLAT frames 
./parallel_manager.sh ./process_flat_eclipse_para.sh ${MD}/ BIAS SKYFLAT_${FILTER}
#
# process SCIENCE frames (flatfielding, superflatfielding, defringing)
./parallel_manager.sh ./process_science_eclipse_para.sh ${MD}/ BIAS SKYFLAT_${FILTER} \
                      SCIENCE_${FILTER} NORESCALE NOFRINGE
./parallel_manager.sh ./create_illumfringe_para.sh ${MD}/ SCIENCE_${FILTER}
./parallel_manager.sh ./process_science_illum_fringe_eclipse_para.sh ${MD}/ \
                      SCIENCE_${FILTER} RESCALE
#
# create postage stamps of SCIENCE images:
./create_binnedmosaics_WFI.sh ${MD} SCIENCE_${FILTER} WFI OFCSF 8 -32
#
# you should take a look at the created mosaics at this stage. Usually
# you would use them to identify whether preprocessing steps should
# be iterated or whether masks should be created (for instance to mark
# satellite tracks). For the example set the only necessary masks
# are WFI.2000-12-26T07:30:37.238_[1-4].reg. Make sure they are in the
# ${MD}/SCIENCE_${FILTER}/reg directory before proceeding.

#
# create weight frames
./parallel_manager.sh ./create_norm_para.sh ${MD} SKYFLAT_${FILTER}
./parallel_manager.sh ./create_norm_para.sh ${MD} SCIENCE_${FILTER}
./parallel_manager.sh ./create_global_weights_flags_para.sh ${MD} \
       SKYFLAT_${FILTER}_norm 0.7 1.3 DARK -9 9 SCIENCE_${FILTER}_norm 0.9 1.1
./parallel_manager.sh create_weights_para.sh ${MD} SCIENCE_${FILTER} OFCSF
#
# Photometric calibration
#
# first process standardstar frames in exactly the same way as the
# science observations.
./parallel_manager.sh ./process_standard_eclipse_para.sh ${MD} BIAS SKYFLAT_${FILTER} \
       SCIENCE_${FILTER} STANDARD_${FILTER} NORESCALE
./parallel_manager.sh ./create_illumfringe_para.sh ${MD} STANDARD_${FILTER}
./parallel_manager.sh ./process_science_illum_fringe_eclipse_para.sh ${MD} STANDARD_${FILTER} \
       RESCALE
#
# From the preprocessed images in ${MD}/STANDARD_${FILTER} you have to determine
# the absolute photometric calibration at this stage. Scripts to
# execute this task within the THELI pipeline will be released in a later
# version.....

#
# update headers with previously determined, photometric information.
./create_absphot_header.sh ${MD} SCIENCE_${FILTER} OFCSF 725 \
                           ${REDDIR}/night_725_R_result.asc 2
./create_absphot_header.sh ${MD} SCIENCE_${FILTER} OFCSF 726 \
                           ${REDDIR}/night_726_R_result.asc 2

#
# include the following calls if you checked your results up to now
# and if you want to clean up disk space
## ./cleanfiles.sh ${MD}/BIAS WFI "."
## ./cleanfiles.sh ${MD}/BIAS WFI "OC."
## ./cleanfiles.sh ${MD}/DARK WFI "."
## ./cleanfiles.sh ${MD}/DARK WFI "OC."
## ./cleanfiles.sh ${MD}/SKYFLAT_${FILTER} WFI "."
## ./cleanfiles.sh ${MD}/SKYFLAT_${FILTER} WFI "OC."
## ./cleanfiles.sh ${MD}/SCIENCE_${FILTER}/SPLIT_IMAGES WFI "."
## rmdir ${MD}/SCIENCE_${FILTER}/SPLIT_IMAGES
## ./cleanfiles.sh ${MD}/SCIENCE_${FILTER}/OFC_IMAGES WFI "OFC."
## rmdir ${MD}/SCIENCE_${FILTER}/OFC_IMAGES
## ./clesnfiles.sh ${MD}/SCIENCE_${FILTER}/SUB_IMAGES WFI "OFC_sub."
## rmdir ${MD}/SCIENCE_${FILTER}/SUB_IMAGES
## ./cleanfiles.sh ${MD}/STANDARD_${FILTER}/SPLIT_IMAGES WFI "."
## rmdir ${MD}/STANDARD_${FILTER}/SPLIT_IMAGES
## ./cleanfiles.sh ${MD}/STANDARD_${FILTER}/OFC_IMAGES WFI "OFC."
## rmdir ${MD}/STANDARD_${FILTER}/OFC_IMAGES

#
# sort the SCIENCE frames in different sets; here only a single set is present
# and all images are moved to ${MD}/set_1
./distribute_sets.sh ${MD} SCIENCE_${FILTER} OFCSF 1000

# 
# Here, SET processing is performed:
#
# create catalogues for astrometric and photometric calibration
./parallel_manager.sh ./create_astromcats_weights_para.sh ${MD} set_1 OFCSF WEIGHTS OFCSF.weight

if [ ${ASTROMMETHOD} != "SCAMP" ]
then
  #
  # run ASTROMETRIX and PHOTOMETRIX
  ./create_astrometrix_astrom.sh ${MD} set_1 OFCSF
  ./create_photometrix.sh ${MD} set_1 OFCSF
else
  # alternatively to the previous two scripts you
  # can perform astrometry/relative photometry with scamp.
  # In this case the following script call is necessary:
  ./create_scamp_astrom_photom.sh ${MD} set_1 OFCSF USNO-B1
fi

./create_stats_table.sh ${MD} set_1 OFCSF headers${ASTROMADD}
./create_absphotom_photometrix.sh ${MD} set_1
#
# create disgnostic plots
./make_checkplot_stats.sh ${MD} set_1 chips.cat5 STATS set_1

# subtract the sky from science images
./parallel_manager.sh ./create_skysub_para.sh ${MD} set_1 OFCSF "." ".sub."

# perform final image co-addition; if you want to use the experimental
# header update feature after co-addition (see below) you ALWAYS
# have to provide a coaddition condition (-l option) to the following
# script. 
./prepare_coadd_swarp.sh -m ${MD} -s set_1 -e "OFCSF.sub" -n TEST \
                                  -w ".sub" -eh headers${ASTROMADD} \
                                  -r 170.661597 -d -21.70969\
                                  -l ${MD}/set_1/cat/chips.cat5 STATS\
                                     "(SEEING<2.0);" \
                                     ${MD}/set_1/cat/TEST.cat
                                               
./parallel_manager.sh ./resample_coadd_swarp_para.sh ${MD} set_1 \
         "OFCSF.sub" TEST ${REDDIR}
./perform_coadd_swarp.sh ${MD} set_1 TEST

#
# HERE THE FORMAL RESPONSIBILITY OF THE PIPELINE ENDS
# THE STEPS DESCRIBED IN THE FOLLOWING ARE EXPERIMENTAL
# AND NOT YET CLEANLY IMPLEMENTED IN THE PIPELINE FLOW.

#
# update the header of the co-added image with information on
# total exposure time, effective gain, magnitude zeropoint information

#
# first get the magnitude zeropoint for the co-added image:
# {NOTE: some implementations of the 'tail' command do not
# support the '-n' option used in the following command; 
# the command is supposed to list the LAST line of the ldactoasc
# output; use the GNU version of 'tail' if you are in doubt whether 
# yours works fine)
if [ -f ${MD}/set_1/cat/chips_phot.cat5 ]; then
  MAGZP=`ldactoasc -i ${MD}/set_1/cat/chips_phot.cat5 -t ABSPHOTOM -k COADDZP | tail -n 1`
else
  MAGZP=-1.0  
fi
#
# now do the actual header update
./update_coadd_header.sh ${MD} set_1 TEST STATS coadd ${MAGZP} "(SEEING<2.0);" 
