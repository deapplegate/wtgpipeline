#! /bin/bash -xv

### special coaddition script: astrometrix is run first
###
### the astro-/photometry can be done via SCAMP (preferred) or
### ASTROMETRIX
###
### $Id: do_Subaru_coadd_MACS0911.sh,v 1.3 2009-01-27 00:39:44 dapple Exp $

. progs.ini
. bash_functions.include

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki05/anja/SUBARU

cluster="MACS0911+17"  # cluster nickname as in /nfs/slac/g/ki/ki02/xoc/anja/SUBARU/SUBARU.list

FILTERS="W-C-IC"
ASTROM_FILTERS=""

NAXIS1=12000
NAXIS2=12000
IMAGESIZE="${NAXIS1},${NAXIS2}"

# Do astrometric calibration with SCAMP or ASTROMETRIX ?
ASTROMMETHOD=SCAMP

# only for Scamp (use SDSS-R6 or 2MASS ) :
ASTROMETRYCAT=SDSS-R6

# for astrometrix (use SDSS5 or USNOB1):
ASTROM_ASTROMETRYCAT=SDSS5

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
./BonnLogger.py clear

##############################
### prep stuff, per filter ###
##############################

##################################################################
### Capture Variables
./BonnLogger.py config \
    cluster=${cluster} \
    filterlist="${FILTERS}"

for filter in ${FILTERS}
do

  export BONN_FILTER=${filter}
  echo ${filter}
  ./BonnLogger.py clear

  ./setup_general.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE instrument_$$
  export INSTRUMENT=`cat instrument_$$`
  rm instrument_$$
  . ${INSTRUMENT:?}.ini

  echo ${NCHIPS}

  #Find Ending
  testfile=`ls -1 $SUBARUDIR/$cluster/${filter}/SCIENCE/*_2*.fits | awk 'NR>1{exit};1'`
  ending=`basename ${testfile} | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`

  echo ${ending}

  ./BonnLogger.py clear
  ./BonnLogger.py config \
      cluster=${cluster} \
      filter=${filter} \
      config=${config} \
      ending=${ending}

  ##########################
  ### prepare coaddition ###
  ##########################

  ###adds astrometric info; makes directory cat with ${image}_${chip}${ending}.cat
  if [ ! -d  ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat ];then

      if [ -d  ${SUBARUDIR}/${cluster}/${filter}/WEIGHTS_raw ];then
	  ./parallel_manager.sh  ./create_astromcats_weights_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} WEIGHTS_raw ${ending}.weight
      else
	  ./parallel_manager.sh  ./create_astromcats_weights_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} WEIGHTS ${ending}.weight     
      fi

  ### check PSF in individual exposures
  ### via running SE, finding stars, extra
  ### all done in cat directory
  ### writes to .cat, adds .cat0 _ksb.cat1 _ksb.cat2 _ksb_tmp.cat2 _tmp.cat1 _tmp1.cat1  and PSFcheck/ , copy/
  
  ./parallel_manager.sh ./check_science_PSF_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
  ./check_science_PSF_plot.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
  ./merge_sex_ksb.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}

  fi

  ### run astrometrix (if necessary)
  for af in ${ASTROM_FILTERS}
  do
    if [ ${filter} = ${af} ];then

        ### makes astrom/ and headers/
	./create_run_list_mult.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} INSTRUM CONFIG ROTATION uniqruns_$$.txt NOSPLIT
	RUNS=""
	NRUNS=0
	while read SUBRUN
	  do
	  RUNS="${RUNS} ${REDDIR}/${SUBRUN}.txt"
	  NRUNS=$(( ${NRUNS} + 1 ))
	done < ${TEMPDIR}/uniqruns_$$.txt    
	echo ${RUNS}

	./create_astrometrix_astrom_run.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ${ASTROM_ASTROMETRYCAT} ${RUNS}

        ### check whether the previous step worked
	nhead=`ls -1 ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/headers/*.head | wc | awk '{print $1}'`
	if [ ${nhead} -eq 0 ]; then
	    echo "No header files were created - something's wrong!"
	    exit 2;
	fi
    fi
  done

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


export BONN_FILTER=${SCAMP_FILTERS}

./BonnLogger.py clear
./BonnLogger.py config \
    cluster=${cluster} \
    filterlist="${SCAMP_FILTERS}" \
    astrommethod=${ASTROMMETHOD} \
    astrometrycat=${ASTROMETRYCAT} \

#./create_scamp_astrom_astrom_photom.sh ${LINE} ${ASTROMETRYCAT}


for filter in ${FILTERS}
do
  export BONN_FILTER=${filter}
  echo ${filter}

  ./setup_general.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE instrument_$$
  export INSTRUMENT=`cat instrument_$$`
  rm instrument_$$
  . ${INSTRUMENT:?}.ini


  echo ${NCHIPS}

  #Find Ending
  testfile=`ls -1 $SUBARUDIR/$cluster/${filter}/SCIENCE/*_2*.fits | awk 'NR>1{exit};1'`
  ending=`basename ${testfile} | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`

  ./BonnLogger.py clear
  ./BonnLogger.py config \
      cluster=${cluster} \
      filter=${filter} \
      config=${config} \
      ending=${ending}

  ### makes plots/
  ./create_stats_table.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} headers${ASTROMADD}
  ./create_absphotom_photometrix.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE
  ./make_checkplot_stats.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE chips.cat6 STATS ${cluster}
  
### makes .sub.fits files
#  ./parallel_manager.sh ./create_skysub_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ".sub" TWOPASS

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
  
  ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster} STATS coadd ${MAGZP} AB "(manual)"


### make PSF plots, and write star reference catalog
  ./check_psf_coadd.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster} coadd.fits ${NAXIS1} ${NAXIS2}

  ###################################
  ##CHECKPOINT
  ###################################
#  ./BonnLogger.py checkpoint Coadd

done


