#! /bin/bash -xv

### template superscript to coadd a set of images
### (set meaning images of the same object, possibly different nights)
###
### $Id: do_Subaru_coadd_MACS0018_V.sh,v 1.4 2010-02-02 23:04:24 dapple Exp $

. progs.ini
. bash_functions.include

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki02/xoc/anja/SUBARU

cluster="MACS0018+16"  # cluster nickname as in /nfs/slac/g/ki/ki02/xoc/anja/SUBARU/SUBARU.list
filter="W-J-V"


###############################################
######################
#Some Setup Stuff

export BONN_TARGET=$cluster
export BONN_FILTER=$filter


lookupfile=/nfs/slac/g/ki/ki02/xoc/anja/SUBARU/SUBARU.list

#Find Ending
testfile=`ls -1 $SUBARUDIR/$cluster/$filter/SCIENCE/SUPA*_2*.fits | awk 'NR>1{exit};1'`
ending=`filename $testfile | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`

########################################
### Reset Logger
./BonnLogger.py clear

./setup_SUBARU.sh ${SUBARUDIR}/${cluster}/${filter}/SCIENCE
export INSTRUMENT=SUBARU
. ${INSTRUMENT:?}.ini


##################################################################
### Capture Variables
./BonnLogger.py config \
    cluster=${cluster} \
    filter=${filter} \
    config=${config} \
    ending=${ending}


#####################
## weight creation ##
#####################

### C: Processing for each Ind Image ###

#./parallel_manager.sh ./spikefinder_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE SUPA ${ending}

  #### transform ds9-region file into ww-readable file:
#./convertRegion2Poly.py ${SUBARUDIR}/${cluster}/${filter} SCIENCE
#./transform_ds9_reg_alt.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE
#
#### C: CHIP PROCESSING ###
#
#./parallel_manager.sh ./create_weights_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
#
#./parallel_manager.sh ./create_science_weighted.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE WEIGHTS ${ending}
#

#run once, at end of first time through. Here, you'll be able to edit the region files, and adjust the masks.
#./maskBadOverscans.py ${SUBARUDIR}/${cluster}/${filter} SCIENCE SUPA
#./maskAutotracker.py ${SUBARUDIR}/${cluster}/${filter} SCIENCE


#./create_binnedmosaics.sh ${SUBARUDIR}/${cluster}/${filter} WEIGHTS SUPA ${ending}.weight 8 -32
#./create_binnedmosaics.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE_weighted SUPA ${ending}.weighted 8 -32



#echo "Todo: Mask images by hand for remaining defects (satelite trails, blobs, etc).
#Use the images in SCIENCE_weighted for masking.
#maskImages.pl may be useful for managing region files."
#echo "For Simplicity, make sure you save region files to SCIENCE/reg (use maskImages.pl -r)"
#echo "Goto C: Chip Processing"
#
#exit 0;
#
#./makePNGs.pl ${SUBARUDIR}/${cluster}/${filter}/SCIENCE_weighted/BINNED
#
##################
### coaddition ###
##################


ra=`grep ${cluster} ${lookupfile} | awk '{print $3}'`
dec=`grep ${cluster} ${lookupfile} | awk '{print $4}'`

echo ${cluster} ${ra} ${dec}

###adds astrometric info; makes directory cat with ${image}_${chip}${ending}.cat
#./parallel_manager.sh  ./create_astromcats_weights_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} WEIGHTS ${ending}.weight
#
#### check PSF in individual exposures
#### via running SE, finding stars, extra
#### all done in cat directory
#### writes to .cat, adds .cat0 _ksb.cat1 _ksb.cat2 _ksb_tmp.cat2 _tmp.cat1 _tmp1.cat1  and PSFcheck/ , copy/
#
#./parallel_manager.sh ./check_science_PSF_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
#./check_science_PSF_plot.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
#./merge_sex_ksb.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
#
#### makes astrom/ and headers/
#./create_run_list.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ROTATION uniqruns_$$.txt NOSPLIT
#RUNS=""
#NRUNS=0
#while read SUBRUN
#do
#  RUNS="${RUNS} ${REDDIR}/${SUBRUN}.txt"
#  NRUNS=$(( ${NRUNS} + 1 ))
#done < ${TEMPDIR}/uniqruns_$$.txt    
#echo ${RUNS}
#./create_astrometrix_astrom_run.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} USNOB1 ${RUNS}
#
#### check whether the previous step worked
#nhead=`ls -1 ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/headers/*.head | wc | awk '{print $1}'`
#if [ ${nhead} -eq 0 ]; then
#    echo "No header files were created - something's wrong!"
#    exit 2;
#fi
#
#### makes photom/ ; writes to headers/
#./create_photometrix.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending}
#
#### makes plots/
#./create_stats_table.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} headers
#./create_absphotom_photometrix.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE
#./make_checkplot_stats.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE chips.cat6 STATS ${cluster}
#
#### makes .sub.fits files
#./parallel_manager.sh ./create_skysub_delink_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${ending} ".sub" TWOPASS
#
./prepare_coadd_swarp.sh -m ${SUBARUDIR}/${cluster}/${filter} \
                         -s SCIENCE \
                         -e "${ending}.sub" \
                         -n ${cluster} \
                         -w ".sub" \
                         -eh headers \
                         -r ${ra} \
                         -d ${dec} \
                         -l ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips.cat6 STATS \
                            "(SEEING<2.0);" \
                            ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/${cluster}.cat

./parallel_manager.sh ./resample_coadd_swarp_para.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE "${ending}.sub" ${cluster} ${REDDIR}

./perform_coadd_swarp.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster}


### add header keywords

value ${cluster}
writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}/coadd.fits OBJECT "${VALUE} / Target" REPLACE

value ${filter}
writekey ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/coadd_${cluster}/coadd.fits FILTER "${VALUE} / Filter" REPLACE

### update photometry
if [ -f ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips_phot.cat5 ]; then
    MAGZP=`${P_LDACTOASC} -i ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/cat/chips_phot.cat5 -t ABSPHOTOM -k COADDZP | tail -n 1`
else
    MAGZP=-1.0
fi

./update_coadd_header.sh ${SUBARUDIR}/${cluster}/${filter} SCIENCE ${cluster} STATS coadd ${MAGZP} Vega "(SEEING<2.0)"
