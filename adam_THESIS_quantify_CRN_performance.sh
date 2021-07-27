#!/bin/bash
set -xv
#run on eye_CRnum0_Pnum0.fits first
file="/nfs/slac/kipac/fs1/u/awright/eyes/eye-10_3_cr.2.1/W-C-RC/both/edge_out/inputs/eye_CRnum0_Pnum0.fits"
#can use this dir if needed: /u/ki/awright/my_data/thesis_stuff/CRN_final_purecomp/

## first the stuff that's in create_weights_raw_delink_para_CRNitschke_setup.sh
INSTRUMENT=SUBARU
. ${INSTRUMENT:?}.ini > /tmp/out.log 2>&1
. progs.ini > /tmp/out.log 2>&1
SATLEVEL=${SATURATION:-30000}



runCRN=0
runold=1

filter='W-C-RC'
cluster='THESIS'
files=`\ls /nfs/slac/kipac/fs1/u/awright/eyes/eye-10_3_cr.2.1/W-C-RC/both/edge_out/inputs/eye_CRnum[0-9]_Pnum*.fits  /nfs/slac/kipac/fs1/u/awright/eyes/eye-10_3_cr.2.1/W-C-RC/both/edge_out/inputs/eye_CRnum1[0-9]_Pnum*.fits /nfs/slac/kipac/fs1/u/awright/eyes/eye-10_3_cr.2.1/W-C-RC/both/edge_out/inputs/eye_CRnum20_Pnum*.fits`

for file in ${files}
do
	BASE=`basename ${file} .fits`
	CHIP=10
	#rm tmp_file.tmp
	#./adam_THESIS_get_sextract_thresholds.py ${file} tmp_file.tmp
	#cat CRNitschke_final_eye_training.txt tmp_file.tmp >> CRNitschke_final_eye_training.tmp.txt
	#sort CRNitschke_final_eye_training.tmp.txt | uniq | column -t >> CRNitschke_final_eye_training.txt

	#adam# START MY STUFF!
	#adam# determine the seeing and get the optimal sextractor thresholds
	rms_fwhm_dt_ft=( `grep $BASE CRNitschke_final_eye_training.txt | awk '{print $2, $3, $4, $5}'`)
	rms=${rms_fwhm_dt_ft[0]}
	fwhm=${rms_fwhm_dt_ft[1]}
	dt=${rms_fwhm_dt_ft[2]}
	ft=${rms_fwhm_dt_ft[3]}
	#adam# run sextractor to get the cosmics
	#CRN-files#
	#       1.) data_SCIENCE_cosmics/SEGMENTATION_CRN-cosmics_${cluster}_${filter}.${BASE}.fits
	#       2.) data_SCIENCE_cosmics/FILTERED_CRN-cosmics_${cluster}_${filter}.${BASE}.fits \
	#       3.) data_SCIENCE_cosmics/CATALOG_CRN-cosmics_${cluster}_${filter}.${BASE}.cat
	#       check with: ls -lrth /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/ > CRN-cosmics_latest_run.log
	if [ "${runCRN}" == "1" ]; then
		if [ ! -f "/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_CRN-cosmics_${cluster}_${filter}.${BASE}.fits" ]; then
		  ${P_SEX} ${file}   -c /u/ki/awright/thiswork/eyes/CRNitschke/config-sex.10_3_cr \
				-SEEING_FWHM ${fwhm} \
				-FILTER_NAME /u/ki/awright/thiswork/eyes/CRNitschke/retina-eye.10_3_cr.ret \
				-FILTER_THRESH ${ft} \
				-DETECT_THRESH ${dt} \
				-ANALYSIS_THRESH ${dt} \
				-DETECT_MINAREA 1 \
				-CHECKIMAGE_TYPE SEGMENTATION,FILTERED \
				-CHECKIMAGE_NAME /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_CRN-cosmics_${cluster}_${filter}.${BASE}.fits,/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/FILTERED_CRN-cosmics_${cluster}_${filter}.${BASE}.fits \
				-CATALOG_NAME /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/CATALOG_CRN-cosmics_${cluster}_${filter}.${BASE}.cat
		else
		  echo "SKIPPING sextractor for ${file}"
		fi
		exit_stat=$? 
		if [ "${exit_stat}" -gt "0" ]; then
		    echo "adam-look: create_weights_raw_delink_para_CRNitschke.sh failed for file=${file}"
		    exit 1
		fi 
		#adam# now put in the FT400 stuff in order to pick up extra cosmics
		ft400=$(echo "400.0 / $rms" |bc -l)
		#adam# run sextractor to get the FT400 cosmics
		#CRN-files#
		#       4.) data_SCIENCE_cosmics/FILTERED_FT400_CRN-cosmics_${cluster}_${filter}.${BASE}.fits \
		#       5.) data_SCIENCE_cosmics/CATALOG_FT400_CRN-cosmics_${cluster}_${filter}.${BASE}.cat
		#       check (1-6) with: ls -lrth /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/ > CRN-cosmics_latest_run.log
		if [ ! -f "/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/FILTERED_FT400_CRN-cosmics_${cluster}_${filter}.${BASE}.fits" ]; then
		  ${P_SEX} ${file}   -c /u/ki/awright/thiswork/eyes/CRNitschke/config-sex.10_3_cr \
				  -SEEING_FWHM ${fwhm} \
				  -FILTER_NAME /u/ki/awright/thiswork/eyes/CRNitschke/retina-eye.10_3_cr.ret \
				  -FILTER_THRESH ${ft400} \
				  -DETECT_THRESH ${dt} \
				  -ANALYSIS_THRESH ${dt} \
				  -DETECT_MINAREA 1 \
				  -CHECKIMAGE_TYPE FILTERED \
				  -CHECKIMAGE_NAME /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/FILTERED_FT400_CRN-cosmics_${cluster}_${filter}.${BASE}.fits \
				  -CATALOG_NAME /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/CATALOG_FT400_CRN-cosmics_${cluster}_${filter}.${BASE}.cat
		else
		  echo "SKIPPING sextractor FT400 for ${file}"
		fi
		exit_stat=$? 
		if [ "${exit_stat}" -gt "0" ]; then
		    echo "adam-look: create_weights_raw_delink_para_CRNitschke.sh failed for file=${file}"
		    exit 1
		fi 
		#adam# put keywords in the headers of these files:
		/u/ki/awright/InstallingSoftware/pythons/header_key_add.py /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/FILTERED_FT400_CRN-cosmics_${cluster}_${filter}.${BASE}.fits CRN_FT=${ft400} CRN_DT=${dt} CRN_DMA=1 MYSEEING=${fwhm} MYRMS=${rms} MYOBJ=${cluster}
		/u/ki/awright/InstallingSoftware/pythons/header_key_add.py /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/FILTERED_CRN-cosmics_${cluster}_${filter}.${BASE}.fits CRN_FT=${ft} CRN_DT=${dt} CRN_DMA=1 MYSEEING=${fwhm} MYRMS=${rms} MYOBJ=${cluster}
		/u/ki/awright/InstallingSoftware/pythons/header_key_add.py /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_CRN-cosmics_${cluster}_${filter}.${BASE}.fits CRN_FT=${ft} CRN_DT=${dt} CRN_DMA=1 MYSEEING=${fwhm} MYRMS=${rms} MYOBJ=${cluster}
		/u/ki/awright/InstallingSoftware/pythons/header_key_add.py ${file} MYSEEING=${fwhm} MYOBJ=${cluster} FILTER=${filter} MYRMS=${rms} IMAGEID=$CHIP
		#adam#now get the stars
		#CRN-files#
		#       6.) data_SCIENCE_stars/SEGMENTATION_stars_${BASE}OCF.fits 
		#       7.) data_SCIENCE_stars/CATALOG_stars_${BASE}OCF.cat
		#       check with: ls -lrth /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_stars/ > CRN-stars_latest_run.log
		#       check with: ls -lrth /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_stars/ > CRN-stars_latest_run.log
		if [ ! -f "/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_stars/SEGMENTATION_CRN-stars_${cluster}_${filter}.${BASE}.fits" ]; then
		  /u/ki/awright/thiswork/eyes/CRNitschke/stars2block.py ${file}
		else
		  echo "SKIPPING stars2block.py for ${file}"
		fi
		exit_stat=$? 
		if [ "${exit_stat}" -gt "0" ]; then
		    echo "adam-look: create_weights_raw_delink_para_CRNitschke.sh failed for file=${file}"
		    exit 1
		fi 
		#adam# now run the blocked_blender!
		#CRN-files#
		#       8.)  data_SCIENCE_compare/BBout_ORIGINAL_MACS0416-24_W-S-Z+.SUPA0125868_4.fits
		#       9.) data_SCIENCE_compare/BBout_WOblend_MACS0416-24_W-S-Z+.SUPA0125868_4.fits
		#       10.) data_SCIENCE_compare/BB_ERASED_bthresh075_BBCR_MACS0416-24_W-S-Z+.SUPA0125868_4.fits
		#       11.) data_SCIENCE_compare/BBrevised_bthresh075_BBCR_MACS0416-24_W-S-Z+.SUPA0125868_4.fits
		#       12.) data_SCIENCE_cosmics/SEGMENTATION_BB_CRN-cosmics_MACS0416-24_W-S-Z+.SUPA0125868_4.fits
		#       LOTS OF PLOTS IN: /u/ki/awright/data/eyes/CRNitschke_output/plot_SCIENCE_compare/
		#       check with:ls -lrth /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_compare/ > CRN-compare_last_run.log
		#                  ls -lrth /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_BB_CRN*.fits >> CRN-compare_last_run.log
		if [ ! -f "/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_BB_CRN-cosmics_${cluster}_${filter}.${BASE}.fits" ]; then
		  /u/ki/awright/thiswork/eyes/CRNitschke/blocked_blender.2.2.py ${file}
		else
		  echo "SKIPPING blocked_blender.2.2.py for ${file}"
		fi
		exit_stat=$? 
		if [ "${exit_stat}" -gt "0" ]; then
		    echo "adam-look: create_weights_raw_delink_para_CRNitschke.sh failed for file=${file}"
		    exit 1
		fi 
		#SS# next line runs StarStripper.py
		#CRN-files#
		#       13.) data_SCIENCE_cosmics/SEGMENTATION_KeepOrRM-starlike_cosmics_MACS0416-24_W-J-B.SUPA0126101_7.fits
		#       14.) data_SCIENCE_cosmics/StarRMout_KeepOrRM-purified_cosmics_MACS0416-24_W-J-B.SUPA0126101_7.fits
		#       15.) data_SCIENCE_cosmics/SEGMENTATION_BBSS_CRN-cosmics_MACS0416-24_W-J-B.SUPA0126101_7.fits
		#       LOTS OF PLOTS IN: /u/ki/awright/data/eyes/CRNitschke_output/plot_SCIENCE_SS/
		#       check with:ls -lrth /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_KeepOrRM-starlike_cosmics*.fits > CRN-SS_last_run.log
		#                  ls -lrth /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_BBSS_CRN*.fits >> CRN-SS_last_run.log
		#                  ls -lrth /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/StarRMout_KeepOrRM-purified_cosmics*.fits >> CRN-SS_last_run.log
		if [ ! -f "/u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_BBSS_CRN-cosmics_${cluster}_${filter}.${BASE}.fits" ]; then
		  /u/ki/awright/thiswork/eyes/CRNitschke/StarStripper.py ${file}
		else
		  echo "SKIPPING StarStripper.py for ${file}"
		fi
		exit_stat=$? 
		if [ "${exit_stat}" -gt "0" ]; then
		    echo "adam-look: create_weights_raw_delink_para_CRNitschke.sh failed for file=${file}"
		    exit 1
		fi 
		#adam# END MY STUFF!
		# Expand the cosmic ray masking:
		if [ ${config} == "10_3" ]; then
			if [ ${filter} == "W-J-B" ]; then
			  flmid="BB"
			elif [ ${filter} == "W-S-G+" ]; then
			  flmid="BB"
			elif [ ${filter} == "W-J-V" ]; then
			  flmid="BB"
			elif [ ${filter} == "W-C-RC" ]; then
			  seeing_ok=$(echo "${fwhm}<0.70" |bc -l)
			  if [ ${seeing_ok} -eq 1 ]; then
			      flmid="BBSS"
			  else
				flmid="BB"
			  fi
			elif [ ${filter} == "W-S-I+" ]; then
			  seeing_ok=$(echo "${fwhm}<0.90" |bc -l)
			  if [ ${seeing_ok} -eq 1 ]; then
			      flmid="BBSS"
			  else
				flmid="BB"
			  fi
			elif [ ${filter} == "W-C-IC" ]; then
			  seeing_ok=$(echo "${fwhm}<0.80" |bc -l)
			  if [ ${seeing_ok} -eq 1 ]; then
			      flmid="BBSS"
			  else
				flmid="BB"
			  fi
			elif [ ${filter} == "W-S-Z+" ]; then
			  seeing_ok=$(echo "${fwhm}<1.20" |bc -l)
			  if [ ${seeing_ok} -eq 1 ]; then
			      flmid="BBSS"
			  else
				flmid="BB"
			  fi
			else
			  echo "exiting because none the filter " ${filter} " isn't recognized as a filter"
			  exit 1
			fi
		elif [ ${config} == "10_2" ]; then
		    seeing_ok=$(echo "${fwhm}<1.00" |bc -l)
		    if [ ${seeing_ok} -eq 1 ]; then
			flmid="BBSS"
		    else
			flmid="BB"
		    fi
		else
		    echo "exiting because none the config " ${config} " isn't recognized as a config"
		    exit 1
		fi
		echo "BB or BBSS (filter=" ${filter} " seeing=" ${fwhm} " config=" ${config} "):" ${flmid}
		#SS# next line uses BBSS output!
		cp /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_${flmid}_CRN-cosmics_${cluster}_${filter}.${BASE}.fits ${TEMPDIR}/cosmic_${CHIP}_$$.fits
		sfdir/expand_cosmics_mask ${TEMPDIR}/cosmic_${CHIP}_$$.fits  ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits
		exit_stat=$? 
		if [ "${exit_stat}" -gt "0" ]; then
		    echo "adam-look: create_weights_raw_delink_para_CRNitschke.sh failed for file=${file}"
		    exit 1
		fi 
		#compare to /nfs/slac/kipac/fs1/u/awright/eyes/eye-10_3_cr.2.1/W-C-RC/both/edge_out/outputs/
		OUTDIR="/u/ki/awright/my_data/thesis_stuff/CRN_final_purecomp/"

		OUTIMAGECRN="${OUTDIR}/CRNmask_${BASE}.fits"
		exOUTIMAGECRN="${OUTDIR}/CRNmask_expanded_${BASE}.fits"
		#cp /u/ki/awright/data/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_${flmid}_CRN-cosmics_${cluster}_${filter}.${BASE}.fits ${OUTIMAGECRN}
		mv ${TEMPDIR}/cosmic_${CHIP}_$$.fits  ${OUTIMAGECRN}
		mv ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits  ${exOUTIMAGECRN}
	fi

	if [ "${runold}" == "1" ]; then
		OUTDIR="/u/ki/awright/my_data/thesis_stuff/CRN_final_purecomp/"

		OUTIMAGEOLD="${OUTDIR}/OLDmask_${BASE}.fits"
		exOUTIMAGEOLD="${OUTDIR}/OLDmask_expanded_${BASE}.fits"

		## now run the old-style masker
		MASKOLD=${CONF}/cosmic.ret.sex
		conffile=cosmic.conf.sex
		${P_SEX} ${file} -c ${conffile} -CHECKIMAGE_NAME \
		                    ${TEMPDIR}/cosmic_${CHIP}_$$.fits \
		                    -FILTER_NAME ${MASKOLD} \
		                    -CATALOG_NAME ${TEMPDIR}/cosmic.cat_$$ \
		                    -SEEING_FWHM ${fwhm}
		sfdir/expand_cosmics_mask ${TEMPDIR}/cosmic_${CHIP}_$$.fits  ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits
		exit_stat=$? 
		if [ "${exit_stat}" -gt "0" ]; then
		    echo "adam-look: create_weights_raw_delink_para_CRNitschke.sh failed for file=${file}"
		    exit 1
		fi
		mv ${TEMPDIR}/cosmic_${CHIP}_$$.fits  ${OUTIMAGEOLD}
		mv ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits  ${exOUTIMAGEOLD}
		#./adam_make_comparable_CRmask.py ${file} ${OUTIMAGECRN} ${OUTIMAGEOLD}
	fi
done
echo "adam_THESIS_CRN_performance_metrics.py"
