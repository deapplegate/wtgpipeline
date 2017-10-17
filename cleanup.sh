#!/bin/bash
set -xv



#Cleans up run directories.
############
#WARNING: DO NOT RUN THIS UNLESS PREPROCESSING/COADDING IS DONE!!!!
#############

# $1 : Directory to cleanup

#CVSID $Id: cleanup.sh,v 1.11 2009-08-27 20:03:57 dapple Exp $

##################################

echo "******************************************************************"
echo "WARNING: DO NOT RUN THIS UNLESS PREPROCESSING/COADDING IS DONE!!!!"
echo "******************************************************************"
echo ""
echo ""
#echo "Confirm: Runs cleanup.sh on $1? [y/n]"
#read
#
#if [ "$REPLY" != "y" ]; then
#    echo "Exiting!"
#    exit 0;
#fi
#
#################################

CURDIR=`pwd`


##################################

function zipdir {
    # $1 : dir to zip
    echo "Zipping $1"
    if [ -d $1 ]; then
	files=`find $1 -name \* -print | awk '($1 !~ /ORIGINALS/){print}'`
	if [ ! -z "$files" ]; then
	    gzip $files
	fi
	if [ -n "${files}" ] && [ -e "$1.tarz" ]; then
	    rm -f $1.tarz
	fi
    fi
    echo "Done"

}

################################

function remdir {
    # $1 : dir
    echo "Removing $1"
    if [ -d $1 ]; then
	rm -rf $1
	echo "Done"
    else
	echo "$1 Doesn't Exist!"
    fi
}

#################################

cd $1
zipdir BASE_WEIGHT
zipdir DOMEFLAT_norm
zipdir SKYFLAT_norm
zipdir SCIENCE_norm

#NOT SPLIT_IMAGES, needed for badoverscan masking
remdir SCIENCE/OC_IMAGES
rm -f SCIENCE/*OC.fits

remdir SCIENCE_weighted
remdir SCIENCE_mask
zipdir WEIGHTS

if [ -d DOMEFLAT_SET0 ]; then
    rm -f DOMEFLAT_SET0/SUPA*.fits
    remdir DOMEFLAT_SET0/BINNED
fi

if [ -d SKYFLAT_SET0 ]; then
    rm -f SKYFLAT_SET0/SUPA*.fits
    remdir SKYFLAT_SET0/BINNED
fi

remdir STANDARD_weighted
remdir STANDARD/OCF_IMAGES


if [ ! -e SCIENCE/SCIENCE_1.fits ]; then
    echo "Cannot determine FLAT DIR to keep. Exiting"
    exit 0
fi

KEEP_FLAT_DIR_SC1=`readlink SCIENCE/SCIENCE_1.fits`
KEEP_FLAT_DIR=`dirname $KEEP_FLAT_DIR_SC1`
KEEP_FLAT=`basename $KEEP_FLAT_DIR`

FLATDIRS=`find . -maxdepth 1 -name 'SCIENCE_*_SET*' | awk -v ORS=' ' '!(/_norm/) {print}' `
for flatdir in $FLATDIRS; do
    FLAT=`basename $flatdir`

    rm -f $FLAT/SUPA*_sub.fits
    remdir $FLAT/OCF_IMAGES
    remdir $FLAT/SUB_IMAGES

    zipdir ${FLAT}_norm

    if [ $FLAT != $KEEP_FLAT ]; then
	echo "   Don't keep!"
	remdir $FLAT
    fi
done

normdirs=`find . -maxdepth 1 -name 'SCIENCE_*_SET*_norm' | awk -v ORS=' ' '{print}' `
for normdir in $normdirs; do

    zipdir ${normdir}

done


cd $CURDIR