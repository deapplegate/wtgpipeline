#!/bin/bash -u
#################
# $Id: submit_photo_batch_coma.sh,v 1.1 2010-03-31 19:31:48 anja Exp $
#################
# Submits a cluster to the batch queue
#
# ./submit_photo_batch.sh cluster "modes" (3sec)



SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
logdir=${SUBARUDIR}/photologs

cluster=$1
modes=$2

program="./do_photometry.sh"
if [ $# -ge 3 ]; then
    program="./do_photometry_3sec.sh"
fi

queue=kipac-xocq

modestring=`echo ${modes} | sed -e 's/ /./g'`


jobid=${cluster}.${modestring}


bsub -K -q ${queue} -J ${jobid} -oo ${logdir}/${jobid}.log -eo ${logdir}/${jobid}.err ${program} ${cluster} ${modes}

