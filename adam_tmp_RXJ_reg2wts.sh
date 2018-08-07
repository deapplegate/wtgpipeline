#! /bin/bash -xv
#adam-use# does 3 things, last is optional:
# 	1.) make regions compatible
# 	2.) put them in flags/weights
# 	3.) (OPTIONAL) redo coaddition! (don't have to redo astrom/photom usually, might want to redo science_weighted, maybe!)
#adam-example# ./adam_reg2weights_filter.sh "RXJ2129" "W-C-RC"
. progs.ini > /tmp/progs.out 2>&1
. bash_functions.include > /tmp/bash_functions.out 2>&1

export cluster=$1  # cluster nickname as in /nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
filters=$2
#adam-example#cluster=MACS0416-24
#adam-example#filter_run_pairs=(W-C-RC_2010-11-04 W-J-B_2010-11-04 W-S-Z+_2010-11-04)

REDDIR=`pwd`
lookupfile=/nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
export INSTRUMENT=SUBARU
filter_list=""
#counter=0
test -f /tmp/filter_list.log && rm -f /tmp/filter_list.log

for filter in ${filters}
do
    #counter=$(( $counter + 1 ))

    ########################
    ### Some Setup Stuff ###
    ########################
    export filter=`echo ${filter} | awk -F'_' '{print $1}'`
    echo "filter=" ${filter}
    testfile=`ls -1 ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/SUP*_2*IR.fits | awk 'NR>1{exit};1'`
    if [ -z ${testfile} ] ; then testfile=`ls -1 ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/SUP*_2*I.fits | awk 'NR>1{exit};1'` ; fi
    export ending=`basename ${testfile} | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`
    echo "ending=" ${ending}
    ./setup_SUBARU.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE
    . ${INSTRUMENT:?}.ini > /tmp/INSTRUMENT.log 2>&1
    export BONN_TARGET=${cluster} ; export BONN_FILTER=${filter}
    #filter_list="${filter_list} ${filter}"
    echo ${filter} >> /tmp/filter_list.log

    ###############################
    ### make regions compatible ###
    ###############################
    #adam# makes regions readable by rest of pipeline (include in final masking script).transform ds9-region file into ww-readable file:
    #adam# converts `box` regions to `polygon`
    ./convertRegion2Poly.py ${SUBARUDIR}/${cluster}/${filter} SCIENCE
    #adam# changes `polygon` to `POLYGON`!
    ./transform_ds9_reg_alt.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE
    #adam# deletes region files that are empty
    ./clean_empty_regionfiles.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/reg/*.reg

    ########################################
    ### put regions in weight/flag files ###
    ########################################
    #adam# now add these region masks to the weight/flag files
    ./parallel_manager.sh add_regionmasks.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} WEIGHTS ${filter} 2>&1 | tee -a OUT-add_regionmasks_${filter}_${cluster}.log

    ### optional thing here ### #adam# could re-do the science_weighted if I wanted to check out how they look
    ./parallel_manager.sh create_science_weighted.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE WEIGHTS ${ending} 2>&1 | tee -a OUT-create_science_weighted_${filter}_${cluster}.log

done

