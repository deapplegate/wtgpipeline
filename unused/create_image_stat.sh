#!/bin/bash -xv

# Written 2004-10-12 by
# Joerg Dietrich <dietrich@astro.uni-bonn.de>
#
# requires GNU paste !!
#

# creates statistics about OC 
# images of calibration files
# these are mainly needed for the
# creation of WEB pages (script pipelog.py).
# The statistics are saved in the form
# of a catalog chip_?_stat.cat in a cat
# subdirectory.
#
# 25.11.04:
# Bug fixes for the use of exptime.
#
# 24.11.04:
# - I included the image ending as command line
#   argument (was always OC before)
# - The exposure time is now included in the
#   stat catalog.
#
# 14.07.05:
# Add _${CHIP}_ to all immode files to avoid name collisions between
# parallel processes. To the same end I removed a 'cd' command to the
# /$1/$2 directory and continue working in the working directory.
#
# 04.12.2005:
# I rewrote the script so that it uses the imstats from the imcat
# utilities instead of immode from FLIPS.
#
# 05.12.2005:
# The initial file list for the imstats command comes from a simple
# command line expansion now. The older find command did not ensure 
# a certain order of the elements which lead to errors when the
# imstats results were merged with those from dfits.

# $1: main directory
# $2: calib directory
# $3: image ending
# $4: chip

. ${INSTRUMENT:?}.ini

if [ ! -d "/$1/$2/cat" ]; then
    mkdir /$1/$2/cat
fi

for CHIP in $4
do
    ${P_IMSTATS} /$1/$2/*_${CHIP}$3.fits -s \
	${STATSXMIN} ${STATSXMAX} ${STATSYMIN} ${STATSYMAX} -o \
	${TEMPDIR}/immode.dat_${CHIP}_$$

    ${P_GAWK} '($1 != "#") {l=split($1, file, "/"); print file[l], $2, $3, $4, $5}' ${TEMPDIR}/immode.dat_${CHIP}_$$ > ${TEMPDIR}/stat_cat_in_${CHIP}_1_$$
    ${P_DFITS} /$1/$2/*_${CHIP}$3.fits | ${P_FITSORT} -d EXPTIME | ${P_GAWK} '{print $2}' \
	> stat_cat_in_${CHIP}_2_$$
    paste stat_cat_in_${CHIP}_1_$$ stat_cat_in_${CHIP}_2_$$ > ${TEMPDIR}/stat_cat_in_${CHIP}_$$
    ${P_ASCTOLDAC} -i ${TEMPDIR}/stat_cat_in_${CHIP}_$$ -o /$1/$2/cat/chip_${CHIP}_stat.cat -t IMAGES \
	-c ${CONF}/create_image_stat.asctoldac.conf

    rm ${TEMPDIR}/immode.dat_${CHIP}_$$
    rm ${TEMPDIR}/stat_cat_in_${CHIP}_?_$$ ${TEMPDIR}/stat_cat_in_${CHIP}_$$
done
    
    