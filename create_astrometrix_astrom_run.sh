#!/bin/bash
set -xv
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
. ${INSTRUMENT:?}.ini

# this script performs astrometry by using astrometrix 
# this version performs operations only on the images contained
# in a list (typically a run)
#
# 12.05.2004:
# I removed linking of previously created catalogs by
# singleastrom. The configuration parameters of ASTROMETRIX
# seem to give better results when performing astrometry
# with ASTROMETRIX. Hence, new catalogs are created.
#
# 25.06.2004:
# introduced the possibility to give a standardstar catalog
# for ASTROMETRIX (optional argument; if none is given USNO
# is used)
#
# 09.07.2004:
# I again use the catalogs created from singleastrom as
# input for ASTROMETRIX. They are cleaner now where we
# use weights in the creation of singleframe catalogs.
#
# 14.04.2005:
# - I rewrote the script significantly so that it performs
#   the 'initk' step indenpendently on several runs but considers
#   all runs simultaneously in the 'global' step.
#   The fourth argument now gives the standardstar catalog to
#   be used (it HAS to be given now) and the 5th argument up
#   to the last argument the run lists of a set.
# - I corrected a bug in the final header writing.
#
# 22.12.2005:
# - I changed the selection criteria for the catalogs to be used.
#   Now all objects are required to have a semi minor axis larger
#   than 2 pixels (SExtractor parameter B_IMAGE) and we now tolerate
#   objects that have close neighbours or that are saturated.
#   We experienced that usually the position of such objects still
#   can be determined accurately enough and hence astrometric
#   alignments are more accurate.
# - An image list consisting of all images processed in the
#   runs is created. This list is necessary if PHOTOMETRIX
#   is called after ASTROMETRIX.
#
# 28.08.2006:
# more robust file listing by 'find' instead of 'ls'.
# The letter led to 'Argument list too long' errors when
# many images are involved in the processing.
#
# 07.04.2007:
# I changed/included the following parameters in the ASTROMETRIX
# initk step:
# radius:     60 -> 65
# pstol:      3 (new parameter)
# MAXNUM_LIN: 20000 -> 30000
# Those parameters are driven by CFHTLS data. They have to be
# made configurable at some point.
#
# 07.05.2007:
# For each run the image with the highest object number (and
# hence that taken under the best observing conditions IF we
# assume equal exposure times) is taken as reference for determining
# the linear offset (ASTROMETRIX initk step)
#
# 03.08.2007:
# Increase of the maximum number of standardstar objects retrieved
# via the net. We now reject objects fainter than mag 20 within
# ASTROMETRIX. Hence, there is no reason to not request all available
# objects first.
#
# 22.08.2007:
# The executable of SExtractor is set to 'sex_theli' as
# it is called now within the THELI pipeline.
#
# 23.10.2007:
# If the linear solution (astrometrix initk step) for some image
# is not acceptable we perform this step iteratively with other 
# images in the set.

# TODO:
# We could do a better job in determining the 'best' image
# for linear offset determination (changes from 07.05.2007) 
# by taking into account the exposure time of images.

# CVSId: $Id: create_astrometrix_astrom_run.sh,v 1.5 2009-01-16 22:19:13 anja Exp $

# $1: main dir.
# $2: science dir. (the cat dir is a subdirectory of this)
# $3: extension
# $4: standardstar catalog to use (OPTIONAL: default to USNO)
# $5-$#: lists of files to be processed (the lists have to contain the
#        BASENAMES of the files, i.e. filename=BASENAME_${CHIP}$3.fits;
#        the lists have to be given together with the full path)

STARCAT=$4
LISTS=""
DIR=`pwd`

# preliminary work:

cd /$1/$2/

if [ ! -d "astrom" ]; then
  mkdir astrom
  mkdir astrom/$2
fi

cd astrom/$2

# create links for the catalogs as those have
# already been created for the LDAC astrometric
# solution

FILES=`${P_FIND} /$1/$2/cat/ -maxdepth 1 -name \*$3.cat`

for CAT in ${FILES}
do
  BASE=`basename ${CAT} .cat`
#  ${P_LDACFILTER} -i ${CAT} -t LDAC_OBJECTS -c "(FLAGS<1);" \
#                  -o ${BASE}.ldac
  ${P_LDACFILTER} -i ${CAT} -t LDAC_OBJECTS -c "((FLAGS<2)OR(FLAGS=16))AND(B_IMAGE>2.0);" \
                  -o ${BASE}.ldac

done

cd ..

# remove global list (for photometrix) if it
# exists already:
if [ -f $2.list ]; then
  rm -f $2.list
fi

# now run 'astrom -initk' on all runs individually:
j=5
while [ "${j}" -le "$#" ]
do
  # first create the astrometrix filelist from the run
  # to be considered:
  
  LISTBASE=`basename ${!j} .txt`
  
  # build list argument for global astrometry call:
  if [ "${j}" -eq "5" ]; then
    LISTS="$2_${LISTBASE}.list"    
  else
    LISTS="${LISTS},$2_${LISTBASE}.list"  
  fi 
  
  # count the number of objects in each exposure
  # We want to choose that with the largest number
  # of objects as the reference for determining 
  # a first order solution.
  BASE=`basename ${!j}`
  test -f nobjs_${BASE} && rm -f nobjs_${BASE}

  while read file
  do
    i=1
    NOBJ=0
    while [ "${i}" -le "${NCHIPS}" ]
    do
      NOBJIM=`${P_LDACTOASC} -b -i ./$2/${file}_${i}$3.ldac -t LDAC_OBJECTS -k NUMBER | wc -l`
      NOBJ=`${P_GAWK} 'BEGIN{print '${NOBJ}'+('${NOBJIM}'+0)}'`
      i=$(( $i + 1 )) 
    done
    echo ${file}" "${NOBJ} >> nobjs_${BASE}
  done < ${!j}

  # sort according to object number and put the
  # exposure with the largest object number on top of
  # the list so that ASTROMETRIX uses it as reference.
  ${P_SORT} -g -r -k 2,2 nobjs_${BASE} | awk '{print $1}' > sort_nobjs_${BASE}

  NFILES=`wc -l sort_nobjs_${BASE} | cut -d " " -f 1,1`

  # If the image with the highest number of objects does not give
  # a satisfactory linear solution we repeak the astrometrix 'initk'
  # step with the image having the second highest number of objects
  # and so on. The acceptance is determined with the variance of the
  # linear offsets from individual chips. Typically the linear offset 
  # is several hundred pixels for some chip if anything went wrong 
  # and hence such cases are easily identified.
  ACCEPT=0
  ELEMENT=1
  while [ ${ACCEPT} -eq 0 ] && [ ${ELEMENT} -le ${NFILES} ]
  do
    ${P_GAWK} 'BEGIN { start='${ELEMENT}' } { line[NR] = $0 } 
               END { 
               print line[start]; 
               for(i = 1; i <= NR; i++)
               {
                 if(i != start)
                 {
                   print line[i];
                 }
               }}' sort_nobjs_${BASE} > ${TEMPDIR}/tmp.txt_$$

    test -f $2_${LISTBASE}.list && rm -f $2_${LISTBASE}.list

    while read FILE
    do
      i=1
      while [ "${i}" -le "${NCHIPS}" ]
      do
        echo $2/${FILE}_${i}$3.fits >> $2_${LISTBASE}.list
        if [ ${ELEMENT} -eq 1 ]
        then
          # create global list for photometrix
          echo $2/${FILE}_${i}$3.fits >> $2.list
        fi

        i=$(( $i + 1 )) 
      done
    done < ${TEMPDIR}/tmp.txt_$$

    ${P_PERL} -e 'print join("\n", @INC);'
    ${P_PERL} ${S_ASTROMETRIX} \
     -initk -s table=$2_${LISTBASE}.dat -s list=$2_${LISTBASE}.list \
     -s fits_dir=$1 -s catalog=${STARCAT} \
     -s narrow=n -s thresh=10 -s radius=65 -s groupccd=y -s cats_dir="" \
     -s MAXNUM_LIN=100000 -s outdir_top=/$1/$2/astrom -s pstol=3. \
     -s SEX=sex_theli   
    
    # test whether the linear solution is acceptable.
    # We consider the variance of the linear shifts for individual
    # chips and reject the solution if it is too large.
    # The acceptance variance is hardcoded to 70 in the moment.
    # (TO BE IMPROVED).
    # If less than 3 chips are involved we DO NOT perform this check.
    FAIL=`${P_GAWK} 'BEGIN {meanoffx = 0.; meanoffy = 0.; 
                            sigmaoffx = 0.; sigmaoffy = 0.; n = 0} 
                     $1 !~ /^#/ {meanoffx += $2; meanoffy += $3; 
                                 sigmaoffx += $2 * $2; sigmaoffy += $3 * $3; 
                                 n += 1} 
                     END { if( n > 2)
                           {
                             meanoffx /= n; meanoffy /= n; 
                             sigmaoffx = sqrt(sigmaoffx / n - meanoffx**2);
                             sigmaoffy = sqrt(sigmaoffy / n - meanoffy**2);
                             if( sigmaoffx > 70. || sigmaoffy > 70.)
                             {
                               print 1;
                             }
                             else
                             {
                               print 0;
                             }
                           }
                           else
                           {
                             print 0;
                           }
                         }' $2_${LISTBASE}.dat`

    if [ ${FAIL} -eq 1 ]
    then
      mv  $2_${LISTBASE}.dat $2_${LISTBASE}_run${ELEMENT}.dat
      ELEMENT=$(( ${ELEMENT} + 1 ))
    else
      ACCEPT=1
    fi
  done

  j=$(( $j + 1 ))
done

${P_PERL} ${S_ASTROMETRIX} -global -s list=${LISTS}

cd ..

# finally copy the astrometrix headers to the right place
# and rename them

if [ ! -d "headers" ]; then
  mkdir headers
fi

${P_FIND} ./astrom/astglob/ -name \*head -exec cp {} ./headers \;

cd ./headers
${P_FIND} . -name \*_1$3.head -print > files_$$

while read file
do
  i=1
  BASE=`basename ${file} _1$3.head`
  while [ "${i}" -le "${NCHIPS}" ]
  do
    mv ${BASE}_${i}$3.head ${BASE}_${i}.head
    i=$(( $i + 1 )) 
  done
done < files_$$

rm -f files_$$

cd ${DIR}



#adam-BL# log_status $?
