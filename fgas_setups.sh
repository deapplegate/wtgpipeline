#!/bin/bash
set -v
rm adam_SHNT-automask.sh
export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU/
for cluster in `cat ${SUBARUDIR}/targets.txt`
do
    for pprun in `cat ${SUBARUDIR}/${cluster}/ppruns_10_3.txt`
    do
	export filter=${pprun%_*}
        export run=${pprun#W*_}
	rm ./automask_${cluster}_${filter}_${run}.sh OUT-automask_${cluster}_${filter}_${run}.log
        echo "export cluster=${cluster}" >> automask_${cluster}_${filter}_${run}.sh
	echo "export filter=${pprun%_*}" >> automask_${cluster}_${filter}_${run}.sh
        echo "export run=${pprun#W*_}" >> automask_${cluster}_${filter}_${run}.sh
        export ending=`grep "$pprun" ~/wtgpipeline/fgas_pprun_endings.txt | awk '{print $2}'`
        echo "export ending=${ending}" >> automask_${cluster}_${filter}_${run}.sh
	cat bash_shebang.sh automask_${cluster}_${filter}_${run}.sh adam_do_fgas_automasking-template.sh > tmp.tmp
	mv tmp.tmp automask_${cluster}_${filter}_${run}.sh
	chmod u+x automask_${cluster}_${filter}_${run}.sh
	echo "./automask_${cluster}_${filter}_${run}.sh 2>&1 | tee -a OUT-automask_${cluster}_${filter}_${run}.log" >> adam_SHNT-automask.sh
        #./create_weights_raw_delink_para_CRNitschke_setup.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS ${filter} 2>&1 | tee -a OUT-CRN_setup_${cluster}_${filter}_${run}.log
    done
done
cat bash_shebang.sh adam_SHNT-automask.sh > tmp.tmp
mv tmp.tmp adam_SHNT-automask.sh
chmod u+x adam_SHNT-automask.sh
