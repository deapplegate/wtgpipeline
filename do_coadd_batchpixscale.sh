#! /bin/bash -xv

### new coaddition script
###
### the astro-/photometry can be done via SCAMP (preferred) or
### ASTROMETRIX
###
### $Id: do_coadd_batchpixscale.sh,v 1.2 2011/03/29 23:13:51 dapple Exp $

. progs.ini
. bash_functions.include

echo $PYTHONPATH

##################################

cluster=$1
filter=$2
# possible coaddition modes:
# - "all" : all images, needs to be run first!
# - "good" : only chips with not too elliptical PSF
# - "rotation" : split by rotation
# - "exposure" : one coadd per exposure
# - "3s" : coadds the SDSS 3s exposure
# - "pretty" : coadds the deep and 3s cluster exposure
# - "gabodsid"
requested_coadds=$3


## of the form: "good:((fjgj=gjg)AND(hghg=fjfjf)) all:(fjf=ssss)"
custom_conditions=$4   #optional, NEEDS TO BE A FILE!!!
use_ending=$5   #optional
keep_cats=$6    #optional  -> may be "yes"

###########################

if [ -n "${custom_conditions}" ]; then
    custom_conditions=`cat ${custom_conditions}`
fi

constructed_condition=
function constructConditions {
    coadd_type=$1
    standing_condition=$2   #always apply
    default_condition=$3    #apply if no custom conditions

    #look for custom conditions
    custom_condition=''
    for entry in ${custom_conditions}; do
	custom_condition=`echo ${entry} | awk -F':' '( $1 ~ /'${coadd_type}'/){print $2}'`
	if [ -n "${custom_condition}" ]; then
	    break
	fi
    done

    if [ -z "${custom_condition}" ]; then
	custom_condition=${default_condition}
    fi

    if [ -z "${standing_condition}" ] && [ -z "${custom_condition}" ]; then
	constructed_condition=""
	return
    fi
    
    if [ -n "${standing_condition}" ] && [ -z "${custom_condition}" ]; then
	constructed_condition="${standing_condition};"
	return
    fi

    if [ -z "${standing_condition}" ] && [ -n "${custom_condition}" ]; then
	constructed_condition="${custom_condition};"
	return
    fi

    constructed_condition="(${standing_condition}AND${custom_condition});"
    return
 
}

###########################

echo ${requested_coadds}

######################################

export BONN_LOG=1
export BONN_TARGET=${cluster}
export BONN_FILTER=${filter}

./BonnLogger.py clear

########################################

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki05/anja/SUBARU

##########################################


NAXIS1=12000
NAXIS2=12000
IMAGESIZE="${NAXIS1},${NAXIS2}"

export PIXSCALEOUT=0.15

################################

ASTROMMETHOD=SCAMP
ASTROMETRYCAT=`cat ${SUBARUDIR}/Scamp_cat.list | grep "${cluster}" | awk '{if(cl==$1) print $2}' cl=${cluster}`
if [ -z "$ASTROMETRYCAT" ]; then
    ./BonnLogger.py comment "Can't find astrometry cat"
    exit 1
fi
ASTROMADD="_scamp_photom_${ASTROMETRYCAT}"
   
#####################################

lookupfile=/nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
ra=`grep ${cluster} ${lookupfile} | awk '{if(cl==$1)print $3}' cl=${cluster}`
dec=`grep ${cluster} ${lookupfile} | awk '{if(cl==$1)print $4}' cl=${cluster}`

echo ${cluster} ${ra} ${dec}

#######################################


./setup_general.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE instrument_$$
export INSTRUMENT=`cat instrument_$$`
if [[ ( -z ${INSTRUMENT} ) || ( "${INSTRUMENT}" = "UNKNOWN" ) ]]; then
    echo "setup_general failed. Probably due to BonnLogger"
    exit 5
fi
rm instrument_$$
. ${INSTRUMENT:?}.ini

./BonnLogger.py config \
    cluster=${cluster} \
    filter=${filter} \
    config=${config} \
    ending=${ending} \
    astrommethod=${ASTROMMETHOD} \
    astrometrycat=${ASTROMETRYCAT} \

######################
#  #Find Ending
  case ${filter} in
      "I" )
	  ending=mos
	  ;;
      "u" | "g" | "r" | "i" | "z" | "r_CALIB" )
	  if [ -f ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/*_2*.fits ]; then
	    testfile=`dfits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/*_2*.fits | fitsort -d BADCCD | awk '{if($2!=1 && $1!~"sub.fits") print $0}' | awk '{if(NR==1) print $1}'`
          else
	    testfile=`dfits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/*_1*.fits | fitsort -d BADCCD | awk '{if($2!=1 && $1!~"sub.fits") print $0}' | awk '{if(NR==1) print $1}'`
          fi
	  ending=C
	  ;;
      "K" )
	  ending=K
	  ;;
      * )
	  testfilename=`dfits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/*_2*.fits | fitsort -d BADCCD | awk '{if($2!=1 && $1!~"sub.fits") print $0}' | awk '{if(NR==1) print $1}'`
	  testfile=${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${testfilename}
	  echo ${testfile}
	  base=`basename ${testfile} .fits`
	  if [ -f $SUBARUDIR/$cluster/${filter}/SCIENCE/${base}I.fits ]; then
	      testfile=$SUBARUDIR/$cluster/${filter}/SCIENCE/${base}I.fits
	  fi
	  if [ -f $SUBARUDIR/$cluster/${filter}/SCIENCE/${base}RI.fits ]; then
	      testfile=$SUBARUDIR/$cluster/${filter}/SCIENCE/${base}RI.fits
	  fi
	  ending=`basename ${testfile} | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`	  
	  ;;
  esac

lastchar=`echo $ending | awk '{print substr($1,length)}'`
if [ "$lastchar" = "I" ]; then

    origEnding=`echo $ending | awk '{print substr($1,1,length-1)}'`

    for f in `ls $SUBARUDIR/$cluster/$filter/WEIGHTS/*${origEnding}.flag.fits`; 
    do
	base=`basename $f ${origEnding}.flag.fits`
	ln -s $f $SUBARUDIR/$cluster/$filter/WEIGHTS/${base}${ending}.flag.fits
    done
fi

if [ -n "${use_ending}" ]; then
    ending=${use_ending}
fi

ZP=`dfits ${testfile} | fitsort -d ZP | awk '{print $2}'`

if [ "${ZP}" != "KEY_N/A" ] && [ "${INSTRUMENT}" == "MEGAPRIME" ]; then
	MAGZP=${ZP}
else
        MAGZP="-1.0"
fi

#####################

for coadd in ${requested_coadds}; do

if [ ${coadd} == "all" ] && [ ${filter} != "K" ] && [ ${filter} != "I" ]; then

  #####################

#  ./parallel_manager.sh ./fixbadccd_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE WEIGHTS ${ending}
  
  ./test_coadd_ready.sh ${SUBARUDIR}/${cluster} ${filter} ${ending} ${ASTROMETRYCAT} ${ASTROMADD}
  if [ $? -gt 0 ]; then
      echo "test_coadd_ready failed"
      exit 1
  fi

  
  ######################

#if [ -z "${keep_cats}" ] || [ "${keep_cats}" != "yes" ]; then
#
#  if [ -d ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat ]; then
#      rm -rf ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat
#  fi
#
#  rm -f /tmp/*
#
#  ./parallel_manager.sh ./create_astromcats_weights_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} WEIGHTS ${ending}.weight
#        
#  ./parallel_manager.sh ./check_science_PSF_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
#
#  #./check_science_PSF_plot.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
#  
#  ./merge_sex_ksb.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
#  
#  ./create_stats_table_chips.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} headers${ASTROMADD}
#  
#  ./create_absphotom_photometrix.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE
#  
#  ./check_science_PSF_plot.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}  
#  ./make_checkplot_stats.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE chips.cat6 STATS ${cluster}
#
#fi
  ./setup_general.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE instrument_$$ 
  rm instrument_$$
  #########################
  
#  case ${INSTRUMENT} in
#      "SUBARU" | "'SUBARU'" )
#  	./parallel_manager.sh ./create_skysub_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ".sub" THREEPASS
#  	#./create_skysub_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ".sub" THREEPASS 1 2 3 4 5 6 7 8 9 10
#	;;
#      * )
#  	./parallel_manager.sh ./create_skysub_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ".sub" TWOPASS
#  	;;
#  esac
#
  ##########################

  calib=`awk 'BEGIN{if("'${filter}'"~"CALIB") print "1"; else print "0"}'`
  
    if [ ${calib} -eq 0 ]; then
	constructConditions all "" "((((RA>(${ra}-0.5))AND(RA<(${ra}+0.5)))AND((DEC>(${dec}-0.5))AND(DEC<(${dec}+0.5))))AND(SEEING<1.9))"
    else
	constructConditions all "" "(((RA>(${ra}-0.5))AND(RA<(${ra}+0.5)))AND((DEC>(${dec}-0.5))AND(DEC<(${dec}+0.5))))"
    fi
	
 CONDITION=${constructed_condition}
 
  ./prepare_coadd_swarp.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                           -s SCIENCE \
                           -e "${ending}.sub" \
                           -n ${cluster}_${coadd}_${PIXSCALEOUT} \
                           -w ".sub" \
                           -eh headers${ASTROMADD} \
                           -r ${ra} \
                           -d ${dec} \
                           -i ${IMAGESIZE} \
                           -p ${PIXSCALEOUT} \
                           -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 STATS \
                              ${CONDITION} \
                              ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_${coadd}_${PIXSCALEOUT}.cat

  ./parallel_manager.sh ./apply_ringmask_para.sh ${SUBARUDIR} ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}_${PIXSCALEOUT} ${ending}.sub

  ./parallel_manager.sh ./resample_coadd_swarp_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd}_${PIXSCALEOUT} ${REDDIR}

  ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd}_${PIXSCALEOUT} MEDIAN

  ic -p 8 '16 1 %1 1e-6 < ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE//coadd_${cluster}_${coadd}_${PIXSCALEOUT}/coadd.weight.fits > ${SUBARUDIR}/${cluster}/${filter}/SCIENCE//coadd_${cluster}_${coadd}_${PIXSCALEOUT}/coadd.flag.fits

  ./setup_general.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE instrument_$$ 
  rm instrument_$$

  ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd}_${PIXSCALEOUT} STATS coadd ${MAGZP} AB ${CONDITION}

  coaddmodes="${coaddmodes} all_${PIXSCALEOUT}"

##############################

elif [ ${coadd} == "gabodsid" ]; then 

  GABODSIDS=`${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 -t STATS -b -k GABODSID | sort | uniq | awk '{printf "%i ", $0}'`

  for GABODSID in ${GABODSIDS}
  do
    constructConditions gabodsid "(GABODSID=${GABODSID})"  
    CONDITION=${constructed_condition}
  ./prepare_coadd_swarp.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                           -s SCIENCE \
                           -e "${ending}.sub" \
                           -n ${cluster}_gabodsid${GABODSID}_${PIXSCALEOUT} \
                           -w ".sub" \
                           -eh headers${ASTROMADD} \
                           -r ${ra} \
                           -d ${dec} \
                           -i ${IMAGESIZE} \
                           -p ${PIXSCALEOUT} \
                           -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 STATS \
                              ${CONDITION} \
                              ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_gabodsid${GABODSID}_${PIXSCALEOUT}.cat
  
    ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_gabodsid${GABODSID}_${PIXSCALEOUT} ${REDDIR} ${cluster}_all_${PIXSCALEOUT}

    ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_gabodsid${GABODSID}_${PIXSCALEOUT}
  
    ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_gabodsid${GABODSID}_${PIXSCALEOUT} STATS coadd ${MAGZP} AB ${CONDITION} 
    
    ./BonnLogger.py clear
    coaddmodes="${coaddmodes} gabodsid${GABODSID}_${PIXSCALEOUT}"

  done

##############################

elif [ ${coadd} == "good" ]; then
     constructConditions good "(IMAGEID!=6)" "((seeing_rh_al<0.8)AND(e_abs<0.08))"
    CONDITION=${constructed_condition}
    echo "${CONDITION}"

    nsub=`find ${SUBARUDIR}/${cluster}/${filter}/SCIENCE -maxdepth 1 -name "*.sub.fits" | wc -l`
    if [ ${nsub} -eq 0 ]; then
      case ${INSTRUMENT} in
       "SUBARU" | "'SUBARU'" )
  	 ./parallel_manager.sh ./create_skysub_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ".sub" THREEPASS
  	 ;;
       * )
  	 ./parallel_manager.sh ./create_skysub_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ".sub" TWOPASS
  	 ;;
      esac
    fi

  ./prepare_coadd_swarp_chips.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                           -s SCIENCE \
                           -e "${ending}.sub" \
                           -n ${cluster}_${coadd}_${PIXSCALEOUT} \
                           -w ".sub" \
                           -eh headers${ASTROMADD} \
                           -r ${ra} \
                           -d ${dec} \
                           -i ${IMAGESIZE} \
                           -p ${PIXSCALEOUT} \
			   -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat8 CHIPS_STATS \
                              ${CONDITION} \
                              ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_${coadd}.cat

  ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd}_${PIXSCALEOUT} ${REDDIR} ${cluster}_all_${PIXSCALEOUT}

  ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd}_${PIXSCALEOUT}

  ic -p 8 '16 1 %1 1e-6 < ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE//coadd_${cluster}_${coadd}_${PIXSCALEOUT}/coadd.weight.fits > ${SUBARUDIR}/${cluster}/${filter}/SCIENCE//coadd_${cluster}_${coadd}_${PIXSCALEOUT}/coadd.flag.fits

  ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd}_${PIXSCALEOUT} CHIPS_STATS coadd ${MAGZP} AB ${CONDITION}

  coaddmodes="${coaddmodes} good_${PIXSCALEOUT}"

##############################
### new rotation coadd: split by both night and rotation

elif [ ${coadd} == "rotation" ]; then 

  ROTATIONS=`${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 -t STATS -b -k ROTATION | sort | uniq | awk '{printf "%i ", $0}'`

  ${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 -t STATS -b -k GABODSID ROTATION | sort | uniq > gabrot_$$.dat

  while read GABODSID ROTATION
  do
    constructConditions rotation "(((IMAGEID!=6)AND(GABODSID=${GABODSID}))AND(ROTATION=${ROTATION}))" ""
    CONDITION=${constructed_condition}
    echo ${CONDITION}

  ./prepare_coadd_swarp_chips.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                           -s SCIENCE \
                           -e "${ending}.sub" \
                           -n ${cluster}_gab${GABODSID}-rot${ROTATION}_${PIXSCALEOUT} \
                           -w ".sub" \
                           -eh headers${ASTROMADD} \
                           -r ${ra} \
                           -d ${dec} \
                           -i ${IMAGESIZE} \
                           -p ${PIXSCALEOUT} \
                           -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat8 CHIPS_STATS \
                              ${CONDITION} \
                              ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_gab${GABODSID}-rot${ROTATION}_${PIXSCALEOUT}.cat

    ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_gab${GABODSID}-rot${ROTATION}_${PIXSCALEOUT} ${REDDIR} ${cluster}_all_${PIXSCALEOUT}

    ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_gab${GABODSID}-rot${ROTATION}_${PIXSCALEOUT}

    ic -p 8 '16 1 %1 1e-6 < ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE//coadd_${cluster}_gab${GABODSID}-rot${ROTATION}/coadd.weight.fits > ${SUBARUDIR}/${cluster}/${filter}/SCIENCE//coadd_${cluster}_gab${GABODSID}-rot${ROTATION}/coadd.flag.fits
  
    ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_gab${GABODSID}-rot${ROTATION}_${PIXSCALEOUT} CHIPS_STATS coadd ${MAGZP} AB ${CONDITION} 

    coaddmodes="${coaddmodes} gab${GABODSID}-rot${ROTATION}_${PIXSCALEOUT}"

  done < gabrot_$$.dat

###################################


###################################

elif [ ${coadd} == "exposure" ] && [ ${filter} != "K" ] && [ ${filter} != "I" ]; then 

  calib=`awk 'BEGIN{if("'${filter}'"~"CALIB") print "1"; else print "0"}'`

  if [ ${calib} -eq 0 ]; then
  ${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 -t STATS -s -b -k EXPOSURE IMAGENAME > exposures_$$.list

    while read EXPOSURE IMAGENAME 
    do
      constructConditions exposure "(EXPOSURE=${EXPOSURE})" ""
      CONDITION=${constructed_condition}

    ./prepare_coadd_swarp.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                             -s SCIENCE \
                             -e "${ending}.sub" \
                             -n ${cluster}_${IMAGENAME}_${PIXSCALEOUT} \
                             -w ".sub" \
                             -eh headers${ASTROMADD} \
                             -r ${ra} \
                             -d ${dec} \
                             -i ${IMAGESIZE} \
                             -p ${PIXSCALEOUT} \
                             -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 STATS \
                                ${CONDITION} \
                                ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_${IMAGENAME}_${PIXSCALEOUT}.cat
  
      ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${IMAGENAME_${PIXSCALEOUT}} ${REDDIR} ${cluster}_all_${PIXSCALEOUT}
  
      ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${IMAGENAME}_${PIXSCALEOUT}

      
      ic -p 8 '16 %1 %2 1e-6 < ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE//coadd_${cluster}_${IMAGENAME}_${PIXSCALEOUT}/coadd.flag.fits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE//coadd_${cluster}_${IMAGENAME}_${PIXSCALEOUT}/coadd.weight.fits | ic -p 8 '16 %1 %1 0 == ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE//coadd_${cluster}_${IMAGENAME}_${PIXSCALEOUT}/coadd.flag.fits > ${SUBARUDIR}/${cluster}/${filter}/SCIENCE//coadd_${cluster}_${IMAGENAME}_${PIXSCALEOUT}/coadd.flag.temp.fits
      mv ${SUBARUDIR}/${cluster}/${filter}/SCIENCE//coadd_${cluster}_${IMAGENAME}_${PIXSCALEOUT}/coadd.flag.temp.fits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE//coadd_${cluster}_${IMAGENAME}_${PIXSCALEOUT}/coadd.flag.fits


      ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${IMAGENAME}_${PIXSCALEOUT} STATS coadd ${MAGZP} AB ${CONDITION}
    
      coaddmodes="${coaddmodes} ${IMAGENAME}_${PIXSCALEOUT}"
  
    done < exposures_$$.list
    rm exposures_$$.list
  fi


###################################

elif [ ${coadd} == "3s" ]; then 

  calib=`awk 'BEGIN{if("'${filter}'"~"CALIB") print "1"; else print "0"}'`

  if [ ${calib} -eq 1 ]; then
      ./prepare_coadd_swarp_3s.sh -m ${SUBARUDIR}/${cluster}/${filter} \
	                          -s SCIENCE \
                                  -e "${ending}.sub" \
                                  -n ${cluster}_${coadd} \
                                  -w ".sub" \
                                  -eh headers${ASTROMADD} \
                                  -r ${ra} \
                                  -d ${dec} \
                                  -i ${IMAGESIZE} \
                                  -p ${PIXSCALEOUT}

      ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd} ${REDDIR} ${cluster}_all

      ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd}

      ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd} STATS coadd ${MAGZP} AB ${CONDITION}
              
      coaddmodes="${coaddmodes} 3s"
  fi


###################################

elif [ ${coadd} == "pretty" ]; then 

  lastchar=`echo ${ending} | awk '{print substr($1,length)}'`
  if [ "$lastchar" = "R" ]; then
      ending=`echo $ending | awk '{print substr($1,1,length-1)}'`
  fi

  if [ ! -f ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/*_2${ending}.sub.fits ]; then
    ./parallel_manager.sh ./create_skysub_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ".sub" THREEPASS
  fi

  CONDITION="(((((RA>(${ra}-0.5))AND(RA<(${ra}+0.5)))AND(DEC>(${dec}-0.5)))AND(DEC<(${dec}+0.5)))AND(SEEING<1.9));"
  ./prepare_coadd_swarp_pretty.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                           -s SCIENCE \
                           -e "${ending}.sub" \
                           -n ${cluster}_${coadd} \
                           -w ".sub" \
                           -eh headers${ASTROMADD} \
                           -r ${ra} \
                           -d ${dec} \
                           -i ${IMAGESIZE} \
                           -p ${PIXSCALEOUT} \
                           -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 STATS \
                              ${CONDITION} \
                              ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_${coadd}.cat

  ./parallel_manager.sh ./resample_coadd_swarp_pretty_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd} ${REDDIR}

  ./perform_coadd_swarp_pretty.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd} MEDIAN
#
#  ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd} STATS coadd ${MAGZP} AB ${CONDITION}

###################################

elif [ ${coadd} == "all" ] && [ ${filter} == "K" ] || [ ${filter} == "I" ]; then

    if [ -d ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all ]; then
	rm -rf ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all
    fi
    mkdir ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all

    cd ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all
  imagebase=`basename ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/*_1${ending}.fits ${ending}.fits`    
    cp ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/headers${ASTROMADD}/${imagebase}.head \
        ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${imagebase}${ending}.head

    swarp ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${imagebase}${ending}.fits \
	-WEIGHT_IMAGE \
	${SUBARUDIR}/${cluster}/${filter}/WEIGHTS/${imagebase}${ending}.weight.fits \
	-WEIGHT_TYPE MAP_WEIGHT \
	-IMAGE_SIZE ${IMAGESIZE} -CENTER_TYPE MANUAL -CENTER ${ra},${dec} -PIXELSCALE_TYPE MANUAL -PIXEL_SCALE ${PIXSCALEOUT} \
	-IMAGEOUT_NAME ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits

    fthedit coadd.fits DUMMY10 add 0
    fthedit coadd.fits DUMMY11 add 0
    fthedit coadd.fits DUMMY12 add 0
    fthedit coadd.fits DUMMY13 add 0
    fthedit coadd.fits DUMMY14 add 0
    fthedit coadd.fits DUMMY15 add 0
    fthedit coadd.fits DUMMY16 add 0
    fthedit coadd.fits DUMMY17 add 0
    fthedit coadd.fits DUMMY18 add 0
    fthedit coadd.fits DUMMY19 add 0

   ${P_IC} -p 8 '16 1 %1 0 == ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.weight.fits > ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.flag.fits

    fthedit coadd.fits DUMMY0 add 0
    fthedit coadd.fits DUMMY1 add 0
    fthedit coadd.fits DUMMY2 add 0
    fthedit coadd.fits DUMMY3 add 0
    fthedit coadd.fits DUMMY4 add 0
    fthedit coadd.fits DUMMY5 add 0
    fthedit coadd.fits DUMMY6 add 0
    fthedit coadd.fits DUMMY7 add 0
    fthedit coadd.fits DUMMY8 add 0
    fthedit coadd.fits DUMMY9 add 0

   MAGZERO1=`dfits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${imagebase}${ending}.fits | fitsort -d MAGZERO1 | awk '{print $2}'`
   MAG_ZERO=`dfits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${imagebase}${ending}.fits | fitsort -d MAG_ZERO | awk '{print $2}'`
   EXPTIME=`dfits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${imagebase}${ending}.fits | fitsort -d EXPTIME | awk '{print $2}'`
    
    if [ "${MAGZERO1}" != "KEY_N/A" ]; then
	MAGZP=${MAGZERO1}
    elif [ ${filter} == "K" ] && [ "${MAG_ZERO}" != "KEY_N/A" ]; then
	MAGZP=`awk 'BEGIN{print '${MAG_ZERO}'-2.5*log('${EXPTIME}')/log(10)+1.85}'`  # vega to AB
    else
	MAGZP="-1.0"
    fi

    cd ${REDDIR}

  ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd} STATS coadd ${MAGZP} AB ${CONDITION}

  value ${EXPTIME}
  writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/coadd.fits EXPTIME "${VALUE} / exposure time" REPLACE

  if [ ${filter} == "I" ]; then
       GAIN=2.1
  elif [ ${filter} == "K" ]; then
       GAIN=3.8
  fi

  GAINEFF=`awk 'BEGIN{print '${GAIN}'*'${EXPTIME}'}'`
  value ${GAINEFF}
  writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/coadd.fits GAIN "${VALUE} / effective gain" REPLACE     

  coaddmodes="${coaddmodes} all"

else
    
    constructConditions ${coadd} "(SEEING<1.9)" ""
    CONDITION=${constructed_condition}

    ./prepare_coadd_swarp_chips.sh -m ${SUBARUDIR}/${cluster}/${filter} \
        -s SCIENCE \
        -e "${ending}.sub" \
        -n ${cluster}_${coadd} \
        -w ".sub" \
        -eh headers${ASTROMADD} \
        -r ${ra} \
        -d ${dec} \
        -i ${IMAGESIZE} \
        -p ${PIXSCALEOUT} \
	-l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat8 CHIPS_STATS \
        ${CONDITION} \
        ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_${coadd}.cat
    
    
    ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd} ${REDDIR} ${cluster}_all
    
    ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd}
    
    ic -p 8 '16 1 %1 1e-6 < ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE//coadd_${cluster}_${coadd}/coadd.weight.fits > ${SUBARUDIR}/${cluster}/${filter}/SCIENCE//coadd_${cluster}_${coadd}/coadd.flag.fits
    
    ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd} CHIPS_STATS coadd ${MAGZP} AB ${CONDITION}
    
    coaddmodes="${coaddmodes} ${coadd}"

fi

done


for coaddmode in ${coaddmodes}
do
  echo ${coaddmode}

  ### add header keywords
 
  value ${cluster}
  writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coaddmode}/coadd.fits OBJECT "${VALUE} / Target" REPLACE
  
  value ${filter}
  writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coaddmode}/coadd.fits FILTER "${VALUE} / Filter" REPLACE

  ### update photometry
  if [ -f ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips_phot.cat5 ]; then
      MAGZP=`${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips_phot.cat5 -t ABSPHOTOM -k COADDZP | tail -n 1`
      value ${MAGZP}
      writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coaddmode}/coadd.fits MAGZP "${VALUE} / Magnitude zeropoint" REPLACE
  else
      MAGZP=-1.0
  fi

### make PSF plots, and write star reference catalog
  ./check_psf_coadd.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coaddmode} coadd.fits

#  if [ ${filter} == "K" ]; then
#      ./fit_phot_K.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coaddmode} coadd.fits
#  fi

done
