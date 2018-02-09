#! /bin/bash -xv
#adam-does# consolidate directories
#adam-call_example# 	./adam_do_linking_filter_dirs.sh "MACS0416-24" "W-C-RC_2010-11-04 W-J-B_2010-11-04 W-S-Z+_2010-11-04"
# 	./adam_do_linking_filter_dirs.sh "MACS1226+21" "W-C-IC_2010-02-12 W-C-IC_2011-01-06 W-C-RC_2006-03-04 W-C-RC_2010-02-12 W-J-B_2010-02-12 W-J-V_2010-02-12 W-S-G+_2010-04-15 W-S-I+_2010-04-15 W-S-Z+_2011-01-06"

. progs.ini
. bash_functions.include

export cluster=$1  # cluster nickname as in /nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
filter_run_pairs=$2
#adam-call_example#cluster=MACS0416-24
#adam-call_example#filter_run_pairs=(W-C-RC_2010-11-04 W-J-B_2010-11-04 W-S-Z+_2010-11-04)

REDDIR=`pwd`
lookupfile=/nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
#adam# lookupfile (SUBARU.list) has list of clusters and positions
export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU/
export INSTRUMENT=SUBARU

for filter_run in ${!#}
do
    ### FINAL LOOP | 1.) make regions compatible 2.) put them in flags/weights 3.) consolidate directories ###

    ########################
    ### Some Setup Stuff ###
    ########################
    export filter=`echo ${filter_run} | awk -F'_' '{print $1}'`
    export run=`echo ${filter_run} | awk -F'_' '{print $2}'`
    echo "run=" ${run}
    echo "filter=" ${filter}
    #Find Ending
    testfile=`ls -1 ${SUBARUDIR}/${cluster}/${filter}_${run}/SCIENCE/SUP*_2*.fits | awk 'NR>1{exit};1'`
    export ending=`basename ${testfile} | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`
    echo "ending=" ${ending}
    
    #########################################
    ### Consolidate into filter directory ###
    #########################################
    if [ ! -d ${SUBARUDIR}/${cluster}/${filter} ]; then
        mkdir ${SUBARUDIR}/${cluster}/${filter}
        mkdir ${SUBARUDIR}/${cluster}/${filter}/SCIENCE
        mkdir ${SUBARUDIR}/${cluster}/${filter}/WEIGHTS
    fi
    cd ${SUBARUDIR}/${cluster}/${filter}/SCIENCE
    ln -s ../../${filter}_${run}/SCIENCE/SUP*fits .
    cd ${SUBARUDIR}/${cluster}/${filter}/WEIGHTS
    ln -s ../../${filter}_${run}/WEIGHTS/SUP*fits .
    cd ${REDDIR}
    
done
exit 0;
