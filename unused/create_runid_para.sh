#!/bin/bash -xv

# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 24.11.05:
# Instead of giving the keyword to be substituted
# on the command line we take the next free DUMMY
# keyword and substitute it with RUN.
#
# 02.05.2006:
# I replaced the 'replacekey' command by a call to
# 'writekey'. This ensures proper treatment if the 
# script is run multiple times.

# the script gives every image a RUNID 
# (it replaces a superfluous header keyword
# by RUN) (parallel version)

. ${INSTRUMENT:?}.ini
. bash_functions.include

# $1: main dir
# $2: science dir (the cat dir is a subdirectory of this)
# $3: extension
#     This argument contains the "." before the fits
#     extension.
# $4: The runID the image should get. This is a string
#     without the surrounding '...' characteristic for
#     a string in FITS format
# $5: chips to be processed

for CHIP in $5
do
  ls -1 /$1/$2/*_${CHIP}$3fits > ${TEMPDIR}/uniqueidimages_$$

  cat ${TEMPDIR}/uniqueidimages_$$ |\
  {
    while read file
    do
      nextdummy ${file}
      if [ ${NEXTDUMMY} -ne -1 ]; then
        VALUE="'$4'"
	writekey ${file} RUN "${VALUE}" REPLACE
        # the following touch ensures that the file 
        # gets a new timestamp (necessary to overcome
        # kernel bugs not updating the change time after
        # memory mapping)
        touch ${file}
      fi
    done
  }
done