#!/bin/bash
set -xv

# script to convolve an image to a 'worse' seeing
# with a Gaussian kernel
#
# The script implicitely assumes a zero background
# of the original image

# HISTORY
# =======
#
# 28.11.2008:
# temporary files are removed at the end of the script.


#$1: path to image
#$2: science image name
#$3: weight image name
#$4: original seeing of image (run determine_seeing.sh)
#$5: new seeing
#$6: name of convolved image; it will go $1

. progs.ini

PIXSCALE=`dfits $1/$2 | fitsort -d CDELT1 | awk '{print -3600*$2}'`


# It is necessary to delete 'old' smoothing kernels because
# we do not yet know which filename will be given to a new one:
${P_FIND} $1 -name gauss\*conv -exec rm -f {} \;

# first determine a smoothing kernel:
./create_gausssmoothing_kernel.py $4 $5 ${PIXSCALE} $1 

# It does not matter which config file we use for the following
# SExtractor run:
${P_SEX} $1/$2\
    -c ${SCIENCECONF}/default.sex \
    -PARAMETERS_NAME ${SCIENCECONF}/default.param\
    -CATALOG_NAME ${TEMPDIR}/tmp.cat_$$ \
    -WEIGHT_IMAGE $1/$3 -WEIGHT_TYPE MAP_WEIGHT\
    -CHECKIMAGE_TYPE FILTERED \
    -CHECKIMAGE_NAME /$1/$6 \
    -FILTER_NAME $1/gauss.conv \
    -FILTER Y\
    -PIXEL_SCALE ${PIXSCALE}\
    -BACK_TYPE MANUAL \
    -BACK_VALUE 0.0 \
    -DETECT_MINAREA 20 -DETECT_THRESH 50

test -f ${TEMPDIR}/tmp.cat_$$ && rm -f ${TEMPDIR}/tmp.cat_$$
