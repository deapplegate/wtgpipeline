#!/bin/bash
set -xv

for dir in 2009-03-28_W-J-V/ 2009-04-29_W-J-B/ 2009-04-29_W-S-Z+/ 2009-09-19_W-J-V/ 2010-03-12_W-C-RC/ 2010-03-12_W-J-B/ 2010-03-12_W-S-Z+/ 2010-11-04_W-J-B/ 2010-11-04_W-S-Z+/
do
    ./cp_aux_data.sh ${SUBARUDIR} ${dir} ~/data/from_archive/fgas_smoka_raw/fs_${dir}/
done

