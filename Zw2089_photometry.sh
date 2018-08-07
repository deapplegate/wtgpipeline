#!/bin/bash
set -xv

## Zw2089 lensing vars:
export cluster=Zw2089

ending=OCFSIR
config="10_3"

export filter=W-J-V
export SUBARUDIR=//gpfs/slac/kipac/fs1/u/awright/SUBARU/
. SUBARU.ini
. progs.ini

export detect_filter=${filter};export lensing_filter=${filter}



#./adam_do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_PHOTO.log
#exit_stat=$?
#if [ "${exit_stat}" -gt "0" ]; then
#        exit ${exit_stat};
#fi
#sleep 20
#bjobs
#exit 0

./adam_do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper MERGE STARS BIGMACSCALIB BIGMACSAPPLY 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_allmodes.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi
exit 0

./adam_do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper SDSS 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_SDSSmode.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi

./adam_do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper BIGMACSCALIB BIGMACSAPPLY 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_bigmacs.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi
