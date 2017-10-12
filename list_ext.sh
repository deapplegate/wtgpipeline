#!/bin/bash

# 28.05.03:
# rewrote the script for the bash shell
#
# 30.05.04:
# output goes to a TEMPDIR directory (if it 
# is defined) 
#
# changed the hardwiring of indice=8 to
# indice=${NCHIPS}

echo " FLIPS - list_ext"
if [ $# -ne 3 ] ; then
  echo " Create a list in FLIPS format"
  echo " Syntax:  list_ext path ext name"
  echo " Example: list_ext /local/h-t2-dr/dr7/UH8K-JCC/M31-V/443 ODF immode"
  echo "          creates @in-immmode with files 443*nODF* sorted with n=0->7"
  exit
fi

if [ -f @in-$3 ]; then
   rm -f @in-$3
fi

# set TEMPDIR to a default value
# if it is not defined
TEMPDIR=${TEMPDIR:="."}

number=1
indice=${NCHIPS}

while [ "${indice}" -gt "0" ]
do
  echo "ls $1*_$number$2* -> ${TEMPDIR}/@in-$3"
  ls $1*_$number$2* >> ${TEMPDIR}/@in-$3
  number=$(( ${number} + 1 ))  
  indice=$(( ${indice} - 1 ))  
done

exit 

