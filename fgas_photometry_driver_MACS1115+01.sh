#!/bin/bash
set -xv
## only important ones
export SUBARUDIR=/u/ki/awright/data/
export bonn=/u/ki/awright/wtgpipeline/
export subdir=${SUBARUDIR}
export subarudir=${SUBARUDIR}

export ending="OCFSRI"
export detect_filter=W-C-RC
export lensing_filter=W-C-RC
export INSTRUMENT=SUBARU
export cluster=MACS1115+01
export filter="W-C-RC"
export lens="gabodsid1554"
export lensing_coadd_type="gabodsid1554"
export lensing_image=${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${lensing_coadd_type}/coadd.fits
export lensing_dir=`dirname ${lensing_image}`
export lensing_base=`basename ${lensing_image} .fits`
export lensing_weight=${lensing_dir}/${lensing_base}.weight.fits
export lensing_flag=${lensing_dir}/${lensing_base}.flag.fits
export LENSDIR=${SUBARUDIR}/${cluster}/LENSING_${filter}_${filter}_aper/${lensing_coadd_type}
export PHOTDIR=${subarudir}/${cluster}/PHOTOMETRY_${filter}_aper

#./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO 2>&1 | tee -a OUT-adam_do_photometry_final_starcat-PHOTO.log
#./get_error_log.sh OUT-adam_do_photometry_final_starcat-PHOTO.log
#bjobs -a
#exit 0;

#./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper MERGE STARS 2>&1 | tee -a OUT-adam_do_photometry_final_starcat-MERGE_STARS.log
#./get_error_log.sh OUT-adam_do_photometry_final_starcat-MERGE_STARS.log
#exit 0;

#...then cd ~/ldaclensing and run the first few steps of adam_outline.sh, ending with the 2nd run of check_psf_coadd_vis_new.sh
#then run the photometric zps with bigmacs (and get the SDSS catalog)
test -f OUT-adam_do_photometry_final_starcat-SDSS.log && rm -f OUT-adam_do_photometry_final_starcat-SDSS.log
./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper SDSS 2>&1 | tee -a OUT-adam_do_photometry_final_starcat-SDSS.log
exit_stat=$? #use ${PIPESTATUS[0]} if it's <command> | tee -a OUT-command.log                                         
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi
./get_error_log.sh OUT-adam_do_photometry_final_starcat-SDSS.log

./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper BIGMACSCALIB BIGMACSAPPLY 2>&1 | tee -a OUT-adam_do_photometry_final_starcat-BIGMACSCALIB_BIGMACSAPPLY.log
exit_stat=$? #use ${PIPESTATUS[0]} if it's <command> | tee -a OUT-command.log                                         
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi
./get_error_log.sh OUT-adam_do_photometry_final_starcat-BIGMACSCALIB_BIGMACSAPPLY.log


#then run the photo-zs with BPZ
. bpz.ini
./adam_bpz_wrapper.py 2>&1 | tee -a OUT-adam_bpz_wrapper_${cluster}.log
exit_stat=$? #use ${PIPESTATUS[0]} if it's <command> | tee -a OUT-command.log                                         
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi

#...then cd ~/ldaclensing and continue on with adam_outline.sh
