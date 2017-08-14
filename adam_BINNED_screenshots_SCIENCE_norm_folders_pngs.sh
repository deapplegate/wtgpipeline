#!/bin/bash
set -xv
#adam-does# this script will make subdirs for each target in SCIENCE_norm/BINNED/ and make a screenshot of those images in order to make picking superflat targets easier
#adam-example# ./adam_BINNED_screenshots_SCIENCE_norm_folders_pngs.sh 2015-06-18_W-J-B
pprun=$1
#########for pprun in 2009-03-28_W-J-V 2009-03-28_W-S-I+ 2009-09-19_W-J-V 2009-04-29_W-S-Z+ 2009-04-29_W-J-B 2010-03-12_W-J-B 2010-03-12_W-S-Z+ 2010-03-12_W-C-RC 2010-11-04_W-J-B 2010-11-04_W-S-Z+ 2012-07-23_W-C-RC 2013-06-10_W-S-Z+
dfits -x 1 ~/data/${pprun}/SCIENCE/ORIGINALS/SUPA*.fits | fitsort OBJECT > tmp.log
cut -c 18- tmp.log | sed 's/\ /_/g' | sed 's/_*\t*$//g' > tmp.log1
cut -c -16 tmp.log > tmp.log0
paste tmp.log0 tmp.log1 > tmp.log
sed -i.old 's/\t/\ /g;/FILE/d;s/\.fits/_mosOCFN.fits/g;s/^/cp /g;s/\/z=[0-9.]*//g' tmp.log
cat bash_shebang.sh tmp.log > sort_${pprun}_OCFNs.sh
chmod u+x sort_${pprun}_OCFNs.sh
mv sort_${pprun}_OCFNs.sh ~/data/${pprun}/SCIENCE_norm/BINNED/

awk '{print $3}' tmp.log | sort | uniq > ~/data/${pprun}/SCIENCE_norm/BINNED/objects.list

for obj in `awk '{print $3}' tmp.log | sort | uniq`
do
	mkdir ~/data/${pprun}/SCIENCE_norm/BINNED/${obj}
done

cd ~/data/${pprun}/SCIENCE_norm/BINNED/
./sort_${pprun}_OCFNs.sh

for obj in `cat objects.list`
do
	supas=`grep "${obj}" sort_${pprun}_OCFNs.sh | awk '{print $2}' | sed 's/_mosOCFN.fits//g' | paste -s -d_ `
	titlestr="${obj}:${supas}"
	echo "${pprun}-${obj}: ${supas}" >> ~/bonnpipeline/adam_check_postH_SCIENCE_norm_folders_pngs.list
	ls ${obj}/SUPA*mosOCFN.fits
	ds9 -title $titlestr -view info no -view magnifier no -view panner no -view buttons no -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 ${obj}/SUPA*mosOCFN.fits -zoom to fit -saveimage png ${obj}_scale96.png -quit
	ds9 -title $titlestr -view info no -view magnifier no -view panner no -view buttons no -frame lock image -geometry 2000x2000 -cmap bb -scale limits .98 1.01 ${obj}/SUPA*mosOCFN.fits -zoom to fit -saveimage png ${obj}_scale98.png -quit
	echo "echo \"ds9 -title $titlestr -frame lock image -geometry 2000x2000 -cmap bb -scale limits .96 1.01 ~/data/${pprun}/SCIENCE_norm/BINNED/${obj}/SUPA*mosOCFN.fits -zoom to fit \"" >> ~/bonnpipeline/adam_check_postH_SCIENCE_norm_folders_pngs.sh
	echo "xv ${pprun}/SCIENCE_norm/BINNED/${obj}_scale96.png ${pprun}/SCIENCE_norm/BINNED/${obj}_scale98.png" >> ~/bonnpipeline/adam_check_postH_SCIENCE_norm_folders_pngs.sh
done

cd ~/bonnpipeline
