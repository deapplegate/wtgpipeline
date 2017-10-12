#! /bin/bash -xv

### new coaddition script
###
### the astro-/photometry can be done via SCAMP (preferred) or
### ASTROMETRIX
###
### $Id: do_Subaru_coadd_template.sh,v 1.29 2009-07-17 02:54:49 anja Exp $

. progs.ini
. bash_functions.include

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU

cluster="MACS1931-26"  # cluster nickname as in /nfs/slac/g/ki/ki02/xoc/anja/SUBARU/SUBARU.list

FILTERS="W-J-B W-J-B_2007-07-18_CALIB W-J-V W-J-V_2007-07-18_CALIB W-C-RC W-C-RC_2007-07-18_CALIB W-C-IC W-C-IC_2007-07-18_CALIB W-S-Z+ W-S-Z+_2007-07-18_CALIB"
FILTERS="W-C-IC_2007-07-18_CALIB"

NAXIS1=10000
NAXIS2=10000
IMAGESIZE="${NAXIS1},${NAXIS2}"

export PIXSCALE=0.2

# possible coaddition modes:
# - "all" : all images, needs to be run first!
# - "good" : only chips with not too elliptical PSF
# - "rotation" : split by rotation
# - "exposure" : one coadd per exposure
coadd=all

# Do astrometric calibration with SCAMP or ASTROMETRIX ?
ASTROMMETHOD=SCAMP
#ASTROMMETHOD=ASTROMETRIX

# only for Scamp (use SDSS-R6 or NOMAD-1 ) :
ASTROMETRYCAT=2MASS

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
#adam-BL#./BonnLogger.py clear


##################################################
### after possible calibration across filters: ###
### need to work per filter again              ###
##################################################

for filter in ${FILTERS}
do
  export BONN_FILTER=${filter}
  echo ${filter}

  #adam-BL#./BonnLogger.py clear

  ./setup_general.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE instrument_$$
  export INSTRUMENT=`cat instrument_$$`
  rm -f instrument_$$
  . ${INSTRUMENT:?}.ini

  #Find Ending
  case ${filter} in
      "I" )
	  ending=mos
	  ;;
      "u" | "g" | "r" | "i" | "z" )
	  ending=C
	  ;;
      * )
	  testfile=`ls -1 $SUBARUDIR/$cluster/${filter}/SCIENCE/*_2*.fits | awk 'NR>1{exit};1'`
	  base=`basename ${testfile} .fits`
#	  if [ -f $SUBARUDIR/$cluster/${filter}/SCIENCE/${base}I.fits ]; then
#	      testfile=$SUBARUDIR/$cluster/${filter}/SCIENCE/${base}I.fits
#	  fi
	  ending=`basename ${testfile} | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`	  
	  ;;
  esac

  #adam-BL#./BonnLogger.py clear

  #adam-BL#./BonnLogger.py config \
  #adam-BL#    cluster=${cluster} \
  #adam-BL#    filter=${filter} \
  #adam-BL#    config=${config} \
  #adam-BL#    ending=${ending} \
  #adam-BL#    astrommethod=${ASTROMMETHOD} \
  #adam-BL#    astrometrycat=${ASTROMETRYCAT} \

  if [ -d  ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat ] && [ ! -d  ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scamp ];then
      echo "Move ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat to ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scamp ? [y/n]"
      read move
      case ${move} in
	  "y" | "Y" | "yes" | "Yes" )
	      mv ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scamp
	      ;;
	  "n" | "N" | "no" | "No" )
	      echo "";;
	  * )
	      echo "Please answer yes or no. The assumption here is that"
              echo "the previous catalogs were generated only for scamp, "
              echo "and that we need to make new ones."
	      echo "Exiting script."
	      exit 2;
      esac
  fi

lastchar=`echo $ending | awk '{print substr($1,length)}'`
if [ "$lastchar" = "I" ]; then

    origEnding=`echo $ending | awk '{print substr($1,1,length-1)}'`

    for f in `ls $SUBARUDIR/$cluster/$filter/WEIGHTS/*${origEnding}.flag.fits`; 
    do
	base=`basename $f ${origEnding}.flag.fits`
	ln -s $f $SUBARUDIR/$cluster/$filter/WEIGHTS/${base}${ending}.flag.fits
    done
fi

#####################

coaddmodes=""

if [ ${coadd} == "all" ]; then

  ./parallel_manager.sh ./fixbadccd_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE WEIGHTS ${ending}

  ./test_coadd_ready.sh ${SUBARUDIR}/${cluster} ${filter} ${ending} ${ASTROMETRYCAT}

######################
  
  if [ -d ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat ];then
      rm -rf ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat
  fi

  if [ ! -d ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat ];then

  ###adds astrometric info; makes directory cat with ${image}_${chip}${ending}.cat
      ./parallel_manager.sh ./create_astromcats_weights_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} WEIGHTS ${ending}.weight

  ### check PSF in individual exposures
  ### via running SE, finding stars, extra
  ### all done in cat directory
  ### writes to .cat, adds .cat0 _ksb.cat1 _ksb.cat2 _ksb_tmp.cat2 _tmp.cat1 _tmp1.cat1  and PSFcheck/ , copy/
  
  ./parallel_manager.sh ./check_science_PSF_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
#  ./check_science_PSF_plot.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
  ./merge_sex_ksb.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}

  fi

  ### makes plots/
  ./create_stats_table_chips.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} headers${ASTROMADD}

  ./create_absphotom_photometrix.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE

  ### makes plots/
  ./check_science_PSF_plot.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}  
  ./make_checkplot_stats.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE chips.cat6 STATS ${cluster}

  ### makes .sub.fits files
  ./parallel_manager.sh ./create_skysub_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ".sub" THREEPASS
  echo ${IMAGESIZE}



###########################

    CONDITION="(SEEING<2.0);"

  ./prepare_coadd_swarp.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                           -s SCIENCE \
                           -e "${ending}.sub" \
                           -n ${cluster}_${coadd} \
                           -w ".sub" \
                           -eh headers${ASTROMADD} \
                           -r ${ra} \
                           -d ${dec} \
                           -i ${IMAGESIZE} \
                           -p ${PIXSCALE} \
                           -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 STATS \
                              ${CONDITION} \
                              ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_${coadd}.cat

  ./parallel_manager.sh ./apply_ringmask_para.sh ${SUBARUDIR} ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd} ${ending}.sub

  ./parallel_manager.sh ./resample_coadd_swarp_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd} ${REDDIR}

  coaddmodes="all"

##############################

elif [ ${coadd} == "good" ]; then
    CONDITION="((e_abs<0.1)AND(SEEING<1.5));"
  ./prepare_coadd_swarp_chips.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                           -s SCIENCE \
                           -e "${ending}.sub" \
                           -n ${cluster}_${coadd} \
                           -w ".sub" \
                           -eh headers${ASTROMADD} \
                           -r ${ra} \
                           -d ${dec} \
                           -i ${IMAGESIZE} \
                           -p ${PIXSCALE} \
			   -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat8 CHIPS_STATS \
                              ${CONDITION} \
                              ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_${coadd}.cat


  ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd} ${REDDIR} ${cluster}_all

  coaddmodes="good"

##############################

elif [ ${coadd} == "rotation" ]; then 

  ROTATIONS=`${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 -t STATS -b -k ROTATION | sort | uniq | awk '{printf "%i ", $0}'`

  for ROTATION in ${ROTATIONS}
  do
    CONDITION="(ROTATION=${ROTATION});"
  ./prepare_coadd_swarp.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                           -s SCIENCE \
                           -e "${ending}.sub" \
                           -n ${cluster}_rot${ROTATION} \
                           -w ".sub" \
                           -eh headers${ASTROMADD} \
                           -r ${ra} \
                           -d ${dec} \
                           -i ${IMAGESIZE} \
                           -p ${PIXSCALE} \
                           -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 STATS \
                              ${CONDITION} \
                              ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_rot${ROTATION}.cat
  
    ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_rot${ROTATION} ${REDDIR} ${cluster}_all
  
    coaddmodes="${coaddmodes} rot${ROTATION}"

  done

###################################

elif [ ${coadd} == "exposure" ]; then 

  ${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 -t STATS -s -b -k EXPOSURE IMAGENAME > exposures_$$.list

  while read EXPOSURE IMAGENAME 
  do
    CONDITION="(EXPOSURE=${EXPOSURE});"
    ./prepare_coadd_swarp.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                           -s SCIENCE \
                           -e "${ending}.sub" \
                           -n ${cluster}_${IMAGENAME} \
                           -w ".sub" \
                           -eh headers${ASTROMADD} \
                           -r ${ra} \
                           -d ${dec} \
                           -i ${IMAGESIZE} \
                           -p ${PIXSCALE} \
                           -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 STATS \
                              ${CONDITION} \
                              ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_${IMAGENAME}.cat
  
    ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${IMAGENAME} ${REDDIR} ${cluster}_all
  
    coaddmodes="${coaddmodes} ${IMAGENAME}"

  done < exposures_$$.list
  rm -f exposures_$$.list

###################################

elif [ ${coadd} == "3s" ]; then 

    ./prepare_coadd_swarp_3s.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                           -s SCIENCE \
                           -e "${ending}.sub" \
                           -n ${cluster}_${coadd} \
                           -w ".sub" \
                           -eh headers${ASTROMADD} \
                           -r ${ra} \
                           -d ${dec} \
                           -i ${IMAGESIZE} \
                           -p ${PIXSCALE}

    ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd} ${REDDIR} ${cluster}_all
  
    coaddmodes="${coaddmodes} 3s"


###################################

elif [ ${coadd} == "pretty" ]; then 

  case ${filter} in
      "W-J-B" | "W-J-V" | "W-C-RC" | "W-C-IC" | "W-S-I+" | "W-S-Z+" | "W-J-U" )
	  if ls ${SUBARUDIR}/${cluster}/${filter}_????-??-??_CALIB ; then
	      ./prepare_coadd_swarp_pretty.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                           -s SCIENCE \
                           -e "${ending}.sub" \
                           -n ${cluster}_${coadd} \
                           -w ".sub" \
                           -eh headers${ASTROMADD} \
                           -r ${ra} \
                           -d ${dec} \
                           -i ${IMAGESIZE} \
                           -p ${PIXSCALE}

		./parallel_manager.sh ./resample_coadd_swarp_pretty_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd} ${REDDIR} ${cluster}_all

		coaddmodes="${coaddmodes} pretty"
	  fi
	  ;;
  esac

###################################

else
    echo "adam-look | error: coadd goal ${coadd} not known!"
    #adam-BL# log_status 1 "coadd goal ${coadd} not known!"	
    exit 2
fi

echo ${coaddmodes}

for coaddmode in ${coaddmodes}
do
  echo ${coaddmode}
  ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coaddmode}

  ### add header keywords
 
  value ${cluster}
  writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coaddmode}/coadd.fits OBJECT "${VALUE} / Target" REPLACE
  
  value ${filter}
  writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coaddmode}/coadd.fits FILTER "${VALUE} / Filter" REPLACE

  ### update photometry
  if [ -f ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips_phot.cat5 ]; then
      MAGZP=`${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips_phot.cat5 -t ABSPHOTOM -k COADDZP | tail -n 1`
  else
      MAGZP=-1.0
  fi
  
  ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coaddmode} STATS coadd ${MAGZP} AB ${CONDITION}

### make PSF plots, and write star reference catalog
  ./check_psf_coadd.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coaddmode} coadd.fits ${NAXIS1} ${NAXIS2}

done

  ###################################
  ##CHECKPOINT
  ###################################
##adam-BL#  ./BonnLogger.py checkpoint Coadd

done

exit 0;
###############
# Create Smoothed Images

if [ "${coadd}" = "all" ]; then
    ./create_smoothed_coadd.sh ${SUBARUDIR}/${cluster} "${FILTERS}" SCIENCE ${cluster}_${coadd} coadd.fits
fi
