#!/bin/bash
set -xv
#adam-does# use this to make screenshots of certain FLATS/SUPERFLATS for comparison

for pprun in 2010-03-12_W-J-B 2010-11-04_W-J-B 2009-09-19_W-J-V 2010-03-12_W-C-RC
do
	ds9 -view buttons no -view info no -view filename no -view panner no -frame lock image -geometry 2000x2000 -cmap bb -scale limits .95 1.05 ~/data/$pprun/SCIENCE_norm_DOMEFLAT/BINNED/*.fits -zoom to fit -saveimage jpeg DOMEFLAT_${pprun}.jpeg 75 -quit
	sleep 10
	ds9 -view buttons no -view info no -view filename no -view panner no -frame lock image -geometry 2000x2000 -cmap bb -scale limits .95 1.05 ~/data/$pprun/SCIENCE_norm_SKYFLAT/BINNED/*.fits -zoom to fit -saveimage jpeg SKYFLAT_${pprun}.jpeg 75 -quit
done
