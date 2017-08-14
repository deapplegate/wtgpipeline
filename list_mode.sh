#!/bin/bash 

# 28.05.03:
# rewrote the script for the bash shell
#
# 30.05.04:
# output goes to a TEMPDIR directory (if it 
# is defined) 


echo " FLIPS - list_mode"
if [ $# -ne 1 ] ; then
  echo " Create a set of lists in FLIPS format from the immode.dat file"
  echo " Syntax:  list_mode filename type_image nom"
  echo " Example: list_mode immode.dat d imcombine"
  echo "          creates @in-imcombine.n n={0,...,7} with files *dn*"
  exit
fi

# set TEMPDIR to a default value
# if it is not defined
TEMPDIR=${TEMPDIR:="."}

number=1 
indice=${NCHIPS} 

while [ "${indice}" -gt "0" ]
do
  echo "more $1 | grep $number$2 > @in-$3.$number"
  more $1 | grep $number$2 > ${TEMPDIR}/@in-$3.$number
  number=$(( ${number} + 1 ))  
  indice=$(( ${indice} - 1 ))  
done

exit

