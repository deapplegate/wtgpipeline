#! /bin/bash
set -xv
#adam-example#./adam_do_fgas_automasking.sh MACS1115+01 "W-J-B_2010-03-12 W-S-Z+_2009-04-29 W-S-Z+_2010-03-12 W-C-RC_2010-03-12 W-J-B_2009-04-29"
#adam-does# Has 3 parts:
# 	#(1)# distributes sets, runs spikefinder, runs CRNitshke, creates weights
# 	#(2)# by-hand masking
# 	#(3)# incorporate regions into weights/flags and consolidate directories
#adam-call_example# 	./do_masking_master_adam.sh "MACS0416-24" "W-C-RC_2010-11-04 W-J-B_2010-11-04 W-S-Z+_2010-11-04"
# 	./adam_do_masking_master.sh "MACS1226+21" "W-C-IC_2010-02-12 W-C-IC_2011-01-06 W-C-RC_2006-03-04 W-C-RC_2010-02-12 W-J-B_2010-02-12 W-J-V_2010-02-12 W-S-G+_2010-04-15 W-S-I+_2010-04-15 W-S-Z+_2011-01-06"
# 	./adam_do_masking_master.sh "Zw2089" "W-J-V_2007-02-13 W-J-V_2010-12-05 W-S-I+_2009-03-28 W-J-V_2010-03-12 W-S-I+_2007-02-13"

### script to run the steps for masking image sets
### 
### this used to be the first part of the do_Subaru_coadd_template scripts;
### is now disjunct
###
### $Id: do_masking.sh,v 1.3 2010-10-05 22:27:58 dapple Exp $

. progs.ini  > /tmp/progs.ini.log 2>&1
. bash_functions.include  > /tmp/bash_functions.include.log 2>&1

export cluster=MACS1115+01

REDDIR=`pwd`
lookupfile=/nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
#adam# lookupfile (SUBARU.list) has list of clusters and positions
export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
export INSTRUMENT=SUBARU

#adam# pick the ending, filter, and run
#adam-call_example#export ending="OCF" #gets this itself later on
#adam-call_example#export run="2010-11-04"
#adam-call_example#export filter="W-C-RC" #export filter="W-J-B" #export filter="W-S-Z+"

#####################################################################################################
#####################################################################################################
### #(1)# STARTING LOOP #(1)# distributes sets, runs spikefinder, runs CRNitshke, creates weights ###
#####################################################################################################
#####################################################################################################


filter_run=W-J-B_2009-04-29
########################
### Some Setup Stuff ###
########################
export filter=`echo ${filter_run} | awk -F'_' '{print $1}'`
export run=`echo ${filter_run} | awk -F'_' '{print $2}'`
echo "run=" ${run}
echo "filter=" ${filter}
export pprun="${run}_${filter}"
export ending=`grep "$pprun" ~/bonnpipeline/fgas_pprun_endings.txt | awk '{print $2}'`
echo "ending=" ${ending}

###./BonnLogger.py clear
###export BONN_FILTER=${filter}; export BONN_TARGET=${run}
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
./parallel_manager.sh ./create_science_weighted.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE WEIGHTS ${ending}
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
    exit ${exit_stat};
fi
#adam# makes: SCIENCE_weighted/ directory and all of it's contents, such as ~/data/A2744/W-S-I+_2008-08-01/SCIENCE_weighted/SUPA0100117_10OCF.weighted.fits

###adam# masks the radial region surrounding the edges of the FOV of the image.
##./parallel_manager.sh ./adam_apply_RADIAL_MASK_para.sh ${SUBARUDIR} ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE/ ${SUBARUDIR}/${cluster}/${filter}_${run}/WEIGHTS/ ${ending}

###adam-SKIPPED###
###adam# fixed issue with stars landing on overscan regions, which previously masked horizontal lines. (don't need unless you see this issue appearing in the new data)
#### run once, at end of first time through. Here, you'll be able to edit the region files, and adjust the masks.
###./maskBadOverscans.py ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE SUPA
###./create_binnedmosaics_empty.sh ${SUBARUDIR}/${cluster}/${filter}_${run} WEIGHTS SUP ${ending}.weight 8 -32
###./create_binnedmosaics_empty.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE_weighted SUP ${ending}.weighted 8 -32

echo "Todo: Mask images by hand for remaining defects (satelite trails, blobs, etc).  Use the images in SCIENCE_weighted for masking.  maskImages.pl may be useful for managing region files."
echo "For Simplicity, make sure you save region files to SCIENCE/reg (use maskImages.pl -r)"
echo "./maskImages.pl -r ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE/reg/ -l toMask_${cluster}_${filter}_${run}-start.list -d ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE_weighted/ SUP"
echo "Once done with by-hand masking, Goto FINAL LOOP "

exit 0;
