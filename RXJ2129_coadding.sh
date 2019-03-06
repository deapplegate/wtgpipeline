#!/bin/bash
set -xv


export cluster=RXJ2129
export ending=OCFSIR
export filter=W-C-RC
str=''
for i in 1 2 3 4 5 6 7 8 9 10 ; do str=" ${SUBARUDIR}/RXJ2129/W-C-RC/SCIENCE/SUPA0135171_${i}OCFSI.fits -region load SUPA0135171_${i}.reg ${str} " ; done
echo $str

# after initial coadd

## make some useful smoothed images
adam_make_autosuppression_ims.py #makes autosuppression directory with images that can be used to place stellar halos
Note this might help: adam_use_fix_autosuppression.sh
adam_make_backmask_ims.py

## check for background subtract errors:
./adam_BACKsubERRORcheck.sh MACS0429-02

## first do backmasking for all supas:
supa=SUPA0135166
python -i -- backmask.py ${SUBARUDIR}/${cluster}/W-C-RC/SCIENCE/BACKMASK/${supa}-all.coadd.smoothed.fits /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-C-RC/SCIENCE/${supa}_[0-9]*${ending}.fits

## apply those masks to the weights
./adam_reg2weights_filter.sh ${cluster} ${filter}

## if there is anything else that must be done by-hand on chips:

./maskImages.pl -r /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-J-V/SCIENCE/reg/ -l toMask_Zw2089.log -d /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-J-V/SCIENCE_weighted/ SUP


# apply edge, asteroid, and star masks to flags:
 star and asteroid coadd-level masking
 ./mask_coadd.sh ${cluster} W-C-RC #make coadd.stars.reg, then fix it in ds9
 ds9 -cmap bb -zscale ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits -regions load ${SUBARUDIR}/${cluster}/masks/coadd.stars.reg &
 ./mask_coadd.sh ${cluster} W-C-RC coadd.stars.reg 2>&1 | tee -a OUT-mask_coadd.stars.log
 ds9 -zscale -rgb -red ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_good/coadd.fits -green ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits -blue ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits -regions load ${SUBARUDIR}/${cluster}/masks/coadd.asteroids.reg &
 ./mask_coadd.sh ${cluster} W-C-RC coadd.asteroids.reg gabodsid1554 2>&1 | tee -a OUT-mask_coadd.asteroids.log

## make edgemask
export lensing_coadd_type="gabodsid1554"
cp /u/ki/awright/wtgpipeline/coadd_template.edgemask.reg ${SUBARUDIR}/${cluster}/masks/coadd_${lensing_filter}_${lensing_coadd_type}.edgemask.reg
./mask_coadd.sh ${cluster} W-C-RC coadd_${lensing_filter}_${lensing_coadd_type}.edgemask.reg "good"
./adam_quicktools_convertRegion2Poly_single_file.py /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/masks/coadd.final_combination.reg
for lensing_coadd_type in "gabodsid4356" "gabodsid2965" "all" "good"
do
	./mask_coadd.sh ${cluster} ${filter} coadd.final_combination.reg ${lensing_coadd_type} 2>&1 | tee -a OUT-mask_coadd.final.${cluster}.log 
done

# SUPPRESSION RINGS:

## setup template directory, which might be rotation dependent
mkdir ~/my_data/SUBARU/RXJ2129/W-C-RC/SCIENCE/autosuppression/template_rings_rot1
...

## make pre-smoothed images for ring placement /autosuppression_smoothed_chips/SUPA0135166_8OCFSI_smoothed.fits
vim /adam_make_autosuppression_chip_ims2.py #set make_smooth and make_reg=1
./adam_make_autosuppression_chip_ims2.py ~/my_data/SUBARU/${cluster}/${filter}/SCIENCE/ ${ending}

## set rings in-place for chips at the center of the rings (save in wcs):
ds9e ../autosuppression_smoothed_chips/SUPA0135166_8OCFSI_smoothed.fits -region load SUPA0135166_8.reg &
ds9e ../autosuppression_smoothed_chips/SUPA0135166_4OCFSI_smoothed.fits -region load SUPA0135166_4.reg &


## cp from the center-ring chips to the other chips that star's rings overflow into (4-> 5,10,9 and 8 -> 7,3)
for fl in `\ls SUPA01351*_8.reg` ; do ochip=`basename ${fl} _8.reg` ; cp ${fl} ${ochip}_3.reg ; done
for fl in `\ls SUPA01351*_8.reg` ; do ochip=`basename ${fl} _8.reg` ; cp ${fl} ${ochip}_7.reg ; done
for fl in `\ls SUPA01351*_4.reg` ; do ochip=`basename ${fl} _4.reg` ; cp ${fl} ${ochip}_5.reg ; done
for fl in `\ls SUPA01351*_4.reg` ; do ochip=`basename ${fl} _4.reg` ; cp ${fl} ${ochip}_9.reg ; done
for fl in `\ls SUPA01351*_4.reg` ; do ochip=`basename ${fl} _4.reg` ; cp ${fl} ${ochip}_10.reg ; done

## set rings in-place for overflow chips (save in image or in wcs and move in next step):
ds9e ../autosuppression_smoothed_chips/SUPA0135166_7OCFSI_smoothed.fits -region load SUPA0135166_7.reg &
ds9e ../autosuppression_smoothed_chips/SUPA0135166_3OCFSI_smoothed.fits -region load SUPA0135166_3.reg &
ds9e ../autosuppression_smoothed_chips/SUPA0135166_5OCFSI_smoothed.fits -region load SUPA0135166_5.reg &
ds9e ../autosuppression_smoothed_chips/SUPA0135166_9OCFSI_smoothed.fits -region load SUPA0135166_9.reg &
ds9e ../autosuppression_smoothed_chips/SUPA0135166_10OCFSI_smoothed.fits -region load SUPA0135166_10.reg &

## if needed, move from wcs to image coords:
./adam_quicktools_reg_wcs2phys.sh

## lastly do the subtraction:
queue='medium'
export ending=OCFSI
export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU/
export cluster=MACS1115+01
export filter=W-C-RC

./batch_suppress.sh ${cluster} ${filter} /nfs/slac/g/ki/ki18/anja/SUBARU/${cluster}/${filter}/SCIENCE/autosuppression/ $ending $queue
## remember I put the put_flags_in_weights.py script into the do_coadd_batch.sh script, so now everything should work ok

## redo the coadd
# first put settings in here: RXJ2129_good_coadd_conditions.txt
./adam_pre_coadd_cleanup.sh ${cluster} ${filter}
./do_coadd_batch.sh ${cluster} ${filter} "all good exposure gabodsid" ${cluster}_good_coadd_conditions.txt ${ending} 2>&1 | tee -a OUT-coadd_${cluster}.${filter}.log

## then do photometric zp:
vim adam_do_photometry.sh  #check settings
./adam_do_photometry.sh ${cluster} ${filter} ${filter} aper PHOTO MERGE STARS BIGMACSCALIB BIGMACSAPPLY
export cluster=Zw2089 ; export detect_filter=${filter};export lensing_filter=${filter} ;export ending=OCFSIR ; export config="10_3"
vim ./adam_do_photometry.sh
#vim ./adam_do_photometry.sh
export cluster=RXJ2129 ; export detect_filter=${filter};export lensing_filter=${filter} ;export ending=OCFSRI ; export config="10_3"
./adam_do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper PHOTO  2>&1 | tee -a OUT-adam_do_photometry_${cluster}_PHOTO.log
./adam_do_photometry.sh ${cluster} ${detect_filter} ${lensing_filter} aper MERGE STARS BIGMACSCALIB BIGMACSAPPLY 2>&1 | tee -a OUT-adam_do_photometry_${cluster}_allmodes.log

for fl in `\ls /nfs/slac/g/ki/ki18/anja/SUBARU//MACS1115+01/W-C-RC/SCIENCE/coadd_MACS1115+01_*/coadd.fits` ; do ./adam_quicktools_fix_header_verify.py ${fl} ; ./SeeingClearly_for_coadds.py ${fl} ; done
