#!/bin/bash -xv

# the script coadds the images finally
# by a call to IRAF

# not paralellised version !!!
# assuming one processor

. ${INSTRUMENT:?}.ini

#$1: name of the cl-script (4 charracters)

# create links of the science and weight frames:
DIR=`pwd`

i=1

while [ "${i}" -le "${NPARA}" ]
do
  cd ${IRAFDIR[${i}]}

  SCRIPT=`ls $1*cl`
  {
    echo "eis"
    #
    echo "flprc"
    echo "cl < ${SCRIPT}"
    echo "flprc"
    echo "logout"
  } | ${P_CL} >& log_${i} &

  i=$(( $i + 1 ))
done

wait

cd ${DIR}






