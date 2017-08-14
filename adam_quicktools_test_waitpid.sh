#!/bin/bash -v
#adam-does# use this code if you need to wait until other jobs are finished running before you run the next thing
#adam-SHNT# this is a test, first of all it doesn't work yet as is
COUNTER=0
while [  $COUNTER -lt 3000 ]; do
	echo The counter is $COUNTER
	dones=( 0 0 0 0 0 )
	jid_count=0
	#adam-SHNT# this is a test, second of all it doesn't work with command-line inputs for the job ids
	for jid in "1470 1471 1472 1473 1482"
	do
		let jid_count=jid_count+1
		nlines=`jobs -p | grep "${jid}" | wc -l `
		if [ "${nlines}" != "0" ];then
			sleep 8
		else
			let dones[${jid_count}]=dones[${jid_count}]+1
		fi
	done

	echo "dones=" ${dones[@]}
	if [ "dones[1]" == "1" -a "dones[2]" == "1" -a "dones[3]" == "1" -a "dones[4]" == "1" -a "dones[5]" == "1" ];then
		COUNTER=3000
	else
		let COUNTER=COUNTER+1 
	fi
done

echo "STARTING!"

