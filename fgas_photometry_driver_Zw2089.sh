#!/bin/bash
set -xv

export cluster=Zw2089 ; export detect_filter=W-J-V;export lensing_filter=W-J-V ;export ending=OCFSIR ; export config="10_3"
#grep Zw2089 cluster_cat_filters.dat
#Zw2089 SDSS-R6 W-J-B W-J-B_2015-12-15_CALIB W-J-V W-C-RC W-C-RC_2015-12-15_CALIB W-S-I+ W-S-Z+ W-S-Z+_2015-12-15_CALIB


./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO 2>&1 | tee -a OUT-adam_do_photometry_final_starcat-PHOTO.log
./get_error_log.sh OUT-adam_do_photometry_final_starcat-PHOTO.log
bjobs -a
exit 0;

./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper MERGE STARS 2>&1 | tee -a OUT-adam_do_photometry_final_starcat-MERGE_STARS.log
./get_error_log.sh OUT-adam_do_photometry_final_starcat-MERGE_STARS.log
exit 0;

#...then cd ~/ldaclensing and run the first few steps of adam_outline.sh, ending with the 2nd run of check_psf_coadd_vis_new.sh
#then run the photometric zps with bigmacs (and get the SDSS catalog)

./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper SDSS 2>&1 | tee -a OUT-adam_do_photometry_final_starcat-SDSS.log
./get_error_log.sh OUT-adam_do_photometry_final_starcat-SDSS.log

./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper BIGMACSCALIB BIGMACSAPPLY 2>&1 | tee -a OUT-adam_do_photometry_final_starcat-BIGMACSCALIB_BIGMACSAPPLY.log
./get_error_log.sh OUT-adam_do_photometry_final_starcat-BIGMACSCALIB_BIGMACSAPPLY.log
exit 0;

#then run the photo-zs with BPZ
./adam_bpz_wrapper.py 2>&1 | tee -a OUT-adam_bpz_wrapper_${cluster}.log

#...then cd ~/ldaclensing and continue on with adam_outline.sh
