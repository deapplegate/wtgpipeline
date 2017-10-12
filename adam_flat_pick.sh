#!/bin/bash
set -xv

#2010-03-12_W-J-B/SCIENCE_SKYFLAT
#2010-11-04_W-J-B/SCIENCE_SKYFLAT
#2009-09-19_W-J-V/SCIENCE_SKYFLAT
#2010-03-12_W-C-RC/SCIENCE_SKYFLAT
#2009-03-28_W-J-V/SCIENCE_SKYFLAT


for pprun in 2010-03-12_W-J-B 2010-11-04_W-J-B 2009-09-19_W-J-V 2010-03-12_W-C-RC
do
  #\ls -d ~/data/$pprun/SCIENCE_norm*/BINNED
  ls ~/data/$pprun/SCIENCE_norm_DOMEFLAT/BINNED/*.fits | wc -l
  ls ~/data/$pprun/SCIENCE_norm_SKYFLAT/BINNED/*.fits | wc -l
done


