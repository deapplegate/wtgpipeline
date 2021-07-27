#!/bin/bash
set -xv
export INSTRUMENT=SUBARU
export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU
export run="2010-11-04"
export cluster=MACS0416-24

export ending="OCFR"
export filter=W-C-RC
echo "adam-STARTING: ${cluster} ${filter} 'all exposure good' 'none' ${ending} " >> coadd_many_logger_${cluster}.log
./do_coadd_batch.sh ${cluster} ${filter} "all exposure good" 'none' ${ending} > OUT-do_coadd_batch-${cluster}_${filter}.log 2>&1
grep -n -i "exit [1-9]\|except\|error" OUT-do_coadd_batch-${cluster}_${filter}.log >> coadd_many_logger_${cluster}.log
echo "adam-ENDING: ${cluster} ${filter} 'all exposure good' 'none' ${ending} " >> coadd_many_logger_${cluster}.log

export ending="OCF"
export filter=W-J-B
echo "adam-STARTING: ${cluster} ${filter} 'all' 'none' ${ending} " >> coadd_many_logger_${cluster}.log
./do_coadd_batch.sh ${cluster} ${filter} "all" "none" ${ending}  > OUT-do_coadd_batch-${cluster}_${filter}.log 2>&1
grep -n -i "exit [1-9]\|except\|error" OUT-do_coadd_batch-${cluster}_${filter}.log >> coadd_many_logger_${cluster}.log
echo "adam-ENDING: ${cluster} ${filter} 'all' 'none' ${ending} " >> coadd_many_logger_${cluster}.log

export filter=W-S-Z+
echo "adam-STARTING: ${cluster} ${filter} 'all' 'none' ${ending} " >> coadd_many_logger_${cluster}.log
./do_coadd_batch.sh ${cluster} ${filter} "all" "none" ${ending}  > OUT-do_coadd_batch-${cluster}_${filter}.log 2>&1
grep -n -i "exit [1-9]\|except\|error" OUT-do_coadd_batch-${cluster}_${filter}.log >> coadd_many_logger_${cluster}.log
echo "adam-ENDING: ${cluster} ${filter} 'all' 'none' ${ending} " >> coadd_many_logger_${cluster}.log

./adam_make_backmask_ims.py /u/ki/awright/data/MACS0416-24/W-C-RC/SCIENCE/

export filter=W-J-B
echo "adam-STARTING: ${cluster} ${filter} 'exposure' 'none' ${ending} " >> coadd_many_logger_${cluster}.log
./do_coadd_batch.sh ${cluster} ${filter} "exposure" "none" ${ending}  > OUT-do_coadd_batch-${cluster}_${filter}.log2 2>&1
echo "adam-ENDING: ${cluster} ${filter} 'exposure' 'none' ${ending} " >> coadd_many_logger_${cluster}.log

export filter=W-S-Z+
echo "adam-STARTING: ${cluster} ${filter} 'exposure' 'none' ${ending} " >> coadd_many_logger_${cluster}.log
./do_coadd_batch.sh ${cluster} ${filter} "exposure" "none" ${ending}  > OUT-do_coadd_batch-${cluster}_${filter}.log2 2>&1
echo "adam-ENDING: ${cluster} ${filter} 'exposure' 'none' ${ending} " >> coadd_many_logger_${cluster}.log
