#!/bin/bash
#adam-does# kills the job running on nohup that was submitted by ./adam_quickools_nohupify_run_job.sh
#adam-example#	./adam_quicktools_nohupify_kill_job.sh 'run_phot' # will kill the process './run_phot.sh $INSTRUMENT $cluster'
commandname=$1
echo "commandname=" $commandname
if [ -z "${commandname}"] ;then
	echo "insufficient inputs! Need name of command. ex: ./adam_nohupify_kill_job.sh 'run_phot' "
	exit 1
fi

logfile=scratch/OUT-${commandname}_NOHUPIFY.log
pidfile=scratch/PID-${commandname}_NOHUPIFY.log
echo "pidfile=" ${pidfile} 
echo "logfile=" ${logfile} 

kill -9 `cat ${pidfile}`

