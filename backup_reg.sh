#!/bin/bash


SUBARUDIR=/nfs/slac/g/ki/ki05/anja/SUBARU

curdate=`date +%y-%m-%d_%H-%M`

REPOSITORY=${SUBARUDIR}/regionbackup_${curdate}
if [ -d ${REPOSITORY} ]; then
    echo "Backup Dir Exists!?"
    exit 1
fi
mkdir ${REPOSITORY}

dirs=`ls -1 $SUBARUDIR`

runs=`echo "$dirs" | awk -v ORS=' ' '(/^[[:digit:]][[:digit:]][[:digit:]][[:digit:]]-/) {print}'`

for run in $runs; do
    
    if [ -d $SUBARUDIR/$run/reg ]; then
	if [ ! -d $REPOSITORY/$run ]; then
	    mkdir $REPOSITORY/$run
	fi
	cp $SUBARUDIR/$run/reg/*.reg $REPOSITORY/$run/
    fi
done

clusters=`echo "$dirs" | awk -v ORS=' ' '(!/^[[:digit:]][[:digit:]][[:digit:]][[:digit:]]-/) {print}'`

for cluster in $clusters; do

    filters=`ls -1 $SUBARUDIR/$cluster/`
    for filter in $filters; do
	
	if [ -d $SUBARUDIR/$cluster/$filter/SCIENCE/reg ]; then
	    mkdir -p $REPOSITORY/$cluster/$filter
	    cp $SUBARUDIR/$cluster/$filter/SCIENCE/reg/*.reg $REPOSITORY/$cluster/$filter
	fi
    done
done


tar -zcvf ${SUBARUDIR}/regionbackup_${curdate}.tar.gz ${REPOSITORY}
chmod 444 ${SUBARUDIR}/regionbackup_${curdate}.tar.gz