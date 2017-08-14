#! /bin/bash -xv
#adam-example# runs update_config_header.sh on all filter directories applying to a specific cluster
#adam-note# hi there
#adam-comments# runs update_config_header.sh on all filter directories applying to a specific cluster
#adam-use# runs update_config_header.sh on all filter directories applying to a specific cluster
. progs.ini
. bash_functions.include

export cluster=$1  # cluster nickname as in /nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
filter_run_pairs=$2
REDDIR=`pwd`
export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
export INSTRUMENT=SUBARU

for filter_run in ${filter_run_pairs[@]}
do
    ### FINAL LOOP | 1.) make regions compatible 2.) put them in flags/weights 3.) consolidate directories ###

    ########################
    ### Some Setup Stuff ###
    ########################
    export filter=`echo ${filter_run} | awk -F'_' '{print $1}'`
    export run=`echo ${filter_run} | awk -F'_' '{print $2}'`
    echo "run=" ${run}
    echo "filter=" ${filter}
    
    #########################################
    ### Consolidate into filter directory ###
    #########################################
    ./update_config_header.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE SUBARU ${cluster}
    
done
exit 0;
