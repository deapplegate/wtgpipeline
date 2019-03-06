#!/bin/bash
set -xv


## PHOTO ##
test -f OUT-adam_do_photometry_final_starcat-PHOTO_${cluster}.log && mv OUT-adam_do_photometry_final_starcat-PHOTO_${cluster}.log scratch/

./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO 2>&1 | tee -a OUT-adam_do_photometry_final_starcat-PHOTO_${cluster}.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi

./get_error_log.sh OUT-adam_do_photometry_final_starcat-PHOTO_${cluster}.log
bjobs -a
exit 0;


## MERGE_STARS ##
test -f OUT-adam_do_photometry_final_starcat-MERGE_STARS_${cluster}.log && mv OUT-adam_do_photometry_final_starcat-MERGE_STARS_${cluster}.log scratch/

./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper MERGE STARS 2>&1 | tee -a OUT-adam_do_photometry_final_starcat-MERGE_STARS_${cluster}.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi

./get_error_log.sh OUT-adam_do_photometry_final_starcat-MERGE_STARS_${cluster}.log
exit 0;



## START OF LDACLENSING SCRIPTS ##

#...then cd ~/ldaclensing and run the first few steps of adam_outline.sh, ending with the 2nd run of check_psf_coadd_vis_new.sh
#then run the photometric zps with bigmacs (and get the SDSS catalog)




## SDSS ##
test -f OUT-adam_do_photometry_final_starcat-SDSS_${cluster}.log && mv OUT-adam_do_photometry_final_starcat-SDSS_${cluster}.log scratch/

./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper SDSS 2>&1 | tee -a OUT-adam_do_photometry_final_starcat-SDSS_${cluster}.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi

./get_error_log.sh OUT-adam_do_photometry_final_starcat-SDSS_${cluster}.log


## BIGMACSCALIB_BIGMACSAPPLY ##
test -f OUT-adam_do_photometry_final_starcat-BIGMACSCALIB_BIGMACSAPPLY_${cluster}.log && mv OUT-adam_do_photometry_final_starcat-BIGMACSCALIB_BIGMACSAPPLY_${cluster}.log scratch/
./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper BIGMACSCALIB BIGMACSAPPLY 2>&1 | tee -a OUT-adam_do_photometry_final_starcat-BIGMACSCALIB_BIGMACSAPPLY_${cluster}.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi

./get_error_log.sh OUT-adam_do_photometry_final_starcat-BIGMACSCALIB_BIGMACSAPPLY_${cluster}.log
exit 0;


## BPZ ##
#then run the photo-zs with BPZ
test -f  OUT-adam_bpz_wrapper_${cluster}.log && mv OUT-adam_bpz_wrapper_${cluster}.log scratch/

./adam_bpz_wrapper.py 2>&1 | tee -a OUT-adam_bpz_wrapper_${cluster}.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi

./get_error_log.sh OUT-adam_bpz_wrapper_${cluster}.log

#...then cd ~/ldaclensing and continue on with adam_outline.sh
