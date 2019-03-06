#!/bin/bash -xv

# the script gives every image a unique ID 
# (EISID) for the coaddition
# it replaces a superfluous keyword in image headers

# 
# 15.03.2003:
# the int number of the EISID keyword is now
# right justified
#
# 26.01.2004:
# The third argument now contains the "."
# before the fits extension. This prevents that
# empty strings have to be given as third argument
# (what made problem if this script was called
# within another script)
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 


. ${INSTRUMENT:?}.ini

# $1: main dir
# $2: science dir (the cat dir is a subdirectory of this)
# $3: extension (added by add_image_calibs)
#     This argument contains the "." before the fits
#     extension.
# $4: superfluous keyword to be replaced (BLANK, PI-COI)
# $5: starting value (usually 1)

ls -1 /$1/$2/*$3fits > ${TEMPDIR}/uniqueidimages_$$

i=$5

cat ${TEMPDIR}/uniqueidimages_$$ |\
{
  while read file
  do
    LEN=$(( 20 - ${#i} ))

    BLANK=""
    j=1
    while [ "${j}" -le "${LEN}" ]
    do
      BLANK="${BLANK} "
      j=$(( $j + 1 ))
    done  

    VALUE="${BLANK}${i}" 
    ${P_REPLACEKEY} ${file} "EISID   = ${VALUE}" "$4"
    i=$(( $i + 1 ))
  done
}
