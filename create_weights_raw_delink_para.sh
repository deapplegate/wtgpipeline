#!/bin/bash
set -xv
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
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
#
# 10.04.2008:  AvdL
# edited so that 'spikefinder' masks can be used
#
# 01.07.2008: (AvdL)
# removed link structure
#
#adam: changed filter AGAIN

# $Id: create_weights_raw_delink_para.sh,v 1.9 2010-02-18 02:50:18 dapple Exp $

# $1: main directory
# $2: science dir.
# $3: image extension (ext) on ..._iext.fits (i is the chip number)
#     note that spikefinder images have an additional .sf
# $4: weight directory
# $5: Filter to use for cosmic ray detection (OPTIONAL)
# ${!#}: chips to be processed

. ${INSTRUMENT:?}.ini

REDDIR=`pwd`

# set cosmic ray mask to use:
MASK=${CONF}/cosmic.ret.sex

export WEIGHTSDIR=${1}/${4}

#adam# this actually does match the value for the 10_3 config
SATLEVEL=${SATURATION:-30000}

if [ $# -eq 6 ]; then
   MASK=$5
fi

for CHIP in ${!#}
do
  ${P_FIND} $1/$2/ -maxdepth 1 -name \*_${CHIP}$3.fits \
            -print > ${TEMPDIR}/crw_images_$$

  FILE=`${P_GAWK} '(NR==1) {print $0}' ${TEMPDIR}/crw_images_$$`


#  fi
  
  cat ${TEMPDIR}/crw_images_$$ |\
  {
    while read file
    do
      BASE=`basename ${file} $3.fits`

      # first run sextractor to determine the seeing:
      ${P_SEX} ${file} -c ${DATACONF}/singleastrom.conf.sex \
			 -CATALOG_NAME ${TEMPDIR}/seeing_$$.cat \
	                 -FILTER_NAME ${DATACONF}/default.conv\
			 -CATALOG_TYPE "ASCII" \
			 -DETECT_MINAREA 5 -DETECT_THRESH 5.\
			 -ANALYSIS_THRESH 1.2 \
			 -PARAMETERS_NAME ${DATACONF}/singleastrom.ascii.param.sex 

      NLINES=`wc ${TEMPDIR}/seeing_$$.cat | ${P_GAWK} '{print $1}'`
      fwhm=`${P_GAWK} 'BEGIN {binsize=10./'${NLINES}'; 
			  nbins=int(((3.0-0.3)/binsize)+0.5);
			  for(i=1; i<=nbins; i++) bin[i]=0}
			 { if(($3*'${PIXSCALE}' > 0.3) && ($3*'${PIXSCALE}' < 3.0)) 
                         {
			     actubin=int(($3*'${PIXSCALE}'-0.3)/binsize);
			     bin[actubin]+=1; 
                         }
                       }
		         END {max=0; k=0 
			 for(i=1;i<=nbins; i++)
			 {
			   if(bin[i]>max)
			   { 
			     max=bin[i];
			     k=i;
			   }
			 }
			 print 0.3+k*binsize}' ${TEMPDIR}/seeing_$$.cat`

      if [ "A${fwhm}" = "A0.0" ]; then
	  fwhm=1.0
      fi

      undersampl=`${P_GAWK} 'BEGIN{if('${fwhm}'<0.5) print 1; else print 0}'`

      if [ ${undersampl} -eq 1 ]; then
	  conffile="${CONF}/cosmic.conf.sex -DETECT_THRESH 10"
      else
	  conffile=${REDDIR}/cosmic.conf.sex
      fi

      #adam-SHNT# I believe this is where EyE should go
      # first run sextractor to identify cosmic rays:

      ${P_SEX} ${file} -c ${conffile} -CHECKIMAGE_NAME \
                          ${TEMPDIR}/cosmic_${CHIP}_$$.fits \
                          -FILTER_NAME ${MASK} \
                          -CATALOG_NAME ${TEMPDIR}/cosmic.cat_$$ \
                          -SEEING_FWHM ${fwhm}


	# Expand the cosmc ray making:
	#adam# expand_cosmics_mask only extends by one pixel (not good enough), this doesn't help the fact that we're actually missing some things entirely
       sfdir/expand_cosmics_mask ${TEMPDIR}/cosmic_${CHIP}_$$.fits  ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits
       mv ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits  ${TEMPDIR}/cosmic_${CHIP}_$$.fits 
      # create ww config file on the fly

      if [ -r "$1/$2/diffmask/${BASE}$3.sf.fits" ]; then
	  echo "WEIGHT_NAMES ${WEIGHTSDIR}/globalweight_${CHIP}.fits,${TEMPDIR}/cosmic_${CHIP}_$$.fits,${file},/$1/$2/diffmask/${BASE}$3.sf.fits"                               >  ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_MIN -1e9,-1e9,-${SATLEVEL},0.1"       >> ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_MAX 1e9,0.1,${SATLEVEL},1"       >> ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_OUTFLAGS 0,1,2,4"       >> ${TEMPDIR}/${BASE}.ww_$$
      else
	  echo "WEIGHT_NAMES ${WEIGHTSDIR}/globalweight_${CHIP}.fits,${TEMPDIR}/cosmic_${CHIP}_$$.fits,${file}" \
	                                          >  ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_MIN -1e9,-1e9,-${SATLEVEL}"           >> ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_MAX 1e9,0.1,${SATLEVEL}"         >> ${TEMPDIR}/${BASE}.ww_$$
	  echo "WEIGHT_OUTFLAGS 0,1,2"          >> ${TEMPDIR}/${BASE}.ww_$$
      fi
      #
      echo "FLAG_NAMES ${WEIGHTSDIR}/globalflag_${CHIP}.fits"                        >> ${TEMPDIR}/${BASE}.ww_$$
      echo 'FLAG_MASKS "0x42"'                        >> ${TEMPDIR}/${BASE}.ww_$$
      echo 'FLAG_WMASKS "0x42"'                       >> ${TEMPDIR}/${BASE}.ww_$$
      echo 'FLAG_OUTFLAGS "32,64"'                     >> ${TEMPDIR}/${BASE}.ww_$$
      #
      if [ -s "/$1/$2/reg/${BASE}.reg" ]; then
        echo "POLY_NAMES /$1/$2/reg/${BASE}.reg"  >> ${TEMPDIR}/${BASE}.ww_$$
        echo "POLY_OUTFLAGS 256"                    >> ${TEMPDIR}/${BASE}.ww_$$
      else
        echo 'POLY_NAMES ""'                      >> ${TEMPDIR}/${BASE}.ww_$$
        echo 'POLY_OUTFLAGS ""'                   >> ${TEMPDIR}/${BASE}.ww_$$
      fi
      #
      echo "OUTWEIGHT_NAME ${WEIGHTSDIR}/${BASE}$3.weight.fits"  >> ${TEMPDIR}/${BASE}.ww_$$
      echo "OUTFLAG_NAME ${WEIGHTSDIR}/${BASE}$3.flag.fits"  >> ${TEMPDIR}/${BASE}.ww_$$
      
      # then run weightwatcher

      ${P_WW} -c ${TEMPDIR}/${BASE}.ww_$$
      rm -f ${TEMPDIR}/${BASE}.ww_$$

      # clean up temporary files
      if [ -f ${TEMPDIR}/cosmic_${CHIP}_$$.fits ]; then
          rm -f ${TEMPDIR}/cosmic_${CHIP}_$$.fits
      fi
      
      if [ -f ${TEMPDIR}/cosmic.cat_$$ ]; then
          rm -f ${TEMPDIR}/cosmic.cat_$$
      fi

    done
  }
  test -f ${TEMPDIR}/crw_images_$$ && rm -f  ${TEMPDIR}/crw_images_$$
done


#adam-BL# log_status $?
