#1.) get data from smoka website
see Evernote

#2.) preprocessing:
do_Subaru_preprocess_10_2_adam.sh do_Subaru_preprocess_10_2_simple.sh do_Subaru_preprocess_10_3_adam.sh do_Subaru_preprocess_10_3_simple.sh do_Subaru_preprocess_adam.sh do_Subaru_preprocess_config8.sh do_Subaru_preprocess_notes.sh do_Subaru_preprocess_template.sh

#3.) distribute sets and mask
adam_do_masking_master.sh 
#old# distribute_sets_subaru.sh and do_masking.sh OR instructions.sh

#4.) directories changed from $filter_$run to $filter AND setup header files (for each ${filter}) AND do the cross-talk correction
./adam_do_linking_filter_dirs.sh ${cluster} ${filter_run_pairs}
./adam_do_update_headers.sh ${cluster} ${filter_run_pairs}
adam_CTcorr_make_images_para.sh
adam_CTcorr_run_correction_para.py
#4a.) change directory structure
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}_*/SCIENCE/SUPA*.fits /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}/SCIENCE/
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}_*/WEIGHTS/SUPA*.fits /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}/WEIGHTS/
#4b.) setup header files (for each ${filter})
./update_config_header.sh /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}/SCIENCE SUBARU ${cluster}
#4c.) do the cross talk correction for 10_3 ONLY!

#5.) initial astrometry
#have `mode=astrom` in do_Subaru_register_4batch.sh
./do_Subaru_register_4batch.sh ${cluster} 2MASS astrom "W-J-B W-C-RC W-S-Z+"
#OR if in SDSS footprint: SDSS DR10 Finding Chart Tool at skyserver.sdss.org
./do_Subaru_register_4batch.sh ${cluster} SDSS-R6 astrom "W-J-B W-J-V W-C-RC W-C-IC W-S-Z+" 
#adam-CHECK# after astrometry call check the output plots in /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}/SCIENCE/astrom_scamp_2MASS/plots

#6.) illumination correction ( see Evernote)
ipython develop_simple_ic/simple_ic.py

#7.) final astrometry
#have `mode=photom` in do_Subaru_register_4batch.sh
./do_Subaru_register_4batch.sh ${cluster} 2MASS photom "W-J-B W-C-RC W-S-Z+"
#OR if in SDSS footprint: SDSS DR10 Finding Chart Tool at skyserver.sdss.org
./do_Subaru_register_4batch.sh ${cluster} SDSS-R6 photom "W-J-B W-J-V W-C-RC W-C-IC W-S-Z+"
#adam-CHECK# check the output plots in /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}/SCIENCE/astrom_photom_scamp_2MASS/plots

#8.) coaddition ("all" and "exposure" for all filters, also "good" for lensing filter)
#in one code: adam_coadd_many.sh
./adam_coadd_many.sh ${cluster} ${ending} ${filter}
#example: ./adam_coadd_many.sh "MACS0416-24" "OCFR" "W-J-B W-C-RC W-S-Z+"
./do_coadd_batch.sh ${cluster} ${filter} "all exposure" 2>&1 | tee -a OUT-do_coadd_batch-all_exposure-${cluster}_${filter}.log

#9.) backmasking and stellar rings (masking at chip-level in light of coadd-level information)
#9a.) backmasking (see Evernote)
adam_make_backmask_ims.py
#9b.) stellar rings (see Evernote)
#make rings by fitting ~/bonnpipeline/rings.reg on top of individual stars at the chip-level in ds9 (see Evernote)
adam_make_autosuppression_ims.py #makes autosuppression directory with images that can be used to place stellar halos
#might help: adam_use_fix_autosuppression.sh 
#Currently $ending would be "OCF", once the IC works, it should be "OCFR". probably $queue should be "long"
./batch_suppress.sh MACS0416-24 W-C-RC /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/autosuppression $ending $queue
./move_suppression.sh MACS0416-24 W-C-RC  $ending


#10.) star and asteroid coadd-level masking
./mask_coadd.sh MACS1226+21 W-C-RC #make coadd.stars.reg, then fix it in ds9
ds9 -cmap bb -zscale ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits -regions load ${SUBARUDIR}/${cluster}/masks/coadd.stars.reg &
./mask_coadd.sh MACS1226+21 W-C-RC coadd.stars.reg 2>&1 | tee -a OUT-mask_coadd.stars.log
ds9 -zscale -rgb -red ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_good/coadd.fits -green ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits -blue ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits -regions load ${SUBARUDIR}/${cluster}/masks/coadd.asteroids.reg &
./mask_coadd.sh MACS1226+21 W-C-RC coadd.asteroids.reg 2>&1 | tee -a OUT-mask_coadd.asteroids.log

#11.) do_photometry.sh
export cluster=MACS0416-24; export ending="OCFR" ; export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU ; export INSTRUMENT=SUBARU
export cluster=MACS1226+21; export ending="OCFI" ;export INSTRUMENT=SUBARU ;export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU/
export detect_filter=W-C-RC;export lensing_filter=W-C-RC
./do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO MERGE STARS SDSS CALIB APPLY SLR

##last ran##
./do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper STARS SDSS CALIB 2>&1 | tee -a scratch/OUT-do_photometry_STARS_SDSS_CALIB.log 
#todo# APPLY SLR
