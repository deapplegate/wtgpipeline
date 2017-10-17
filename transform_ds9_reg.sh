#!/bin/bash
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 18.11.2004:
# TEMPDIR is set to "." as default if it
# is not defined.
#
# 23.12.2005:
# Files already in saoimage format are no longer
# destroyed by running this script.

# This file transforms reg files created with DS9
# into saoimage format (needed for this pipeline).

# $1: main dir
# $2: science dir (contains the reg directory)

# set TEMPDIR to a default value
# if it is not defined
TEMPDIR=${TEMPDIR:="."}

REDDIR=`pwd`

cd $1/$2/reg

if [ -f ${TEMPDIR}/filelist_$$ ]; then
   rm -f ${TEMPDIR}/filelist_$$
fi

ls *.reg > ${TEMPDIR}/filelist_$$

if [ ! -d ORIGINALS ]; then
  mkdir ORIGINALS
fi
cp *.reg ORIGINALS/

cat ${TEMPDIR}/filelist_$$ |\
{
  while read file
  do
    awk -F \( '{ if(index($1, "POLYGON") == 0) {
                   print "# " $0} else {print $0}
              }' ${file} > ${file}2
    sed 's/# image\;polygon/ POLYGON/g' ${file}2 > tmp_$$
    mv tmp_$$ ${file}
  done
}

rm -f *reg2 ${TEMPDIR}/filelist_$$

cd $REDDIR
#adam-BL# log_status $?
