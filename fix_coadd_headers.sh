#!/bin/bash
set -xv

export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU/
#mkdir /nfs/slac/kipac/fs1/u/awright/batch_files/coadd_MACS1115+01/
. SUBARU.ini
. progs.ini
for cluster in MACS0429-02 RXJ2129
do
	export cluster=${cluster}
	for fl in `\ls ${SUBARUDIR}/${cluster}/W-*/SCIENCE/coadd_${cluster}_*/coadd.fits` 
	do
		./adam_quicktools_fix_header_verify.py ${fl} 
		./SeeingClearly_for_coadds.py ${fl} 
	done
done

exit 0
export filter='W-C-RC'
export detect_filter=${filter};export lensing_filter=${filter} ;export ending=OCFSRI ; export config="10_2"



#./adam_do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_PHOTO.log
#if [ "${exit_stat}" -gt "0" ]; then
#        exit ${exit_stat};
#fi
#sleep 200
#bjobs
./adam_do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper BIGMACSAPPLY 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_BIGMACSAPPLY.log
exit_stat=$?
if [ "${exit_stat}" -gt "0" ]; then
        exit ${exit_stat};
fi

#./adam_do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper MERGE STARS BIGMACSCALIB BIGMACSAPPLY 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_allmodes.log
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
