#!/bin/bash
set -xv
#adam-example# ./resample_coadd_swarp_para.sh /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-J-B SCIENCE OCFI.sub MACS1115+01_all /u/ki/awright/bonnpipeline/
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

#adam-del# setstartchip='0'
#adam-del# startchip='0'
for CHIP in $6
do
  #adam-del# if [ ${setstartchip} -eq "0" ]; then
  #adam-del# 	  startchip=${CHIP}
  #adam-del# 	  setstartchip='1'
  #adam-del# fi
  RESULTDIR[${CHIP}]="/$1/$2/coadd_$4"      
done

for CHIP in $6
do

    cd ${RESULTDIR[${CHIP}]}

    if [ ! -f coadd.head ]; then
      cp $5/coadd_${COADDFILENAME}.head ./coadd.head
      cp coadd.head coadd.flag.head
    fi
    #adam-del# if [ ! -f ./coadd.head_${startchip} ]; then
    #adam-del#    cp $5/coadd_${COADDFILENAME}.head ./coadd.head_${startchip}
    #adam-del#    cp coadd.head_${startchip} coadd.flag.head_${startchip}
    #adam-del# fi

    ${P_FIND} . -maxdepth 1 -name \*_${CHIP}$3.fits > ${TEMPDIR}/files_$$.list

    # test whether we have something to do at all! In case that only individual
    # chips need to be co-added it may be that the preceeding find command returns
    # an empty file.

    if [ -s ${TEMPDIR}/files_$$.list ]; then
    
      #${P_SWARP} -c ${DATACONF}/create_coadd_swarp.swarp \
      #           -RESAMPLE Y -COMBINE N \
      #           -RESAMPLE_SUFFIX .$4.resamp.fits \
      #           -RESAMPLE_DIR . -INPUTIMAGE_LIST ${TEMPDIR}/files_$$.list\
      #           -NTHREADS 1 #-VERBOSE_TYPE QUIET
      ${P_SWARP} -c ${DATACONF}/create_coadd_swarp.swarp \
                 -RESAMPLE Y -COMBINE N \
                 -RESAMPLE_SUFFIX .$4.resamp.fits \
                 -RESAMPLE_DIR . @${TEMPDIR}/files_$$.list\
                 -NTHREADS 1 -VERBOSE_TYPE FULL
                 #adam-old# -HEADER_SUFFIX .head_${startchip} \
	if [ "$?" -gt "0" ]; then exit $? ; fi
	#adam-tmp# rm -f ${TEMPDIR}/files_$$.list
    else
      echo "adam-look resample_coadd_swarp_para.sh: nothing in ${TEMPDIR}/files_$$.list"

    fi

    ${P_FIND} . -maxdepth 1 -name \*_${CHIP}$3.flag.fits > ${TEMPDIR}/files.flag_$$.list
    if [ "$?" -gt "0" ]; then exit $? ; fi
    if [ -s ${TEMPDIR}/files.flag_$$.list ]; then

	while read file
	do
	  BASE=`basename ${file} .flag.fits`

    	  #write config file for ww
    	  echo "WEIGHT_NAMES ${BASE}.weight.fits"                         >  ${TEMPDIR}/${BASE}.ww_$$
          echo 'WEIGHT_MIN "1e-12"'                                       >> ${TEMPDIR}/${BASE}.ww_$$
          echo 'WEIGHT_MAX "1e12"'                                        >> ${TEMPDIR}/${BASE}.ww_$$
    	  echo 'WEIGHT_OUTFLAGS "16"'                                     >> ${TEMPDIR}/${BASE}.ww_$$
    	  #										  
    	  echo "FLAG_NAMES ${file}"                                       >> ${TEMPDIR}/${BASE}.ww_$$
    	  echo 'FLAG_MASKS "0x7f"'                                        >> ${TEMPDIR}/${BASE}.ww_$$
    	  echo 'FLAG_WMASKS "0x0"'                                        >> ${TEMPDIR}/${BASE}.ww_$$
    	  echo 'FLAG_OUTFLAGS "32,64,128,256,512,1024,2048"'              >> ${TEMPDIR}/${BASE}.ww_$$
    	  #										  
          echo 'POLY_NAMES ""'                                            >> ${TEMPDIR}/${BASE}.ww_$$
          echo 'POLY_OUTFLAGS ""'                                         >> ${TEMPDIR}/${BASE}.ww_$$
	  #
    	  echo 'OUTWEIGHT_NAME ""'                                        >> ${TEMPDIR}/${BASE}.ww_$$
    	  echo "OUTFLAG_NAME ${TEMPDIR}/${BASE}.flag.fits"                >> ${TEMPDIR}/${BASE}.ww_$$

	  ${P_WW} -c ${TEMPDIR}/${BASE}.ww_$$
	  if [ "$?" -gt "0" ]; then exit $? ; fi
	  #adam-tmp# rm -f ${TEMPDIR}/${BASE}.ww_$$

	  INSTRUM=`dfits "${BASE}.fits" | fitsort -d INSTRUM | awk '{print $2}'`
	  CONFIG=`dfits "${BASE}.fits" | fitsort -d CONFIG | awk '{print $2}'`
	  IMAGEID=`dfits "${BASE}.fits" | fitsort -d IMAGEID | awk '{print $2}'`
	  case ${INSTRUM} in
	      "SUBARU" | "'SUBARU'" )
		  CCDTYPE=`${P_GAWK} '{if($1=='${IMAGEID}') print 2^($2-1)}' ${BONNDIR}/chip_types_c${CONFIG}.dat` ;;
	      "CFH12K" | "'CFH12K'" )
		  CCDTYPE=`${P_GAWK} '{if($1=='${IMAGEID}') print 2^($2-1)}' ${BONNDIR}/chip_types_CFH12K.dat` ;;
	      * )
		  CCDTYPE=1 ;;
	  esac

	  rm -f ${file}
	  ${P_IC} '%1 '${CCDTYPE}' +' ${TEMPDIR}/${BASE}.flag.fits > ${file}
	  if [ "$?" -gt "0" ]; then exit $? ; fi
	  rm -f ${TEMPDIR}/${BASE}.flag.fits
	  
	done < ${TEMPDIR}/files.flag_$$.list
      
      ${P_SWARP} -c ${DATACONF}/create_coadd_swarp.swarp \
	  -BACK_TYPE MANUAL \
	  -BACK_DEFAULT 0.0 \
	  -COMBINE N -RESAMPLE Y \
	  -FSCALASTRO_TYPE NONE \
	  -FSCALE_KEYWORD FKESCALE \
	  -IMAGEOUT_NAME coadd.flag.fits \
	  -RESAMPLE_DIR . \
	  -RESAMPLE_SUFFIX .$4.resamp.fits \
	  -RESAMPLING_TYPE NEAREST \
	  -SUBTRACT_BACK N \
	  -WEIGHTOUT_NAME "./dummy_$$.fits" \
	  -WEIGHT_TYPE NONE \
	  -VERBOSE_TYPE FULL \
	  -NTHREADS 1 \
	  -MEM_MAX 4096 \
	  -VMEM_MAX 6144 \
	  -VMEM_DIR "/tmp" \
	  @${TEMPDIR}/files.flag_$$.list
          #adam-old# -HEADER_SUFFIX .flag.head_${startchip} \
	  #adam-old#-INPUTIMAGE_LIST ${TEMPDIR}/files.flag_$$.list
	  #adam-old# -COMBINE_TYPE MAX \
      if [ "$?" -gt "0" ]; then exit $? ; fi
      #adam-tmp# rm -f ${TEMPDIR}/files.flag_$$.list *.flag.$4.resamp.weight.fits
      rm -f *.flag.$4.resamp.weight.fits
    else
      echo "adam-look resample_coadd_swarp_para.sh: nothing in ${TEMPDIR}/files.flag_$$.list"
    fi
    cd ${BONNDIR}

done
