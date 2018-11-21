#!/bin/bash -xv

# the script creates weights for science frames.
# It assumes the global weight images in the WEIGHT
# directory and the reg files in the sciencedir/reg
# directory.
#
# 30.05.04:
# temporary files go to a TEMPDIR directory 
#
# 24.08.04:
# the SExtractor call to produce the cosmic ray mask now
# produces a DUMMY catalog in TEMPDIR (avoiding a lot of
# stdout messages during the processing)
#
# 15.10.05:
# a line break (in the argument images of ww) 
# in the case where a reg file is present
# led to problems on aibn202. Hence, I removed it.
#
# 25.04.2006:
# temporarily created FITS files (cosmic ray masks)
# are removed at the end of the script.
#
# 17.07.2006:
# the temporary file cosmic.cat is renamed to a unique name
# including the process number. It is also removed at the
# end of image processing.
#
# 22.09.2006:
# - I introduced the possibility to use specific cosmic ray mask
#   if necessary. The location of such masks has to be given
#   as (optional) command line argument. If a mask is not
#   provided the standard 'cosmic.ret.sex' mask is used.
# - I made the listing of files more robust if many files
#   are involved (by using 'find' instead of 'ls')
#
# 01.08.2007:
# some cleaning of not needed temporary files added


# $1: main directory
# $2: science dir.
# $3: image extension (ext) on ..._iext.fits (i is the chip number)
# $4: Filter to use for cosmic ray detection (OPTIONAL)
# ${!#}: chips to be processed

. ${INSTRUMENT:?}.ini

# set cosmic ray mask to use:
MASK=${CONF}/cosmic.ret.sex

if [ $# -eq 5 ]; then
   MASK=$4
fi

for CHIP in ${!#}
do
  ${P_FIND} /$1/$2/ -maxdepth 1 -name \*_${CHIP}$3.fits \
            -print > ${TEMPDIR}/crw_images_$$

  FILE=`${P_GAWK} '(NR==1) {print $0}' ${TEMPDIR}/crw_images_$$`

  if [ -L ${FILE} ]; then
    LINK=`${P_READLINK} ${FILE}`
    RESULTDIR=`dirname ${LINK}`
  else
    RESULTDIR="/$1/WEIGHTS"
  fi
  
  cat ${TEMPDIR}/crw_images_$$ |\
  {
    while read file
    do
      BASE=`basename ${file} $3.fits`

      # first run sextractor to identify cosmic rays:
      ${P_SEX} ${file} -c ${CONF}/cosmic.conf.sex -CHECKIMAGE_NAME \
                          ${TEMPDIR}/cosmic_${CHIP}_$$.fits \
                          -FILTER_NAME ${MASK} \
                          -CATALOG_NAME ${TEMPDIR}/cosmic.cat_$$
      
      # then run weightwatcher
      # this assumes the use of the spikefinder....
      # Case 1: With .reg files to load and diffractrion mask files
      # Case 2: With diffraction mask, no .reg file
      # Case 3: With .reg file, no diffraction mask
      # Case 4: Neither a diff. mask nor a .reg file.
      if [ -r "/$1/$2/reg/${BASE}.reg" && -r "$1/$2/diffmask/${BASE}OFCS_diffmask.fits" ]; then
        ${P_WW} -c ${CONF}/weights.ww\
     		      -WEIGHT_NAMES ${RESULTDIR}/globalweight_${CHIP}.fits,${TEMPDIR}/cosmic_${CHIP}_$$.fits,$1/$2/diffmask/${BASE}OFCS_diffmask.fits,${file}\
		      -WEIGHT_MIN -1e9,-1e9,0.1,0\
		      -WEIGHT_MAX  1e9,0.1,1.1,30000\
		      -WEIGHT_OUTFLAGS	0,16,32,128\
     		      -FLAG_NAMES ""\
     		      -POLY_NAMES "/$1/$2/reg/${BASE}.reg"\
     		      -OUTWEIGHT_NAME ${RESULTDIR}/${BASE}$3.weight.fits\
     		      -OUTFLAG_NAME ""
      elif [ -r "$1/$2/diffmask/${BASE}OFCS_diffmask.fits" ]; then
	${P_WW} -c ${CONF}/weights.ww\
     		      -WEIGHT_NAMES ${RESULTDIR}/globalweight_${CHIP}.fits,${TEMPDIR}/cosmic_${CHIP}_$$.fits,$1/$2/diffmask/${BASE}OFCS_diffmask.fits,${file}\
		      -WEIGHT_MIN -1e9,-1e9,0.1,0\
		      -WEIGHT_MAX  1e9,0.1,1.1,30000\
		      -WEIGHT_OUTFLAGS	0,16,32,128\
     		      -FLAG_NAMES ""\
     		      -OUTWEIGHT_NAME ${RESULTDIR}/${BASE}$3.weight.fits\
     		      -OUTFLAG_NAME ""
      elif [ -r "/$1/$2/reg/${BASE}.reg" ]; then	     
         ${P_WW} -c ${CONF}/weights.ww\
     		      -WEIGHT_NAMES ${RESULTDIR}/globalweight_${CHIP}.fits,${TEMPDIR}/cosmic_${CHIP}_$$.fits,${file}\
		      -WEIGHT_MIN -1e9,-1e9,0\
		      -WEIGHT_MAX  1e9,0.1,30000\
		      -WEIGHT_OUTFLAGS	0,16,128\
     		      -FLAG_NAMES ""\
     		      -POLY_NAMES "/$1/$2/reg/${BASE}.reg"\
     		      -OUTWEIGHT_NAME ${RESULTDIR}/${BASE}$3.weight.fits\
     		      -OUTFLAG_NAME ""
      else 
	 ${P_WW} -c ${CONF}/weights.ww\
     		      -WEIGHT_NAMES ${RESULTDIR}/globalweight_${CHIP}.fits,${TEMPDIR}/cosmic_${CHIP}_$$.fits,${file}\
		      -WEIGHT_MIN -1e9,-1e9,0\
		      -WEIGHT_MAX  1e9,0.1,30000\
		      -WEIGHT_OUTFLAGS	0,16,128\
     		      -FLAG_NAMES ""\
     		      -OUTWEIGHT_NAME ${RESULTDIR}/${BASE}$3.weight.fits\
     		      -OUTFLAG_NAME ""   
      fi

      
      if [ "${RESULTDIR}" != "/$1/WEIGHTS" ]; then
        ln -s ${RESULTDIR}/${BASE}$3.weight.fits /$1/WEIGHTS/${BASE}$3.weight.fits
      fi

      # clean up temporary files
      if [ -f ${TEMPDIR}/cosmic_${CHIP}_$$.fits ]; then
          rm ${TEMPDIR}/cosmic_${CHIP}_$$.fits
      fi
      
      if [ -f ${TEMPDIR}/cosmic.cat_$$ ]; then
          rm ${TEMPDIR}/cosmic.cat_$$
      fi

    done
  }
  test -f ${TEMPDIR}/crw_images_$$ && rm  ${TEMPDIR}/crw_images_$$
done


