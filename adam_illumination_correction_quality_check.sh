#!/bin/bash
#set -xv

echo "\n" ${pprun} "simple_ic.py outputs a lot of plots/images and they are all useful if you need the nitty gritty details, but if you just want a simple check on how good the results look, then you can cd ~/data/${cluster}/PHOTOMETRY/ILLUMINATION/${FILTER}/${FILTER}_${RUN} and check for these attributes with these commands. There are examples from MACS1226+21/W-C-RC_2010-02-12 provided."

#example: cd ~/data/MACS1226+21/PHOTOMETRY/ILLUMINATION/W-C-RC/W-C-RC_2010-02-12
export filter_run_pairs=( W-S-Z+_2009-04-29 W-J-B_2009-04-29 W-J-B_2010-03-12 W-S-Z+_2010-03-12 W-C-RC_2010-03-12 )
export cluster='MACS1115+01'

for pprun in ${filter_run_pairs[@]}
do
	run=${pprun#W*_}
	filter=${pprun%_*}
	cd ~/data/${cluster}/PHOTOMETRY/ILLUMINATION/${filter}/${pprun}/ 
	echo "\n" ${pprun} "hopefully no pattern in the residuals"
	ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale reducedchi___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_W-*_15bins_diff_mean.fits &
	xv reducedchi___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_W-*_15bins_diffbinned_adam.png
	#example: reducedchi___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_W-C-RC_2010-02-12_15bins_diff_mean.fits
	#example: reducedchi___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_W-C-RC_2010-02-12_15bins_diffbinned_adam.png

	echo "\n" ${pprun} "hopefully no pattern in where stars are detected and rejected"
	xv reducedchi___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_W-*_15bins_pos_adam.png rejects___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_pos_adam.png
	#example: reducedchi___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_W-C-RC_2010-02-12_15bins_pos_adam.png
	#example: rejects___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_pos_adam.png

	echo "\n" ${pprun} "hopefully look dome-like and symetrical"
	ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale [0-1]/correction___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_ROT[0-1]_adam.fits [0-1]/nochipzps___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_ROT[0-1]_adam.fits
	#example: correction___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_ROT0_adam.fits
	#example: nochipzps___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_ROT0_adam.fits

	echo "\n" ${pprun} 'hopefully correction looks dome-like and symetrical, while corrected/nocorrected looks noisey ("_no_pos" helps to determine if the position zps are doing all the work or not)'
	ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale [0-1]/sdss_star_*___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_15bins_diff_mean.fits
	#example: sdss_star_corrected_data_ROT0_W-C-RC___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_15bins_diff_mean.fits
	#example: sdss_star_correction_ROT0_W-C-RC___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_15bins_diff_mean.fits
	#example: sdss_star_no_pos-corrected_data_ROT0_W-C-RC___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_15bins_diff_mean.fits
	#example: sdss_star_nocorrected_data_ROT0_W-C-RC___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_15bins_diff_mean.fits

	echo "\n" ${pprun} "hopefully corrected looks much flatter than nocorrected and correction looks smooth"
	xv [0-1]/sdss_star_correct*_ROT*___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_15bins_diffbinned_adam.png &
	xv [0-1]/sdss_star_nocorrected_data_ROT*___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_15bins_diffbinned_adam.png
	#example: sdss_star_nocorrected_data_ROT0_W-C-RC___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_15bins_diffbinned_adam.png
	#example: sdss_star_corrected_ROT0_W-C-RC___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_15bins_diffbinned_adam.png
	#example: sdss_star_correction_ROT0_W-C-RC___sample_size-is-all__calc_illum-is-True__sample-is-sdss__try_linear-is-True_15bins_diffbinned_adam.png
done
