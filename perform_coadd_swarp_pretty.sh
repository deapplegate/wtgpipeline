#!/bin/bash
set -xv
#adam-BL#. BonnLogger.sh
#adam-BL#. log_start
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

. progs.ini > /tmp/progs.out 2>&1

BONNDIR=`pwd`
HEADDIR="/u/ki/awright/data/coadd_headers/" 

# construct a unique name for the coadd.head file
# of this co-addition:
#
# The following 'sed' ensures a 'unique' construction with the
# '/' character which can appear in arbitrary combinations in
# file- and pathnames.
TMPNAME_1=`echo ${1##/*/} | sed -e 's!/\{2,\}!/!g' -e 's!^/*!!' -e 's!/*$!!'`
TMPNAME_2=`echo ${2} | sed -e 's!/\{2,\}!/!g' -e 's!^/*!!' -e 's!/*$!!'`
COADDFILENAME=${TMPNAME_1}_${TMPNAME_2}_${3}

cd /$1/$2/coadd_$3

if [ ! -f coadd.head ]; then
  cp ${HEADDIR}/coadd_${COADDFILENAME}.head ./coadd.head
  cp ./coadd.head ./coadd.flag.head
fi

# collect the files to be co-added
if [ -f files.list_$$ ]; then
  rm -f files.list_$$
fi

if [ -f files.sizes_$$ ]; then
  rm -f files.sizes_$$
fi
sleep 5

${P_DFITS} *.sub.$3.resamp.fits | ${P_FITSORT} -d NAXIS1 NAXIS2 > files.sizes_$$

while read file naxis1 naxis2
do
  if [ ${naxis1} -eq 1 ] || [ ${naxis2} -eq 1 ]; then
      base=`basename ${file} .sub.$3.resamp.fits`
      rm -f ${base}*fits
  fi
done < files.sizes_$$

${P_FIND} . -name \*.sub.$3.resamp.fits -print > files.list_$$

if [ ! -s files.list_$$ ]; then
    echo "No Files Found!"
    #adam-BL#log_status 2 "No Files Found!"
fi

### set swarp COMBINE type:
COMBINETYPE="WEIGHTED"
if [ $# -eq 4 ]; then
  COMBINETYPE=$4
fi

##### and simply go!!!
${P_SWARP} -c ${DATACONF}/create_coadd_swarp.swarp \
           -RESAMPLE N -COMBINE Y \
           -IMAGEOUT_NAME coadd.fits \
           -WEIGHTOUT_NAME coadd.weight.fits \
           -COMBINE_TYPE MEDIAN \
           -NTHREADS ${NPARA} \
           -MEM_MAX 4096 \
           -VMEM_MAX 6144 \
           -VMEM_DIR "/tmp" \
           @files.list_$$
           #adam-old#-INPUTIMAGE_LIST files.list_$$

rm -f files.list_$$ files.sizes_$$

mv coadd.fits median.fits
mv coadd.weight.fits median.weight.fits

swarp *copy*.resamp.fits median.fits -c ${DATACONF}/create_coadd_swarp.swarp \
           -RESAMPLE N -COMBINE Y -COMBINE_TYPE WEIGHTED

rm -f median.fits median.weight.fits *.sub.*fits *.sub.head *.sub.copy.head

cd ${BONNDIR}

#adam-BL#log_status $?
