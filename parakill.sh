#!/bin/bash
# script that kills a process including all
# the childs and child's childs

#$1: process number of the root process

KILLJOBS="$1 "

function killchild() {
  i=1
  JOBS=""
  JOBS=`ps -eaf | awk '{if($3=='$1') printf("%d ", $2)}'`
  echo $1": "${JOBS}
  
  if [ -z JOBS ]; then
    return
  else
    KILLJOBS="${KILLJOBS} ${JOBS}"
    for JOB in ${JOBS}
    do
      killchild ${JOB}
#      kill -9 ${JOB}
    done
  fi
}

killchild $1
echo ${KILLJOBS}
    for JOB in ${KILLJOBS}
    do
      kill ${JOB}
    done
