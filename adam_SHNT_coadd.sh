#!/bin/bash
set -xv
## here is how I'm going to handle the 10_2 chip 6 mask now:
## rename 's/fits/fits\.old/g' /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-*[A-Z+]/WEIGHTS/SUPA00*_6OCF*.fits
## for fl in `\ls /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-*[A-Z+]/WEIGHTS/SUPA00*_6OCF*.fits.old` ; do newdir=`dirname ${fl}` ; newfl=`basename ${fl} .old` ; ic '%1 0 *' ${fl} > ${newdir}/${newfl} ; done
## for fl in `\ls /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-*[A-Z+]/WEIGHTS/SUPA00*_6OCF*I.fits.old` ; do newdir=`dirname ${fl}` ; newfl=`basename ${fl} .old` ; ic '%1 0 *' ${fl} > ${newdir}/${newfl} ; done
## rename 's/fits/fits\.old/g' /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-*[A-Z+]/WEIGHTS/SUPA00*_6OCF*I.weight.fits
## for fl in `\ls /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-S-I+/WEIGHTS/SUPA00*_6OCF*I.weight.fits.old` ; do newdir=`dirname ${fl}` ; newfl=`basename ${fl} .old` ; ic '%1 0 *' ${fl} > ${newdir}/${newfl} ; done

export cluster=Zw2089
export filter=W-C-RC
source deactivate
./do_coadd_batch.sh ${cluster} ${filter} "all exposure good" 2>&1 | tee -a OUT-do_coadd_batch-all_exposure-${cluster}_${filter}.log
./do_coadd_batch.sh ${cluster} "${filter}_2015-12-15_CALIB" "all 3s" 2>&1 | tee -a OUT-do_coadd_batch-all_exposure-${cluster}_${filter}_CALIB.log
export filter=W-J-V
./do_coadd_batch.sh ${cluster} ${filter} "all exposure good gabodsid" 2>&1 | tee -a OUT-do_coadd_batch-${cluster}_${filter}.log
exit 0;
export filter=W-S-I+
./do_coadd_batch.sh ${cluster} ${filter} "all exposure gabodsid" 'none' 'OCFSI' 2>&1 | tee -a OUT-do_coadd_batch-${cluster}_${filter}.log

##
SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
logdir=${SUBARUDIR}/coaddlogs
queue=long

export cluster=Zw2089
export filter=W-J-B
#jobid=${cluster}.${filter}
#bsub -W 7000 -q ${queue} -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} ${filter} "all exposure"
jobid="${cluster}.${filter}_2015-12-15_CALIB"
bsub -W 7000 -q ${queue} -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} "${filter}" "${modes}" "none" "OCFSI"
bsub -W 2000 -q ${queue} -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} "${filter}_2015-12-15_CALIB" "all exposure 3s"
export filter=W-S-Z+
#jobid=${cluster}.${filter}
#bsub -W 7000 -q ${queue} -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} ${filter} "all exposure"
jobid="${cluster}.${filter}_2015-12-15_CALIB"
bsub -W 2000 -q ${queue} -J ${jobid} -o ${logdir}/${jobid}.log -e ${logdir}/${jobid}.err ./do_coadd_batch.sh ${cluster} "${filter}_2015-12-15_CALIB" "all exposure 3s"

## RXJ2129
export cluster=RXJ2129
rm OUT-create_scamp_photom-end_no_overwrite_RXJ2129.log2
./create_scamp_photom-end_no_overwrite.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-J-B SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-J-V SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-C-RC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-S-I+ SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-S-Z+ SCIENCE  26000 SDSS-R6 2>&1 | tee -a OUT-create_scamp_photom-end_no_overwrite_RXJ2129.log2

## MACS0429-02
export cluster=MACS0429-02
./create_scamp_photom-end_no_overwrite.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B_2015-12-15_CALIB SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-V SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-V_2009-01-23_CALIB SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-RC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-RC_2009-01-23_CALIB SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-IC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-IC_2006-12-21_CALIB SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+ SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+_2015-12-15_CALIB SCIENCE 26000 PANSTARRS 2>&1 | tee -a OUT-create_scamp_photom-end_no_overwrite_MACS0429-02.log
./get_error_log.sh OUT-create_scamp_photom-end_no_overwrite_MACS0429-02.log

