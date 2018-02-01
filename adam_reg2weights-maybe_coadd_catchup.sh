#! /bin/bash -xv
#adam-use# does 3 things, last is optional:
# 	1.) make regions compatible
# 	2.) put them in flags/weights
# 	3.) (OPTIONAL) redo coaddition! (don't have to redo astrom/photom usually, might want to redo science_weighted, maybe!)
#adam-example# ./adam_reg2weights-maybe_coadd_catchup.sh "MACS1226+21" "W-C-IC_2010-02-12 W-C-RC_2010-02-12 W-J-B_2010-02-12 W-J-V_2010-02-12 W-S-G+_2010-04-15 W-S-I+_2010-04-15 W-C-IC_2011-01-06 W-S-Z+_2011-01-06 W-C-RC_2006-03-04"
#adam-example# ./adam_reg2weights-maybe_coadd_catchup.sh $cluster $filter_runs
. progs.ini > /tmp/progs.out 2>&1
. bash_functions.include > /tmp/bash_functions.out 2>&1

export cluster=$1  # cluster nickname as in /nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
filter_run_pairs=$2
#adam-example#cluster=MACS0416-24
#adam-example#filter_run_pairs=(W-C-RC_2010-11-04 W-J-B_2010-11-04 W-S-Z+_2010-11-04)

REDDIR=`pwd`
lookupfile=/nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
export INSTRUMENT=SUBARU
filter_list=""
#counter=0
test -f /tmp/filter_list.log && rm -f /tmp/filter_list.log

for filter_run in ${filter_run_pairs[@]}
do
    #counter=$(( $counter + 1 ))

    ########################
    ### Some Setup Stuff ###
    ########################
    export filter=`echo ${filter_run} | awk -F'_' '{print $1}'`
    export run=`echo ${filter_run} | awk -F'_' '{print $2}'`
    echo "run=" ${run}
    echo "filter=" ${filter}
    testfile=`ls -1 ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE/SUP*_2*.fits | awk 'NR>1{exit};1'`
    export ending=`basename ${testfile} | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`
    echo "ending=" ${ending}
    ./setup_SUBARU.sh ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE
    . ${INSTRUMENT:?}.ini > /tmp/INSTRUMENT.log 2>&1
    export BONN_TARGET=${cluster} ; export BONN_FILTER=${filter}_${run}
    #filter_list="${filter_list} ${filter}"
    echo ${filter} >> /tmp/filter_list.log

    ###############################
    ### make regions compatible ###
    ###############################
    #adam# makes regions readable by rest of pipeline (include in final masking script).transform ds9-region file into ww-readable file:
    #adam# converts `box` regions to `polygon`
    ./convertRegion2Poly.py ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE
    #adam# changes `polygon` to `POLYGON`!
    ./transform_ds9_reg_alt.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE
    #adam# deletes region files that are empty
    ./clean_empty_regionfiles.sh ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE/reg/*.reg

    ########################################
    ### put regions in weight/flag files ###
    ########################################
    #adam# now add these region masks to the weight/flag files
    ./parallel_manager.sh add_regionmasks.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS ${filter} 2>&1 | tee -a OUT-add_regionmasks_${filter}_${cluster}_${run}.log

    ### optional thing here ### #adam# could re-do the science_weighted if I wanted to check out how they look
    #./parallel_manager.sh create_science_weighted.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE WEIGHTS ${ending} 2>&1 | tee -a OUT-create_science_weighted_${filter}_${cluster}_${run}.log

done

##########################################
### EVERYTHING BELOW HERE IS OPTIONAL! ###
##########################################

#echo ${filter_list} > /tmp/filter_list.log
uniq_filter_list=`cat /tmp/filter_list.log | uniq | paste -s -d\ `
echo "uniq_filter_list=" ${uniq_filter_list}
#./do_Subaru_register_4batch.sh ${cluster} "SDSS-R6" "astrom" ${uniq_filter_list} > do_Subaru_register_4batch_MACS1226+21_astrom.log 2>&1
# NOTE: should run IC here!
#./do_Subaru_register_4batch.sh ${cluster} "SDSS-R6" "photom" ${uniq_filter_list} > do_Subaru_register_4batch_MACS1226+21_photom.log 2>&1

#for filter_run in ${filter_run_pairs[@]}
#do
#
#    ########################
#    ### Some Setup Stuff ###
#    ########################
#    export filter=`echo ${filter_run} | awk -F'_' '{print $1}'`
#    export run=`echo ${filter_run} | awk -F'_' '{print $2}'`
#    echo "run=" ${run}
#    echo "filter=" ${filter}
#    testfile=`ls -1 ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE/SUP*_2*.fits | awk 'NR>1{exit};1'`
#    export ending=`basename ${testfile} | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`
#    echo "ending=" ${ending}
#    ./setup_SUBARU.sh ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE
#    . ${INSTRUMENT:?}.ini
#    export BONN_TARGET=${cluster} ; export BONN_FILTER=${filter}_${run}
#    #adam# might have to re-do the astrom/photom (but that's not a per-filter activity!)
#
#    #adam# redo the coaddition! (lensing filter only)
#    #./do_coadd_batch.sh ${cluster} ${filter} "all exposure good" 2>&1 | tee -a OUT-do_coadd_batch_${filter}_${cluster}_${run}.log
#    #adam# redo the coaddition! (non-lensing filters)
#    #./do_coadd_batch.sh ${cluster} ${filter} "all" 2>&1 | tee -a OUT-do_coadd_batch_${filter}_${cluster}_${run}.log
#
#done
exit 0;
