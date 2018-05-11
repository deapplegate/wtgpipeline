#!/bin/bash -u
#################
# $Id: submit_coadd_batch3.sh,v 1.3 2010-07-20 19:46:21 dapple Exp $
#################
# Submits a cluster to the batch queue
#
# ./submit_coadd_batch.sh cluster "modes" filter1 filter 2 filter3

clustlist=cluster_cat_filters.dat

SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
logdir=${SUBARUDIR}/coaddlogs

cluster=$1
#modes=$2
rm adam_fgas_coadding_${cluster}.log*

queue="large"

filters=`grep ${cluster} ${clustlist} | awk '{for (i=3;i<=NF;i++) printf "%s ", $i}'`

echo "Cluster: ${cluster}"
echo "Filters: ${filters}"
#echo "Modes:   ${modes}"
echo "Queue:   ${queue}"

export cluster=${cluster}
for filter in ${filters}
do

if [[ ${filter} == *"_CALIB" ]]; then
	modes="all exposure 3s"
	time=1000
elif [[ ${filter} == "W-C-RC" ]]; then
	modes="all exposure good gabodsid"
	time=7000
elif [[ ${filter} == "W-J-V" ]]; then
	modes="all exposure good gabodsid"
	time=7000
elif [[ ${filter} == "W-S-I+" ]]; then
	modes="all exposure good gabodsid"
	time=7000
elif [[ ${filter} == "W-C-IC" ]]; then
	modes="all exposure good gabodsid"
	time=7000
else
	time=7000
	modes="all exposure gabodsid"
fi
#modestring=`echo ${modes} | sed -e 's/ /./g'`
#
#jobid=${cluster}.${filter}.${modestring}
jobid=${cluster}.${filter}

test -f ${logdir}/${jobid}.log && rm ${logdir}/${jobid}.log
test -f ${logdir}/${jobid}.err && rm ${logdir}/${jobid}.err

#adam-tmp# ./adam_pre_coadd_cleanup.sh ${cluster} ${filter}

#adam-old# bsub -W ${time} -q ${queue} -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} ${filter} "${modes}"
echo "${jobid}: ./do_coadd_batch.sh ${cluster} ${filter} ${modes}" >> adam_fgas_coadding_${cluster}.log
echo "bsub -W ${time} -m bulletfarm -q ${queue} -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} ${filter} \"${modes}\" 'none' \${ending} " >> adam_fgas_coadding_${cluster}.log3

done
##

exit 0;
filter="W-J-V"
jobid=${cluster}.${filter}
test -f ${logdir}/${jobid}.log && rm ${logdir}/${jobid}.log
test -f ${logdir}/${jobid}.err && rm ${logdir}/${jobid}.err
bsub -W ${time} -q ${queue} -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} ${filter} "${modes}"
filter="W-C-RC"
jobid=${cluster}.${filter}
test -f ${logdir}/${jobid}.log && rm ${logdir}/${jobid}.log
test -f ${logdir}/${jobid}.err && rm ${logdir}/${jobid}.err
bsub -W ${time} -q ${queue} -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} ${filter} "${modes}"
filter="W-C-IC"
jobid=${cluster}.${filter}
test -f ${logdir}/${jobid}.log && rm ${logdir}/${jobid}.log
test -f ${logdir}/${jobid}.err && rm ${logdir}/${jobid}.err
bsub -W ${time} -q ${queue} -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} ${filter} "${modes}"
