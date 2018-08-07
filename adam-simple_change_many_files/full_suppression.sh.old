#!/bin/bash

cluster=$1
filter=$2
suppressiondir=$3
ending=$4
queue=$5
options=$6

#Run Options
#default is all
#CLEAN
#REGEN
#SUPPRESS
#MOVE
#IC
#BADCCD


if [ -z "${options}" ]; then
    options="CLEAN REGEN SUPPRESS MOVE IC BADCCD"
fi

subarudir=/nfs/slac/g/ki/ki18/anja/SUBARU

CLEAN=`echo $options | grep CLEAN`
if [ -n "${CLEAN}" ]; then
    ./clean_oldIC.sh $cluster $filter
fi

REGEN=`echo $options | grep REGEN`
if [ -n "${REGEN}" ]; then
    ./batch_regen.sh $cluster $filter $queue
    if [ "$?" != "0" ]; then
	exit 2
    fi
fi

SUPPRESS=`echo $options | grep SUPPRESS`
if [ -n "${SUPPRESS}" ]; then
    ./batch_suppress.sh $cluster $filter $suppressiondir $ending $queue
    if [ "$?" != "0" ]; then
	exit 3
    fi
fi

MOVE=`echo $options | grep MOVE`
if [ -n "${MOVE}" ]; then 
    ./move_suppression.sh $cluster $filter $ending
    if [ "$?" != "0" ]; then
	exit 4
    fi
fi

IC=`echo $options | grep IC`
if [ -n "${IC}" ]; then
    ./batch_ic.sh $cluster $filter $queue
    if [ "$?" != "0" ]; then
	exit 5
    fi
fi

BADCCD=`echo $options | grep BADCCD`
if [ -n "${BADCCD}" ]; then
    
    rext=''
    use_rext=`ls ${subarudir}/${cluster}/${filter}/SCIENCE/*RI.fits | wc -l`
    
    if [ "${use_rext}" != "0" ]; then
	rext=R
    fi

    ./propagate_badccd.sh ${subarudir}/${cluster}/${filter}/SCIENCE ${ending} ${ending}${rext}I
    if [ "$?" != "0" ]; then
	exit 6
    fi
fi



