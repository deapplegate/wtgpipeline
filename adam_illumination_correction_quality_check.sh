#!/bin/bash
set -v
#adam-does# this gives a simple check on the simple_ic.py results
#adam-note# you must change the following vars: cluster, filter_run_pairs, and ref
cluster=$1
export filter_run_pairs=( `./my_cluster_params.py ${cluster} 'PPRUN'` )
echo "\n" ${pprun} "simple_ic.py outputs a lot of plots/images and they are all useful if you need the nitty gritty details, but if you just want a simple check on how good the results look, then you can cd ~/data/${cluster}/PHOTOMETRY/ILLUMINATION/${FILTER}/${FILTER}_${RUN} and check for these attributes with these commands. There are examples from MACS1226+21/W-C-RC_2010-02-12 provided."

#example: cd ~/data/MACS1226+21/PHOTOMETRY/ILLUMINATION/W-C-RC/W-C-RC_2010-02-12
#adam-old# export filter_run_pairs=( W-S-Z+_2009-04-29 W-J-B_2009-04-29 W-J-B_2010-03-12 W-S-Z+_2010-03-12 W-C-RC_2010-03-12 )
#adam-old# export cluster='MACS1115+01'
ref=$2 #ref=s: sdss OR ref=p: panstarrs
if [ ${ref} = 'p' ]; then
	refcatcaps="PANSTARRS"
	refcatsmall="panstarrs"
	extra_nametag=""
	#extra_nametag="PANSTARRS"
	testtag="adamPAN3"
elif [ ${ref} = 's' ]; then
	refcatcaps="SDSS"
	refcatsmall="sdss"
	extra_nametag=""
	testtag="adamSDSS3"
fi
#export cluster='RXJ2129'
#export filter_run_pairs=( W-C-RC_2012-07-23 W-J-B_2010-11-04 W-S-Z+_2010-11-04 )
#export cluster='MACS1226+21'
#export filter_run_pairs=( W-J-B_2010-02-12 W-J-V_2010-02-12 W-C-RC_2010-02-12 W-C-IC_2010-02-12 W-C-IC_2011-01-06 W-S-Z+_2011-01-06 )
#export filter_run_pairs=( W-J-V_2010-02-12 W-C-RC_2010-02-12 W-C-IC_2010-02-12 W-C-IC_2011-01-06 W-S-Z+_2011-01-06 )
#export cluster='A2204'
#export filter_run_pairs=( W-S-I+_2009-03-28 W-J-V_2009-09-19 )

for pprun in ${filter_run_pairs[@]}
do
	run=${pprun#W*_}
	filter=${pprun%_*}
	cd ~/my_data/SUBARU/${cluster}/PHOTOMETRY/ILLUMINATION_${refcatcaps}/${filter}/${pprun}/ 
	ls reducedchi_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_W-*_15bins_diff_mean.fits
	ls reducedchi_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_W-*_15bins_diffbinned_${testtag}.png
	ls reducedchi_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_W-*_15bins_pos_${testtag}.png rejects_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_pos_${testtag}.png
	ls [0-1]/correction_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_ROT[0-1]_${testtag}.fits [0-1]/nochipzps_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_ROT[0-1]_${testtag}.fits
	ls [0-1]/${refcatsmall}_star_*_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_15bins_diff_mean.fits
	ls [0-1]/${refcatsmall}_star_correct*_ROT*_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_15bins_diffbinned_${testtag}.png
	ls [0-1]/${refcatsmall}_star_nocorrected_data_ROT*_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_15bins_diffbinned_${testtag}.png

	echo "${pprun} hopefully no pattern in where stars are detected and rejected"
	xv reducedchi_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_W-*_15bins_pos_${testtag}.png
	xv rejects_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_pos_${testtag}.png
	#example: reducedchi_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_W-C-RC_2010-02-12_15bins_pos_${testtag}.png
	#example: rejects_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_pos_${testtag}.png

	echo " ${pprun} hopefully no pattern in the residuals"
	titlestr="${refcatsmall}_${pprun}_hopefully_no_pattern_in_the_residuals"
	ds9 -title ${titlestr} -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale reducedchi_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_W-*_15bins_diff_mean.fits  -zoom to fit &
	xv reducedchi_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_W-*_15bins_diffbinned_${testtag}.png
	#example: reducedchi_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_W-C-RC_2010-02-12_15bins_diff_mean.fits
	#example: reducedchi_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_W-C-RC_2010-02-12_15bins_diffbinned_${testtag}.png

	echo "${pprun} hopefully look dome-like and symetrical"
	titlestr="${refcatsmall}_${pprun}_hopefully_look_dome-like_and_symetrical"
	ds9 -title ${titlestr} -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale [0-1]/correction_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_ROT[0-1]_${testtag}.fits [0-1]/nochipzps_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_ROT[0-1]_${testtag}.fits -zoom to fit
	exit_stat=$? #use ${PIPESTATUS[0]} if it's <command> | tee -a OUT-command.log
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	#example: correction_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_ROT0_${testtag}.fits
	#example: nochipzps_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_ROT0_${testtag}.fits

	echo ${pprun} 'hopefully correction looks dome-like and symetrical, while corrected/nocorrected looks noisey ("_no_pos" helps to determine if the position zps are doing all the work or not)'
	titlestr="${refcatsmall}_${pprun}_hopefully_corrected/nocorrected_looks_noisey,while_correction_looks_dome-like_and_symetrical---no_pos_helps_determine_if_position_zps_help"
	ds9 -title ${titlestr} -tile grid layout 5 2 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale [0-1]/${refcatsmall}_star_*sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_15bins_diff_mean.fits [0-1]/${refcatsmall}_star_correction*sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_15bins_diff_err.fits -zoom to fit &
	exit_stat=$? #use ${PIPESTATUS[0]} if it's <command> | tee -a OUT-command.log
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi
	#example: ${refcatsmall}_star_corrected_data_ROT0_W-C-RC_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_15bins_diff_mean.fits
	#example: ${refcatsmall}_star_correction_ROT0_W-C-RC_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_15bins_diff_mean.fits
	#example: ${refcatsmall}_star_no_pos-corrected_data_ROT0_W-C-RC_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_15bins_diff_mean.fits
	#example: ${refcatsmall}_star_nocorrected_data_ROT0_W-C-RC_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_15bins_diff_mean.fits

	echo "${pprun} hopefully corrected looks much flatter than nocorrected and correction looks smooth"
	display [0-1]/${refcatsmall}_star_corrected_data_ROT*sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_15bins_diffbinned_${testtag}.png &
	exit_stat=$? #use ${PIPESTATUS[0]} if it's <command> | tee -a OUT-command.log
	if [ "${exit_stat}" -gt "0" ]; then
		exit ${exit_stat};
	fi

	#adam-tmp# display [0-1]/${refcatsmall}_star_nocorrected_data_ROT*sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_15bins_diffbinned_${testtag}.png
	#example: ${refcatsmall}_star_nocorrected_data_ROT0_W-C-RC_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_15bins_diffbinned_${testtag}.png
	#example: ${refcatsmall}_star_corrected_ROT0_W-C-RC_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_15bins_diffbinned_${testtag}.png
	#example: ${refcatsmall}_star_correction_ROT0_W-C-RC_${extra_nametag}__sample_size-is-all__calc_illum-is-True__sample-is-${refcatsmall}__try_linear-is-True_15bins_diffbinned_${testtag}.png
	echo ~/my_data/SUBARU/${cluster}/PHOTOMETRY/ILLUMINATION_${refcatcaps}/${filter}/${pprun}/ 
done
