#!/bin/bash -u
#################
# $Id: submit_photo_batch.sh,v 1.2 2010-01-15 19:17:13 dapple Exp $
#################
# Submits a cluster to the batch queue
#
# ./submit_photo_batch.sh cluster "modes" (3sec)



SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
logdir=${SUBARUDIR}/photologs

cluster=$1
modes=$2

program="./do_photometry.sh"
if [ $# -ge 3 ]; then
    program="./do_photometry_3sec.sh"
fi

queue=xlong

modestring=`echo ${modes} | sed -e 's/ /./g'`


jobid=${cluster}.${modestring}


bsub -R '!bali && linux64 && rhel50' -q ${queue} -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ${program} ${cluster} ${modes}

