#!/bin/bash
set -xv
#adam-chain#CRN! Runs the CRNitschke cosmic ray masker. BUT ONLY ON ONE FILE AT A TIME!
#adam-does# this code executes the CRNitschke cosmic finder on all of the images!
#adam-call_example# ./parallel_manager.sh create_weights_raw_delink_para_CRNitschke_file.sh ${SUBARUDIR}/${cluster}/${filter}_${run} SCIENCE ${ending} WEIGHTS ${filter} filename.fits
#adam-predecessor# create_weights_raw_delink_para_10_3_cr.sh

# $1: main directory
# $2: science dir.
# $3: image extension (ext) on ..._iext.fits (i is the chip number)
#     note that spikefinder images have an additional .sf
# $4: weight directory
# $5: Filter to use for cosmic ray detection (OPTIONAL)
# $6: file

. ${INSTRUMENT:?}.ini > /tmp/subaru_ini_output.log 2>&1
REDDIR=`pwd`
export WEIGHTSDIR=${1}/${4}

#adam# this actually does match the value for the 10_3 config
SATLEVEL=${SATURATION:-30000}

#adam# this is needed for the 10_2 config
#if [ $# -eq 6 ]; then
#   MASK=$5
#fi

#you MUST run create_weights_raw_delink_para_CRNitschke_setup.sh FIRST!!!

echo "START: create_weights_raw_delink_para_CRNitschke_file.sh $1 $2 $3 $4 $5 ${!#}"
filter=$5
file=$6
BASE=`basename ${file} $3.fits`
BASE_len=${#BASE}
CHIP_pos=$(echo "$BASE_len - 1" |bc -l)
CHIP=${BASE:CHIP_pos}
if [ $CHIP -eq 0 ]; then CHIP=10 ; fi
#SHNT
#adam# START MY STUFF!
#adam# determine the seeing and get the optimal sextractor thresholds
rms_fwhm_dt_ft=( `grep $BASE CRNitschke_final_${cluster}_${run}_${filter}.txt | awk '{print $2, $3, $4, $5}'`)
rms=${rms_fwhm_dt_ft[0]}
fwhm=${rms_fwhm_dt_ft[1]}
dt=${rms_fwhm_dt_ft[2]}
ft=${rms_fwhm_dt_ft[3]}
#adam# run sextractor to get the cosmics
#CRN-files#
#	1.) data_SCIENCE_cosmics/SEGMENTATION_CRN-cosmics_${cluster}_${filter}.${BASE}.fits
#	2.) data_SCIENCE_cosmics/FILTERED_CRN-cosmics_${cluster}_${filter}.${BASE}.fits \
#	3.) data_SCIENCE_cosmics/CATALOG_CRN-cosmics_${cluster}_${filter}.${BASE}.cat
# 	check with: ls -lrth /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/ > CRN-cosmics_latest_run.log
${P_SEX} ${file}   -c /u/ki/awright/thiswork/eyes/CRNitschke/config-sex.10_3_cr \
		-SEEING_FWHM ${fwhm} \
		-FILTER_NAME /u/ki/awright/thiswork/eyes/CRNitschke/retina-eye.10_3_cr.ret \
		-FILTER_THRESH ${ft} \
		-DETECT_THRESH ${dt} \
		-ANALYSIS_THRESH ${dt} \
		-DETECT_MINAREA 1 \
		-CHECKIMAGE_TYPE SEGMENTATION,FILTERED \
		-CHECKIMAGE_NAME /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_CRN-cosmics_${cluster}_${filter}.${BASE}.fits,/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/FILTERED_CRN-cosmics_${cluster}_${filter}.${BASE}.fits \
		-CATALOG_NAME /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/CATALOG_CRN-cosmics_${cluster}_${filter}.${BASE}.cat
#adam# now put in the FT400 stuff in order to pick up extra cosmics
ft400=$(echo "400.0 / $rms" |bc -l)
#adam# run sextractor to get the cosmics
#CRN-files#
#	4.) data_SCIENCE_cosmics/FILTERED_FT400_CRN-cosmics_${cluster}_${filter}.${BASE}.fits \
#	5.) data_SCIENCE_cosmics/CATALOG_FT400_CRN-cosmics_${cluster}_${filter}.${BASE}.cat
# 	check (1-6) with: ls -lrth /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/ > CRN-cosmics_latest_run.log
${P_SEX} ${file}   -c /u/ki/awright/thiswork/eyes/CRNitschke/config-sex.10_3_cr \
		-SEEING_FWHM ${fwhm} \
		-FILTER_NAME /u/ki/awright/thiswork/eyes/CRNitschke/retina-eye.10_3_cr.ret \
		-FILTER_THRESH ${ft400} \
		-DETECT_THRESH ${dt} \
		-ANALYSIS_THRESH ${dt} \
		-DETECT_MINAREA 1 \
		-CHECKIMAGE_TYPE FILTERED \
		-CHECKIMAGE_NAME /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/FILTERED_FT400_CRN-cosmics_${cluster}_${filter}.${BASE}.fits \
		-CATALOG_NAME /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/CATALOG_FT400_CRN-cosmics_${cluster}_${filter}.${BASE}.cat
#adam# put keywords in the headers of these files:
/u/ki/awright/InstallingSoftware/pythons/header_key_add.py /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/FILTERED_FT400_CRN-cosmics_${cluster}_${filter}.${BASE}.fits CRN_FT=${ft400} CRN_DT=${dt} CRN_DMA=1 MYSEEING=${fwhm} MYRMS=${rms} MYOBJ=${cluster}
/u/ki/awright/InstallingSoftware/pythons/header_key_add.py /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/FILTERED_CRN-cosmics_${cluster}_${filter}.${BASE}.fits CRN_FT=${ft} CRN_DT=${dt} CRN_DMA=1 MYSEEING=${fwhm} MYRMS=${rms} MYOBJ=${cluster}
/u/ki/awright/InstallingSoftware/pythons/header_key_add.py /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_CRN-cosmics_${cluster}_${filter}.${BASE}.fits CRN_FT=${ft} CRN_DT=${dt} CRN_DMA=1 MYSEEING=${fwhm} MYRMS=${rms} MYOBJ=${cluster}
/u/ki/awright/InstallingSoftware/pythons/header_key_add.py ${file} MYSEEING=${fwhm} MYOBJ=${cluster}
#adam#: now get the stars
#CRN-files#
#	6.) data_SCIENCE_stars/SEGMENTATION_stars_${BASE}OCF.fits 
# 	7.) data_SCIENCE_stars/CATALOG_stars_${BASE}OCF.cat
# 	check with: ls -lrth /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_stars/ > CRN-stars_latest_run.log
/u/ki/awright/thiswork/eyes/CRNitschke/stars2block.py ${file}
#adam# now run the blocked_blender!
#CRN-files#
#	8.)  data_SCIENCE_compare/BBout_ORIGINAL_MACS0416-24_W-S-Z+.SUPA0125868_4.fits
# 	9.) data_SCIENCE_compare/BBout_WOblend_MACS0416-24_W-S-Z+.SUPA0125868_4.fits
# 	10.) data_SCIENCE_compare/BB_ERASED_bthresh075_BBCR_MACS0416-24_W-S-Z+.SUPA0125868_4.fits
# 	11.) data_SCIENCE_compare/BBrevised_bthresh075_BBCR_MACS0416-24_W-S-Z+.SUPA0125868_4.fits
# 	12.) data_SCIENCE_cosmics/SEGMENTATION_BB_CRN-cosmics_MACS0416-24_W-S-Z+.SUPA0125868_4.fits
# 	LOTS OF PLOTS IN: /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/plot_SCIENCE_compare/
# 	check with:ls -lrth /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_compare/ > CRN-compare_last_run.log
# 		   ls -lrth /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_BB_CRN*.fits >> CRN-compare_last_run.log
/u/ki/awright/thiswork/eyes/CRNitschke/blocked_blender.2.2.py ${file}
#adam# #SS# next line runs StarStripper.py
#CRN-files#
#	13.) data_SCIENCE_cosmics/SEGMENTATION_KeepOrRM-starlike_cosmics_MACS0416-24_W-J-B.SUPA0126101_7.fits
#	14.) data_SCIENCE_cosmics/StarRMout_KeepOrRM-purified_cosmics_MACS0416-24_W-J-B.SUPA0126101_7.fits
#	15.) data_SCIENCE_cosmics/SEGMENTATION_BBSS_CRN-cosmics_MACS0416-24_W-J-B.SUPA0126101_7.fits
# 	LOTS OF PLOTS IN: /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/plot_SCIENCE_SS/
# 	check with:ls -lrth /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_KeepOrRM-starlike_cosmics*.fits > CRN-SS_last_run.log
# 		   ls -lrth /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_BBSS_CRN*.fits >> CRN-SS_last_run.log
# 		   ls -lrth /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/StarRMout_KeepOrRM-purified_cosmics*.fits >> CRN-SS_last_run.log
/u/ki/awright/thiswork/eyes/CRNitschke/StarStripper.py ${file}
#adam# END MY STUFF!
if [ ${filter} == "W-J-B" ]; then
    flmid="BB"
elif [ ${filter} == "W-S-G+" ]; then
    flmid="BB"
elif [ ${filter} == "W-J-V" ]; then
    flmid="BB"
elif [ ${filter} == "W-C-RC" ]; then
    flmid="BB"
elif [ ${filter} == "W-S-I+" ]; then
    flmid="BB"
elif [ ${filter} == "W-C-IC" ]; then
    flmid="BB"
elif [ ${filter} == "W-S-Z+" ]; then                                                                                                                                                                            
    flmid="BBSS"
else
    echo "exiting because none the filter " ${filter} " isn't recognized as a filter"
    exit 1
fi
echo "BB or BBSS: " ${filter} ${flmid}
# Expand the cosmic ray masking:
#SS# next line uses BBSS output!
cp /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_${flmid}_CRN-cosmics_${cluster}_${filter}.${BASE}.fits ${TEMPDIR}/cosmic_${CHIP}_$$.fits
sfdir/expand_cosmics_mask ${TEMPDIR}/cosmic_${CHIP}_$$.fits  ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits
mv ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits  ${TEMPDIR}/cosmic_${CHIP}_$$.fits 
# create ww config file on the fly
#SHNT:check and make sure cosmic flags (#1) are in the right spots by checking the ${WEIGHTSDIR}/${BASE}$3.flag.fits file
#CRN-files#
# 	16.)${SUBARUDIR}/${cluster}/${filter}_${run}/WEIGHTS/${BASE}${ending}.flag.fits
# 	check with: ls -lrth ${SUBARUDIR}/${cluster}/${filter}_${run}/WEIGHTS/*${ending}.flag.fits > CRN-weights_last_run.log #not necessary
if [ -r "$1/$2/diffmask/${BASE}$3.sf.fits" ]; then
    echo "WEIGHT_NAMES ${WEIGHTSDIR}/globalweight_${CHIP}.fits,${TEMPDIR}/cosmic_${CHIP}_$$.fits,${file},/$1/$2/diffmask/${BASE}$3.sf.fits" > ${TEMPDIR}/${BASE}.ww_$$
    echo "WEIGHT_MIN -1e9,-1e9,-${SATLEVEL},0.1"       >> ${TEMPDIR}/${BASE}.ww_$$
    echo "WEIGHT_MAX 1e9,0.1,${SATLEVEL},1"       >> ${TEMPDIR}/${BASE}.ww_$$
    echo "WEIGHT_OUTFLAGS 0,1,2,4"       >> ${TEMPDIR}/${BASE}.ww_$$
else
    echo "WEIGHT_NAMES ${WEIGHTSDIR}/globalweight_${CHIP}.fits,${TEMPDIR}/cosmic_${CHIP}_$$.fits,${file}" > ${TEMPDIR}/${BASE}.ww_$$
    echo "WEIGHT_MIN -1e9,-1e9,-${SATLEVEL}"           >> ${TEMPDIR}/${BASE}.ww_$$
    echo "WEIGHT_MAX 1e9,0.1,${SATLEVEL}"         >> ${TEMPDIR}/${BASE}.ww_$$
    echo "WEIGHT_OUTFLAGS 0,1,2"          >> ${TEMPDIR}/${BASE}.ww_$$
fi
#
echo "FLAG_NAMES ${WEIGHTSDIR}/globalflag_${CHIP}.fits"                        >> ${TEMPDIR}/${BASE}.ww_$$
echo 'FLAG_MASKS "0x42"'                        >> ${TEMPDIR}/${BASE}.ww_$$
echo 'FLAG_WMASKS "0x42"'                       >> ${TEMPDIR}/${BASE}.ww_$$
echo 'FLAG_OUTFLAGS "32,64"'                     >> ${TEMPDIR}/${BASE}.ww_$$
#
if [ -s "/$1/$2/reg/${BASE}.reg" ]; then
    echo "POLY_NAMES /$1/$2/reg/${BASE}.reg"  >> ${TEMPDIR}/${BASE}.ww_$$
    echo "POLY_OUTFLAGS 256"                    >> ${TEMPDIR}/${BASE}.ww_$$
else
    echo 'POLY_NAMES ""'                      >> ${TEMPDIR}/${BASE}.ww_$$
    echo 'POLY_OUTFLAGS ""'                   >> ${TEMPDIR}/${BASE}.ww_$$
fi
#
echo "OUTWEIGHT_NAME ${WEIGHTSDIR}/${BASE}$3.weight.fits"  >> ${TEMPDIR}/${BASE}.ww_$$
echo "OUTFLAG_NAME ${WEIGHTSDIR}/${BASE}$3.flag.fits"  >> ${TEMPDIR}/${BASE}.ww_$$

# then run weightwatcher
${P_WW} -c ${TEMPDIR}/${BASE}.ww_$$
rm -f ${TEMPDIR}/${BASE}.ww_$$

# clean up temporary files
if [ -f ${TEMPDIR}/cosmic_${CHIP}_$$.fits ]; then
    rm -f ${TEMPDIR}/cosmic_${CHIP}_$$.fits
fi

if [ -f ${TEMPDIR}/cosmic.cat_$$ ]; then
    rm -f ${TEMPDIR}/cosmic.cat_$$
fi

