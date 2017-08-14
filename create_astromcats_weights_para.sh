#!/bin/bash -xv
. BonnLogger.sh
. log_start
# CVSId: $Id: create_astromcats_weights_para.sh,v 1.12 2010-02-18 02:49:45 dapple Exp $

# the scripts creates catalogs used for astrometry with the
# ASTROMETRIX tool. To create clean catalogs we use the
# WEIGHT maps. We run SExtractor two times: The first run to 
# determine a reasonable value for the image seeing that
# is used in the second run.

#
# 28.04.2006:
# - I commented the creation of 'clean' catalogs (all objects with
#   a SExtractor flag larger than 1 filtered from the raw detections).
#   Those catalogs are currently not used within the pipeline
# - I removed the errorneous removal of a temporary catalogue
#
# 29.09.2006:
# CCDs which are marked as BAD (keyword BADCCD) are not included
# in the catalogue extraction process.
#
# 01.08.2007:
# some cleaning of not needed temporary files added

#$1: main directory
#$2: science dir.
#$3: image extension (ext) on ..._iext.fits (i is the chip number)
#$4: WEIGHTS directory
#$5: image extension for weight images 
#$6: chips to work on


. ${INSTRUMENT:?}.ini 

if [ ! -d "/$1/$2/cat" ]; then
  mkdir /$1/$2/cat
fi

if [ ! -d "/$1/$2/cat" ]; then
  log_status 2 "Cannot write to directory!"
  exit 2
fi


echo $6
for CHIP in $6
do
  ${P_FIND} /$1/$2/ -maxdepth 1 -name \*_${CHIP}$3.fits > ${TEMPDIR}/astromimages_$$
  
  cat ${TEMPDIR}/astromimages_$$ |\
  {
    while read file
    do
      # check for BADCCD; if an image has a BADCCD mark of '1' it is
      # NOT included in the catalogue extraction process

      BADCCD=`${P_DFITS} ${file} | ${P_FITSORT} BADCCD | ${P_GAWK} '($1!="FILE") {print $2}'`

      if [ "${BADCCD}" != "1" ]; then

        BASE=`basename ${file} .fits`
        WBASE=`basename ${file} $3.fits`
        #
        # now run sextractor to determine the seeing:
        ${P_SEX} ${file} -c ${DATACONF}/singleastrom.conf.sex \
  			 -CATALOG_NAME ${TEMPDIR}/seeing_$$.cat \
  	                 -FILTER_NAME ${DATACONF}/default.conv\
  			 -CATALOG_TYPE "ASCII" \
  			 -DETECT_MINAREA 5 -DETECT_THRESH 5.\
  			 -ANALYSIS_THRESH 1.2 \
  			 -PARAMETERS_NAME ${DATACONF}/singleastrom.ascii.param.sex \
  	                 -WEIGHT_IMAGE /$1/$4/${WBASE}$5.fits\
                         -WEIGHT_TYPE MAP_WEIGHT
  
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
        
        #now run sextractor to extract the objects
        sex ${file} -c ${DATACONF}/singleastrom.conf.sex\
  		       -CATALOG_NAME /$1/$2/cat/${BASE}.cat \
	               -FLAG_IMAGE "" \
  		       -SEEING_FWHM ${fwhm} \
  		       -DETECT_MINAREA 3 -DETECT_THRESH 3.\
	               -FILTER N -CLEAN N \
  	               -WEIGHT_IMAGE /$1/$4/${WBASE}$5.fits\
                         -WEIGHT_TYPE MAP_WEIGHT
        
        rm ${TEMPDIR}/seeing_$$.cat
      fi
    done
  }
done

test -f ${TEMPDIR}/astromimages_$$ && rm ${TEMPDIR}/astromimages_$$


log_status $?
