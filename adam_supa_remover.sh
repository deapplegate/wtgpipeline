#!/bin/bash
set -xv
#adam-example# ./adam_supa_remover.sh " " "2015-12-15_W-S-Z+SF2" "SUPA0154805 SUPA0154806 SUPA0154807 SUPA0154811 SUPA0154812 SUPA0154813 SUPA0154814 SUPA0154815 SUPA0154816 SUPA0154817 SUPA0154820 SUPA0154821 SUPA0154822 SUPA0154823 SUPA0154824 SUPA0154825 SUPA0155001 SUPA0155002 SUPA0155003"
#adam-example# ./adam_supa_remover.sh MACS1115+01 2009-04-29_W-J-B  "SUPA0109618"
#adam-example# ./adam_supa_remover.sh MACS1115+01 2009-04-29_W-S-Z+ "SUPA0109611 SUPA0109612"
#adam-example# ./adam_supa_remover.sh MACS1115+01 2010-03-12_W-C-RC "SUPA0120142 SUPA0120143"
#adam-maybe later# ./adam_supa_remover.sh MACS1115+01 2009-04-29_W-S-Z+ "SUPA0109610 SUPA0109613 SUPA0109614"
#adam-example# ./adam_supa_remover.sh MACS1115+01 2009-03-28_W-S-I+ "SUPA0108308 SUPA0108309 SUPA0108310 SUPA0108311 SUPA0108312 SUPA0108313 SUPA0108314 SUPA0108315 SUPA0108319 SUPA0108320"

cluster=$1
dir=$2
supas=$3
echo "dir=" $dir
echo "supas=" $supas

if [ ! -e /gpfs/slac/kipac/fs1/u/anja/adam_needs_more_space/fgas_trash/${dir} ] ; then
	mkdir /gpfs/slac/kipac/fs1/u/anja/adam_needs_more_space/fgas_trash/${dir}
fi
trashcan="/gpfs/slac/kipac/fs1/u/anja/adam_needs_more_space/fgas_trash/${dir}"

for supa in ${supas[@]}
do
	find ~/data/${dir} -name "${supa}*" -exec \ls {} >> ~/data/${dir}/supas_removed.log \;
	##find ~/data/${dir} -name "${supa}*" -exec rm {} \;
	find ~/data/${dir} -name "${supa}*" -exec mv {} ${trashcan} \;
	if [ ! -z ${cluster} ] ; then
		filter=${dir#2*_}
		run=${dir%_*}
		echo "run filter = " ${run} ${filter}
		if [ -d ~/data/${cluster}/${filter}_${run}/ ] ; then
			#find ~/data/${cluster}/${filter}_${run}/ -type l -name "${supa}*" -exec rm {} \;
			find ~/data/${cluster}/${filter}_${run}/ -name "${supa}*" -exec mv {} ${trashcan} \;
		fi
		if [ -d ~/data/${cluster}/${filter}/ ] ; then
			#find ~/data/${cluster}/${filter}/ -type l -name "${supa}*" -exec rm {} \;
			find ~/data/${cluster}/${filter}/ -name "${supa}*" -exec mv {} ${trashcan} \;
		fi
		astrom_dir=`\ls -d ~/data/${cluster}/W-*/SCIENCE/astrom_photom_scamp_*/`
		if [ -d ${astrom_dir} ] ; then
			find ${astrom_dir} -type l -name "${supa}*" -exec rm {} \;
			find ${astrom_dir} -name "${supa}*" -exec mv {} ${trashcan} \;
		fi
	fi

done
