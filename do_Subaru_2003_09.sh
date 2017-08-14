#! /bin/bash -xv

# superscript to reduce the dataset subaru0903
#
#

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki02/xoc/anja/SUBARU

RAWDATA=/nfs/slac/g/ki/ki11/daveb/rawdata/subaru0903
RAWDATA=/nfs/slac/g/ki/ki02/xoc/anja/SUBARU/auxiliary/2003-09-25_BIAS

run=2003-09-25

#####################################################################
####  preliminary stuff:  copy images, bring them in pipeline format,
####  sort into subdirectories
#####################################################################

#cp ${RAWDATA}/SUPA*.fits* ${SUBARUDIR}
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
#
#
#cd ${REDDIR}
#
#exit 0;

### create and load the SUBARU.ini file

./setup_SUBARU.sh ${SUBARUDIR}/${run}_*/SCIENCE/ORIGINALS
export INSTRUMENT=SUBARU


##################################################################
# process the BIAS frames (per chip)
##################################################################

#./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_BIAS BIAS

### first quality check: run  imstats  , if necessary, reject files:
# ./check_files.sh  ${SUBARUDIR}/${run}_BIAS BIAS "" 8000 12000

### overscan-correct BIAS frames, OC+BIAS correct flats
./parallel_manager.sh ./process_bias_eclipse_para.sh ${SUBARUDIR}/${run}_BIAS BIAS


filters="W-J-V W-C-IC W-J-B"
filters="W-C-IC W-J-B"

for filter in ${filters}
do

### re-split the files, overwrite headers

mv ${SUBARUDIR}/${run}_${filter}/STANDARD_STAR ${SUBARUDIR}/${run}_${filter}/STANDARD

./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} SCIENCE
./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} DOMEFLAT
./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} STANDARD

#####################################################################
## pre-processing of individual chips
#####################################################################



#mkdir ${SUBARUDIR}/${run}_${filter}/BIAS
#cp ${SUBARUDIR}/${run}_BIAS/BIAS/BIAS_*.fits ${SUBARUDIR}/${run}_${filter}/BIAS

#./parallel_manager.sh ./process_flat_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS DOMEFLAT

done
