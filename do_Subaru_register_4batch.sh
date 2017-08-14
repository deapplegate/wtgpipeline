#! /bin/bash -xv

### script to register image sets
###
### the astro-/photometry is via SCAMP 
###
### $Id: do_Subaru_register_4batch.sh,v 1.12 2010-10-05 02:29:02 anja Exp $

. progs.ini
. bash_functions.include

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU

cluster=$1  # cluster nickname as in /nfs/slac/g/ki/ki02/xoc/anja/SUBARU/SUBARU.list
catalog=$2  # catalog to be used for SCAMP
mode=photom     # "astrom" or "photom"

FILTERS=""
i=3
while [ "$i" -le "$#" ]
do
  FILTERS="${FILTERS} ${!i}"
  i=$(( $i + 1 ))
done

# Do astrometric calibration with SCAMP or ASTROMETRIX (no longer supported in this script) ?
ASTROMMETHOD=SCAMP

# only for Scamp (use SDSS-R6,  NOMAD-1, or 2MASS ) :
ASTROMETRYCAT=${catalog}

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

#########################################
### Capture Variables
./BonnLogger.py config \
    cluster=${cluster} \
    filterlist="${FILTERS}" \
    imagesize="${IMAGESIZE}" \
    astrommethod="${ASTROMMETHOD}" \
    astrometrycat="${ASTROMETRYCAT}" \
    astromadd="${ASTROMADD}"
    

##############################
### prep stuff, per filter ###
##############################


for filter in ${FILTERS}
do

  export BONN_FILTER=${filter}
  echo ${filter}
  ./BonnLogger.py clear

  ./setup_general.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE instrument_$$
  INSTRUMENT=`cat instrument_$$`
  rm instrument_$$

  if [ ${INSTRUMENT} == "UNKNOWN" ]; then
      echo "INSTRUMENT UNKNOWN: Defaulting to SUBARU"
      echo "Need to add INSTRUM key to ${SUBARUDIR}/${cluster}/${filter}/SCIENCE files if otherwise!"
      read -p 'Set INSTRUM to SUBARU [y/n]?' confirm
      if [ ${confirm} == 'y' ]; then
	  ./setup_SUBARU.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE
	  INSTRUMENT=SUBARU
	  ./update_config_header.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE ${INSTRUMENT}
      else
	  read -p 'Set INSTRUM to MEGAPRIME [y/n]?' confirm2
	  if [ ${confirm2} == 'y' ]; then
	      INSTRUMENT=MEGAPRIME
	      ./update_config_header_megaprime.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE ${INSTRUMENT}
	  else
	      echo "Need to add INSTRUM key to ${SUBARUDIR}/${cluster}/${filter}/SCIENCE files."
	      exit 2;
	  fi
      fi
  fi

  echo ${NCHIPS}

  echo ${INSTRUMENT}

  . ${INSTRUMENT:?}.ini
  export INSTRUMENT

  echo ${NCHIPS}

  ./BonnLogger.py clear
  ./BonnLogger.py config \
      cluster=${cluster} \
      filter=${filter} \
      config=${config}

  ##########################
  ### prepare coaddition ###
  ##########################

  case ${mode} in
      "astrom" )
#	  if [ -d ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scamp ]; then
#	      rm -rf ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scamp
#	  fi
	
	  if [ ! -d ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scamp ]; then
	  ###adds astrometric info; makes directory cat with ${image}_${chip}*.cat
	  ./parallel_manager.sh ./create_astromcats_scamp_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE WEIGHTS
	  fi
	  ;;
      "photom" )
	  case ${filter} in
	      "u" | "g" | "r" | "i" | "z" | "B" | "I" | "K" | "U-WHT" | "B-WHT" | "r_CALIB" )
		  if [ ! -d ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scampIC ]; then
		      mkdir ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scampIC
		      cd ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scampIC
		      ln -s ../cat_scamp/*.cat .
		      cd ${REDDIR}
		  fi
		  ;;
	      * )
		  if [ -d ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scampIC ]; then
		      rm -rf ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scampIC
		  fi

		  testfile=`dfits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/*_2*.fits | fitsort -d BADCCD | awk '{if($2!=1 && $1!~"sub.fits") print $0}' | awk '{if(NR==1) print $1}'`
		  echo ${testfile}
		  base=`basename ${testfile} .fits`
		  if [ -f $SUBARUDIR/$cluster/${filter}/SCIENCE/${base}I.fits ]; then
		      testfile=$SUBARUDIR/$cluster/${filter}/SCIENCE/${base}I.fits
		  fi
		  if [ -f $SUBARUDIR/$cluster/${filter}/SCIENCE/${base}RI.fits ]; then
		      testfile=$SUBARUDIR/$cluster/${filter}/SCIENCE/${base}RI.fits
		  fi
		  ending=`basename ${testfile} | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`

#		  ./parallel_manager.sh ./unfixbadccd_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE WEIGHTS ${ending}

		  if [ ! -d ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scampIC ]; then
		    if [ "${ending}" == "OCF" ] || [ "${ending}" == "OCFS" ]; then
		      mkdir ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scampIC
		      cd ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat_scampIC
		      ln -s ../cat_scamp/*.cat .
		      cd ${REDDIR}  
		    else
		      echo "./parallel_manager.sh ./create_astromcats_scampIC_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE WEIGHTS"
		      exit 0;
		    fi
		  fi
		  ;;
	  esac
	  ;;
      * )
	  echo "Specify astrom or photom mode."
	  exit 2
	  ;;
  esac

  ### prep for scamp:
  LINE="${LINE} ${SUBARUDIR}/${cluster}/${filter} SCIENCE "

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

    echo "This script supports only registration via scamp."
    echo "Use an older version for use with astrometrix."
    exit 2;
  
else
    
  export BONN_FILTER=${FILTERS}

  ./BonnLogger.py clear
  ./BonnLogger.py config \
      cluster=${cluster} \
      filterlist="${FILTERS}" \
      astrommethod=${ASTROMMETHOD} \
      astrometrycat=${ASTROMETRYCAT} \

  case ${mode} in
      "astrom" )
	  ./create_scamp_astrom_photom.sh ${LINE} ${ASTROMETRYCAT}
	  ;;
      "photom" )
	  ./create_scamp_photom.sh ${LINE} 23000 ${ASTROMETRYCAT}
	  ;;
      * )
	  echo "Specify astrom or photom mode."
	  exit 2
	  ;;
  esac

fi




