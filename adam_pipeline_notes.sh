#1.) get data from smoka website
see Evernote

#2.) preprocessing:
do_Subaru_preprocess_10_2_adam.sh do_Subaru_preprocess_10_2_simple.sh do_Subaru_preprocess_10_3_adam.sh do_Subaru_preprocess_10_3_simple.sh do_Subaru_preprocess_adam.sh do_Subaru_preprocess_config8.sh do_Subaru_preprocess_notes.sh do_Subaru_preprocess_template.sh

if including the BFcorr, then you have to use process_science_4channels_eclipse_para-noos_BFCTcorr.sh instead!!!
# if you haven't yet done distribute sets, then do this:./distribute_sets_subaru.sh ${SUBARUDIR} ${run}_${filter}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list
#3.) distribute sets and mask
adam_do_masking_master.sh 
#old# distribute_sets_subaru.sh and do_masking.sh OR instructions.sh

#4.) directories changed from $filter_$run to $filter AND setup header files (for each ${filter}) AND do the cross-talk correction
cluster='MACS0429-02'
filter_run_pairs='W-J-B_2015-12-15 W-S-Z+_2015-12-15'
./adam_do_linking_filter_dirs.sh ${cluster} W-C-RC_2012-07-23 W-J-B_2010-11-04 W-S-Z+_2010-11-04 W-S-Z+_2013-06-10 2>&1 | tee -a OUT-adam_do_linking_filter_dirs.log
./adam_do_update_headers.sh ${cluster} W-J-B_2015-12-15 W-S-Z+_2015-12-15 2>&1 | tee -a OUT-adam_do_update_headers_dirs.log

#CTcorr uses: adam_CTcorr_make_images_para.sh adam_CTcorr_run_correction_para.py
Made batch wrapper for them using the combo of these:
    * adam_TEMPLATE_switcher.py
    * adam_CTcorr_allOCF-TEMPLATE.sh

#4a.) change directory structure
#ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}_*/SCIENCE/SUPA*.fits /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}/SCIENCE/
#ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}_*/WEIGHTS/SUPA*.fits /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}/WEIGHTS/
#4b.) setup header files (for each ${filter})
#./update_config_header.sh /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}/SCIENCE SUBARU ${cluster}
#4c.) do the cross talk correction for 10_3 ONLY!


#5.) initial astrometry
#have `mode=astrom` in do_Subaru_register_4batch.sh
./do_Subaru_register_4batch.sh ${cluster} 2MASS astrom "W-J-B W-C-RC W-S-Z+"
#OR if in SDSS footprint: SDSS DR10 Finding Chart Tool at skyserver.sdss.org
./do_Subaru_register_4batch.sh ${cluster} SDSS-R6 astrom "W-J-B W-J-V W-C-RC W-C-IC W-S-Z+" 
#adam-CHECK# after astrometry call check the output plots in /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}/SCIENCE/astrom_scamp_2MASS/plots
## if using panstarrs for astrometric ref or for IC, then run this:
./adam_download_panstarrs_catalog.py && ./adam_combine_and_fix_panstarrs_catalog.py && ./adam_illumcorr_panstarrs_catalog.py
./do_Subaru_register_4batch.sh ${cluster} PANSTARRS astrom "W-J-B W-J-V W-C-RC W-C-IC W-S-Z+" 


#6.) illumination correction ( see Evernote)
## before running simple_ic.py, I need to have OBJNAME in all images (and consistent in all images). Might as well do the same for OBJECT and MYOBJ too.
vim pre_ic_headers.sh
## I also should rename PPRUN to PPRUN0 and have filter_run be the pattern for PPRUN
ipython simple_ic_SDSS.py
ipython simple_ic_PANSTARRS.py
## check IC results with:
./adam_illumination_correction_quality_check.sh


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
filter=W-S-Z+
#example: bsub -q long -W 7000 -R rhel60 -o /nfs/slac/kipac/fs1/u/awright/batch_files/bsubbable//OUT-2017-8-23-do_coadd_batch_${filter}.out  -e /nfs/slac/kipac/fs1/u/awright/batch_files/bsubbable//OUT-2017-8-23-do_coadd_batch_${filter}.err "./do_coadd_batch.sh MACS1115+01 W-S-Z+ 'all exposure good' /u/ki/awright/wtgpipeline/foo OCFSFI"
#ds9 -zscale -rgb -red ${SUBARUDIR}/${cluster}/W-S-Z+/SCIENCE/coadd_${cluster}_good/coadd.fits -green ${SUBARUDIR}/${cluster}/W-C-RC/SCIENCE/coadd_${cluster}_all/coadd.fits -blue ${SUBARUDIR}/${cluster}/W-J-B/SCIENCE/coadd_${cluster}_all/coadd.fits -regions load ${SUBARUDIR}/${cluster}/masks/coadd.asteroids.reg &
## THESE MIGHT ALSO BE HELPFUL:
# make coadds easy to view in ds9 together:
# 	adam_make_coadds_dir.sh
# 	MACS1115+01_coadd.log
# make looping over filter and submitting coadd jobs to the cluster easier:
# 	submit_coadd_batch3.sh



#9.) backmasking and stellar rings (masking at chip-level in light of coadd-level information)
#9a.) backmasking (see Evernote)
adam_make_backmask_ims.py
# finish all of the backmasking run (below) to apply all of the regions to the final coadds and remake the coadds
./adam_reg2weights-maybe_coadd_catchup.sh ${cluster} "W-C-RC_2010-11-04" > OUT-backmask_catchup.log 2>&1
#9b.) stellar rings (see Evernote)
#make rings by fitting ~/wtgpipeline/rings.reg on top of individual stars at the chip-level in ds9 (see Evernote)
adam_make_autosuppression_ims.py #makes autosuppression directory with images that can be used to place stellar halos
#might help: adam_use_fix_autosuppression.sh 
#Currently $ending would be "OCF", once the IC works, it should be "OCFR". probably $queue should be "long"
queue=medium
ending=OCFSI
./batch_suppress.sh ${cluster} ${filter} /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}/SCIENCE/autosuppression $ending $queue
#./batch_suppress.sh ${cluster} ${filter} /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}/SCIENCE/autosuppression/10_2/ $ending $queue
./move_suppression.sh MACS0416-24 W-C-RC  $ending
## soften_rings.sh: might be helpful if the rings appear to have over-subtracted things a bit.



#10.) star and asteroid coadd-level masking
./mask_coadd.sh ${cluster} W-C-RC #make coadd.stars.reg, then fix it in ds9
ds9 -cmap bb -zscale ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits -regions load ${SUBARUDIR}/${cluster}/masks/coadd.stars.reg &
./mask_coadd.sh ${cluster} W-C-RC coadd.stars.reg 2>&1 | tee -a OUT-mask_coadd.stars.log
ds9 -zscale -rgb -red ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_good/coadd.fits -green ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits -blue ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits -regions load ${SUBARUDIR}/${cluster}/masks/coadd.asteroids.reg &
./mask_coadd.sh ${cluster} W-C-RC coadd.asteroids.reg gabodsid1554 2>&1 | tee -a OUT-mask_coadd.asteroids.log



#11.) do_photometry.sh
## everything together here: fgas_photometry_driver_template.sh
export cluster=MACS0416-24; export ending="OCFR" ; export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU ; export INSTRUMENT=SUBARU
export cluster=MACS1226+21; export ending="OCFI" ;export INSTRUMENT=SUBARU ;export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU/
export detect_filter=W-C-RC;export lensing_filter=W-C-RC
export cluster=Zw2089 ; export detect_filter=W-J-V;export lensing_filter=W-J-V ;export ending=OCFSIR ; export config="10_3"
# first make sure this is right: cluster_cat_filters.dat
./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO MERGE STARS SDSS BIGMACSCALIB BIGMACSAPPLY
#or is it?: ./adam_do_photometry_final_starcat.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO MERGE STARS BIGMACSCALIB BIGMACSAPPLY

# Now with PureStarCalib, do this:

#1# ./adam_do_photometry_final_starcat.sh modes: PHOTO MERGE STARS SHAPES [ SDSS ]
# 	NOT photometry scripts also measure shapes! ( just made a SHAPES mode for adam_do_photometry_final_starcat.sh )
#	example: lensext='good' ; filter="W-C-RC" ; cluster="MACS0416-24"
#	adam-example# ./measure_shapes_wrapper.sh ${cluster} ${filter} ${lensext}
#2# cd ~/gravitas/ldacpipeline/ ... get poly fit, etc.
#3# return to this directory and do BIGMACSCALIB BIGMACSAPPLY

#12.) photo-z calculation using bpz.py
#adam-note#  inputfile= /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.cat
#adam-note#  outputfile= /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.APER1.1.CWWSB_capak.list.all.EVERY.cat
#adam-look# OK, now instead of adam_bpz_wrapper.py, we're using ./adam_bpz_wrapper_v2.py
cd ~/gravitas/photoz_analysis/ 
vim adam_bpz_wrapper_v2.py
. bpz.ini
./adam_bpz_wrapper_v2.py

#Ok, now you can move on to the lensing scripts!
cd ~/ldaclensing
vim adam_outline.sh
