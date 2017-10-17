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


echo " FLIPS - list_ext_para"
if [ $# -ne 5 ] ; then
  echo " Create a list in FLIPS format"
  echo " Syntax:  list_ext path ext name processnumber chips"
  echo " Example: list_ext /local/h-t2-dr/dr7/UH8K-JCC/M31-V/443 ODF immode"
  echo "          creates @in-immmode with files 443*nODF* sorted with n=0->7"
  exit
fi

if [ -f @in-$3_$4 ]; then
   rm -f @in-$3_$4
fi

# set TEMPDIR to a default value
# if it is not defined
TEMPDIR=${TEMPDIR:="."}

for CHIP in $5
do
  echo "ls $1*_${CHIP}$2* -> @in-$3_$4"
  ls $1*_${CHIP}$2* >> ${TEMPDIR}/@in-$3_$4
done

exit 

