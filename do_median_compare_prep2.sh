#!/bin/bash -xv

cluster=$1
filter=$2


export BONN_LOG=0
export BONN_TARGET=${cluster}
export BONN_FILTER=${filter}


. progs.ini
. bash_functions.include

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki05/anja/SUBARU
CLUSTERDIR=$SUBARUDIR/test_coadd/${cluster}_${filter}

IMAGESIZE="12000,12000"
# Do astrometric calibration with SCAMP or ASTROMETRIX ?
ASTROMMETHOD=SCAMP

# only for Scamp (use SDSS-R6 or 2MASS ) :
ASTROMETRYCAT=SDSS-R6

ASTROMADD=""
if [ ${ASTROMMETHOD} = "SCAMP" ]; then
   ASTROMADD="_scamp_${ASTROMETRYCAT}"
   
fi

lookupfile=$SUBARUDIR/SUBARU.list

ra=`grep ${cluster} ${lookupfile} | awk '{print $3}'`
dec=`grep ${cluster} ${lookupfile} | awk '{print $4}'`

echo ${cluster} ${ra} ${dec}


coadds="Weighted Median"


######################
float_scale=2
function float_eval()
{
    local stat=0
    local result=0.0
    if [[ $# -gt 0 ]]; then
        result=$(echo "scale=$float_scale; $*" | bc -q 2>/dev/null)
        stat=$?
        if [[ $stat -eq 0  &&  -z "$result" ]]; then stat=1; fi
    fi
    echo $result
    return $stat
}

######################

####
#0.) Setup
###

#if [ ! -d $CLUSTERDIR ]; then
#    mkdir $CLUSTERDIR
#    mkdir $CLUSTERDIR/RAW_SCIENCE
#    for coadd in $coadds; do
#	mkdir -p $CLUSTERDIR/$coadd/SCIENCE
#	mkdir $CLUSTERDIR/$coadd/WEIGHTS
#    done
#fi
#
#for coadd in $coadds; do
#    cd $CLUSTERDIR/$coadd/SCIENCE
#    cp $SUBARUDIR/$cluster/$filter/SCIENCE/$cluster.cat .
#    cp -r $SUBARUDIR/$cluster/$filter/SCIENCE/cat .
#    ln -s $SUBARUDIR/$cluster/$filter/SCIENCE/diffmask .
#    cp -r $SUBARUDIR/$cluster/$filter/SCIENCE/headers_* .
#done
##
#cd $CLUSTERDIR/RAW_SCIENCE
#ln -s $SUBARUDIR/$cluster/$filter/SCIENCE/SUPA*.fits .
#
#cd $CLUSTERDIR/Weighted/SCIENCE
#ln -s $SUBARUDIR/$cluster/$filter/SCIENCE/reg .
#
#cd $CLUSTERDIR/Weighted/WEIGHTS
#ln -s $SUBARUDIR/$cluster/$filter/WEIGHTS/SUPA*weight.fits .
#
#cd $CLUSTERDIR/Median/SCIENCE
#ln -s $SUBARUDIR/$cluster/$filter/SCIENCE/SUPA*FS.fits .
#ln -s $SUBARUDIR/$cluster/$filter/SCIENCE/SPLIT_IMAGES .
#mkdir reg
#
#cd $CLUSTERDIR/Median/WEIGHTS
#ln -s $SUBARUDIR/$cluster/$filter/WEIGHTS/global*.fits .
#
#cd $REDDIR
#
#
#
#

#INSTRUMENT
./setup_SUBARU.sh ${SUBARUDIR}/test_coadd/${cluster}_${filter}/RAW_SCIENCE
export INSTRUMENT=SUBARU
. ${INSTRUMENT:?}.ini


testfile=`ls -1 $CLUSTERDIR/RAW_SCIENCE/SUPA*_2*.fits | awk 'NR>1{exit};1'`
ending=`filename $testfile | awk -F'_2' '{print $2}' | awk -F'.' '{print $1}'`


#######
#2.) Create Injection Lists
####


##master list
gallist=$CLUSTERDIR/gallist.txt

./makeGallist.pl $gallist
#
###make detection image (to be used with mask_aper only!)
cd $IRAFDIR
cp $gallist $cluster.$filter.gallist
{
    echo flprc
    echo noao
    sleep 1
    echo artdata
    sleep 1
    echo mkobjects $cluster.$filter.fits ncols=12000 nlines=12000 background=1 objects=\"$cluster.$filter.gallist\" magzero=40
    sleep 1
    echo flprc
    echo log
    } | ${P_CL}
mv $cluster.$filter.fits $CLUSTERDIR/detect.fits
cd $REDDIR



#	    
######
##3.) Make Median Weights
###
#
#
#
#./maskBadOverscans.py $CLUSTERDIR/Median SCIENCE SUPA
#./convertRegion2Poly.py $CLUSTERDIR/Median SCIENCE
#./transform_ds9_reg_alt.sh $CLUSTERDIR/Median SCIENCE
#./parallel_manager.sh ./create_weights_delink_para.sh $CLUSTERDIR/Median SCIENCE ${ending}
#
##
##
########
###4.) Coadd Images
#####
##
#./parallel_manager.sh ./create_skysub_delink_para.sh $CLUSTERDIR RAW_SCIENCE ${ending} ".sub" TWOPASS
##
##
for coadd in $coadds; do
#
#    cd $CLUSTERDIR/$coadd/SCIENCE
#    rm SUPA*.fits
#    ln -s ../../RAW_SCIENCE/SUPA*fits .
#    cd $REDDIR
#
#    if [ -f coadd.head ]; then
#	rm coadd.head
#    fi
#    
#    ./prepare_coadd_swarp.sh -m $CLUSTERDIR/$coadd \
#	-s SCIENCE \
#	-e "${ending}.sub" \
#	-n ${cluster} \
#	-w ".sub" \
#	-eh headers${ASTROMADD} \
#	-r ${ra} \
#	-d ${dec} \
#	-i ${IMAGESIZE} \
#	-l $CLUSTERDIR/$coadd/SCIENCE/cat/chips.cat6 STATS \
#	"(SEEING<2.0);" \
#	$CLUSTERDIR/$coadd/SCIENCE/${cluster}.cat
#
#
    ./parallel_manager.sh ./resample_coadd_swarp_para.sh $CLUSTERDIR/$coadd SCIENCE "${ending}.sub" ${cluster} ${REDDIR}
##
done
##
#####save some time!
##
./createObjectLists.py $gallist $CLUSTERDIR/Median/SCIENCE/coadd_$cluster/*.resamp.fits
#
##
##   
##inject objects into images
cd $IRAFDIR
for file in $CLUSTERDIR/Median/SCIENCE/coadd_$cluster/*.resamp.fits; do
    basename=`basename $file .fits`
    rootname=`basename $file .sub.$cluster.resamp.fits`
    exptime=`dfits $CLUSTERDIR/Median/SCIENCE/$rootname.fits | fitsort EXPTIME | awk '(! /FILE/){print $2}'`
    cp $file $rootname.fits
    gallist=$CLUSTERDIR/Median/SCIENCE/coadd_$cluster/$basename.gallist
    cp $gallist $rootname.gallist
    {
	echo flprc
	echo noao
	sleep 1
	echo artdata
	sleep 1
	echo mkobjects $rootname.fits objects=\"$rootname.gallist\" exptime=$exptime magzero=27 gain=$GAIN
	sleep 1
	echo flprc
	echo log
    } | ${P_CL}
    mv $rootname.fits $file
done
cd $REDDIR


cd $CLUSTERDIR/Weighted/SCIENCE/coadd_$cluster
rm *.resamp.fits
ln -s ../../../Median/SCIENCE/coadd_$cluster/*.resamp.fits .
cd $REDDIR



for coadd in $coadds; do

    if [ "$coadd" = "Median" ]; then
	./perform_coadd_swarp.sh $CLUSTERDIR/$coadd SCIENCE ${cluster} MEDIAN
    else
	./perform_coadd_swarp.sh $CLUSTERDIR/$coadd SCIENCE ${cluster}
    fi


  ### add header keywords

    value ${cluster}
    writekey $CLUSTERDIR/$coadd/SCIENCE/coadd_${cluster}/coadd.fits OBJECT "${VALUE} / Target" REPLACE
  
    value ${filter}
    writekey $CLUSTERDIR/$coadd/SCIENCE/coadd_${cluster}/coadd.fits FILTER "${VALUE} / Filter" REPLACE
  

  ### update photometry
  if [ -f $CLUSTERDIR/$coadd/SCIENCE/cat/chips_phot.cat5 ]; then
      MAGZP=`${P_LDACTOASC} -i $CLUSTERDIR/$coadd/SCIENCE/cat/chips_phot.cat5 -t ABSPHOTOM -k COADDZP | tail -n 1`
  else
      MAGZP=-1.0
  fi
  
  ./update_coadd_header.sh $CLUSTERDIR/$coadd SCIENCE ${cluster} STATS coadd ${MAGZP} Vega "(SEEING<2.0)"

done
