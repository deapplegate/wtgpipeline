#!/bin/bash
set -xv

cat cluster.status | { 
    while read cluster filter ending status ; do 
	n_ppruns=`cat illum.status | grep $cluster | grep $filter | awk '{print $5}' | wc -l` ; 
	n_complete=`cat illum.status | grep $cluster | grep $filter | awk '{print $5}' | grep yes | wc -l` ; 

	if [ "$n_ppruns" = "$n_complete" ] ; then 
	    echo $cluster $filter $ending ready ; 
	else 
	    echo $cluster $filter $ending skip ; 
	fi ; 
    done ; 
} > coadd.status