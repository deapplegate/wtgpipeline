#!/bin/bash
set -xuv

rm -f clusters.err_report.list clusters.err_report.report clusters.torun clusters.done.list

grep "to run" cluster.status | { 
    while read cluster filter ending status; do 

	export BONN_TARGET=$cluster; 
	export BONN_FILTER=$filter; 
	
	didrun=`./BonnLogger.py last 1 | grep "2009-06" | awk '($2 ~ /2009-06-2[45]/){print $2}'`; 
	
	if [ -z "$didrun" ]; then 
	    echo $cluster $filter $ending to run >> clusters.torun; 
	else 
	    newstat=`./BonnLogger.py last 1 | grep check_psf_coadd | grep "Status: 0"`; 
	    if [ -z "$newstat" ]; then 
		
		echo $cluster $filter >> clusters.err_report.list; 
		echo $cluster $filter; 
		./BonnLogger.py last 1; 
		echo; 
		echo; 
	    else 
		echo $cluster $filter done>> clusters.done.list; 
	    fi; 
	fi; 
    done; 
} > clusters.err_report.report

