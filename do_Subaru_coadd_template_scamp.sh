#! /bin/bash -xv

### new coaddition script
###
### the astro-/photometry can be done via SCAMP (preferred) or
### ASTROMETRIX
###
### $Id: do_Subaru_coadd_template_scamp.sh,v 1.8 2009-01-16 22:19:13 anja Exp $

. progs.ini
. bash_functions.include

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU

cluster="A2219"  # cluster nickname as in /nfs/slac/g/ki/ki02/xoc/anja/SUBARU/SUBARU.list

FILTERS="W-J-V W-J-B W-C-RC_2004-07-18 I"

IMAGESIZE="12000,12000"

# Do astrometric calibration with SCAMP or ASTROMETRIX ?
ASTROMMETHOD=SCAMP
#ASTROMMETHOD=ASTROMETRIX

# only for Scamp (use SDSS-R6 or 2MASS ) :
ASTROMETRYCAT=SDSS-R6

# for astrometrix (use SDSS5 or USNOB1):
ASTROMETRYCAT=SDSS5

ASTROMADD=""
if [ ${ASTROMMETHOD} = "SCAMP" ]; then
   ASTROMADD="_scamp_${ASTROMETRYCAT}"
   
fi

# need to keep track of the max number of NCHIPS for scamp
NCHIPSMAX=0

###############################################
######################
#Some Setup Stuff

export BONN_TARGET=${cluster}
export BONN_FILTER=${FILTERS}

lookupfile=/nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list

ra=`grep ${cluster} ${lookupfile} | awk '{print $3}'`
dec=`grep ${cluster} ${lookupfile} | awk '{print $4}'`

echo ${cluster} ${ra} ${dec}

LINE=""

#######################################
## Reset Logger
#adam-BL#./BonnLogger.py clear

##############################
### prep stuff, per filter ###
##############################

##################################################################
### Capture Variables
#adam-BL#./BonnLogger.py config \
#adam-BL#    cluster=${cluster} \
#adam-BL#    filterlist="${FILTERS}"

for filter in ${FILTERS}
do

  export BONN_FILTER=${filter}
  echo ${filter}

  echo ${filter}
  ./setup_SUBARU.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE
  export INSTRUMENT=SUBARU
  . ${INSTRUMENT:?}.ini

  #Find Ending
  testfile=`ls -1 $SUBARUDIR/$cluster/${filter}/SCIENCE/SUPA*_2*.fits | awk 'NR>1{exit};1'`
  ending=`basename ${testfile} | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`

  echo ${ending}

  #adam-BL#  ./BonnLogger.py clear
  #adam-BL#  ./BonnLogger.py config \
  #adam-BL#      cluster=${cluster} \
  #adam-BL#      filter=${filter} \
  #adam-BL#      config=${config} \
  #adam-BL#      ending=${ending}

  ##########################
  ### prepare coaddition ###
  ##########################
  
  ###adds astrometric info; makes directory cat with ${image}_${chip}${ending}.cat
  ./parallel_manager.sh  ./create_astromcats_weights_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} WEIGHTS ${ending}.weight

  ### check PSF in individual exposures
  ### via running SE, finding stars, extra
  ### all done in cat directory
  ### writes to .cat, adds .cat0 _ksb.cat1 _ksb.cat2 _ksb_tmp.cat2 _tmp.cat1 _tmp1.cat1  and PSFcheck/ , copy/
  
  ./parallel_manager.sh ./check_science_PSF_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
  ./check_science_PSF_plot.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
  ./merge_sex_ksb.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}

  ### prep for scamp:
  LINE="${LINE} ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}"

  if [ ${NCHIPS} -gt ${NCHIPSMAX} ];then
      NCHIPSMAX=${NCHIPS}
  fi

done

echo ${LINE}
echo ${NCHIPSMAX}
export NCHIPSMAX

####################################################################
### astrometric and photometric calibration:                     ###
###   this can be done with scamp for all filters simultaneously ###
###   or with astrometrix and photometrix                        ###
####################################################################

if [ ${ASTROMMETHOD} != "SCAMP" ]; then

  for filter in ${FILTERS}
  do

  ./setup_SUBARU.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE
  export INSTRUMENT=SUBARU
  . ${INSTRUMENT:?}.ini

  #Find Ending
  testfile=`ls -1 $SUBARUDIR/$cluster/${filter}/SCIENCE/SUPA*_2*.fits | awk 'NR>1{exit};1'`
  ending=`basename ${testfile} | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`

  export BONN_FILTER=${filter}
  echo ${filter}
  #adam-BL#  ./BonnLogger.py clear
  #adam-BL#  ./BonnLogger.py config \
  #adam-BL#      cluster=${cluster} \
  #adam-BL#      filter=${filter} \
  #adam-BL#      config=${config} \
  #adam-BL#      ending=${ending} \
  #adam-BL#    astrommethod=${ASTROMMETHOD}

  ### makes astrom/ and headers/
  ./create_run_list.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ROTATION uniqruns_$$.txt NOSPLIT
  RUNS=""
  NRUNS=0
  while read SUBRUN
  do
    RUNS="${RUNS} ${REDDIR}/${SUBRUN}.txt"
    NRUNS=$(( ${NRUNS} + 1 ))
  done < ${TEMPDIR}/uniqruns_$$.txt    
  echo ${RUNS}
  ./create_astrometrix_astrom_run.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ${ASTROMETRYCAT} ${RUNS}
  
  ### check whether the previous step worked
  nhead=`ls -1 ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/headers/*.head | wc | awk '{print $1}'`
  if [ ${nhead} -eq 0 ]; then
      echo "No header files were created - something's wrong!"
      exit 2;
  fi
  
  ### makes photom/ ; writes to headers/
  ./create_photometrix.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}

  done

else

  export BONN_FILTER=${FILTERS}

  #adam-BL#./BonnLogger.py clear
  #adam-BL#./BonnLogger.py config \
  #adam-BL#    cluster=${cluster} \
  #adam-BL#    filterlist="${FILTERS}" \
  #adam-BL#    astrommethod=${ASTROMMETHOD} \
  #adam-BL#    astrometrycat=${ASTROMETRYCAT} \

  ./create_scamp_astrom_photom.sh ${LINE} ${ASTROMETRYCAT}

fi

##################################################
### after possible calibration across filters: ###
### need to work per filter again              ###
##################################################

for filter in ${FILTERS}
do
  export BONN_FILTER=${filter}
  echo ${filter}

  ./setup_SUBARU.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE
  export INSTRUMENT=SUBARU
  . ${INSTRUMENT:?}.ini

  #Find Ending
  testfile=`ls -1 $SUBARUDIR/$cluster/${filter}/SCIENCE/SUPA*_2*.fits | awk 'NR>1{exit};1'`
  ending=`basename ${testfile} | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`

  #adam-BL#./BonnLogger.py config \
  #adam-BL#    cluster=${cluster} \
  #adam-BL#    filter=${filter} \
  #adam-BL#    config=${config} \
  #adam-BL#    ending=${ending} \
  #adam-BL#    astrommethod=${ASTROMMETHOD} \
  #adam-BL#    astrometrycat=${ASTROMETRYCAT} \

  ### makes plots/
  ./create_stats_table.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} headers${ASTROMADD}
  ./create_absphotom_photometrix.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE
  ./make_checkplot_stats.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE chips.cat6 STATS ${cluster}
  
### makes .sub.fits files
#  ./parallel_manager.sh ./create_skysub_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ".sub" TWOPASS
#  echo ${IMAGESIZE}

  ./prepare_coadd_swarp.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                           -s SCIENCE \
                           -e "${ending}.sub" \
                           -n ${cluster} \
                           -w ".sub" \
                           -eh headers${ASTROMADD} \
                           -r ${ra} \
                           -d ${dec} \
                           -i ${IMAGESIZE} \
                           -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 STATS \
                              "(SEEING<2.0);" \
                              ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}.cat

  ./parallel_manager.sh ./resample_coadd_swarp_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster} ${REDDIR}
  
  ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}
  
  
  ### add header keywords
 
  value ${cluster}
  writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}/coadd.fits OBJECT "${VALUE} / Target" REPLACE
  
  value ${filter}
  writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}/coadd.fits FILTER "${VALUE} / Filter" REPLACE
  

  ### update photometry
  if [ -f ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips_phot.cat5 ]; then
      MAGZP=`${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips_phot.cat5 -t ABSPHOTOM -k COADDZP | tail -n 1`
  else
      MAGZP=-1.0
  fi
  
  ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster} STATS coadd ${MAGZP} AB "(SEEING<2.0)"

  ###################################
  ##CHECKPOINT
  ###################################
#  #adam-BL#./BonnLogger.py checkpoint Coadd

done


