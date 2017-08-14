#! /bin/bash -xv

# superscript to reduce the dataset subaru0602
#
#

REDDIR=`pwd`

#export SUBARUDIR=/nfs/slac/g/ki/ki02/xoc/anja/SUBARU
export SUBARUDIR=/u/br/mallen/work/SUBARU/



RAWDATA=/nfs/slac/g/ki/ki11/daveb/rawdata/subaru0602

run=2002-06-04

#####################################################################
####  preliminary stuff:  copy images, bring them in pipeline format,
####  sort into subdirectories
#####################################################################
#
#cp ${RAWDATA}/SUPA*.fits.gz ${SUBARUDIR}
#
#### (re-)pack the original images
#
#cd ${SUBARUDIR}
#
#gunzip *.fits.gz
#
#find . -maxdepth 1 -name SUPA????????\*fits > allfiles_$$.txt
#
#sed 's/[0-9]\.fits//' allfiles_$$.txt | sort | uniq > uniqfiles_$$.txt
#
#if [ ! -d RAWDATA ]; then
#  mkdir ${run}_RAWDATA
#fi
#
#while read IMAGE
#do
#  BASE=`basename ${IMAGE}`
#  echo ${BASE}
#  mefcreate ${BASE}?.fits -OUTPUT_IMAGE ${BASE}.fits 
#  mv ${BASE}?.fits ${run}_RAWDATA
#done < uniqfiles_$$.txt
#
#rm allfiles_$$.txt
#rm uniqfiles_$$.txt
# 
## sort images by type, filter
#
#find . -maxdepth 1 -name SUPA???????\*fits > allfiles_mef_$$.txt
#
#while read IMAGE
#do
#  BASE=`basename ${IMAGE}`
#
#  filter=`dfits -x 1 ${BASE} | fitsort FILTER01 | awk '{if($1=="'${BASE}'") print $2}'`
#
#  obstype=`dfits -x 1 ${BASE} | fitsort DATA-TYP | awk '{if($1=="'${BASE}'") print $2}'`
#
#  exptime=`dfits -x 1 ${BASE} | fitsort EXPTIME | awk '{if($1=="'${BASE}'") print $2}'`
#
#  long=`awk 'BEGIN{if('${exptime}'>=30) print 1; else print 0}'`
#
#  if [ "${obstype}" = "OBJECT" ];then
#     if [ ${long} -eq 1 ]; then
#         obstype=SCIENCE
#     else
#         obstype=STANDARD
#     fi
#  fi
#
#  if [ "${obstype}" = "BIAS" ] || [ "${obstype}" = "DARK" ]; then
#      filter=${obstype}
#  fi
#
#  if [ ! -d ${run}_${filter} ]; then
#    mkdir ${run}_${filter}
#  fi
#
#  if [ ! -d ${run}_${filter}/${obstype} ]; then
#    mkdir ${run}_${filter}/${obstype}
#  fi
#
#  if [ ! -d ${run}_${filter}/${obstype}/ORIGINALS ]; then
#    mkdir ${run}_${filter}/${obstype}/ORIGINALS
#  fi
#
#  echo ${BASE} ${obstype} ${exptime} ${long}
#  
#  mv ${BASE} ${run}_${filter}/${obstype}/ORIGINALS
#
#done < allfiles_mef_$$.txt
#
#rm allfiles_mef_$$.txt
#
#cd ${REDDIR}

##################################################################
### create and load the SUBARU.ini file
### !!! DO NOT COMMENT THIS BLOCK !!!
##################################################################

./setup_SUBARU.sh ${SUBARUDIR}/${run}_*/SCIENCE/ORIGINALS
export INSTRUMENT=SUBARU


##################################################################
# process the BIAS frames (per chip)
##################################################################

#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_BIAS BIAS

### first quality check: run  imstats  , if necessary, reject files:
# ./check_files.sh  ${SUBARUDIR}/${run}_BIAS BIAS "" 8000 12000

### overscan-correct BIAS frames, OC+BIAS correct flats
#./parallel_manager.sh ./process_bias_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS



####################################################################
# pre-processing of individual chips,
# per filter
####################################################################

### this can be set up to loop over the filters 
#filters="W-J-V W-C-IC W-J-B"
filters="W-C-RC"

for filter in ${filters}
do

  #### if necessary, rename the STANDARD directory
  #mv ${SUBARUDIR}/${run}_${filter}/STANDARD_STAR ${SUBARUDIR}/${run}_${filter}/STANDARD
  
  
  #### re-split the files, overwrite headers
  #### (note that you may have to substitute DOMEFLAT for SKYFLAT)
  
  #./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
  #./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} SKYFLAT
  #./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} STANDARD
  
  
  #### copy the master BIAS
  #mkdir ${SUBARUDIR}/${run}_${filter}/BIAS
  #cp ${SUBARUDIR}/${run}_BIAS/BIAS/BIAS_*.fits ${SUBARUDIR}/${run}_${filter}/BIAS
  
  #### overscan+bias correct the FLAT fields
  #./parallel_manager.sh ./process_flat_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS SKYFLAT
  
  #### OC+flat SCIENCE frames, create superflat
  #./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS SKYFLAT SCIENCE NORESCALE NOFRINGE
  #./maskBadOverscans.py ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA
  #./maskAutotracker.py ${SUBARUDIR}/${run}_${filter} SCIENCE
 # ./spikefinder.sh  ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA OFCS
 # ./parallel_manager.sh ./create_illumfringe_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
 # ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE RESCALE ILLUM
  
#  ./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA OFCS 8 -32
  #### at this stage: inspect SCIENCE/BINNED frames; if necessary, reject individual frames (bright stars, etc.)
  #### by listing them in file  superflat_exclusion
  #### ---> repeat previous step
  
  #### also at this stage: mask artefacts in individual frames: satellite tracks, etc.
  #### transform ds9-region file into ww-readable file:
  #./transform_ds9_reg_alt.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
  
  
  ### create weight images
  #./parallel_manager.sh ./create_norm_para.sh ${SUBARUDIR}/${run}_${filter} SKYFLAT
  #./parallel_manager.sh ./create_norm_para.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
  #./parallel_manager.sh ./create_global_weights_para.sh ${SUBARUDIR}/${run}_${filter} SKYFLAT_norm 0.6 1.3 BIAS -9 9 SCIENCE_norm 0.9 1.1

  # create_global_weights_para.sh first 2 numbers are acceptable range of 
  # pixels in normalized flat file. .6 - 1.3 includes corners (may cause 
  # problems in the future, just keep an eye out.   If you have a dark frame, 
  # substitue for BIAS.  basiaclly, tell it all things that you want to feed 
  # in to make global file with the acceptable ranges. first input forms the 
  # basis, any subsequent inputs just flag pixels



  ### note: I've modified create_global_weights_para.sh so that it looks for reg
  ### files in a reg-directory
  
  #./parallel_manager.sh ./create_weights_para_dm.sh ${SUBARUDIR}/${run}_${filter} SCIENCE OFCS
  ### note: I've changed the saturation level to 30000 in weights.ww
  ### (was:62000)
  
  #./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} WEIGHTS SUPA OFCS.weight 8 -32
  
  
  ###################################################################################
  ###### ignore for now
  ###################################################################################
  ###
  ###### process STANDARD frames  ---  ignore for now
  ####./parallel_manager.sh ./process_standard_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS SKYFLAT SCIENCE STANDARD NORESCALE
  ####./parallel_manager.sh ./create_illumfringe_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD
  ####./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} STANDARD RESCALE ILLUM
  ####./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} STANDARD SUPA OFCS 8 -32
  ###
  ###### .... and then???
  
  
  #################################################################################
  ### set-specific processing
  #################################################################################
  
  #groups together cluster pointings from one run -> produces 'set_x' dirs
#  ./distribute_sets.sh ${SUBARUDIR}/${run}_${filter} SCIENCE OFCS 1000

  #exit 0;
  
  #write sets.dat file manually, format:
  #   set_x NAME RA DEC  of cluster
  #   use dfits to look at header to get object name
  cat ${SUBARUDIR}/${run}_${filter}/sets.dat |\
  {
  while read setd name ra dec
  do

    # to be removed
    if [ ${setd} == "set_5" ]; then

    echo ${setd} ${name} ${ra} ${dec}

    #adds astrometric info to weights images
    ./parallel_manager.sh  ./create_astromcats_weights_para.sh ${SUBARUDIR}/${run}_${filter} ${setd} OFCS WEIGHTS OFCS.weight
    
    ### check PSF in individual exposures
    #via running SE, finding stars, extra
    ./parallel_manager.sh ./check_science_PSF_para.sh ${SUBARUDIR}/${run}_${filter} ${setd} OFCS
    ./check_science_PSF_plot.sh ${SUBARUDIR}/${run}_${filter} ${setd} OFCS
    ./merge_sex_ksb.sh ${SUBARUDIR}/${run}_${filter} ${setd} OFCS
    
    
    ./create_run_list.sh ${SUBARUDIR}/${run}_${filter} ${setd} OFCS ROTATION uniqruns_$$.txt NOSPLIT
    RUNS=""
    NRUNS=0
    while read SUBRUN
    do
      RUNS="${RUNS} ${REDDIR}/${SUBRUN}.txt"
      NRUNS=$(( ${NRUNS} + 1 ))
    done < uniqruns_$$.txt    
    ./create_astrometrix_astrom_run.sh ${SUBARUDIR}/${run}_${filter} ${setd} OFCS USNOB1 ${RUNS}
    
    ./create_photometrix.sh ${SUBARUDIR}/${run}_${filter} ${setd} OFCS
    
    ./create_stats_table.sh ${SUBARUDIR}/${run}_${filter} ${setd} OFCS headers
    ./create_absphotom_photometrix.sh ${SUBARUDIR}/${run}_${filter} ${setd}
    ./make_checkplot_stats.sh ${SUBARUDIR}/${run}_${filter} ${setd} chips.cat6 STATS ${setd}
    
    ./parallel_manager.sh ./create_skysub_para.sh ${SUBARUDIR}/${run}_${filter} ${setd} OFCS ".sub" TWOPASS
    
    ./prepare_coadd_swarp.sh -m ${SUBARUDIR}/${run}_${filter} \
                             -s ${setd} \
                             -e "OFCS.sub" \
                             -n ${name} \
                             -w ".sub" \
                             -eh headers \
                             -r ${ra} \
                             -d ${name} \
                             -l ${SUBARUDIR}/${run}_${filter}/${setd}/cat/chips.cat6 STATS \
                                "(SEEING<2.0);" \
                                ${SUBARUDIR}/${run}_${filter}/${setd}/${name}.cat
    
    ./parallel_manager.sh ./resample_coadd_swarp_para.sh ${SUBARUDIR}/${run}_${filter} ${setd} "OFCS.sub" ${name} ${REDDIR}
    ./perform_coadd_swarp.sh ${SUBARUDIR}/${run}_${filter} ${setd} ${name}


    fi
  
  done
  }

done
