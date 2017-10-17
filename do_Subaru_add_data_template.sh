#! /bin/bash -xv

### superscript template to do the preprocessing
### $Id: do_Subaru_add_data_template.sh,v 1.4 2009-05-22 23:21:16 dapple Exp $


. progs.ini

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU

run=2007-07-18
filter="W-J-B"

export BONN_TARGET=${run}
export BONN_FILTER=${filter}


#Find Ending
case ${filter} in
    "I" )
	  ending=mos
	  ;;
    * )
	testfile=`ls -1 $SUBARUDIR/${run}_${filter}/SCIENCE/SUPA*_2OCFS*.fits | awk 'NR>1{exit};1'`
	ending=`basename ${testfile} | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`	  
	;;
esac

FLAT_DIR_SC1=`readlink ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_2_illum.fits`
FLAT_SET=`dirname $FLAT_DIR_SC1 | awk -F'SCIENCE_' '{print $2}'`
FLAT=`echo ${FLAT_SET} |  awk -F'_' '{print $1}'`
SET=`echo ${FLAT_SET} |  awk -F'_' '{print $2}'`
SKYBACK=`basename ${FLAT_DIR_SC1} .fits | awk -F'illum' '{print $2}'`


if [ ${ending} == "OCFSF" ]; then
    FRINGE="FRINGE"
elif [ ${ending} == "OCFS" ]; then
    FRINGE="NOFRINGE"
else
    echo "Unrecognized file ending: ${ending}"
    exit 2
fi


SCIENCEDIR=SCIENCE_${FLAT}_${SET}

export TEMPDIR='.'

export NOREDO=1
#Comment out the lines as you progress through the script



########################################
### Reset Logger
./BonnLogger.py clear

##################################################################
### create and load the SUBARU.ini file
### !!! DO NOT COMMENT THIS BLOCK !!!
##################################################################

./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
export INSTRUMENT=SUBARU

. ${INSTRUMENT:?}.ini

##################################################################

if [ ! -d ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm ] && \
    [ -e ${SUBARUDIR}/${run}_${filter}/SCIENCE_norm/SCIENCE_norm.tarz]; then
    cd ${SUBARUDIR}/${run}_${filter}
    tar -zxvf SCIENCE_norm.tarz
    cd $REDDIR
fi

##################################################################
### Capture Variables
./BonnLogger.py config \
    run=${run} \
    filter=${filter} \
    FLAT=${FLAT} \
    SET=${SET} \
    SKYBACK=${SKYBACK} \
    FRINGE=${FRINGE} \
    STANDARDSTARS=${STANDARDSTARS} \
    config=${config}


##################################################################
# copy in new data
##################################################################

./cp_aux_data.sh ${SUBARUDIR} ${run}_${filter} ${SUBARUDIR}/auxiliary/dapple_extraclusters/new_2009-04-29/${filter}


####################################################################
# pre-processing of individual chips,
# per filter
####################################################################

./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${run}_${filter} SCIENCE


./parallel_manager.sh ./process_standard_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT}_${SET} SCIENCE RESCALE


### Apply Corrections to Science Data
if [ ${FRINGE} == "NOFRINGE" ]; then
  ./parallel_manager.sh ./process_science_illum_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm RESCALE ILLUM ${SKYBACK} SCIENCE
else
  ./parallel_manager.sh ./process_science_illum_fringe_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR}_norm RESCALE ${SKYBACK} SCIENCE
fi

###Rationalize locations of files

cd ${SUBARUDIR}/${run}_${filter}
if [ ! -d ${SCIENCEDIR}/OCF_IMAGES ]; then
    mkdir ${SCIENCEDIR}/OCF_IMAGES
fi
mv SCIENCE/OCF_IMAGES/*.fits ${SCIENCEDIR}/OCF_IMAGES
rmdir SCIENCE/OCF_IMAGES

cd SCIENCE
for file in `ls SUPA*${ending}.fits`; do
    link=`readlink $file`
    if [ "${link}" != "" ]; then
	continue;
    fi
    mv $file ../${SCIENCEDIR}
    ln -s ../${SCIENCEDIR}/${file} .
done
cd ${REDDIR}

./create_binnedmosaics.sh ${SUBARUDIR}/${run}_${filter} ${SCIENCEDIR} SUP ${ending} 8 -32

exit 0;


##########################################################



./splitoff_aux_data.sh ${SUBARUDIR}/${run}_${filter} SCIENCE ${ending} ${SUBARUDIR}/SUBARU.list


##########################################################


###groups together cluster pointings from one run
./distribute_sets_subaru.sh ${SUBARUDIR} ${run}_${filter}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list

### note: this script now also copies globalweight*.fits and globalflag*fits
### to ${SUBARUDIR}/${cluster}/${filter}/WEIGHTS


####################################
##CHECKPOINT
####################################

./BonnLogger.py checkpoint Preprocess
