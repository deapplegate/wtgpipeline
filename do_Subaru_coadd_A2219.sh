#! /bin/bash -xv

### new coaddition script
###
### the astro-/photometry can be done via SCAMP (preferred) or
### ASTROMETRIX
###
### $Id: do_Subaru_coadd_A2219.sh,v 1.3 2009-06-03 23:50:53 dapple Exp $

. progs.ini
. bash_functions.include

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki05/anja/SUBARU

cluster="A2219"  # cluster nickname as in /nfs/slac/g/ki/ki02/xoc/anja/SUBARU/SUBARU.list

FILTERS="W-J-B W-J-V W-C-RC I"


NAXIS1=12000
NAXIS2=12000
IMAGESIZE="${NAXIS1},${NAXIS2}"

export PIXSCALE=0.202

# coadd _all_ images or those with _good_ shear?
coadd=all

# Do astrometric calibration with SCAMP or ASTROMETRIX ?
ASTROMMETHOD=SCAMP
#ASTROMMETHOD=ASTROMETRIX

# only for Scamp (use SDSS-R6 or 2MASS ) :
ASTROMETRYCAT=SDSS-R6

# for astrometrix (use SDSS5 or USNOB1):
#ASTROMETRYCAT=SDSS5

ASTROMADD=""
if [ ${ASTROMMETHOD} = "SCAMP" ]; then
   ASTROMADD="_scamp_${ASTROMETRYCAT}"
   
fi

###############################################
######################
#Some Setup Stuff

# coaddition constraints

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


##################################################
### after possible calibration across filters: ###
### need to work per filter again              ###
##################################################

for filter in ${FILTERS}
do
  export BONN_FILTER=${filter}
  echo ${filter}

  ./setup_general.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE instrument_$$
  export INSTRUMENT=`cat instrument_$$`
  rm instrument_$$
  . ${INSTRUMENT:?}.ini

  #Find Ending
  case ${filter} in
      "I" )
	  ending=mos
	  ;;
      * )
	  testfile=`ls -1 $SUBARUDIR/$cluster/${filter}/SCIENCE/*_2*.fits | awk 'NR>1{exit};1'`
	  ending=`basename ${testfile} | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`	  
	  ;;
  esac

  ./BonnLogger.py clear

  ./BonnLogger.py config \
      cluster=${cluster} \
      filter=${filter} \
      config=${config} \
      ending=${ending} \
      astrommethod=${ASTROMMETHOD} \
      astrometrycat=${ASTROMETRYCAT} \

#  ### makes plots/
#  ./create_stats_table_chips.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} headers${ASTROMADD}
#  ./create_absphotom_photometrix.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE
#  ./make_checkplot_stats.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE chips.cat6 STATS ${cluster}
#
#  ### makes .sub.fits files
##  ./parallel_manager.sh ./create_skysub_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ".sub" TWOPASS
#  echo ${IMAGESIZE}
#
#if [ ${coadd} == "all" ]; then
#  ./prepare_coadd_swarp.sh -m ${SUBARUDIR}/${cluster}/${filter} \
#                           -s SCIENCE \
#                           -e "${ending}.sub" \
#                           -n ${cluster}_${coadd} \
#                           -w ".sub" \
#                           -eh headers${ASTROMADD} \
#                           -r ${ra} \
#                           -d ${dec} \
#                           -i ${IMAGESIZE} \
#                           -p 0.202 \
#                           -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 STATS \
#                              "(SEEING<2.0);" \
#                              ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_${coadd}.cat
#
#  ./parallel_manager.sh ./resample_coadd_swarp_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd} ${REDDIR}
#
#elif [ ${coadd} == "good" ]; then
#  ./prepare_coadd_swarp_chips.sh -m ${SUBARUDIR}/${cluster}/${filter} \
#                           -s SCIENCE \
#                           -e "${ending}.sub" \
#                           -n ${cluster}_${coadd} \
#                           -w ".sub" \
#                           -eh headers${ASTROMADD} \
#                           -r ${ra} \
#                           -d ${dec} \
#                           -i ${IMAGESIZE} \
#			   -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat8 CHIPS_STATS \
#                              "(e_abs<0.1);" \
#                              ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_${coadd}.cat
#
#  ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd} ${REDDIR} ${cluster}_all
#
#else
#    echo "coadd goal ${coadd} not known!"
#    log_status 1 "coadd goal ${coadd} not known!"	
#    exit 2
#fi
#
#  
#  ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd}

  ### add header keywords
 
  value ${cluster}
  writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/coadd.fits OBJECT "${VALUE} / Target" REPLACE
  
  value ${filter}
  writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/coadd.fits FILTER "${VALUE} / Filter" REPLACE

if [ ${filter} == "I" ]; then
    MAGZERO=`dfits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/a2219I_1mos.sub.fits | fitsort -d MAGZERO | awk '{print $2}'`
  value ${MAGZERO}
  writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/coadd.fits MAGZERO "${VALUE} / effective photometric zero point" REPLACE

    MAGZERO1=`dfits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/a2219I_1mos.sub.fits | fitsort -d MAGZERO1 | awk '{print $2}'`
  value ${MAGZERO1}
  writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/coadd.fits MAGZERO1 "${VALUE} / photometric zero point for one second exposure" REPLACE

    EXTINC=`dfits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/a2219I_1mos.sub.fits | fitsort -d EXTINC | awk '{print $2}'`
  value ${EXTINC}
  writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/coadd.fits EXTINC "${VALUE} / extinction coefficient" REPLACE

    AIRMASS=`dfits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/a2219I_1mos.sub.fits | fitsort -d AIRMASS | awk '{print $2}'`
  value ${AIRMASS}
  writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/coadd.fits AIRMASS "${VALUE} / effective airmass of exposure" REPLACE
fi

  ### update photometry
  if [ -f ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips_phot.cat5 ]; then
      MAGZP=`${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips_phot.cat5 -t ABSPHOTOM -k COADDZP | tail -n 1`
  else
      MAGZP=-1.0
  fi
  
####  ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster} STATS coadd ${MAGZP} AB "(SEEING<2.0)"
### make PSF plots, and write star reference catalog
  ./check_psf_coadd.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd} coadd.fits ${NAXIS1} ${NAXIS2}

  ###################################
  ##CHECKPOINT
  ###################################
#  ./BonnLogger.py checkpoint Coadd

done
