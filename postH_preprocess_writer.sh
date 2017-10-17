#! /bin/bash
set -xv

# -W 3000 is 5 hrs
#for pprun in 2015-12-15_W-J-B  2015-12-15_W-S-Z+  2015-12-15_W-C-RC  2013-06-10_W-S-Z+ 2012-07-23_W-C-RC 2010-11-04_W-J-B 2010-11-04_W-S-Z+ 2010-03-12_W-C-RC 2010-03-12_W-J-B 2010-03-12_W-S-Z+ 2009-09-19_W-J-V 2009-04-29_W-J-B 2009-04-29_W-S-Z+ 2009-03-28_W-J-V
for pprun in 2012-07-23_W-C-RC 2010-03-12_W-C-RC 2010-03-12_W-J-B 2010-03-12_W-S-Z+ 2009-09-19_W-J-V 2009-04-29_W-J-B 2009-04-29_W-S-Z+ 2009-03-28_W-J-V
do
	filter=${pprun#2*_}
	run=${pprun%_*}
	#echo "cd /nfs/slac/g/ki/ki18/anja/SUBARU/${run}_${filter}/SCIENCE" >> postH_setup.tmp
	#echo "rm SUPA*_CH*.fits ;  rm SUPA*OCF.fits ; rm SUPA*OCF_sub.fits ; rm SCIENCE_*.fits" >> postH_setup.tmp
	#echo "mv SPLIT_IMAGES/SUPA*.fits . " >> postH_setup.tmp
	#echo "ls ORIGINALS/SUPA*.fits | wc -l " >> postH_setup.tmp
	#echo "ls SUPA*.fits | wc -l " >> postH_setup.tmp
	#echo "ls SUB_IMAGES/" >> postH_setup.tmp
	#echo "ls SPLIT_IMAGES/" >> postH_setup.tmp
	#echo "ls tmp_OCF/" >> postH_setup.tmp
	#echo "" >> postH_setup.tmp

	#sed "s/CHANGEIT/${pprun}/g" postH_preprocess_template.sh > postH_${run}_${filter}_preprocess_step9.sh
	bsub -W 7000 -R rhel60 -o /nfs/slac/g/ki/ki18/anja/SUBARU/batch_files/postH_preprocess/OUT-postH_${run}_${filter}_preprocess_step9.out \
			       -e /nfs/slac/g/ki/ki18/anja/SUBARU/batch_files/postH_preprocess/OUT-postH_${run}_${filter}_preprocess_step9.err \
			       ./postH_${run}_${filter}_preprocess_step9.sh
	#echo "./get_error_log.sh /nfs/slac/g/ki/ki18/anja/SUBARU/batch_files/postH_preprocess/OUT-postH_${run}_${filter}_preprocess_step9.out" >> adam_SHNT.sh
	#echo "vim /nfs/slac/g/ki/ki18/anja/SUBARU/batch_files/postH_preprocess/OUT-postH_${run}_${filter}_preprocess_step9.err" >> adam_SHNT.sh
done
