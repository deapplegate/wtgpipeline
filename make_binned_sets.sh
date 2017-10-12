#!/bin/bash
#adam-example# ./make_binned_sets.sh /nfs/slac/g/ki/ki18/anja/SUBARU/2010-12-05_W-J-V/SCIENCE_norm/BINNED
set -xv
REDDIR=`pwd`
binned_dir=$1
cd $binned_dir

objects=`dfits -x 1 ../../SCIENCE/ORIGINALS/SUPA0*.fits | fitsort OBJECT | awk '{if(FNR==1){} else {print $2}}' | sort | uniq`
for obj in $objects
do
	mkdir $obj
done

echo "#! /bin/bash" >> move_objects.sh
dfits -x 1 ../../SCIENCE/ORIGINALS/SUPA0*.fits | fitsort OBJECT | awk '{if(FNR==1){} else {print "mv",$1,$2}}' | sed 's/\.fits/_mosOCFN.fits/g' >> move_objects.sh
chmod u+x move_objects.sh 
./move_objects.sh

cd $REDDIR

for obj in $objects
do
	echo "adam-look| ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale ${binned_dir}/${obj}/SUPA*_mosOCFN.fits &"
done
