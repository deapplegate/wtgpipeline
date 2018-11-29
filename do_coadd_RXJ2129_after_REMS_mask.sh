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
HEADDIR="${SUBARUDIR}/coadd_headers/"
#export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU

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
lookupfile=/gpfs/slac/kipac/fs1/u/awright/SUBARU/SUBARU.list
#adam-old# lookupfile=/nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
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
          ./test_coadd_ready.sh ${SUBARUDIR}/${cluster} ${filter} ${ending} ${ASTROMETRYCAT} ${ASTROMADD}
          if [ $? -gt 0 ]; then
              echo "adam-Error: test_coadd_ready failed"
              exit 1
          fi
          ######################
          calib=`awk 'BEGIN{if("'${filter}'"~"CALIB") print "1"; else print "0"}'`
          if [ ${calib} -eq 0 ]; then
              constructConditions all "" "((((RA>(${ra}-0.5))AND(RA<(${ra}+0.5)))AND((DEC>(${dec}-0.5))AND(DEC<(${dec}+0.5))))AND(SEEING<1.9))"
          else
              constructConditions all "" "(((RA>(${ra}-0.5))AND(RA<(${ra}+0.5)))AND((DEC>(${dec}-0.5))AND(DEC<(${dec}+0.5))))"
          fi
          CONDITION=${constructed_condition}
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
	  ./adam_gabodsids_combiner.py ${GABODSIDS} > gabodsid_tmp_${cluster}_${filter}.log
	  cat gabodsid_tmp_${cluster}_${filter}.log |\
          {   while read GABODSID GABCOND

          do
            #adam-ask# I changed it to take CONFIG into account when considering the IMAGEID!=6 cut
	    if [ ${GABODSID} -ge 1309 ] && [ ${GABODSID} -lt 3470 ]; then
              echo "10_2 chip configuration"  
              CONFIG="10_2"
            elif [ ${GABODSID} -ge 3470 ] && [ ${GABODSID} -lt 7000 ]; then                                                                                                                                                       
              echo "10_3 chip configuration"  
              CONFIG="10_3"
	    else
              echo "adam-Error: no config recognized for GABODSID=${GABODSID}"
              exit 1;
            fi
            #if [ "${CONFIG}" == "10_3" ]; then
            #    constructConditions gabodsid "(GABODSID=${GABODSID})" ""
            #else
            #    #adam-tmp# constructConditions gabodsid "((IMAGEID!=6)AND(GABODSID=${GABODSID}))" ""
            #    constructConditions gabodsid "(GABODSID=${GABODSID})" ""
            #fi
            constructConditions gabodsid "${GABCOND}"
	    CONDITION=${constructed_condition}

            ./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_gabodsid${GABODSID}
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            ./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}_gabodsid${GABODSID} STATS coadd ${MAGZP} AB ${CONDITION}
            exit_stat=$?
            if [ "${exit_stat}" -gt "0" ]; then
              	echo "adam-Error: problem with update_coadd_header.sh!"
              	exit ${exit_stat};
            fi
            ic -p 8 '16 1 %1 1e-6 < ?' ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_gabodsid${GABODSID}/coadd.weight.fits > ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}_gabodsid${GABODSID}/coadd.flag.fits
	    if [ "$?" -gt "0" ]; then exit $? ; fi
            coaddmodes="${coaddmodes} gabodsid${GABODSID}"
          done  }

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

		constructConditions good "" "(seeing_rh_al<3.5)"
		#adam-tmp# constructConditions good "(IMAGEID!=6)" "(seeing_rh_al<3.5)"
            fi
            CONDITION=${constructed_condition}
            echo "${CONDITION}"
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
                #adam-tmp# constructConditions rotation "(((IMAGEID!=6)AND(GABODSID=${GABODSID}))AND(ROTATION=${ROTATION}))" ""
                constructConditions rotation "((GABODSID=${GABODSID})AND(ROTATION=${ROTATION}))" ""
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

if [ -f gabodsid_tmp_${cluster}_${filter}.log ]; then
	rm gabodsid_tmp_${cluster}_${filter}.log
fi

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
