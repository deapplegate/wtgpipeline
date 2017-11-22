#!/bin/bash -u

queueDir=$1
logfile=$2
queue=$3
npermitted=$4

writeableTestFile=$queueDir/testWriteable

while true; do

#    diskspace=`df -B G /nfs/slac/g/ki/ki06/anja/SUBARU | awk '(NR==3){print $3}' | awk -F'G' '{print $1}'`
#    diskWarningShown=0
#    while [ $diskspace -lt 300 ]; do
#	if [ $diskWarningShown -eq 0 ]; then
#	    curdate=`date`
#	    echo "$curdate : !!! Warning - Low Disk Space !!!" | tee -a $logfile
#	    diskWarningShown=1
#	fi
#	sleep 5m
#	diskspace=`df -B G /nfs/slac/g/ki/ki06/anja/SUBARU | awk '(NR==3){print $3}' | awk -F'G' '{print $1}'`
#    done
#    if [ $diskWarningShown -eq 1 ]; then
#	continue
#    fi
#

    njobs=`bjobs -q $queue | wc -l`
    while [ $njobs -gt $npermitted ]; do
	sleep 1m
	njobs=`bjobs -q $queue | wc -l`
    done

    writeableWarningShown=0
    curdate=`date +%s`
    sleep 1s
    touch $writeableTestFile
    moddate=`stat -c %Y $writeableTestFile`
    while [ -z "$moddate" ] || [ $curdate -gt $moddate ]; do
	if [ $writeableWarningShown -eq 0 ]; then
	    curdate=`date`
	    echo "$curdate : !!!Warning - Cannot write to disk !!!" >> $logfile
	    writeableWarningShown=1
	fi
	sleep 5m
	curdate=`date +%s`
	sleep 1s
	touch $writeableTestFile
	moddate=`stat -c %Y $writeableTstFile`
	
    done
    if [ $writeableWarningShown -eq 1 ]; then
	continue
    fi

    
    noJobWarning=0
    curJobFile=`ls -1 $queueDir/p* | awk '(NR==1){print}'`
    while [ -z "$curJobFile" ]; do
	if [ $noJobWarning -eq 0 ]; then
	    curdate=`date`
	    echo "$curdate : *** Job Queue is Empty ***" >> $logfile
	    noJobsWarning=1
	fi
	sleep 5m
	curJobFile=`ls -1 $queueDir/p* | awk '(NR==1){print}'`
    done
    if [ $noJobWarning -eq 1 ]; then
	continue
    fi

    
    curdate=`date`
    echo "$curdate : Processing $curJobFile" >> $logfile
		    
    $curJobFile
    if [ $? -gt 0 ]; then
	curdate=`date`
	echo "$curdate : !!! Error in running $curJobFile !!!" >> $logfile
	
	jobFileBase=`basename $curJobFile`
	mv $curJobFile $queueDir/error.$jobFileBase
       
    else
	curdate=`date`
	echo "$curdate : Submitted $curJobFile" >> $logfile

	jobFileBase=`basename $curJobFile`
	mv $curJobFile $queueDir/submitted.$jobFileBase

    fi
  
done
