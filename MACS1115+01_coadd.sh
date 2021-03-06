#!/bin/bash
set -xv

export cluster='MACS1115+01'
export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU/ ; export INSTRUMENT=SUBARU
#mkdir /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS1115+01/
export filter='W-C-RC'
./adam_pre_coadd_cleanup.sh MACS1115+01 W-C-RC
./do_coadd_batch.sh MACS1115+01 W-C-RC 'all exposure gabodsid good rot' 'none' OCFSRI 2>&1 | tee -a OUT-2018-do_coadd_batch_${cluster}_${filter}.log
exit 0;
bsub -q long -W 7000 -R rhel60 -o /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS1115+01//OUT-2017-10-20-do_coadd_batch_${filter}.out  -e /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS1115+01//OUT-2017-10-20-do_coadd_batch_${filter}.err "./do_coadd_batch.sh MACS1115+01 W-C-RC 'all exposure gabodsid good rot' 'none' OCFSRI"
exit 0;

export filter=W-J-B
./adam_pre_coadd_cleanup.sh
bsub -q long -W 7000 -R rhel60 -o /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS1115+01//OUT-2017-10-20-do_coadd_batch_${filter}.out  -e /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS1115+01//OUT-2017-10-20-do_coadd_batch_${filter}.err "./do_coadd_batch.sh MACS1115+01 W-J-B 'all exposure' 'none' OCFI"

export filter=W-S-Z+
./adam_pre_coadd_cleanup.sh
bsub -q long -W 7000 -R rhel60 -o /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS1115+01//OUT-2017-10-20-do_coadd_batch_${filter}.out  -e /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS1115+01//OUT-2017-10-20-do_coadd_batch_${filter}.err "./do_coadd_batch.sh MACS1115+01 W-S-Z+ 'all exposure' 'none' OCFSFI"

export filter=W-J-V
./adam_pre_coadd_cleanup.sh
bsub -q long -W 7000 -R rhel60 -o /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS1115+01//OUT-2017-10-20-do_coadd_batch_${filter}.out  -e /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS1115+01//OUT-2017-10-20-do_coadd_batch_${filter}.err "./do_coadd_batch.sh MACS1115+01 W-J-V 'all exposure good' 'none' OCFSI"

export filter='W-C-IC'
./adam_pre_coadd_cleanup.sh
bsub -q long -W 7000 -R rhel60 -o /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS1115+01//OUT-2017-10-20-do_coadd_batch_${filter}.out  -e /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS1115+01//OUT-2017-10-20-do_coadd_batch_${filter}.err "./do_coadd_batch.sh MACS1115+01 W-C-IC 'all exposure' 'none' OCFSI"


wait 700
export cluster='MACS0416-24'
export filter='W-C-RC'
./adam_pre_coadd_cleanup.sh
bsub -q long -W 7000 -R rhel60 -o /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS0416-24//OUT-2017-10-20-do_coadd_batch_${filter}.out -e /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS0416-24//OUT-2017-10-20-do_coadd_batch_${filter}.err "./do_coadd_batch.sh MACS0416-24 ${filter} 'all exposure good ' 'none' OCFR  "

export filter='W-S-Z+'
./adam_pre_coadd_cleanup.sh 
bsub -q long -W 7000 -R rhel60 -o /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS0416-24//OUT-2017-10-20-do_coadd_batch_${filter}.out -e /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS0416-24//OUT-2017-10-20-do_coadd_batch_${filter}.err "./do_coadd_batch.sh MACS0416-24 ${filter} 'all ' 'none' OCF  "

export filter='W-J-B'
./adam_pre_coadd_cleanup.sh
bsub -q long -W 7000 -R rhel60 -o /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS0416-24//OUT-2017-10-20-do_coadd_batch_${filter}.out -e /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS0416-24//OUT-2017-10-20-do_coadd_batch_${filter}.err "./do_coadd_batch.sh MACS0416-24 ${filter} 'all ' 'none' OCF  "
