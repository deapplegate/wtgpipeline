#!/bin/bash 
###################
# Additional Code for BonnLogger.py testing
###################
#CVSID="$Id: testcommand.sh,v 1.2 2008-07-09 01:22:15 dapple Exp $"

echo "This is testcommand.sh"
echo "It was called with the following arguments: $@"

. BonnLogger.sh

code=0
if [ $# -gt 0 ] && [ $1 = 'notarget' ]; then
    echo "Target Not Set"
    cmd=${2}
    arg1=${3}
    arg2=${4}
    arg3=${5}
else
    echo "Target Set"
    export BONN_TARGET=2003-09-25
    export BONN_FILTER=W-J-V
    cmd=${1}
    arg1=${2}
    arg2=${3}
    arg3=${4}
    
fi


if  [ "$cmd" = 'fail' ]; then
    code=${arg1}
    . log_start
elif [ "$cmd" = 'forceRun' ]; then
    . log_force_start

#elif [ $# -gt 1 ]  && [ $2 = 'forceRun' ]; then
#    echo "here"
#    log_force_start $0 "$@"
#    if [ $? -ne 0 ]; then
#	echo "here1"
#	exit 1
#    fi

else
    
    . log_start
fi

if [ "$1" = "comment" ]; then
    log_status $code $2
else
    log_status $code
fi


