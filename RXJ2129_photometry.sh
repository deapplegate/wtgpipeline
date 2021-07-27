#!/bin/bash
set -xv

export cluster=RXJ2129
export ending=OCFSRI
export filter=W-C-RC
export lensing_coadd_type="good"
#vim ./adam_do_photometry.sh
export cluster=RXJ2129 ; export detect_filter=${filter};export lensing_filter=${filter} ;export ending=OCFSRI ; export config="10_3"
./adam_do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO  2>&1 | tee -a OUT-adam_do_photometry_${cluster}_PHOTO.log
./adam_do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper MERGE STARS BIGMACSCALIB BIGMACSAPPLY 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_allmodes.log

#for fl in `\ls /u/ki/awright/data//MACS1115+01/W-C-RC/SCIENCE/coadd_MACS1115+01_*/coadd.fits` ; do ./adam_quicktools_fix_header_verify.py ${fl} ; ./SeeingClearly_for_coadds.py ${fl} ; done
