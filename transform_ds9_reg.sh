#!/bin/bash
. BonnLogger.sh
. log_start
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
   rm ${TEMPDIR}/filelist_$$
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
    sed 's/polygon/POLYGON/g' ${file} > ${file}2
    awk -F \( '{ if(index($1, "image") == 0 && index($1, "physical") == 0 ) print $0}' ${file}2 > ${file}3
    awk -F \( '{ if(index($1, "POLYGON") == 0) {
                   print "# " $0} else {print $0}
              }' ${file}3 > ${file}4
    mv ${file}4 ${file}
  done
}

rm *.reg2 *.reg3 ${TEMPDIR}/filelist_$$

cd $REDDIR
log_status $?
