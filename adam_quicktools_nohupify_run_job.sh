#!/bin/bash
#adam-does# runs a job in nohup so that it will run without any issues, automatically save the output, and will save the pid so that it can be killed with adam_quicktools_nohupify_kill_job.sh if need be
#adam-example#	./adam_quickools_nohupify_run_job.sh 'run_phot' './run_phot.sh $INSTRUMENT $cluster'
commandname=$1
command2run=$2
echo "commandname=" $commandname
echo "command2run=" $command2run
if [ -z "${command2run}" ] ;then
	echo "insufficient inputs! Need name AND command. ex: ./adam_quicktools_nohupify_run_job.sh 'run_phot' './run_phot.sh \$INSTRUMENT \$cluster' "
	exit 1
fi

logfile=~/wtgpipeline/OUT-${commandname}_NOHUPIFY.log
pidfile=~/wtgpipeline/PID-${commandname}_NOHUPIFY.log
echo "pidfile=" ${pidfile} 
echo "logfile=" ${logfile} 

nohup sh -c "${command2run}" > ${logfile} 2>&1 &
echo $! > ${pidfile} 
