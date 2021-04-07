#!/bin/bash
set -xv

. MACS0429-02.ini
. SUBARU.ini
. progs.ini


#./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_PHOTO.log
#exit_stat=$?
#if [ "${exit_stat}" -gt "0" ]; then
#        exit ${exit_stat};
#fi
#exit 0

#./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper MERGE 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_MERGE.log
#exit_stat=$?
#if [ "${exit_stat}" -gt "0" ]; then
#        exit ${exit_stat};
#fi

#./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper STARS 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_STARS.log
#exit_stat=$?
#if [ "${exit_stat}" -gt "0" ]; then
#        exit ${exit_stat};
#fi
#exit 0

#./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper SDSS 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_SDSSmode.log
#./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper SHAPES 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_SHAPESmode.log
#exit_stat=$?
#if [ "${exit_stat}" -gt "0" ]; then
#        exit ${exit_stat};
#fi
#exit 0
#
#cd ~/ldaclensing/

./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper BIGMACSAPPLY 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_bigmacs.log
#./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper BIGMACSCALIB BIGMACSAPPLY 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_bigmacs.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi
