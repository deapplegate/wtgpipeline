#!/bin/bash
set -v

dirs=`\ls -d /u/ki/awright/data/20*_W-*/SCIENCE/diffmask/`
for dir in ${dirs}
do
	echo "${dir}"
	if [ -f "${dir}/plt_shadowcheck_toprow_IMAGE_chip6.png" ] ; then
	    for chipnum in 6 7 8 9 10
	    do
		cat ${dir}/remove_bad_shadows_chip${chipnum}.sh
	        xv ${dir}/plt_shadowcheck_toprow_IMAGE_chip${chipnum}.png &
	        xv ${dir}/plt_shadowcheck_toprow_MASK_chip${chipnum}.png
	    done
        fi
done


