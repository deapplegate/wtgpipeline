#!/bin/bash
#adam-does# this script will make subdirs for each target in SCIENCE_norm/BINNED/ and make a screenshot of those images in order to make picking superflat targets easier
#adam-example# ./adam_BINNED_screenshots_SCIENCE_norm_folders_pngs.sh 2015-06-18_W-J-B
count=0
for pprun in 2009-03-28_W-J-V 2009-03-28_W-S-I+ 2009-09-19_W-J-V 2009-04-29_W-S-Z+ 2009-04-29_W-J-B 2010-03-12_W-J-B 2010-03-12_W-S-Z+ 2010-03-12_W-C-RC 2010-11-04_W-J-B 2010-11-04_W-S-Z+ 2012-07-23_W-C-RC 2013-06-10_W-S-Z+
do
	count=$(( ${count}+1 ))
	num=`\ls ~/data/${pprun}/SCIENCE_norm/BINNED/SUPA*mosOCFN.fits |wc -l`
	titlestr="$pprun: has ${num} images!" 
	echo $titlestr
	if [ ${num} -lt 100 ] ; then
		ds9 -title $titlestr -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 ~/data/${pprun}/SCIENCE_norm/BINNED/SUPA*mosOCFN.fits -zoom to fit &
	else
		echo "TOO many for ${pprun} to open in ds9!"
	fi
done
