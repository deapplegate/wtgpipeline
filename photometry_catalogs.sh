#!/bin/bash -uxv
###############

##########
# Serves as a substitute for the first part of ./do_photometry.sh, to manage unstacked photometry catalog creation.
#############


cluster=$1
queue=$2


subarudir=/nfs/slac/g/ki/ki05/anja/SUBARU


./create_seeing_file.sh $cluster
exit_code=$?
if [ "${exit_code}" != "0" ]; then
    echo "Failure in do_photometry.sh!"
    exit 1
fi

filters=`cat seeing_${cluster}.cat | sed -e "s/${cluster}/cluster/g" | awk -F'cluster' '{print $2}' | awk -F'/' '{print $2}' | sort | uniq`


lensing_filter=`grep "${cluster}" ${subarudir}/lensing.bands | awk '(NR==1){print $2}'`
detection_image=${subarudir}/${cluster}/${lensing_filter}/SCIENCE/coadd_${cluster}_all/coadd.fits

    
for filter in $filters; do

    #temp cause K is a pain in the ass
    if [ "${filter}" == "K" ]; then
	continue
    fi

    jobid=${cluster}.${filter}.cats

    bsub -q ${queue} -o $subarudir/photlogs/$jobid.log -e $subarudir/photlogs/$jobid.err ./run_unstacked_photometry.sh $subarudir $cluster $filter $detection_image


done
    
