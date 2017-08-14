#! /bin/bash -xv

### script to run the steps for masking image sets
### 
### this used to be the first part of the do_Subaru_coadd_template scripts;
### is now disjunct
###
### $Id: do_masking.sh,v 1.3 2010-10-05 22:27:58 dapple Exp $

. progs.ini
. bash_functions.include

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU

cluster=$1  # cluster nickname as in /nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list
#filters="W-J-B_2007-07-18 W-C-RC_2007-07-18 W-J-V_2007-07-18 W-C-IC_2007-07-18"
filters=$2

for filter in $filters; do

if [ ! -d ${SUBARUDIR}/${cluster}/${filter} ]; then
    exit
fi

filtername=`echo $filter | awk -F'_' '{print $1}'`

###############################################
######################
#Some Setup Stuff

#export BONN_TARGET=$cluster
#export BONN_FILTER=$filter


lookupfile=/nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list

#Find Ending
testfile=`ls -1 $SUBARUDIR/$cluster/$filter/SCIENCE/SUP*_2*.fits | awk 'NR>1{exit};1'`
ending=`basename $testfile | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`

########################################
### Reset Logger
#./BonnLogger.py clear

./setup_SUBARU.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE
export INSTRUMENT=SUBARU
. ${INSTRUMENT:?}.ini


###################################################################
#### Capture Variables
#./BonnLogger.py config \
#    cluster=${cluster} \
#    filter=${filter} \
#    config=${config} \
#    ending=${ending}


#####################
## weight creation ##
#####################


#### C: Processing for each Ind Image ###
#
./parallel_manager.sh ./spikefinder_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE SUP ${ending} ${filtername}
###
### transform ds9-region file into ww-readable file:
./convertRegion2Poly.py ${SUBARUDIR}/${cluster}/${filter} SCIENCE
./transform_ds9_reg_alt.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE
./clean_empty_regionfiles.sh ${SUBARUDIR}/${CLUSTER}/${filter}/SCIENCE/reg/*.reg
#
### C: CHIP PROCESSING ###
#
./parallel_manager.sh ./create_weights_raw_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} WEIGHTS

./parallel_manager.sh ./create_science_weighted.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE WEIGHTS ${ending}
#
####run once, at end of first time through. Here, you'll be able to edit the region files, and adjust the masks.
##./maskBadOverscans.py ${SUBARUDIR}/${cluster}/${filter} SCIENCE SUPA
#
#./create_binnedmosaics_empty.sh ${SUBARUDIR}/${cluster}/${filter} WEIGHTS SUP ${ending}.weight 8 -32
#./create_binnedmosaics_empty.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE_weighted SUP ${ending}.weighted 8 -32

echo "Todo: Mask images by hand for remaining defects (satelite trails, blobs, etc).
Use the images in SCIENCE_weighted for masking.
maskImages.pl may be useful for managing region files."
echo "For Simplicity, make sure you save region files to SCIENCE/reg (use maskImages.pl -r)"
echo "Goto C: Chip Processing"

#exit 0;

#############################
### Consolidate into filter directory
#############################

if [ ! -d ${SUBARUDIR}/${cluster}/${filtername} ]; then
    mkdir ${SUBARUDIR}/${cluster}/${filtername}
    mkdir ${SUBARUDIR}/${cluster}/${filtername}/SCIENCE
    mkdir ${SUBARUDIR}/${cluster}/${filtername}/WEIGHTS
fi

cd ${SUBARUDIR}/${cluster}/${filtername}/SCIENCE
ln -s ../../${filter}/SCIENCE/SUP*fits .
cd ${SUBARUDIR}/${cluster}/${filtername}/WEIGHTS
ln -s ../../${filter}/WEIGHTS/SUP*fits .
cd ${REDDIR}

###################################
#CHECKPOINT
###################################
#./BonnLogger.py checkpoint Masking

#./makePNGs.pl ${SUBARUDIR}/${cluster}/${filter}/SCIENCE_weighted/BINNED

done
