#!/bin/bash -xv
. BonnLogger.sh
. log_start
# CVSId: $Id: create_astromcats_scampIC_para.sh,v 1.1 2009-06-30 00:01:06 anja Exp $

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
#$3: WEIGHTS directory
#$4: chips to work on

WEIGHTDIR=$3


. ${INSTRUMENT:?}.ini 

if [ ! -d "/$1/$2/cat_scampIC" ]; then
  mkdir /$1/$2/cat_scampIC
fi

echo $4
for CHIP in $4
do
  ${P_FIND} /$1/$2/ -maxdepth 1 -name \*_${CHIP}[!0-9]\*I.fits > ${TEMPDIR}/astromimages_$$
  
  cat ${TEMPDIR}/astromimages_$$ |\
  {
    while read file
    do
      # check for BADCCD; if an image has a BADCCD mark of '1' it is
      # NOT included in the catalogue extraction process

      BADCCD=`${P_DFITS} ${file} | ${P_FITSORT} BADCCD | ${P_GAWK} '($1!="FILE") {print $2}'`

      if [ "${BADCCD}" != "1" ]; then

        BASE=`basename ${file} .fits`
        #
        # now run sextractor to determine the seeing:
        ${P_SEX} ${file} -c ${DATACONF}/singleastrom.conf.sex \
  			 -CATALOG_NAME ${TEMPDIR}/seeing_$$.cat \
  	                 -FILTER_NAME ${DATACONF}/default.conv\
  			 -CATALOG_TYPE "ASCII" \
  			 -DETECT_MINAREA 5 -DETECT_THRESH 5.\
  			 -ANALYSIS_THRESH 1.2 \
  			 -PARAMETERS_NAME ${DATACONF}/singleastrom.ascii.param.sex\
  	                 -WEIGHT_IMAGE /$1/${WEIGHTDIR}/${BASE}.weight.fits\
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

	CONFIG=`${P_DFITS} ${file} | ${P_FITSORT} CONFIG | ${P_GAWK} '($1!="FILE") {print $2}'`
        
	FLAG='-FLAG_IMAGE ""'
	WEIGHT="-WEIGHT_IMAGE /$1/${WEIGHTDIR}/${BASE}.weight.fits -WEIGHT_TYPE MAP_WEIGHT"
	if [ ${INSTRUMENT} == "SUBARU" ] && [ -f /$1/${WEIGHTDIR}/${BASE}.flag.fits ] && [ ${CONFIG} != "10_3" ] && [ ${CONFIG} != "8" ]; then
	    FLAG="-FLAG_IMAGE /$1/${WEIGHTDIR}/${BASE}.flag.fits"
	    WEIGHT='-WEIGHT_IMAGE ""'
	fi

        EXPTIME=`${P_DFITS} ${file} | ${P_FITSORT} EXPTIME | ${P_GAWK} '($1!="FILE") {print int($2)}'`
	FILTER=`${P_DFITS} ${file} | ${P_FITSORT} FILTER | ${P_GAWK} '($1!="FILE") {print $2}'`

        if [ ${EXPTIME} -le 30 ] || [ ${FILTER} == "W-J-U" ] || [ ${INSTRUMENT} == "MEGAPRIME" ] && [ ${EXPTIME} -le 150 ]; then
            THRESH=1
            MINAREA=3
        else
            THRESH=2.5
            MINAREA=3
        fi

        #now run sextractor to extract the objects
        ${P_SEX} ${file} -c ${DATACONF}/singleastrom.conf.sex\
  		       -CATALOG_NAME /$1/$2/cat_scampIC/${BASE}.cat\
  		       -SEEING_FWHM $fwhm \
  		       -DETECT_MINAREA ${MINAREA} -DETECT_THRESH ${THRESH} \
  	               ${FLAG} ${WEIGHT}
        
        rm ${TEMPDIR}/seeing_$$.cat
      fi
    done
  }
done

test -f ${TEMPDIR}/astromimages_$$ && rm ${TEMPDIR}/astromimages_$$


log_status $?
