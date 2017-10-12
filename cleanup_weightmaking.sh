#!/bin/bash
set -xv



#Cleans up coadd directories
############
#WARNING: DO NOT RUN THIS UNLESS PREPROCESSING/COADDING IS DONE!!!!
#############

# $1 : Directory to cleanup

#CVSID $Id: cleanup_weightmaking.sh,v 1.1 2009-04-29 22:43:10 dapple Exp $

##################################

echo "******************************************************************"
echo "WARNING: DO NOT RUN THIS UNLESS COADDING IS DONE!!!!"
echo "******************************************************************"
echo ""
echo ""
echo "Confirm: Run cleanup_coadd.sh on $1? [y/n]"
#read

#if [ "$REPLY" != "y" ]; then
#    echo "Exiting!"
#    exit 0;
#fi

#################################

CURDIR=`pwd`
cd $1

##################################


function zipdir {
    # $1 : dir to zip
    echo "Zipping $1"
    if [ -d $1 ]; then
	files=`find $1 -name \* -print | awk '($1 !~ /ORIGINALS/){print}'`
	if [ ! -z "$files" ]; then
	    gzip $files
	fi
    fi
    echo "Done"

}

################################


dirs=`ls | grep W`

for dir in $dirs; do

    isNight=`echo $dir | awk -F'_' '{print $2}'`

    if [ "$isNight" != "" ]; then

	rm -rf $dir/WEIGHTS/BINNED
	rm -rf $dir/SCIENCE_weighted
	if [ -d $dir/SCIENCE_sub_weighted ]; then
	    rm -rf $dir/SCIENCE_sub_weighted
	fi
	zipdir $dir/SCIENCE/diffmask

    fi

done