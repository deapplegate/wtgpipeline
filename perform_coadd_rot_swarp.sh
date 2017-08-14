#!/bin/bash -xv
#. BonnLogger.sh
#. log_start
# the script coadds images with
# Emmanuels swarp program. It takes
# the resampled images created by
# resample_coadd_swarp_para.sh.
# So far it cannot be parallelised!
#
# Note that a coaddition with another header
# than that created by prepare_coadd_swarp.sh
# and later used by resample_coadd_swarp_para.sh
# leads to false results !!!

# 02.03.2004:
# The ending of the resampled FITS images is now
# "COADIDENT".resamp.fits instead of simply .resamp.fits
#
# 08.06.2006:
# The existence of the file 'coadd.head' is checked before 
# it is being copied.
#
# 17.07.2006:
# The swarp COMBINE_TYPE parameter can now be given
# as (optional) command line argument. If not provided,
# WEIGHTED is applied.

# 25.07.2006:
# The 'coadd.head' file stored in the reduce directory
# gets a unique name consisting of science dir. and
# co-addition identifier. This allows the execution of several
# co-additions simultaneously.

# 28.08.2006:
# The filenames to be co-added are passed to swarp no longer 
# on the command line but in a file instead. 

# 07.09.2006:
# I corrected a bug in the call to swarp. Images were passed
# on the command line AND via a file list.

# 17.02.2007:
# A flag map for the co-added image is created. It contains a '1'
# where the wqeight map is zero, i.e. bad pixels are marked.
# All other pixels get a value of zero. The flag map is an eight
# bit FITS image.


#$1: main dir.
#$2: science dir.
#$3: coadd identifier
#$4: swarp COMBINE_TYPE (OPTIONAL: WEIGHTED as default)

. ${INSTRUMENT:?}.ini

DIR=`pwd`

# construct a unique name for the coadd.head file
# of this co-addition:
#
# The following 'sed' ensures a 'unique' construction with the
# '/' character which can appear in arbitrary combinations in
# file- and pathnames.
TMPNAME_1=`echo ${1##/*/} | sed -e 's!/\{2,\}!/!g' -e 's!^/*!!' -e 's!/*$!!'`
TMPNAME_2=`echo ${2} | sed -e 's!/\{2,\}!/!g' -e 's!^/*!!' -e 's!/*$!!'`
COADDFILENAME0=${TMPNAME_1}_${TMPNAME_2}_${3}_ROT0
COADDFILENAME1=${TMPNAME_1}_${TMPNAME_2}_${3}_ROT1



cd /$1/$2/coadd_$3

if [ ! -f coadd.ROT0.head ]; then
  cp ${DIR}/coadd_${COADDFILENAME0}.head ./coadd.ROT0.head
fi
if [ ! -f coadd.ROT1.head ]; then
  cp ${DIR}/coadd_${COADDFILENAME1}.head ./coadd.ROT1.head
fi

# collect the files to be co-added
if [ -f files.list_$$ ]; then
  rm files.list_$$
fi




${P_FIND} . -name \*.$3.resamp.fits -print > files.list_$$

touch files.list_ROT0_$$
touch files.list_ROT1_$$

for file in `cat files.list_$$`; do
    BKSUB=`basename ${file} $3.resamp.fits`fits
# echo `imhead < ${BKSUB}| grep ROTATION `
    rot=`imhead < ${BKSUB}| grep ROTATION | awk '{print $2}'`
    if [ ${rot} -eq 0 ]; then
	echo ${file} >> files.list_ROT0_$$
    elif [ ${rot} -eq 1 ]; then
	echo ${file} >> files.list_ROT1_$$
    fi

done



#exit 0;


# set swarp COMBINE type:
COMBINETYPE="WEIGHTED"
if [ $# -eq 4 ]; then
  COMBINETYPE=$4
fi

# and simply go!!!
${P_SWARP} -c ${DATACONF}/create_coadd_swarp.swarp \
           -RESAMPLE N -COMBINE Y \
           -IMAGEOUT_NAME coadd.ROT0.fits \
           -WEIGHTOUT_NAME coadd.weight.ROT0.fits \
           -COMBINE_TYPE ${COMBINETYPE} \
           -INPUTIMAGE_LIST files.list_ROT0_$$


${P_SWARP} -c ${DATACONF}/create_coadd_swarp.swarp \
           -RESAMPLE N -COMBINE Y \
           -IMAGEOUT_NAME coadd.ROT1.fits \
           -WEIGHTOUT_NAME coadd.weight.ROT1.fits \
           -COMBINE_TYPE ${COMBINETYPE} \
           -INPUTIMAGE_LIST files.list_ROT1_$$

#rm files.list_$$


# create a flag map with name coadd.flag.fits.
# Pixels that are zero in the weight map, i.e. bad
# are masked with a '1' in the flag map.
${P_IC} -p 8 '1 0 %1 fabs 1.0e-06 < ?' \
        coadd.weight.ROT0.fits > coadd.flag.ROT0.fits

${P_IC} -p 8 '1 0 %1 fabs 1.0e-06 < ?' \
        coadd.weight.ROT1.fits > coadd.flag.ROT1.fits




cd ${DIR}

#log_status $?
