#!/bin/bash

#MACS1115+01 Zw2089 
. ~/wtgpipeline/SUBARU.ini
. ~/wtgpipeline/progs.ini
flnum=0
for cluster in MACS0429-02 RXJ2129
do
	filters=`grep "${cluster}" cluster_cat_filters.dat | awk -v ORS=' ' '{for(i=3;i<=NF;i++){if($i!~"CALIB" && $i!="K") print $i}}'`
	echo "${cluster} : ${filters}"
	for filter in ${filters}
	do
		echo "${cluster} : ${filters}" >> coadd_seeing_fix_logger.log
		for fl in `\ls ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_*/coadd.fits` 
		do 
			flnum=$((${flnum}+1))
			echo ${flnum} ${fl} >> coadd_seeing_fix_logger.log
			#NN=`grep "Successfully completed" /nfs/slac/kipac/fs1/u/awright/batch_files/bsubbable//OUT-2018-6-5-adam_quicktools_fix_header_verify_${flnum}.out | wc -l`
			NN=`grep "Successfully completed" /nfs/slac/kipac/fs1/u/awright/batch_files/bsubbable//OUT-2018-6-5-SeeingClearly_for_coadds_${flnum}.out | wc -l`
			if [ "${NN}" != "1" ] ; then
				#rm /nfs/slac/kipac/fs1/u/awright/batch_files/bsubbable//OUT-2018-6-5-adam_quicktools_fix_header_verify_${flnum}.out /nfs/slac/kipac/fs1/u/awright/batch_files/bsubbable//OUT-2018-6-5-adam_quicktools_fix_header_verify_${flnum}.err
				#bsub -q short -o /nfs/slac/kipac/fs1/u/awright/batch_files/bsubbable//OUT-2018-6-5-adam_quicktools_fix_header_verify_${flnum}.out -e /nfs/slac/kipac/fs1/u/awright/batch_files/bsubbable//OUT-2018-6-5-adam_quicktools_fix_header_verify_${flnum}.err ./adam_quicktools_fix_header_verify.py ${fl}
				#echo "./adam_quicktools_fix_header_verify.py ${fl}" >> tmp.sh
				#./adam_quicktools_fix_header_verify.py ${fl} 
				rm /nfs/slac/kipac/fs1/u/awright/batch_files/bsubbable//OUT-2018-6-5-SeeingClearly_for_coadds_${flnum}.out /nfs/slac/kipac/fs1/u/awright/batch_files/bsubbable//OUT-2018-6-5-SeeingClearly_for_coadds_${flnum}.err
				bsub -m bulletfarm -q short -o /nfs/slac/kipac/fs1/u/awright/batch_files/bsubbable//OUT-2018-6-5-SeeingClearly_for_coadds_${flnum}.out -e /nfs/slac/kipac/fs1/u/awright/batch_files/bsubbable//OUT-2018-6-5-SeeingClearly_for_coadds_${flnum}.err ./SeeingClearly_for_coadds.py ${fl}
			fi
		done
	done
done

