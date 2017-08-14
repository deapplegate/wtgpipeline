#!/bin/bash

#######
#
# (01/28/2015) adam: now uses the new subaru directory
# and saves output to ${jobid}_${i}.log rather than ${jobid}.log, so that it doesn't overwrite the output
#
#######

#subaru=/nfs/slac/g/ki/ki05/anja/SUBARU
subaru=/nfs/slac/g/ki/ki18/anja/SUBARU

cluster=$1
filter=$2
regdir=$3
ending=$4
queue=$5

logdir=${subaru}/coaddlogs
if [ ! -d ${logdir} ]; then 
   mkdir ${logdir}
fi
jobid=${cluster}.${filter}.suppress

    
for i in 1 2 3 4 5 6 7 8 9 10; do
    bsub -K -oo ${logdir}/${jobid}_${i}.log -eo ${logdir}/${jobid}_${i}.err -q ${queue} ./suppressreflections.py $regdir ${subaru}/${cluster}/${filter}/SCIENCE/*${i}${ending}.fits
done




