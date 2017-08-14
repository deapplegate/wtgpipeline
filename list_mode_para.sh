#!/bin/bash

# 22.09:
# parallel version of list_ext that takes
# the chips to be listed as an extra argument
#
# 28.05.03:
# rewrote the script for the bash shell
#
# 30.05.04:
# output goes to a TEMPDIR directory (if it 
# is defined) 
#
# 18.11.04:
# corrected an error that listed uncorrect
# files if the number of chips is larger than
# 10.
#


echo " FLIPS - list_mode"
if [ $# -ne 5 ] ; then
  echo " Create a set of lists in FLIPS format from the immode.dat file"
  echo " Syntax:  list_mode filename type_image nom processnumber chips"
  echo " Example: list_mode immode.dat d imcombine 4987"
  echo "          creates @in-imcombine.n n={0,...,7} with files *dn*"
  exit  
fi

# set TEMPDIR to a default value
# if it is not defined
TEMPDIR=${TEMPDIR:="."}

for CHIP in $5
do
  echo "more $1 | grep _${CHIP}$2 > @in-$3.${CHIP}_$4"
  more $1 | grep _${CHIP}$2 > ${TEMPDIR}/@in-$3.${CHIP}_$4
done

exit

