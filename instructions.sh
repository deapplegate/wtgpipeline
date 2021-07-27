#! /bin/bash -xv
#adam-does# this code has the next steps (i.e. masking steps) for FF clusters
#adam-use# This is the one to use for MACS0416  and MACS1226 as of Oct 9th

#adam# steps to follow preprocessing: distributing sets and masking

#################### distribute_sets_subaru.sh ########################
#adam# set needed environment variables
export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
export ending="OCF"
export INSTRUMENT="SUBARU"
export run="2010-11-04"
export BONN_TARGET="2010-11-04"

#adam# pick the filter
#export filter="W-C-RC" # FLAT=SKYFLAT
#export BONN_FILTER="W-C-RC" # FLAT=SKYFLAT
#export filter="W-J-B" # FLAT=SKYFLAT
#export BONN_FILTER="W-J-B" # FLAT=SKYFLAT
#export filter="W-S-Z+" # FLAT=SKYFLAT
#export BONN_FILTER="W-S-Z+" # FLAT=SKYFLAT

#(1/4)= distribute_sets_subaru.sh
# copy / link images into cluster directories
#adam# this changes from run_filter directories to directories divided up by clusters
#adam# ending is OCF
#adam# SUBARU.list has list of clusters and positions
#adam# 1000 means within arcsecs of cluster coords?
#adam# this code moves run_filter to cluster/filter_run, copying over
#		SCIENCE/SUPA*_#OCF.fits
#		SCIENCE/SPLIT_IMAGES/SUPA*_#.fits
#		WEIGHTS/globalweight_#.fits
#		WEIGHTS/globalflags_#.fits

#./distribute_sets_subaru.sh ${SUBARUDIR} ${run}_${filter}/SCIENCE ${ending} 1000 /nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list 

##########################./do_masking.sh ${cluster} ${filters}##################
#MACS0416
export cluster=MACS0416-24
export filters=(W-C-RC_${run} W-J-B_${run} W-S-Z+_${run})

#MACS1226
export cluster=MACS1226+21

#both
export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
export ending="OCF"
export INSTRUMENT="SUBARU"
export BONN_TARGET=${cluster}
export BONN_FILTER=${filter}_${run}

# mask artefacts automatically:
#(2/4) & (4/4) re-run as last step = do_masking.sh
#do_masking (1/3)
#adam# spikefinder_para.sh finds saturation spikes, sattelites, and shadow from guider cam
#adam# made: SCIENCE/diffmask/, diffmask/SUPA0125903_10OCF.sf.fits
#adam# this takes ~20 min
#./parallel_manager.sh spikefinder_para.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE SUP ${ending} ${filter}
#exit 0;
#adam-check# make sure that there isn't anything masked that shouldn't be. If there is using spikefinder_para.sh, then use spikefinder_para_NOsh.sh
# 	spikefinder_para_NOsh.sh finds saturation spikes, sattelites, and DOES NOT LOOK FOR shadow from guider cam
# 	spikefinder_para.sh finds saturation spikes, sattelites, and shadow from guider cam
#adam# ds9 ${cluster}/${filter}_${run}/SCIENCE/SUPA*OCF.fits &
#adam# ds9 ${cluster}/${filter}_${run}/SCIENCE/diffmask/SUPA*OCF.sf.fits &

#NOW RUN CRNITSCHKE and make the weight files!
#do_masking (2/3)
#make actual weights from globalweights, diffmask, and the region files
./create_weights_raw_delink_para_CRNitschke_setup.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS ${filter}
./parallel_manager.sh create_weights_raw_delink_para_CRNitschke.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS ${filter}
#made: WEIGHTS/SUPA0100120_10OCF.flag.fits, WEIGHTS/SUPA0100120_10OCF.weight.fits 
#~/data/MACS0416-24/W-S-Z+_2010-11-04/WEIGHTS$ ds9 SUPA0125896_9OCF.weight.fits SUPA0125896_9OCF.flag.fits -regions load ../reg/SUPA0125896_9.reg &

exit 0;
#do_masking (3/3)
#adam# multiplies science by weights. these are only useful for looking at them to see which other things might need to be masked
./parallel_manager.sh create_science_weighted.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE WEIGHTS ${ending}
#made: SCIENCE_weighted/, SCIENCE_weighted/SUPA0100117_10OCF.weighted.fits
exit 0;

#(3/4)= manual masking
# add manual masks, e.g.
#adam# opens images, one after another so you can mask things by hand
#adam# maskImages.pl -d dir prefix
#adam# you have to open ds9 first! (ds9 &)
#adam# help menu: maskImages.pl -h
#ds9 &
#./maskImages.pl -r ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE/reg/ -d ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE_weighted/ SUP 
# OR
#./maskImages.pl -l july3Mask.list -r ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE/reg/ -d ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE_weighted/ SUP 
#adam# ./maskImages.pl -d /u/ki/awright/data/MACS0416-24/W-C-RC_2010-11-04/SCIENCE_weighted/ SUP

#adam# now change the regions I created to polygons
#./convertRegion2Poly.py ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE

#adam# now add these region masks to the weight/flag files
#./parallel_manager.sh add_regionmasks.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS ${filter} 2>&1 | tee -a OUT-add_regionmasks_${filter}_${cluster}_${run}.log

#adam# could re-do the science_weighted if I wanted to check out how they look
#./parallel_manager.sh create_science_weighted.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE WEIGHTS ${ending}

#adam-SKIPPED# don't worry about it
### might want to use  mark_badpixel_regions.pl  , too?
# rerun do_masking.sh
