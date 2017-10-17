#!/bin/bash
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# delete recursively empty directories
# from a given start location.
# It assumes that the UNIX programs
# find, du and gawk are in your path.

# 30.05.04:
# tempaorary files go to a TEMPDIR directory 
#
# 14.08.2005:
# The call of the UNIX 'find' program is now done
# via a variable 'P_FIND'.

# $1: the start directory from that
#     recursively empty directories
#     should be removed

${P_FIND} $1 -type d > ${TEMPDIR}/alldirs_$$

cat ${TEMPDIR}/alldirs_$$ |\
{
  while read directory
  do
    SPACE=`du -s ${directory} | gawk '{print $1}'`

    if [ ${SPACE} -eq "0" ]; then
      echo "removing empty directory ${directory}"
      rmdir ${directory}
    fi 
  done
}

rm -f ${TEMPDIR}/alldirs_$$
#adam-BL# log_status $?
