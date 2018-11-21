#!/bin/bash
set -xv


export cluster=MACS0429-02
export filter=W-J-B
export run=2015-12-15
export ending=OCF
#adam-example#./adam_do_fgas_automasking.sh MACS1115+01 "W-J-B_2010-03-12 W-S-Z+_2009-04-29 W-S-Z+_2010-03-12 W-C-RC_2010-03-12 W-J-B_2009-04-29"
#adam-does# Has 3 parts:
# 	#(1)# distributes sets, runs spikefinder, runs CRNitshke, creates weights
# 	#(2)# by-hand masking
# 	#(3)# incorporate regions into weights/flags and consolidate directories
#adam-call_example# 	./do_masking_master_adam.sh "MACS0416-24" "W-C-RC_2010-11-04 W-J-B_2010-11-04 W-S-Z+_2010-11-04"
# 	./adam_do_masking_master.sh "MACS1226+21" "W-C-IC_2010-02-12 W-C-IC_2011-01-06 W-C-RC_2006-03-04 W-C-RC_2010-02-12 W-J-B_2010-02-12 W-J-V_2010-02-12 W-S-G+_2010-04-15 W-S-I+_2010-04-15 W-S-Z+_2011-01-06"
# 	./adam_do_masking_master.sh "Zw2089" "W-J-V_2007-02-13 W-J-V_2010-12-05 W-S-I+_2009-03-28 W-J-V_2010-03-12 W-S-I+_2007-02-13"

. progs.ini  > /tmp/progs.ini.log 2>&1
. bash_functions.include  > /tmp/bash_functions.include.log 2>&1


export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU/
REDDIR=`pwd`
lookupfile=/nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
#adam# lookupfile (SUBARU.list) has list of clusters and positions
export INSTRUMENT=SUBARU

#./setup_SUBARU.sh ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE
. ${INSTRUMENT:?}.ini > /tmp/subaru_ini.log 2>&1

#./parallel_manager.sh spikefinder_para.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE SUP ${ending} ${filter}
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
    exit ${exit_stat};
fi

### RUN CRNITSCHKE and make the weight files ###
#adam# run CRNitschke and then make actual weight and flag fits files from globalweights, diffmask, and the region files
#adam# setup CRNitschke file makes the CRNitschke_final_${cluster}_${filter}_${run}.txt file with seeing, rms, and sextractor cut values needed for CRN pipeline
#./create_weights_raw_delink_para_CRNitschke_setup.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS 2>&1 | tee -a OUT-cwrdp_CRNitschke_setup_${cluster}_${filter}_${run}.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
    exit ${exit_stat};
fi
#adam# makes: actual weights from globalweights, diffmask, and the region files. Also, all of the CRNitschke pipeline output!
#adam# makes: ~/data/MACS0416-24/W-S-Z+_2010-11-04/WEIGHTS/SUPA0100120_10OCF.flag.fits and SUPA0100120_10OCF.weight.fits 
#./parallel_manager.sh ./create_weights_raw_delink_para_CRNitschke.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS 2>&1 | tee -a OUT-cwrdp_CRNitschke_${cluster}_${filter}_${run}.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
    exit ${exit_stat};
fi
#adam-check# ds9 ~/data/MACS0416-24/W-S-Z+_2010-11-04/SUPA0125896_9OCF.weight.fits ~/data/MACS0416-24/W-S-Z+_2010-11-04/SUPA0125896_9OCF.flag.fits -regions load ~/data/MACS0416-24/W-S-Z+_2010-11-04/SCIENCE/reg/SUPA0125896_9.reg &

#adam# multiplies science by weights. these are only useful for looking at them to see which other things might need to be masked
./parallel_manager.sh ./create_science_weighted.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE WEIGHTS ${ending} 2>&1 | tee -a OUT-create_science_weighted_${cluster}_${filter}_${run}.log2
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
    exit ${exit_stat};
fi
#adam# makes: SCIENCE_weighted/ directory and all of it's contents, such as ~/data/A2744/W-S-I+_2008-08-01/SCIENCE_weighted/SUPA0100117_10OCF.weighted.fits

###adam# masks the radial region surrounding the edges of the FOV of the image.
##./parallel_manager.sh ././science_weighted_apply_RADIAL_MASK_para.sh ${SUBARUDIR} ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE_weighted/ ${ending}

###adam-SKIPPED###
###adam# fixed issue with stars landing on overscan regions, which previously masked horizontal lines. (don't need unless you see this issue appearing in the new data)
#### run once, at end of first time through. Here, you'll be able to edit the region files, and adjust the masks.
###./maskBadOverscans.py ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE SUPA
###./create_binnedmosaics_empty.sh ${SUBARUDIR}/${cluster}/${filter}_${run} WEIGHTS SUP ${ending}.weight 8 -32
###./create_binnedmosaics_empty.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE_weighted SUP ${ending}.weighted 8 -32
./parallel_manager.sh ././science_weighted_apply_RADIAL_MASK_para.sh ${SUBARUDIR} ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE_weighted/ ${ending} 2>&1 | tee -a OUT-apply_Radial_science_weighted_${cluster}_${filter}_${run}.log
./create_binnedmosaics_empty.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE_weighted SUP ${ending}.weighted 8 -32  2>&1 | tee -a OUT-apply_Radial_science_weighted_${cluster}_${filter}_${run}.log

echo "Todo: Mask images by hand for remaining defects (satelite trails, blobs, etc).  Use the images in SCIENCE_weighted for masking.  maskImages.pl may be useful for managing region files."
echo "For Simplicity, make sure you save region files to SCIENCE/reg (use maskImages.pl -r)"
echo "adam-look: ./maskImages.pl -r ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE/reg/ -l toMask_${cluster}_${filter}_${run}-start.list -d ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE_weighted/ SUP"
echo "Once done with by-hand masking, Goto FINAL LOOP "

exit 0;
