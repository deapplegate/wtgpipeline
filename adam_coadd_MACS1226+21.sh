#!/bin/bash
set -xv
export INSTRUMENT=SUBARU
export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
export ending="OCF"
export cluster=MACS1226+21

touch coadd_many_logger_${cluster}.log
export filter=W-C-RC
echo "adam-STARTING: ${cluster} ${filter} 'all exposure good gabodsid rotation' 'none' ${ending} " >> coadd_many_logger_${cluster}.log
./do_coadd_batch.sh ${cluster} ${filter} 'all exposure good gabodsid rotation' 'none' ${ending} 2>&1 | tee -a OUT-do_coadd_batch-${cluster}_${filter}.log
grep -n -i "exit [1-9]\|except\|error" OUT-do_coadd_batch-${cluster}_${filter}.log >> coadd_many_logger_${cluster}.log
echo "adam-ENDING: ${cluster} ${filter} 'all exposure good gabodsid rotation' 'none' ${ending} " >> coadd_many_logger_${cluster}.log

for filter in W-J-B W-J-V W-C-IC W-S-Z+
do
	export filter
	echo "adam-STARTING: ${cluster} ${filter} 'all' 'none' ${ending} " >> coadd_many_logger_${cluster}.log
	./do_coadd_batch.sh ${cluster} ${filter} 'all' 'none' ${ending}  2>&1 | tee -a OUT-do_coadd_batch-${cluster}_${filter}.log
	grep -n -i "exit [1-9]\|except\|error" OUT-do_coadd_batch-${cluster}_${filter}.log >> coadd_many_logger_${cluster}.log
	echo "adam-ENDING: ${cluster} ${filter} 'all' 'none' ${ending} " >> coadd_many_logger_${cluster}.log
done
