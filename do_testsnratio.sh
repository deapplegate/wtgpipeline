#! /bin/bash -xv



####
##NOTE:
### Mirror cluster directory format for coadd_${cluster}
### link in resampled science and weight files

### new coaddition script
###
### the astro-/photometry can be done via SCAMP (preferred) or
### ASTROMETRIX
###
### $Id: do_testsnratio.sh,v 1.2 2009-02-12 21:54:50 dapple Exp $

. progs.ini
. bash_functions.include

REDDIR=`pwd`

export SUBARUDIR=/nfs/slac/g/ki/ki06/anja/SUBARU/test_snratio

cluster="A2219"  # cluster nickname as in /nfs/slac/g/ki/ki02/xoc/anja/SUBARU/SUBARU.list

#FILTERS="W-J-B W-J-V W-C-RC W-C-IC W-S-Z+"
#FILTERS="W-J-V W-C-RC W-C-IC W-S-Z+"
FILTERS="W-J-V"

NAXIS1=12000
NAXIS2=12000
IMAGESIZE="${NAXIS1},${NAXIS2}"

export BONN_LOG=0

export PIXSCALE=0.2

# coadd _all_ images or those with _good_ shear?
coadd=

# Do astrometric calibration with SCAMP or ASTROMETRIX ?
ASTROMMETHOD=SCAMP
#ASTROMMETHOD=ASTROMETRIX

# only for Scamp (use SDSS-R6 or 2MASS ) :
ASTROMETRYCAT=SDSS-R6

# for astrometrix (use SDSS5 or USNOB1):
#ASTROMETRYCAT=SDSS5

ASTROMADD=""
if [ ${ASTROMMETHOD} = "SCAMP" ]; then
   ASTROMADD="_scamp_${ASTROMETRYCAT}"
   
fi

###############################################
######################
#Some Setup Stuff

# coaddition constraints

export BONN_TARGET=${cluster}
export BONN_FILTER=${FILTERS}

lookupfile=/nfs/slac/g/ki/ki05/anja/SUBARU/SUBARU.list

ra=`grep ${cluster} ${lookupfile} | awk '{print $3}'`
dec=`grep ${cluster} ${lookupfile} | awk '{print $4}'`

echo ${cluster} ${ra} ${dec}

LINE=""

#######################################
## Reset Logger
#adam-BL#./BonnLogger.py clear


##################################################
### after possible calibration across filters: ###
### need to work per filter again              ###
##################################################

for filter in ${FILTERS}
do
  export BONN_FILTER=${filter}
  echo ${filter}

  #adam-BL#./BonnLogger.py clear

  ./setup_general.sh /nfs/slac/g/ki/ki05/anja/SUBARU/${cluster}/${filter}/SCIENCE instrument_$$
  export INSTRUMENT=`cat instrument_$$`
  rm -f instrument_$$
  . ${INSTRUMENT:?}.ini

  ending=OCFSRI.sub


  files=`ls ${SUBARUDIR}/${cluster}/${filter}/SCIENCE/SUPA*OCFSRI.sub.fits`
  for file in $files; do

      base=`basename $file .sub.fits`
      dir=`dirname $file`
      ${P_SEX} ${file} -c ${DATACONF}/image-objects.sex \
	  -CHECKIMAGE_NAME ${dir}/${base}.noobjs.fits \
	  -CHECKIMAGE_TYPE SEGMENTATION \
	  -DETECT_MINAREA 5 \
	  -DETECT_THRESH 1.5 \
	  -ANALYSIS_THRESH 1.5 \
	  -WEIGHT_IMAGE ${dir}/${base}.weight.fits \
	  -WEIGHT_TYPE MAP_WEIGHT
      if [ $? != 0 ]; then
	  exit 1
      fi

      
      ${P_IC} '%2 0 %1 0 == ?' ${dir}/${base}.noobjs.fits \
	  ${dir}/${base}.weight.fits \
	  > ${dir}/temp.fits
      if [ $? != 0 ]; then
	  exit 2
      fi

      mv $dir/$base.weight.fits $dir/$base.weight.bkup
      mv ${dir}/temp.fits ${dir}/${base}.weight.fits
      rm -f ${dir}/${base}.noobjs.fits

      cp $file $dir/$base.sub.bkup
      ./gaussianNoise.py ${file} ${dir}/${base}.weight.fits ${dir}/temp.fits
      if [ $? != 0 ]; then
	  exit 3
      fi
      mv ${dir}/temp.fits ${file}
      naxis1=`dfits ${file} | fitsort NAXIS1 | awk '($1 !~ /FILE/){print $2}'`
      naxis2=`dfits ${file} | fitsort NAXIS2 | awk '($1 !~ /FILE/){print $2}'`
      rm -f ${dir}/${base}.weight.fits
      ic -c $naxis1 $naxis2 1 > ${dir}/${base}.weight.fits
      

  done





  ### add header keywords

done
