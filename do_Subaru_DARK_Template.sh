#!/bin/bash
set -xv
######################
# @file do_Subaru_10_2_DARK.sh
# @author Douglas Applegate
# @date 3/27/08
#
# @brief Processes dark frames for 10_2 chip config
######################

# CVSID="$Id: do_Subaru_DARK_Template.sh,v 1.1 2008-04-09 23:15:59 dapple Exp $"

REDDIR=`pwd`

MAXCHIP=10;
DARKDIR=SUBARU_10_2_DARK

RAWDATA=/nfs/slac/g/ki/ki02/xoc/anja/SUBARU/auxiliary/${DARKDIR}

export SUBARUDIR=/nfs/slac/g/ki/ki02/xoc/anja/SUBARU

DARK_NORM_THRESHOLD=5


####################
# Utilities

function createDir {
    
    if [ ! -d ${1} ]; then
	mkdir ${1}
    fi
}

############################################

function repack{

#####################################################################
####  preliminary stuff:  copy images, bring them in pipeline format,
####  sort into subdirectories
#####################################################################

    
    createDir ${SUBARUDIR}/${DARKDIR}

    gunzip ${RAWDATA}/*.fits.gz

    find ${RAWDATA} -maxdepth 1 -name SUPA\*.fits > allfiles_$$.txt

    echo 'Sorting...'

    sed 's/[0-9]\.fits//' allfiles_$$.txt | sort | uniq > uniqfiles_$$.txt

    echo "Done sorting.\n"

    echo "Putting files in mefs..."

    cd ${SUBARUDIR}

    createDir ${DARKDIR}/DARK

    createDir ${DARKDIR}/DARK/ORIGINALS


    while read IMAGE
    do
	BASE=`basename ${IMAGE}`

	mefcreate ${RAWDATA}/${BASE}?.fits -OUTPUT_IMAGE ${BASE}.fits 
	mv ${BASE}.fits ${DARKDIR}/ORIGINALS/DARK
    done < uniqfiles_$$.txt


    rm -f allfiles_$$.txt
    rm -f uniqfiles_$$.txt

    echo "Done\n"

    gzip ${RAWDATA}/*.fits &


    cd ${REDDIR}
}

#################################################################

function createNormMask{

    ./parallel_manager.sh ./create_norm_para.sh ${SUBARUDIR}/${DARKDIR} DARK
    
    for ((CHIP=1;CHIP<=${MAXCHIP};CHIP+=1));
    do
	ic '1 0 %1 ${DARK_NORM_THRESHOLD} < ?' \
	    ${SUBARUDIR}/${DARKDIR}/DARK_norm/DARK_norm_${CHIP}.fits \
	    > ${SUBARUDIR}/${DARKDIR}/DARK_norm/DARK_norm_${CHIP}.mask.fits
    done
}

#####################################################################

function createManualMask {

    ./create_badpixel_mask.sh ${SUBARUDIR}/${DARKDIR} DARK_weighted

    for ((CHIP=1;CHIP<=${MAXCHIP};CHIP+=1)); 
    do
	ic '0 1 %1 0 > ? ' \
	    ${SUBARUDIR}/${DARKDIR}/DARK_mask/DARK_mask_${CHIP}.fits \
	    > ${SUBARUDIR}/${DARKDIR}/DARK_mask/DARK_mask_${CHIP}.mask.fits
    done
}

#####################################################################

function createWeightedImage{

    for ((CHIP=1;CHIP<=${MAXCHIP};CHIP+=1));
    do
	ic '%1 %2 mult' ${SUBARUDIR}/${DARKDIR}/DARK/DARK_${CHIP}.fits \
	    ${SUBARUDIR}/${DARKDIR}/DARK_master/DARK_master_${CHIP}.fits \
	    > ${SUBARUDIR}/${DARKDIR}/DARK_weighted/DARK_weighted_${CHIP}.fits
    done

}

######################################################################

function createMasterMask{
    
    MAXINPUT=(($# - 1))
    if [ $MAXINPUT < 2 ]; then
	for ((CHIP=1;CHIP<=${MAXCHIP};CHIP+=1));
	do
	    cp ${SUBARUDIR}/${DARKDIR}/${1}/${1}_${CHIP}.mask.fits \
		${SUBARUDIR}/${DARKDIR}/DARK_master/DARK_master_${CHIP}.fits
	done
	return
    fi
    
    ICARG='%1 %2 mult'
    for ((CURARG=3;CURARG<=${MAXINPUT};CURARG+=1));
    do
	ICARG="${ICARG} %${CURARG} mult"
    done

    for ((CHIP=1;CHIP<=${MAXCHIP};CHIP+=1)); 
    do
	FILELIST=
	for ((CURARG=1;CURARG<=${MAXINPUT};CURARG+=1));
	do
	    FILELIST="$FILELIST ${SUBARUDIR}/${DARKDIR}/${${CURARG}}/${${CURARG}}_${CHIP}.mask.fits "
	done

	CMD="ic '${ICARG}' ${FILELIST} > ${SUBARUDIR}/${DARKDIR}/DARK_master/DARK_master_${CHIP}.fits"

	${CMD}

    done
}

#####################################################################

function combineIMasks{

    for ((CHIP=1;CHIP<=${MAXCHIP};CHIP+=1));
    do
   	cat ${SUBARUDIR}/${DARKDIR}/DARK_weighted/ORIG_IMASK/DARK_weighted_${CHIP}.imask \
	    ${SUBARUDIR}/${DARKDIR}/DARK_weighted/DARK_weighted_${CHIP}.imask \
	    > ${TEMPDIR}/imask_${CHIP}_$$

	mv ${TEMPDIR}/imask_${CHIP}_$$ \
	    ${SUBARUDIR}/${DARKDIR}/DARK_weighted/DARK_weighted_${CHIP}.imask
    done
}

########################################################################
########################################################################


repack

### create and load the SUBARU.ini file
./setup_SUBARU.sh ${SUBARUDIR}/${DARKDIR}/DARK
export INSTRUMENT=SUBARU
. ${INSTRUMENT:?}.ini


./process_split_Subaru_eclipse.sh ${SUBARUDIR}/${DARKDIR} DARK


### first quality check: run  imstats  , if necessary, reject files:
./check_files.sh  ${SUBARUDIR}/${DARKDIR} DARK "" 8000 12000


echo "Todo: Examine Individual Images for Problems && Reject"
exit


### make stacked DARK frames ###
./parallel_manager.sh ./process_bias_eclipse_para.sh ${SUBARUDIR}/${DARKDIR} DARK

### masking

createDir ${SUBARUDIR}/${DARKDIR}/DARK_master 
createDir ${SUBARUDIR}/${DARKDIR}/DARK_weighted

createNormMask

createMasterMask DARK_norm

createWeightedImage

echo "Todo: Manually Mask DARK Frames"

exit


createManualMask

createMasterMask DARK_norm DARK_mask




#createWeightedImage

#createDir ${SUBARUDIR}/${DARKDIR}/DARK_weighted/ORIG_IMASK
#
#mv ${SUBARUDIR}/${DARKDIR}/DARK_weighted/*.imask \
#    ${SUBARUDIR}/${DARKDIR}/DARK_weighted/ORIG_IMASK
#
#
#echo "TODO: Inspect weighted images for additional masking."
#
#exit
#
#
#
#combineIMasks
#    
#### REPEAT MAKING THE MASK ###
#
#rm -f ${SUBARUDIR}/${DARKDIR}/DARK_mask/DARK_mask_*.fits
#
#createManualMask
#
#createeMasterMask DARK_norm DARK_mask
#
#


