#!/bin/bash
set -xv
#adam-BL#. BonnLogger.sh
#adam-BL#. log_start
# this script performs resampling of data with swarp
# preparing the final coaddition. It can perform
# its task in parallel mode.

# 07.11.2003:
# I corrected a bug in the listing of files belonging to
# a certain chip. The old line
# FILES=`ls $1/$2/coadd_$4/*_${CHIP}*$3.fits` did not work
# correctly for more than 10 chips. 
#
# 25.11.2003:
# the location of the coadd.head file is now given
# as parameter (necessary for reductions on marvin
# where the reduction directories of the individual
# nodes is not the directory where the prepare_coadd_swarp
# script created it)
#
# 02.03.2004:
# The ending of the resampled FITS images is now
# "COADIDENT".resamp.fits instead of simply .resamp.fits
#
# 08.06.2006
# The file 'coadd.head' is no longer removed at the end
# of the processing. If being unlucky it is needed by another
# process exactly at the moment when it is removed by this 
# script. It does not matter if it is not removed anyway.
#
# 25.07.2006:
# The 'coadd.head' file stored in the reduce directory
# gets a unique name consisting of science dir. and
# co-addition identifier. This allows the execution of several
# co-additions simultaneously.
#
# 23.09.2006:
# The filenames of images to be resampled are passed to swarp 
# no longer on the command line but in a file instead. 
#
# 31.10.2006:
# I corrected a major bug introduced in the changes of 23.09.2006!
# (the script was not functional!)
#
# 21.03.2007:
# I included a test to check whether chips need to be co-added 
# at all. This cleanly treats cases where only individual chips
# of a mosaic should be co-added.


#$1: main dir.
#$2: science dir.
#$3: image extension (ext) on ..._iext.fits (i is the chip number)
#$4: coaddition identifier (4 char)
#$5: location of the global coadd.head file

# preliminary work:
. progs.ini > /tmp/out.out 2>&1

# construct a unique name for the coadd.head file
# of this co-addition:
#
# The following 'sed' ensures a 'unique' construction with the
# '/' character which can appear in arbitrary combinations in
# file- and pathnames.
TMPNAME_1=`echo ${1##/*/} | sed -e 's!/\{2,\}!/!g' -e 's!^/*!!' -e 's!/*$!!'`
TMPNAME_2=`echo ${2} | sed -e 's!/\{2,\}!/!g' -e 's!^/*!!' -e 's!/*$!!'`
COADDFILENAME=${TMPNAME_1}_${TMPNAME_2}_${4}
BONNDIR=`pwd`

for CHIP in $6
do
  RESULTDIR[${CHIP}]="/$1/$2/coadd_$4"      
done

for CHIP in $6
do

    cd ${RESULTDIR[${CHIP}]}

    if [ ! -f coadd.head ]; then
        cp $5/coadd_${COADDFILENAME}.head ./coadd.head
    fi

    ${P_FIND} . -maxdepth 1 -name \*_${CHIP}$3.copy.weight.fits > ${TEMPDIR}/weights_$$.list

    cat ${TEMPDIR}/weights_$$.list |\
    {
    while read file
    do
      BASE=`basename ${file} .copy.weight.fits`

      ic '1 %1 0 * +' ${file} > tmp_$$.weight.fits
      
      {
      echo "WEIGHT_NAMES tmp_$$.weight.fits,${BASE}.fits"
      echo "WEIGHT_MIN 0,-100"
      echo "WEIGHT_MAX 10, 20000"
      echo "WEIGHT_OUTFLAGS 0,2"
      #
      echo 'FLAG_NAMES ""'   
      echo 'FLAG_MASKS ""'   
      echo 'FLAG_WMASKS ""'  
      echo 'FLAG_OUTFLAGS ""'
      echo 'POLY_NAMES ""'   
      echo 'POLY_OUTFLAGS ""'
      #
      echo "OUTWEIGHT_NAME tmp2_$$.weight.fits"
      echo 'OUTFLAG_NAME ""'
      } > ${TEMPDIR}/${BASE}.ww_$$
      
      ${P_WW} -c ${TEMPDIR}/${BASE}.ww_$$
      rm -f ${TEMPDIR}/${BASE}.ww_$$
      
      ic '1e-6 %1 %1  0 == ?' tmp2_$$.weight.fits > ${file}

      rm -f tmp_$$.weight.fits tmp2_$$.weight.fits
    done
    }

    ${P_FIND} . -maxdepth 1 -name \*_${CHIP}$3.fits > ${TEMPDIR}/files_$$.list

  # test whether we have something to do at all! In case that only individual
  # chips need to be co-added it may be that the preceeding find command returns
  # an empty file.

    if [ -s ${TEMPDIR}/files_$$.list ]; then
    
      ${P_SWARP} -c ${DATACONF}/create_coadd_swarp.swarp \
                 -RESAMPLE Y -COMBINE N \
                 -RESAMPLE_SUFFIX .$4.resamp.fits \
                 -RESAMPLE_DIR . @${TEMPDIR}/files_$$.list\
                 -NTHREADS 1 #-VERBOSE_TYPE QUIET
                 #adam-old#-RESAMPLE_DIR . -INPUTIMAGE_LIST ${TEMPDIR}/files_$$.list\

	rm -f ${TEMPDIR}/files_$$.list

    fi

    ${P_FIND} . -maxdepth 1 -name \*_${CHIP}$3.copy.fits > ${TEMPDIR}/files_copy_$$.list

    if [ -s ${TEMPDIR}/files_copy_$$.list ]; then
    
      ${P_SWARP} -c ${DATACONF}/create_coadd_swarp.swarp \
                 -RESAMPLE Y -COMBINE N \
                 -RESAMPLE_SUFFIX .$4.resamp.fits \
                 -RESAMPLE_DIR . @${TEMPDIR}/files_copy_$$.list\
                 -NTHREADS 1 -RESAMPLING_TYPE BILINEAR
                 #adam-old# -RESAMPLE_DIR . -INPUTIMAGE_LIST ${TEMPDIR}/files_copy_$$.list\
      if [ "$?" -gt "0" ]; then exit $? ; fi

      rm -f ${TEMPDIR}/files_copy_$$.list

    fi


    ${P_FIND} . -name \*_${CHIP}$3.copy.$4.resamp.weight.fits > ${TEMPDIR}/filelist_$$
    cat ${TEMPDIR}/filelist_$$ |\
    {
    while read file
    do
      ic '%1 1e-16 *' ${file} > tmp_$$.fits
      mv tmp_$$.fits ${file}
    done
    }

    cd ${BONNDIR}

done  
#adam-BL#log_status $?
