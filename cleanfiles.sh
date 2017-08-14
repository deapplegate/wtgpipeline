#!/bin/bash
. BonnLogger.sh
. log_start
# the script cleanes a directory from files
# with a given prefix/ending
# The script takes into account links
#
# 26.01.2004:
# The third argument now contains the "."
# before the fits extension. This prevents that
# empty strings have to be given as third argument
# (what made problem if this script was called
# within another script)
#
# 15.03.2004:
# if a link points again to a link, it is simply
# deleted and NO files are removed. To keep a consistent
# structure, first a pass is made through all
# the data and double links (and those pointing to
# nowhere) are deleted before
# the real deletion process starts.
#
# 30.05.04:
# tempaorary files go to a TEMPDIR directory 

# $1: master directory
# $2: prefix of files
# $3: ending "OFCSFF etc.". Files end with _i$3fits
#     where i is the chip number
#     The ending contains the "." before the fits
#     extension.
 
# preliminary work
. ${INSTRUMENT:?}.ini

if [ -f ${TEMPDIR}/tmp_$$ ]; then
  rm ${TEMPDIR}/tmp_$$
fi

#
# first make a pass to identify double links
# and links pointing to nowhere
i=1
while [ "${i}" -le "${NCHIPS}" ]
do
  ls -1 $1/$2*_${i}$3fits >> ${TEMPDIR}/tmp_$$
  i=$(( $i + 1 ))
done

cat ${TEMPDIR}/tmp_$$ |\
{
  while read file
  do
    if [ -L ${file} ]; then
      REALFILE=`${P_READLINK} ${file}`
      #
      # if REALFILE is again a link, only the
      # link is deleted but NO other files
      if [ -L ${REALFILE} ] || [ ! -e ${REALFILE} ]; then
        rm ${file}
      fi
    fi
  done
}

rm ${TEMPDIR}/tmp_$$
# 
# now do the real deleting of files
#
i=1
while [ "${i}" -le "${NCHIPS}" ]
do
  ls -1 $1/$2*_${i}$3fits >> ${TEMPDIR}/tmp_$$
  i=$(( $i + 1 ))
done

cat ${TEMPDIR}/tmp_$$ |\
{
  while read file
  do
    if [ -L ${file} ]; then
      LINK=`${P_READLINK} ${file}`
      rm ${LINK}
      rm ${file}
    else
      rm ${file}
    fi
  done
}












log_status $?
