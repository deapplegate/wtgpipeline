#!/bin/bash
set -xv
#adam-example# ./do_coadd_batch.sh MACS1115+01 W-J-B 'all exposure ' 'none' OCFI 2>&1 | tee -a OUT-coadd_W-J-B.log2
#adam-example# ./do_coadd_batch.sh ${cluster} ${filter} 'good ' 'none' 'OCFR' 'yes' 'yes' 2>&1 | tee -a OUT-coadd_${cluster}.${filter}.log

### new coaddition script
###
### the astro-/photometry can be done via SCAMP (preferred) or
### ASTROMETRIX
###
### $Id: do_coadd_batch.sh,v 1.26 2011-03-29 22:50:58 anja Exp $

#adam: you have to deactivate the astroconda environment for some reason
source deactivate astroconda


. progs.ini > /tmp/prog.out 2>&1
. bash_functions.include > /tmp/bash_functions.include.out 2>&1

##################################

export cluster=$1
export filter=$2
# possible coaddition modes:
# - "all" : all images, needs to be run first!
# - "good" : only chips with not too elliptical PSF
# - "exposure" : one coadd per exposure
# - "3s" : coadds the SDSS 3s exposure
# - "gabodsid" : split by gabodsid
# - "rotation" : split by rotation and gabodsid
# - "pretty" : coadds the deep and 3s cluster exposure
requested_coadds=$3


## of the form: "good:((fjgj=gjg)AND(hghg=fjfjf)) all:(fjf=ssss)"
custom_conditions=$4   #optional, NEEDS TO BE A FILE!!!
use_ending=$5   #optional
keep_cats=$6    #optional  -> may be "yes"
keep_subs=$7    #optional  -> may be "yes"

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


######################################

export BONN_LOG=1
export BONN_TARGET=${cluster}
export BONN_FILTER=${filter}
#./BonnLogger.py clear

########################################

REDDIR=`pwd`
HEADDIR="/nfs/slac/g/ki/ki18/anja/SUBARU/coadd_headers/"
export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU

##########################################

NAXIS1=10000
NAXIS2=10000
IMAGESIZE="${NAXIS1},${NAXIS2}"
export PIXSCALEOUT=0.2

################################

ASTROMMETHOD=SCAMP
ASTROMETRYCAT=`cat ${SUBARUDIR}/Scamp_cat.list | grep "${cluster}" | awk '{if(cl==$1) print $2}' cl=${cluster}`
if [ -z "$ASTROMETRYCAT" ]; then
    #./BonnLogger.py comment "Can't find astrometry cat"
    exit 1
fi
#adam-tried# ASTROMADD="_scamp_${ASTROMETRYCAT}"
ASTROMADD="_scamp_photom_${ASTROMETRYCAT}"

#####################################

echo ${requested_coadds}
lookupfile=/nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
ra=`grep ${cluster} ${lookupfile} | awk '{if(cl==$1)print $3}' cl=${cluster}`
dec=`grep ${cluster} ${lookupfile} | awk '{if(cl==$1)print $4}' cl=${cluster}`
echo ${cluster} ${ra} ${dec}

#######################################

./setup_general.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE instrument_$$
export INSTRUMENT=`cat instrument_$$`
if [[ ( -z ${INSTRUMENT} ) || ( "${INSTRUMENT}" = "UNKNOWN" ) ]]; then
    #adam# echo "setup_general failed. Probably due to BonnLogger"
    #adam# SET DEFAULT INSTRUMENT=SUBARU
    exit 5

fi
rm -f instrument_$$
. ${INSTRUMENT:?}.ini > /tmp/subaru.out 2>&1

if [ "${INSTRUMENT}" == "SUBARU" ]; then
  #old SUBARU.ini# CONFIG=`grep 'config=' ${INSTRUMENT}.ini | sed 's/config=//g'`
  CONFIG=`grep 'config=' ${INSTRUMENT}.ini | sed 's/export\ config=//g'`
  echo "CONFIG=" $CONFIG
fi

########./BonnLogger.py config \
########    cluster=${cluster} \
########    filter=${filter} \
########    config=${config} \
########    ending=${ending} \
########    astrommethod=${ASTROMMETHOD} \
########    astrometrycat=${ASTROMETRYCAT} \

######################
#   Find Ending
######################
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

for coadd in ${requested_coadds}
do
        if [ ${coadd} == "all" ] && [ ${filter} != "K" ] && [ ${filter} != "I" ]; then
          #####################
          ./parallel_manager.sh ./fixbadccd_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE WEIGHTS ${ending}
          ./test_coadd_ready.sh ${SUBARUDIR}/${cluster} ${filter} ${ending} ${ASTROMETRYCAT} ${ASTROMADD}
          if [ $? -gt 0 ]; then
              echo "adam-Error: test_coadd_ready failed"
              exit 1
          fi
          ######################
          echo "keep_cats=" $keep_cats
          if [ -z "${keep_cats}" ] || [ "${keep_cats}" != "yes" ]; then #if keep_cats is unset or not "yes"
            if [ -d "${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat" ]; then
                rm -rf ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat
            fi
            #rm -rf /tmp/*
            ./parallel_manager.sh ./create_astromcats_weights_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} WEIGHTS ${ending}.weight
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            ./parallel_manager.sh ./check_science_PSF_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            #./check_science_PSF_plot.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
            ./merge_sex_ksb.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            ./create_stats_table_chips.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} headers${ASTROMADD}
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            #adam-note# this file `create_absphotom_photometrix.sh` makes the file chips_phot.cat5 that you don't actually need (it's from an old way of doing the photometry)
            #adam-look# so don't worry about errors from chips_phot.cat5 or from "*Error*: found no such key: ZPCHOICE"
            ./create_absphotom_photometrix.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE
            ./check_science_PSF_plot.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            ./make_checkplot_stats.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE chips.cat6 STATS ${cluster}
	    if [ "$?" -gt "0" ]; then exit $? ; fi
          fi
          rm -f instrument_$$
          #########################
          echo "keep_subs=" $keep_subs
          if [ -z "${keep_subs}" ] || [ "${keep_subs}" != "yes" ]; then
		  case ${INSTRUMENT} in
		      "SUBARU" | "'SUBARU'" )
			./parallel_manager.sh ./create_skysub_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ".sub" THREEPASS
			if [ "$?" -gt "0" ]; then exit $? ; fi
			;;
		      * )
			./parallel_manager.sh ./create_skysub_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ".sub" TWOPASS
			if [ "$?" -gt "0" ]; then exit $? ; fi
			;;
		  esac
	  fi
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
	  #adam-look# don't worry about errors saying '(standard_in) 1: syntax error' as long as there is only one (maybe a problem if you see this for every exposure coadd)
	  #adam-look# don't worry about errors saying 'cp: cannot create regular file `./coadd.head': File exists' and 'cp: cannot create regular file `coadd.flag.head': File exists'
	  if [ "$?" -gt "0" ]; then exit $? ; fi
          ./parallel_manager.sh ./apply_ringmask_para.sh ${SUBARUDIR} ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd} ${ending}.sub
	  if [ "$?" -gt "0" ]; then exit $? ; fi
          ./parallel_manager.sh ./resample_coadd_swarp_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd} ${HEADDIR}
	  if [ "$?" -gt "0" ]; then exit $? ; fi
          ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd} MEDIAN
	  if [ "$?" -gt "0" ]; then exit $? ; fi
          #adam-old# ic -p 8 '16 1 %1 1e-6 < ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/coadd.weight.fits > ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/coadd.flag.fits
	  if [ "$?" -gt "0" ]; then exit $? ; fi
          ./setup_general.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE instrument_$$
          rm -f instrument_$$
          ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd} STATS coadd ${MAGZP} AB ${CONDITION}
          exit_stat=$?
          if [ "${exit_stat}" -gt "0" ]; then
              	echo "adam-Error: problem with update_coadd_header.sh!"
              	exit ${exit_stat};
          fi
          coaddmodes="${coaddmodes} all"

        ##############################
        elif [ ${coadd} == "gabodsid" ]; then
          GABODSIDS=`${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 -t STATS -b -k GABODSID | sort | uniq | awk '{printf "%i ", $0}'`
          for GABODSID in ${GABODSIDS}
          do
            #adam-ask# I changed it to take CONFIG into account when considering the IMAGEID!=6 cut
            if [ "${CONFIG}" == "10_3" ]; then
                constructConditions gabodsid "(GABODSID=${GABODSID})" ""
            else
                constructConditions gabodsid "((IMAGEID!=6)AND(GABODSID=${GABODSID}))" ""
            fi
            CONDITION=${constructed_condition}
            #./prepare_coadd_swarp.sh -m ${SUBARUDIR}/${cluster}/${filter} \
            #                      -s SCIENCE \
            #                      -e "${ending}.sub" \
            #                      -n ${cluster}_gabodsid${GABODSID} \
            #                      -w ".sub" \
            #                      -eh headers${ASTROMADD} \
            #                      -r ${ra} \
            #                      -d ${dec} \
            #                      -i ${IMAGESIZE} \
            #                      -p ${PIXSCALEOUT} \
            #                      -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 STATS \
            #                         ${CONDITION} \
            #                         ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_gabodsid${GABODSID}.cat
            ./prepare_coadd_swarp_chips.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                                   -s SCIENCE \
                                   -e "${ending}.sub" \
                                   -n ${cluster}_gabodsid${GABODSID} \
                                   -w ".sub" \
                                   -eh headers${ASTROMADD} \
                                   -r ${ra} -d ${dec} \
                                   -i ${IMAGESIZE} \
                                   -p ${PIXSCALEOUT} \
                                   -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat8 CHIPS_STATS \
                                      ${CONDITION} \
                                      ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_gabodsid${GABODSID}.cat
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            #maybe#                      -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 STATS \
            ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_gabodsid${GABODSID} ${HEADDIR} ${cluster}_all
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_gabodsid${GABODSID}
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_gabodsid${GABODSID} CHIPS_STATS coadd ${MAGZP} AB ${CONDITION}
            exit_stat=$?
            if [ "${exit_stat}" -gt "0" ]; then
              	echo "adam-Error: problem with update_coadd_header.sh!"
              	exit ${exit_stat};
            fi
	    ./fix_coadd_gabodsid.py ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_gabodsid${GABODSID}/coadd.fits
	    ./fix_coadd_gabodsid-update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_gabodsid${GABODSID} CHIPS_STATS coadd -1.0 AB
            ic -p 8 '16 1 %1 1e-6 < ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_gabodsid${GABODSID}/coadd.weight.fits > ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_gabodsid${GABODSID}/coadd.flag.fits
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            coaddmodes="${coaddmodes} gabodsid${GABODSID}"
          done

        ##############################
        elif [ ${coadd} == "good" ]; then
            #adam-ask# is this right? I mean you could be coadding two different configs here couldn't you (I'm not sure if we should in principle, but we do in practice)
            if [ "${CONFIG}" == "10_3" ]; then
                #adam# constructConditions good "" "((seeing_rh_al<0.8)AND(e_abs<0.08))"
                #adam# I have to have some kind of condition here. else I get an error
                constructConditions good "" "(seeing_rh_al<3.5)"
            else
                #adam# constructConditions good "(IMAGEID!=6)" "((seeing_rh_al<0.8)AND(e_abs<0.08))"
                #adam# this should only happen for MACS1226+21 10_2 "good" mode
                #adam-old# constructConditions good "(IMAGEID!=6)" "((EXPOSURE!=6)AND(EXPOSURE!=7))"
		constructConditions good "(IMAGEID!=6)" "(seeing_rh_al<3.5)"
            fi
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
	  if [ "$?" -gt "0" ]; then exit $? ; fi
          ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd} ${HEADDIR} ${cluster}_all
	  if [ "$?" -gt "0" ]; then exit $? ; fi
          ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd}
	  if [ "$?" -gt "0" ]; then exit $? ; fi
          #adam-note# We can only read the flag values when detecting objects. Since detection is done on the "all" coadd, it's OK to have no rings in the "good" coadd
	  ic -p 8 '16 1 %1 1e-6 < ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/coadd.weight.fits > ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/coadd.flag.fits
	  if [ "$?" -gt "0" ]; then exit $? ; fi
          ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd} CHIPS_STATS coadd ${MAGZP} AB ${CONDITION}
          exit_stat=$?
          if [ "${exit_stat}" -gt "0" ]; then
              	echo "adam-Error: problem with update_coadd_header.sh!"
              	exit ${exit_stat};
          fi
          coaddmodes="${coaddmodes} good"

        ##############################
        ### new rotation coadd: split by both night and rotation
        elif [ ${coadd} == "rotation" ]; then
          ROTATIONS=`${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 -t STATS -b -k ROTATION | sort | uniq | awk '{printf "%i ", $0}'`
          ${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 -t STATS -b -k GABODSID ROTATION | sort | uniq > gabrot_$$.dat
          while read GABODSID ROTATION
          do
            #adam-ask# definitely wrong the old way, right? I changed it to take CONFIG into account when considering the IMAGEID!=6 cut
            if [ "${CONFIG}" == "10_3" ]; then
                constructConditions rotation "((GABODSID=${GABODSID})AND(ROTATION=${ROTATION}))" ""
            else
                constructConditions rotation "(((IMAGEID!=6)AND(GABODSID=${GABODSID}))AND(ROTATION=${ROTATION}))" ""
            fi
            CONDITION=${constructed_condition}
            echo ${CONDITION}
            ./prepare_coadd_swarp_chips.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                                   -s SCIENCE \
                                   -e "${ending}.sub" \
                                   -n ${cluster}_gab${GABODSID}-rot${ROTATION} \
                                   -w ".sub" \
                                   -eh headers${ASTROMADD} \
                                   -r ${ra} \
                                   -d ${dec} \
                                   -i ${IMAGESIZE} \
                                   -p ${PIXSCALEOUT} \
                                   -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat8 CHIPS_STATS \
                                      ${CONDITION} \
                                      ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_gab${GABODSID}-rot${ROTATION}.cat
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_gab${GABODSID}-rot${ROTATION} ${HEADDIR} ${cluster}_all
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_gab${GABODSID}-rot${ROTATION}
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            ic -p 8 '16 1 %1 1e-6 < ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_gab${GABODSID}-rot${ROTATION}/coadd.weight.fits > ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_gab${GABODSID}-rot${ROTATION}/coadd.flag.fits
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_gab${GABODSID}-rot${ROTATION} CHIPS_STATS coadd ${MAGZP} AB ${CONDITION}
            exit_stat=$?
            if [ "${exit_stat}" -gt "0" ]; then
              	echo "adam-Error: problem with update_coadd_header.sh!"
              	exit ${exit_stat};
            fi
            coaddmodes="${coaddmodes} gab${GABODSID}-rot${ROTATION}"
          done < gabrot_$$.dat

        ###################################
        elif [ ${coadd} == "exposure" ] && [ ${filter} != "K" ] && [ ${filter} != "I" ]; then
          calib=`awk 'BEGIN{if("'${filter}'"~"CALIB") print "1"; else print "0"}'`
          calib="0" #adam-tmp# 
          if [ ${calib} -eq 0 ]; then
          ${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 -t STATS -s -b -k EXPOSURE IMAGENAME > exposures_$$.list
            while read EXPOSURE IMAGENAME
            do
              constructConditions exposure "(EXPOSURE=${EXPOSURE})" ""
              CONDITION=${constructed_condition}
              ./prepare_coadd_swarp.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                                     -s SCIENCE \
                                     -e "${ending}.sub" \
                                     -n ${cluster}_${IMAGENAME} \
                                     -w ".sub" \
                                     -eh headers${ASTROMADD} \
                                     -r ${ra} \
                                     -d ${dec} \
                                     -i ${IMAGESIZE} \
                                     -p ${PIXSCALEOUT} \
                                     -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 STATS \
                                        ${CONDITION} \
                                        ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}_${IMAGENAME}.cat
	      if [ "$?" -gt "0" ]; then exit $? ; fi
              ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${IMAGENAME} ${HEADDIR} ${cluster}_all
	      if [ "$?" -gt "0" ]; then exit $? ; fi
              ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${IMAGENAME}
	      if [ "$?" -gt "0" ]; then exit $? ; fi
              ic -p 8 '16 %1 %2 1e-6 < ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${IMAGENAME}/coadd.flag.fits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${IMAGENAME}/coadd.weight.fits | ic -p 8 '16 %1 %1 0 == ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${IMAGENAME}/coadd.flag.fits > ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${IMAGENAME}/coadd.flag.temp.fits
	      if [ "$?" -gt "0" ]; then exit $? ; fi
              mv ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${IMAGENAME}/coadd.flag.temp.fits ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${IMAGENAME}/coadd.flag.fits
              ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${IMAGENAME} STATS coadd ${MAGZP} AB ${CONDITION}
              exit_stat=$?
              if [ "${exit_stat}" -gt "0" ]; then
              	echo "adam-Error: problem with update_coadd_header.sh!"
              	exit ${exit_stat};
              fi
              coaddmodes="${coaddmodes} ${IMAGENAME}"
            done < exposures_$$.list
            rm -f exposures_$$.list
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
	      if [ "$?" -gt "0" ]; then exit $? ; fi
              ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd} ${HEADDIR} ${cluster}_all
	      if [ "$?" -gt "0" ]; then exit $? ; fi
              ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd}
	      if [ "$?" -gt "0" ]; then exit $? ; fi
              ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd} STATS coadd ${MAGZP} AB ${CONDITION}
              exit_stat=$?
              if [ "${exit_stat}" -gt "0" ]; then
              	echo "adam-Error: problem with update_coadd_header.sh!"
              	exit ${exit_stat};
              fi
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
          ./parallel_manager.sh ./resample_coadd_swarp_pretty_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd} ${HEADDIR}
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
                -WEIGHT_IMAGE ${SUBARUDIR}/${cluster}/${filter}/WEIGHTS/${imagebase}${ending}.weight.fits \
                -WEIGHT_TYPE MAP_WEIGHT \
                -IMAGE_SIZE ${IMAGESIZE} -CENTER_TYPE MANUAL -CENTER ${ra},${dec} -PIXELSCALE_TYPE MANUAL -PIXEL_SCALE ${PIXSCALEOUT} \
                -IMAGEOUT_NAME ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_all/coadd.fits
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
            exit_stat=$?
            if [ "${exit_stat}" -gt "0" ]; then
              	echo "adam-Error: problem with update_coadd_header.sh!"
              	exit ${exit_stat};
            fi
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

        ###################################
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
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster}_${coadd} ${HEADDIR} ${cluster}_all
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd}
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            ic -p 8 '16 1 %1 1e-6 < ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/coadd.weight.fits > ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coadd}/coadd.flag.fits
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_${coadd} CHIPS_STATS coadd ${MAGZP} AB ${CONDITION}
            exit_stat=$?
            if [ "${exit_stat}" -gt "0" ]; then
              	echo "adam-Error: problem with update_coadd_header.sh!"
              	exit ${exit_stat};
            fi
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
        if [ -f "${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips_phot.cat5" ]; then
            MAGZP=`${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips_phot.cat5 -t ABSPHOTOM -k COADDZP | tail -n 1`
            value ${MAGZP}
            writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coaddmode}/coadd.fits MAGZP "${VALUE} / Magnitude zeropoint" REPLACE
        else
            MAGZP=-1.0
        fi

        ### make PSF plots, and write star reference catalog
        ./check_psf_coadd.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coaddmode} coadd.fits
	if [ "$?" -gt "0" ]; then exit $? ; fi

        #  if [ ${filter} == "K" ]; then
        #      ./fit_phot_K.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_${coaddmode} coadd.fits
        #  fi
done


if [ ! -d ${SUBARUDIR}/${cluster}/coadds_together_${cluster} ]; then
	mkdir ${SUBARUDIR}/${cluster}/coadds_together_${cluster}
	mkdir ${SUBARUDIR}/${cluster}/coadds_together_${cluster}/flags
	mkdir ${SUBARUDIR}/${cluster}/coadds_together_${cluster}/weights
fi
for coadd_dir in `\ls -d ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_*/`
do
	coadd_name=`basename ${coadd_dir} `
	ln -s ${coadd_dir}/coadd.fits ${SUBARUDIR}/${cluster}/coadds_together_${cluster}/${coadd_name}.${filter}.fits
	ln -s ${coadd_dir}/coadd.flag.fits ${SUBARUDIR}/${cluster}/coadds_together_${cluster}/flags/${coadd_name}.${filter}.flag.fits
	ln -s ${coadd_dir}/coadd.weight.fits ${SUBARUDIR}/${cluster}/coadds_together_${cluster}/weights/${coadd_name}.${filter}.weight.fits
done
echo "adam-look: ds9e ${SUBARUDIR}/${cluster}/coadds_together_${cluster}/coadd_${cluster}_*.fits &"
#adam# may want to run this to make plots of how good the exposures are (might want to throw out bad ones!): ./Plot_cluster_seeing_e1e2.py ${cluster}
