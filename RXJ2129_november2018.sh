#!/bin/bash
set -xv

#./do_REMS_masks_RXJ2129.py
#adam-new#
export ending=OCFSRI
export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU/
export cluster=RXJ2129
export filter=W-C-RC
export config="10_3"

#./do_coadd_RXJ2129_after_REMS_mask.sh ${cluster} ${filter} "all good exposure gabodsid" ${cluster}_good_coadd_conditions.txt ${ending} 'yes' 'yes' 2>&1 | tee -a OUT-coadd_${cluster}.${filter}.log
#./finish_RXJ2129_coadd_headers.sh
#./mask_coadd.sh ${cluster} W-C-RC coadd.final_final_combination.reg 'good' 2>&1 | tee -a OUT-mask_coadd.final.${cluster}.log

#vim ./adam_do_photometry_final_starcat.sh

export lensing_coadd_type="good"
export detect_filter=${filter};export lensing_filter=${filter}
#./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO  2>&1 | tee -a OUT-adam_do_photometry_${cluster}_PHOTO.log
#exit 0;
#grep "Success" /gpfs/slac/kipac/fs1/u/awright/SUBARU//photlogs/RXJ2129.W-C-RC.W-*.aper.cats.log
#./get_error_log.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//photlogs/RXJ2129.W-C-RC.W-*.aper.cats.err

./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper MERGE STARS SDSS 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_MERGE_STARS_SDSS.log
lensext='good' ; filter="W-C-RC"
./measure_shapes_wrapper.sh ${cluster} ${filter} ${lensext} 2>&1 | tee -a OUT-measure_shapes_wrapper_${cluster}.log

exit 0;

cd ~/gravitas/ldaclensing/
#vim adam_outline.sh
./adam_outline.sh ${cluster} ${filter} ${lensext}
exit 0;

./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper BIGMACSCALIB BIGMACSAPPLY 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_BIGMACS.log

#for fl in `\ls /nfs/slac/g/ki/ki18/anja/SUBARU//MACS1115+01/W-C-RC/SCIENCE/coadd_MACS1115+01_*/coadd.fits` ; do ./adam_quicktools_fix_header_verify.py ${fl} ; ./SeeingClearly_for_coadds.py ${fl} ; done

## then do photometric zp for Zw2089?:
#vim adam_do_photometry_final_starcat.sh  #check settings
./adam_do_photometry_final_starcat.sh ${cluster} ${filter} ${filter} aper PHOTO MERGE STARS BIGMACSCALIB BIGMACSAPPLY
export cluster=Zw2089 ; export detect_filter=${filter};export lensing_filter=${filter} ;export ending=OCFSIR ; export config="10_3"
./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO  2>&1 | tee -a OUT-adam_do_photometry_${cluster}_PHOTO.log
./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper MERGE STARS BIGMACSCALIB BIGMACSAPPLY 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_allmodes.log
