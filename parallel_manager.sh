#!/bin/bash
#for CHIPS=10: '1 5 9 '    ' 2 6 10'    ' 3 7 '     ' 4 8 '
. /u/ki/awright/bonnpipeline/${INSTRUMENT:?}.ini > /tmp/INSTRUMENT.out 2>&1 
NPARA=4

# do some initialisations

i=1
while [ "${i}" -le "${NPARA}" ]
do
  PARA[$i]=""
  i=$(( $i + 1 ))
done

# now divide the chips to the processors:

k=1
while [ "${k}" -le "${NCHIPS}" ]
do
  ACTUPROC=1
  while [ "${ACTUPROC}" -le "${NPARA}" ] && [ "${k}" -le "${NCHIPS}" ]
  do
    PARA[${ACTUPROC}]="${PARA[${ACTUPROC}]} ${k}"
    k=$(( $k + 1 ))
    ACTUPROC=$(( $ACTUPROC + 1 ))
  done
done

# finally start all the processes

SCRIPT=$1
shift

k=1
while [ "${k}" -le "${NPARA}" ]
do
  ( ./${SCRIPT} "$@" "${PARA[${k}]}" ) &
  k=$(( $k + 1 ))
done

# wait until all subprocesses have finished
wait

exit 0;

