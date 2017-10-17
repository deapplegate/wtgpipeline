#!/bin/bash
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# this script creates text files with frames
# belonging to a certain 'run'. It is assumed
# that the information about the run is stored
# in a header keyword "RUN".

# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 08.07.2004:
# I introduced the possibility to split up runs 
# having too many images (given in the NSPLIT 
# variable) below
#
# 09.07.2004:
# corrected a bug in the creation of the new uniqruns.txt
# file in case of splitting
#
# 18.07.2006:
# - The header keyword identifying a RUN is now an command
#   line argument and no longer 'RUN' by default.
# - Temporary files get unique filenames including the
#   process number.
#
# 21.09.2006:
# The script has a new command line option to give the
# output file containing the list of runs contained in
# the image set under consideration. This change was made
# to ensure unique names for all produced files. 

# TODO:
# The script creates searches for candidate runs in
# the chips labelled with '1'. This is potentially dangerous
# if chip 1 does not exist for some reason.

#$1: main directory
#$2: science dir.
#$3: image extension (ext) on ..._iext.fits (i is the chip number)
#$4: Header keyword identifying the runs 
#$5: output file containing the output list of all runs
#    (The file will reside in ${TEMPDIR})
#$6: SPLIT/NOSPLIT (optional)

. ${INSTRUMENT:?}.ini

# in case of splitting: the maximum number of files
# so that no splitting takes place
NSPLIT=30

# first find out which runs exist at all
ls -1 /$1/$2/*_1$3.fits > ${TEMPDIR}/files_$$

if [ -f ${TEMPDIR}/runs_$$ ]; then
  rm -f ${TEMPDIR}/runs_$$
fi

cat ${TEMPDIR}/files_$$ |\
{
  while read image
  do 
    ${P_DFITS} ${image} | ${P_FITSORT} -d $4 | ${P_GAWK} '{printf("%s_%s\n", $2, '$$')}' >> ${TEMPDIR}/runs_$$ 
  done
}

sort ${TEMPDIR}/runs_$$ | uniq > ${TEMPDIR}/$5

cat  ${TEMPDIR}/$5 |\
{
  while read run
  do
    if [ -f ${run}.txt ]; then
      rm -f ${run}.txt
    fi
  done
}

# now go through the images again and create
# the run files
cat ${TEMPDIR}/files_$$ |\
{
  while read image
  do 
    RUN=`${P_DFITS} ${image} | ${P_FITSORT} -d $4 | ${P_GAWK} '{printf("%s_%s", $2, '$$')}'`
    BASE=`basename ${image} _1$3.fits`
    echo ${BASE} >> ${RUN}.txt
  done
}

# perform splitting of runs that are too large
# (for LDAC astrometry for instance)
if [ $# -gt 5 ]; then
  if [ "$6" = "SPLIT" ]; then

    if [ -f  ${TEMPDIR}/uniqruns_new_$$.txt ]; then
      rm -f ${TEMPDIR}/uniqruns_new_$$.txt
    fi
 
    cat  ${TEMPDIR}/$5 |\
    {
	while read run
        do
	  NFILES=`wc ${run}.txt | ${P_GAWK} '{print $1}'`
	  NSUBRUNS=`wc ${run}.txt | ${P_GAWK} '{print int($1/'${NSPLIT}')+1}'`
	  if [ ${NSUBRUNS} -le 1 ]; then
	      echo ${run} >> ${TEMPDIR}/uniqruns_new_$$.txt
	  else
	      NLINES=`gawk 'BEGIN{ print int('${NFILES}'/'${NSUBRUNS}'+1.0)}'`
	      split --lines=${NLINES} ${run}.txt ${run}

	      i=1
	      for file in `ls ${run}a*`
	      do
	        mv ${file} ${run}_${i}.txt
		echo ${run}_${i} >> ${TEMPDIR}/uniqruns_new_$$.txt
		i=$(( $i + 1 ))		
	      done
          fi

        done
    }
    mv ${TEMPDIR}/uniqruns_new_$$.txt ${TEMPDIR}/$5
  fi
fi

# clean up temporary files:
rm -f ${TEMPDIR}/files_$$
rm -f ${TEMPDIR}/runs_$$

if [ -f ${TEMPDIR}/uniqruns_new_$$.txt ]; then
  rm -f ${TEMPDIR}/uniqruns_new_$$.txt
fi
#adam-BL# log_status $?
