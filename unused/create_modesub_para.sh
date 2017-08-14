#!/bin/bash -xv

# the script subtracts the mode from the input images
# (with Nick Kaisers stats program). It is used to
# subtract a remaining, non zero, mode from swarp
# resampled images before they are coadded.

# 22.12.2005:
# - I introduced a prefix as selection criterium of the
#   images whose mode has to be subtracted.
# - For the extension the "." before in final .fits extension
#   has to be included in the command line argument now.
#   This avoids empty command line arguments in some 
#   circumstances.
#
# 21.03.2007:
# - I replaces an 'ls' command to search for files
#   by 'find' (more robust to long lists; no error message
#   in case that no files are present).
# - not needed, temporary, files are deleted at the end of 
#   processing.

# $1: main directory
# $2: science directory
# $3: prefix
# $4: extension (including a . before the fits extension)
# $5: chips to be processed

. ${INSTRUMENT:?}.ini

# the chips that are to be processed
for CHIP in $5
do
  ${P_FIND} /$1/$2/ -name ${3}\*_${CHIP}${4}fits > \
            ${TEMPDIR}/modesub_images${CHIP}_$$
  
  cat ${TEMPDIR}/modesub_images${CHIP}_$$ |\
  {
    while read file
    do
      if [ -L ${file} ]; then
          LINK=`${P_READLINK} ${file}`
          RESULTDIR[${CHIP}]=`dirname ${LINK}`
      else
	      RESULTDIR[${CHIP}]="/$1/$2"
      fi

      BASE=`basename ${file} ${4}fits`
      MODE=`${P_STATS} < ${RESULTDIR[${CHIP}]}/${BASE}"${4}fits" | gawk '($1=="mode") {print $3}'`

      ${P_IC} '%1 '${MODE}' -' ${RESULTDIR[${CHIP}]}/${BASE}"${4}fits" > \
                               ${RESULTDIR[${CHIP}]}/${BASE}"tmp.fits"
      mv ${RESULTDIR[${CHIP}]}/${BASE}"tmp.fits" ${RESULTDIR[${CHIP}]}/${BASE}"${4}fits"
    done    
  }

  test -f ${TEMPDIR}/modesub_images${CHIP}_$$ && rm ${TEMPDIR}/modesub_images${CHIP}_$$
done


