#${prefix}!/bin/bash
#adam-example# ./batch_suppress.sh ${cluster} ${filter} ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/autosuppression $ending $queue
#queue=medium
#adam-example# ./batch_suppress.sh ${cluster} ${filter} ~/my_data/SUBARU/Zw2089/W-J-V/SCIENCE/autosuppression ${ending} 'medium'

#######
#
# (01/28/2015) adam: now uses the new subaru directory
# and saves output to ${jobid}_${i}.log rather than ${jobid}.log, so that it doesn't overwrite the output
#
#######

#subaru=/u/ki/awright/data
#subaru=/gpfs/slac/kipac/fs1/u/awright/SUBARU
subaru=/gpfs/slac/kipac/fs1/u/awright/SUBARU/

cluster=$1
filter=$2
regdir=$3
ending=$4
queue=$5

prefix="SUPA003"
logdir=${subaru}/coaddlogs
if [ ! -d ${logdir} ]; then 
   mkdir ${logdir}
fi
jobid=${cluster}.${filter}.suppress

    
for i in 1 2 3 4 5 6 7 8 9 10; do

    bsub -m bulletfarm -W 40 -K -oo ${logdir}/${jobid}_${i}.log -eo ${logdir}/${jobid}_${i}.err -q ${queue} ./suppressreflections.py $regdir ${subaru}/${cluster}/${filter}/SCIENCE/${prefix}*${i}${ending}.fits
done
