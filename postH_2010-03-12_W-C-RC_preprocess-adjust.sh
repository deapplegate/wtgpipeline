#! /bin/bash
set -xv

#adam-does# this is contains all of the preliminaries that you need to start with in order to do the preprocessing steps.
#	primary script to pull from to peg onto the end is from adam_MACS1115-do_Subaru_preprocess.sh
#	search for #adam-CHANGE# for the things you may need to change in certain circumstances
pprun=2010-03-12_W-C-RC
filter=${pprun#2*_}
run=${pprun%_*}
export BONN_TARGET=${run}
export BONN_FILTER=${filter}

####################################################
### the following need to be specified for each run
####################################################
. progs.ini > /tmp/progs.out 2>&1
REDDIR=`pwd`
export INSTRUMENT=SUBARU
export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
#run="2010-03-12" ; filter="W-S-I+";FLAT=SKYFLAT  #Z2701   10_3 2010-03-12_W-S-I+
SET=SET1            # sets time period of flat to use
SKYBACK=256         # in case of SKYFLAT: size of background mesh for superflat illumination construction
                    # use 256 if no "blobs" due to stars are visible (in BVR?) 16 (or 32) if lots of blobs
####################################################
### set FLAT, FRINGE, and ENDING ( fringing correction for Z band only )
####################################################

if [ -d ${SUBARUDIR}/${run}_${filter}/DOMEFLAT ]; then
	FLAT=DOMEFLAT
elif [ -d ${SUBARUDIR}/${run}_${filter}/SKYFLAT ]; then
	FLAT=SKYFLAT
else
    echo "You need flats!"
    exit 2;
fi
FRINGE=NOFRINGE # FRINGE if fringing correction necessary; NOFRINGE otherwise
if [ "${filter}" == "W-S-Z+" ] ; then
	FRINGE="FRINGE"
fi
if [ ${FRINGE} == "FRINGE" ]; then
    ending="OCFSF"
elif [ ${FRINGE} == "NOFRINGE" ]; then
    ending="OCFS"
else
    echo "You need to specify FRINGE or NOFRINGE for the fringing correction!"
    exit 2;
fi
SCIENCEDIR=SCIENCE_${FLAT}_${SET}

####################################################
### set config, can make this changable if you like
####################################################
config="10_3"
#adam-CHANGE# change this if I'm working with multiple configs!
#./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
#exit_stat=$?
#if [ "${exit_stat}" -gt "0" ]; then
#	exit ${exit_stat};
#fi
. ${INSTRUMENT:?}.ini

####################################################
### a quick example
####################################################
#if [ "$config" == "10_3" ] ; then
#	./parallel_manager.sh ./process_science_4channels_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE} #8
#elif [ "$config" == "10_2" ] ; then
#	./parallel_manager.sh ./process_science_eclipse_para.sh ${SUBARUDIR}/${run}_${filter} BIAS ${FLAT} SCIENCE RESCALE ${FRINGE} #8
#else
#	echo "problem with config";exit 1
#fi
#exit_stat=$?
#if [ "${exit_stat}" -gt "0" ]; then
#	exit ${exit_stat};
#fi

####################################################
### START pasting in new stuff below here!
####################################################

ln -s ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR/SUPA*${ending}.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/

if [ ! -d ${SUBARUDIR}/${run}_${filter}/${FLAT} ]; then
    mkdir ${SUBARUDIR}/${run}_${filter}/${FLAT}
fi

for ((CHIP=1;CHIP<=${NCHIPS};CHIP++));
do

    rm ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}.fits
    rm ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}_illum.fits
    rm ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}_fringe.fits

    ln -s ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR/${SCIENCEDIR}_${CHIP}.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}.fits
    ln -s ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR/${SCIENCEDIR}_${CHIP}_illum${SKYBACK}.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}_illum.fits
    if [ ${FRINGE} == "FRINGE" ]; then
    	ln -s ${SUBARUDIR}/${run}_${filter}/$SCIENCEDIR/${SCIENCEDIR}_${CHIP}_fringe${SKYBACK}.fits ${SUBARUDIR}/${run}_${filter}/SCIENCE/SCIENCE_${CHIP}_fringe.fits
    fi
    #ln -s ${SUBARUDIR}/${run}_${filter}/${FLAT}_${SET}/${FLAT}_${SET}_${CHIP}.fits ${SUBARUDIR}/${run}_${filter}/${FLAT}/${FLAT}_${CHIP}.fits

done


##########################################################
