#!/bin/bash
set -xv
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# checks images for integrity. For the moment
# this consists of calculating the mode and
# shifting images that are under/over a given mode
# to a BADMODE directory
# the script cannot be parallelised as chips in
# one parallel channel may be filtered and not in
# another. But we want to filter all chips of an
# image that has ONE or more bad chips
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 11.04.2005:
# I rewrote the script to use the 'imstats' program
# instead of the FLIPS based 'immode'.
#
# 12.04.2005:
# I substituted XMIN etc. by STATSXMIN etc. that are
# now defined in the in the instrument initialisation
# files.
#
# 14.08.2005:
# The call of the UNIX 'find' program is now done
# via a variable 'P_FIND'.
#
# 09.09.2005:
# I corrected a bug in the FIND command. We need to
# test regular files and links, not only regular files.
#
# 12.09.2005:
# The imstats call is now done chip by chip. This prevents
# an "Argument list too long error" for cameras with many
# chips (e.g. MMT with 72).
#
# 05.12.2005:
# - Chips whose NOTUSE or NOTPROCESS flag is set are not considered in
#   the statistics that determine whether to reject exposures.
# - Temporary files are now cleaned up at the end of the
#   script
# - I added a missing TEMPDIR

# $1: main directory (filter)
# $2: science directory
# $3: ending (OFCSFF etc.)
# $4: low limit of files labelled as GOOD
# $5: high limit of files labelled as GOOD

# preliminary work:
. ${INSTRUMENT:?}.ini

if [ -f alldata_$$.dat ]; then
  rm -f alldata_$$.dat
fi

i=1
while [ "${i}" -le "${NCHIPS}" ]
do
  if [ ${NOTUSE[${CHIP}]:=0} -eq 0 ] && [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    ${P_IMSTATS} `${P_FIND} /$1/$2/ \( -type f -o -type l \) -name \*_${i}$3.fits -maxdepth 1` -s \
                 ${STATSXMIN} ${STATSXMAX} ${STATSYMIN} ${STATSYMAX} -o \
                 ${TEMPDIR}/immode.dat_$$

    cat ${TEMPDIR}/immode.dat_$$ >> ${TEMPDIR}/alldata_$$.dat
  else
    echo "Chip ${CHIP} will not be used in $0"  
  fi
  i=$(( $i + 1 ))
done

# now get all sets that have to be moved:
${P_GAWK} '($1 != "#") { if ($2<'$4' || $2 >'$5') {a=match($1, "_[0-9]*'$3'.fits"); print substr($1,1,a-1)}}' \
          ${TEMPDIR}/alldata_$$.dat > ${TEMPDIR}/move_$$

# now do the moving
cat ${TEMPDIR}/move_$$ |\
{
  while read file
  do
    DIR=`dirname ${file}`
    if [ ! -d "${DIR}/BADMODE" ]; then
	mkdir "${DIR}/BADMODE"
    fi

    i=1
    while [ "${i}" -le "${NCHIPS}" ]
    do
      # the following 'if' is necessary as the
      # file(s) may already have been moved
      if [ -f "${file}_${i}$3.fits" ]; then
	 mv ${file}_${i}$3.fits ${DIR}/BADMODE
      fi
      i=$(( $i + 1 ))
    done
  done
}

# clean up:
rm -f ${TEMPDIR}/alldata_$$.dat ${TEMPDIR}/move_$$ ${TEMPDIR}/immode.dat_$$
#adam-BL# log_status $?
