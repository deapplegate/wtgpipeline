#!/bin/bash
set -xv
#adam-does# use this code if you need to wait until other jobs are finished running on the slac batchq before you run the next thing
#adam-SHNT# this is a test, first of all you need to get adam_quicktools_test_waitpid.sh to work, then fix things up here

#JOBID   USER    STAT  QUEUE      FROM_HOST   EXEC_HOST   JOB_NAME   SUBMIT_TIME
#760635  awright RUN   long       ki-ls07     fell0251    *fits .961 Jul 30 22:33
#760638  awright RUN   long       ki-ls07     fell0196    *fits .961 Jul 30 22:33
#760643  awright RUN   long       ki-ls07     fell0303    *fits .961 Jul 30 22:33
#760646  awright RUN   long       ki-ls07     fell0136    *fits .961 Jul 30 22:33
#760650  awright RUN   long       ki-ls07     hequ0029    *fits .961 Jul 30 22:33

COUNTER=0
while [  $COUNTER -lt 300 ]; do
	echo The counter is $COUNTER
	dones=( 0 0 0 0 0 )
	jid_count=0
	#adam-SHNT# this is a test, second of all it doesn't work with command-line inputs for the job ids
	for jid in "760635 760638 760643 760646 760650"
	do
		let jid_count=jid_count+1
		nlines=`bjobs | grep "${jid}" | wc -l `
		if [ "${nlines}" != "0" ];then
			sleep 120
		else
			let dones[${jid_count}]=dones[${jid_count}]+1
		fi
	done

	if [ "dones[1]" == "1" -a "dones[2]" == "1" -a "dones[3]" == "1" -a "dones[4]" == "1" -a "dones[5]" == "1" ];
		COUNTER=300
	else
		let COUNTER=COUNTER+1 
	fi
done

echo "STARTING!"

./do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper MERGE STARS SDSS CALIB APPLY SLR > scratch/OUT-do_photometry-MERGE_STARS_SDSS_CALIB_APPLY_SLR.log 2>&1
