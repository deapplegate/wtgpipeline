#!/bin/bash

# this script resolves the link structure in ag given
# directory after all processing has been done. 
# It moved all files to the given directory (and all
# subdirectories)
#
# 25.01.2004:
# introduced the possibilty to only resolve
# files whose names start with a given pattern.
#
# 31.01.2004:
# if a link points again to a link, it is simply
# deleted and NO files are moved. To keep a consistent
# structure, first a pass is made through all
# the data and double links (and those pointing to
# nowhere) are deleted before
# the moving process starts.
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 07.07.2004:
# I introduced the possibility to give a string
# in the middle of the files to be resolved (as
# third argument; to give the start is necessary 
# in this case)
#
# 14.08.2005:
# The call of the UNIX 'find' program is now done
# via a variable 'P_FIND'.


#$1: directory for that the link structure should
#    be resolved. 
#$2: beginning of the names from the files
#    to be resolved (optional)
#$3: a string contained within the file name
#    (optional)

. progs.ini

#
# first make a pass to identify double links
# and links pointing to nowhere
if [ "$#" -gt "1" ]; then
  if [ "$#" -gt "2" ]; then
    ${P_FIND} $1 -name $2\*$3\* > ${TEMPDIR}/allfiles_$$
  else  
    ${P_FIND} $1 -name $2\* > ${TEMPDIR}/allfiles_$$
  fi  
else
  ${P_FIND} $1 -name \* > ${TEMPDIR}/allfiles_$$
fi

cat ${TEMPDIR}/allfiles_$$ |\
{
  while read FILE
  do
    if [ -L ${FILE} ]; then
      REALFILE=`${P_READLINK} ${FILE}`
      #
      # if REALFILE is again a link, the
      # link is simply deleted and NO files
      # are moved
      if [ -L ${REALFILE} ] || [ ! -e ${REALFILE} ]; then
        rm ${FILE}
      fi
    fi
  done
}

# 
# now really resolve existing links
#
if [ "$#" -gt "1" ]; then
  if [ "$#" -gt "2" ]; then
    ${P_FIND} $1 -name $2\*$3\* > ${TEMPDIR}/allfiles_$$
  else  
    ${P_FIND} $1 -name $2\* > ${TEMPDIR}/allfiles_$$
  fi  
else
  ${P_FIND} $1 -name \* > ${TEMPDIR}/allfiles_$$
fi

cat ${TEMPDIR}/allfiles_$$ |\
{
  while read FILE
  do
    if [ -L ${FILE} ]; then
      REALFILE=`${P_READLINK} ${FILE}`
      DIR=`dirname ${FILE}`
      rm ${FILE}
      mv ${REALFILE} ${DIR}
    fi
  done
}
