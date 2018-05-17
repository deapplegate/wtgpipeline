#!/bin/bash
set -xv

${sedstring}="sed -i.old 's/=\/nfs\/slac\/g\/ki\/ki18\/anja/=\/gpfs\/slac\/kipac\/fs1\/u\/awright/g'  adamSep15_test_non-parallel_resamp.sh adam_bias-do_Subaru_preprocess.sh adam_notes-pick_SKYFLAT_or_DOMEFLAT.sh batch_ic.sh batch_suppress.sh change_headernames.sh do_geo_photometry.sh do_lensing.sh do_photometry.sh do_photometry_3sec.sh do_photometry_alt.sh full_suppression.sh move_suppression.sh photometry_catalogs.sh produce_3sec_cats.sh run_update_configheaders_onall.sh transfer_catbackup.sh "
echo " " >> adam-simple_change_many_files/simple_change_many_files.log
echo "START ${sedstring} " >> adam-simple_change_many_files/simple_change_many_files.log
echo " " >> adam-simple_change_many_files/simple_change_many_files.log
for fl in adamSep15_test_non-parallel_resamp.sh adam_bias-do_Subaru_preprocess.sh adam_notes-pick_SKYFLAT_or_DOMEFLAT.sh batch_ic.sh batch_suppress.sh change_headernames.sh do_geo_photometry.sh do_lensing.sh do_photometry.sh do_photometry_3sec.sh do_photometry_alt.sh full_suppression.sh move_suppression.sh photometry_catalogs.sh produce_3sec_cats.sh run_update_configheaders_onall.sh transfer_catbackup.sh
do
	touch -r ${fl}.old ${fl}
	echo "${fl}" >> adam-simple_change_many_files/simple_change_many_files.log
	mv ${fl}.old adam-simple_change_many_files/
done
echo " END  ${sedstring} " >> adam-simple_change_many_files/simple_change_many_files.log
echo " " >> adam-simple_change_many_files/simple_change_many_files.log
#grep -l "=\/nfs\/slac\/g\/ki\/ki18\/anja" *.sh | paste -s -d\ 
#mv *.old scratch
#grep "=\/nfs\/slac\/g\/ki\/ki18\/anja" *.sh
#grep "=\/nfs\/slac\/g\/ki\/ki18\/anja" *.sh.old
#grep "=\/gpfs/slac\/kipac\/fs1\/u\/awright" *.sh
#sed -i.old 's/=\/nfs\/slac\/g\/ki\/ki18\/anja/=\/gpfs\/slac\/kipac\/fs1\/u\/awright/g'  adamSep15_test_non-parallel_resamp.sh adam_bias-do_Subaru_preprocess.sh adam_notes-pick_SKYFLAT_or_DOMEFLAT.sh batch_ic.sh batch_suppress.sh change_headernames.sh do_geo_photometry.sh do_lensing.sh do_photometry.sh do_photometry_3sec.sh do_photometry_alt.sh full_suppression.sh move_suppression.sh photometry_catalogs.sh produce_3sec_cats.sh run_update_configheaders_onall.sh transfer_catbackup.sh
#grep "=\/gpfs/slac\/kipac\/fs1\/u\/awright" adamSep15_test_non-parallel_resamp.sh adam_bias-do_Subaru_preprocess.sh adam_notes-pick_SKYFLAT_or_DOMEFLAT.sh batch_ic.sh batch_suppress.sh change_headernames.sh do_geo_photometry.sh do_lensing.sh do_photometry.sh do_photometry_3sec.sh do_photometry_alt.sh full_suppression.sh move_suppression.sh photometry_catalogs.sh produce_3sec_cats.sh run_update_configheaders_onall.sh transfer_catbackup.sh
#grep "=\/nfs\/slac\/g\/ki\/ki18\/anja" *.sh.old
#touch -r run_update_configheaders_onall.sh.old run_update_configheaders_onall.sh
#ls -l run_update_configheaders_onall.sh.old run_update_configheaders_onall.sh
#touch -r run_update_configheaders_onall.sh.old run_update_configheaders_onall.sh

