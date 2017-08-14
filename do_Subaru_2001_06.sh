#! /bin/bash -xv

# superscript to reduce the dataset subaru0601
#
# ONLY 2 BIAS FRAMES !!!!!!??????????

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki02/xoc/anja/SUBARU
export INSTRUMENT=Subaru_10_1

RAWDATA=/nfs/slac/g/ki/ki11/daveb/rawdata/subaru0601

run=2001_06
filter=W-J-V

#####################################################################
####  preliminary stuff:  copy images, bring them in pipeline format,
####  sort into subdirectories
#####################################################################

cp ${RAWDATA}/SUPA*.fits.gz ${SUBARUDIR}

### (re-)pack the original images

cd ${SUBARUDIR}

gunzip *.fits.gz

find . -maxdepth 1 -name SUPA????????\*fits > allfiles_$$.txt

sed 's/[0-9]\.fits//' allfiles_$$.txt | sort | uniq > uniqfiles_$$.txt

if [ ! -d RAWDATA ]; then
  mkdir ${run}_RAWDATA
fi

while read IMAGE
do
  BASE=`basename ${IMAGE}`
  echo ${BASE}
  mefcreate ${BASE}?.fits -OUTPUT_IMAGE ${BASE}.fits 
  mv ${BASE}?.fits ${run}_RAWDATA
done < uniqfiles_$$.txt

rm allfiles_$$.txt
rm uniqfiles_$$.txt

# sort images by type, filter

find . -maxdepth 1 -name SUPA???????\*fits > allfiles_mef_$$.txt

while read IMAGE
do
  BASE=`basename ${IMAGE}`

  filter=`dfits -x 1 ${BASE} | fitsort FILTER01 | awk '{if($1=="'${BASE}'") print $2}'`

  obstype=`dfits -x 1 ${BASE} | fitsort DATA-TYP | awk '{if($1=="'${BASE}'") print $2}'`

  exptime=`dfits -x 1 ${BASE} | fitsort EXPTIME | awk '{if($1=="'${BASE}'") print $2}'`

  long=`awk 'BEGIN{if('${exptime}'>=30) print 1; else print 0}'`

  if [ "${obstype}" = "OBJECT" ];then
     if [ ${long} -eq 1 ]; then
         obstype=SCIENCE
     else
         obstype=STANDARD
     fi
  fi

  if [ "${obstype}" = "BIAS" ] || [ "${obstype}" = "DARK" ]; then
      filter=${obstype}
  fi

  if [ ! -d ${run}_${filter} ]; then
    mkdir ${run}_${filter}
  fi

  if [ ! -d ${run}_${filter}/${obstype} ]; then
    mkdir ${run}_${filter}/${obstype}
  fi

  if [ ! -d ${run}_${filter}/${obstype}/ORIGINALS ]; then
    mkdir ${run}_${filter}/${obstype}/ORIGINALS
  fi

  echo ${BASE} ${obstype} ${exptime} ${long}
  
  mv ${BASE} ${run}_${filter}/${obstype}/ORIGINALS

done < allfiles_mef_$$.txt

rm allfiles_mef_$$.txt

cd ${REDDIR}

exit 0;
### re-split the files, overwrite headers

./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_BIAS BIAS
./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} SKYFLAT
./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} STANDARD




#####################################################################
## pre-processing of individual chips
#####################################################################


### first quality check: run  imstats  , if necessary, reject files:
 ./check_files.sh  ${SUBARUDIR}/${run}_${filter} BIAS 8000 12000
mv ${SUBARUDIR}/${run}_BIAS/BIAS/SUPA0010968_*.fits ${SUBARUDIR}/${run}_BIAS/BIAS/BADMODE
mv ${SUBARUDIR}/${run}_BIAS/BIAS/SUPA0011057_*.fits ${SUBARUDIR}/${run}_BIAS/BIAS/BADMODE

### overscan-correct BIAS frames, OC+BIAS correct flats
./parallel_manager.sh ./process_bias_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS
mkdir ${SUBARUDIR}/${run}_${filter}/BIAS
cp ${SUBARUDIR}/${run}_BIAS/BIAS/BIAS_*.fits ${SUBARUDIR}/${run}_${filter}/BIAS

./parallel_manager.sh ./process_flat_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS SKYFLAT

### OC+flat SCIENCE frames, create superflat
./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS SKYFLAT SCIENCE NORESCALE NOFRINGE

./parallel_manager.sh ./create_illumfringe_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE

./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE RESCALE ILLUM

./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA OFCS 8 -32
### at this stage: inspect SCIENCE frames; if necessary, reject individual frames (bright stars, etc.)
### by listing them in file  superflat_exclusion
### ---> repeat previous step

### at this stage: mask artefacts in individual frames: satellite tracks, etc.
### transform ds9-region file into ww-readable file:
 ./transform_ds9_reg_alt.sh ${SUBARUDIR}/${run}_${filter} SCIENCE


### create weight images
./parallel_manager.sh ./create_norm_para.sh ${SUBARUDIR}/${run}_${filter} SKYFLAT
./parallel_manager.sh ./create_norm_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
./parallel_manager.sh ./create_global_weights_para.sh ${SUBARUDIR}/${run}_${filter} SKYFLAT_norm 0.6 1.3 BIAS -9 9 SCIENCE_norm 0.9 1.1
### note: I've modified create_global_weights_para.sh so that it looks for reg
### files in a reg-directory

./parallel_manager.sh ./create_weights_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE OFCS
### note: I've changed the saturation level to 30000 in weights.ww
### (was:62000)

./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} WEIGHTS SUPA OFCS.weight 8 -32


### process STANDARD frames
./parallel_manager.sh ./process_standard_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS SKYFLAT SCIENCE STANDARD NORESCALE
./parallel_manager.sh ./create_illumfringe_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD
./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD RESCALE ILLUM
./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} STANDARD SUPA OFCS 8 -32

### .... and then???


#################################################################################
### set-specific processing
#################################################################################

./distribute_sets.sh ${SUBARUDIR}/${run}_${filter} SCIENCE OFCS 1000

./parallel_manager.sh  ./create_astromcats_weights_para.sh ${SUBARUDIR}/${run}_${filter} set_6 OFCS WEIGHTS OFCS.weight

### check PSF in individual exposures
./parallel_manager.sh ./check_science_PSF_para.sh ${SUBARUDIR}/${run}_${filter} set_6 OFCS
./check_science_PSF_plot.sh ${SUBARUDIR}/${run}_${filter} set_6 OFCS
./merge_sex_ksb.sh ${SUBARUDIR}/${run}_${filter} set_6 OFCS


./create_run_list.sh ${SUBARUDIR}/${run}_${filter} set_6 OFCS ROTATION uniqruns_$$.txt NOSPLIT
RUNS=""
NRUNS=0
while read run
do
  RUNS="${RUNS} ${REDDIR}/${run}.txt"
  NRUNS=$(( ${NRUNS} + 1 ))
done < uniqruns_$$.txt

./create_astrometrix_astrom_run.sh ${SUBARUDIR}/${run}_${filter} set_6 OFCS USNOB1 ${RUNS}

./create_photometrix.sh ${SUBARUDIR}/${run}_${filter} set_6 OFCS

./create_stats_table.sh ${SUBARUDIR}/${run}_${filter} set_6 OFCS headers
./create_absphotom_photometrix.sh ${SUBARUDIR}/${run}_${filter} set_6
./make_checkplot_stats.sh ${SUBARUDIR}/${run}_${filter} set_6 chips.cat6 STATS set_6

./parallel_manager.sh ./create_skysub_para.sh ${SUBARUDIR}/${run}_${filter} set_6 OFCS ".sub" TWOPASS

./prepare_coadd_swarp.sh -m ${SUBARUDIR}/${run}_${filter} \
                         -s set_6 \
                         -e "OFCS.sub" \
                         -n "MACS1423" \
                         -w ".sub" \
                         -eh headers \
                         -r 215.94954167 \
                         -d 24.07863611 \
                         -l ${SUBARUDIR}/${run}_${filter}/set_6/cat/chips.cat6 STATS \
                            "(SEEING<2.0);" \
                            ${SUBARUDIR}/${run}_${filter}/set_6/MACS1423_V.cat

./parallel_manager.sh ./resample_coadd_swarp_para.sh ${SUBARUDIR}/${run}_${filter} set_6 "OFCS.sub" MACS1423 ${REDDIR}
./perform_coadd_swarp.sh ${SUBARUDIR}/${run}_${filter} set_6 MACS1423
