#!/bin/bash -xv
#adam-example# ./adam_coadd_many.sh "MACS0416-24" "OCFR" "W-C-RC";./adam_coadd_many.sh "MACS0416-24" "OCF" "W-J-B W-S-Z+"
#adam-example# ./adam_coadd_many.sh "MACS1226+21" "OCFI" "W-J-B W-J-V W-C-RC W-C-IC W-S-Z+"
export INSTRUMENT=SUBARU
export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
export cluster=$1
export ending=$2
export filters=$3

touch coadd_many_logger_${cluster}.log

for filter in ${filters}
do
	export filter
	if [ ${filter} = "W-C-RC" ];then
		echo "adam-STARTING: ${cluster} ${filter} 'all exposure good' 'none' ${ending} " >> coadd_many_logger_${cluster}.log
		./do_coadd_batch.sh ${cluster} ${filter} "all exposure good" "none" ${ending} 2>&1 | tee -a OUT-do_coadd_batch-${cluster}_${filter}.log
		grep -n -i "exit [1-9]\|except\|error" OUT-do_coadd_batch-${cluster}_${filter}.log >> coadd_many_logger_${cluster}.log
		echo "adam-ENDING: ${cluster} ${filter} 'all exposure good' 'none' ${ending} " >> coadd_many_logger_${cluster}.log
	else
		echo "adam-STARTING: ${cluster} ${filter} 'all' 'none' ${ending} " >> coadd_many_logger_${cluster}.log
		./do_coadd_batch.sh ${cluster} ${filter} "all" 'none' ${ending}  2>&1 | tee -a OUT-do_coadd_batch-${cluster}_${filter}.log
		grep -n -i "exit [1-9]\|except\|error" OUT-do_coadd_batch-${cluster}_${filter}.log >> coadd_many_logger_${cluster}.log
		echo "adam-ENDING: ${cluster} ${filter} 'all' 'none' ${ending} " >> coadd_many_logger_${cluster}.log
	fi
done
