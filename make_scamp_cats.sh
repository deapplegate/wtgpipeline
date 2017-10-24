#!/bin/bash
set -xv
#adam-does# this runs create_astromcats_scamp_para.sh for DECam
#$1: main directory
#$2: science dir.
#$3: WEIGHTS directory
#$4: chips to work on

#MAINDIR="/gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/A2204/r_DECam/"
#SCIENCEDIR="single_V0.0.2A/"
export cluster=A2204
export INSTRUMENT=DECam
export filter=$1
MAINDIR=/gpfs/slac/kipac/fs1/u/anja/DECAM/CLUSTERSCOLLAB_V0.0.2/${cluster}/${filter}_DECam/
SCIENCEDIR=single_V0.0.2A/
WEIGHTDIR=${SCIENCEDIR}
CHIPS=$2


. ${INSTRUMENT:?}.ini > /tmp/INSTRUMENT.out 2>&1
. ~/wtgpipeline/progs.ini > /tmp/progs.ini.out 2>&1

if [ ! -d "/${MAINDIR}/${SCIENCEDIR}/cat_scamp" ]; then
  mkdir /${MAINDIR}/${SCIENCEDIR}/cat_scamp
fi

for CHIP in ${CHIPS}
do
  ${P_FIND} /${MAINDIR}/${SCIENCEDIR}/ -maxdepth 1 -name \*_${CHIP}[!0-9]\*.sub.fits > ${TEMPDIR}/astromimages_$$
  
  cat ${TEMPDIR}/astromimages_$$ |\
  {
    while read file
    do
      # check for BADCCD; if an image has a BADCCD mark of '1' it is
      # NOT included in the catalogue extraction process

      BADCCD=`${P_DFITS} ${file} | ${P_FITSORT} BADCCD | ${P_GAWK} '($1!="FILE") {print $2}'`

      if [ "${BADCCD}" != "1" ]; then

        BASE=`basename ${file} .sub.fits`
 	if [ -e /${MAINDIR}/${SCIENCEDIR}/cat_scamp/${BASE}.cat ];then
		continue
	fi
	dir=`dirname $file`
	cat_fwhm=${dir%/single_V0.0.2A}/cat/${BASE%_*}.cat
        #
        # now run sextractor to determine the seeing:
	ldactoasc -i ${cat_fwhm} -t FIELDS -b -k SEXSFWHM > seeing_data_$$
	#./adam_seeing_pretest.sh ${file} ${TEMPDIR}/seeing_pretest_$$.log
	if [ "$?" -eq "0" ]; then
		fwhm=`sort -n seeing_data_$$ | awk -f ~/wtgpipeline/median.awk`
		#fwhm=`cat ${TEMPDIR}/seeing_pretest_$$.log`
	else
		${P_SEX2} ${file} -c ${DATACONF}/singleastrom.conf.sex \
				 -CATALOG_NAME ${TEMPDIR}/seeing_$$.cat \
				 -FILTER_NAME ${DATACONF}/default.conv\
				 -CATALOG_TYPE "ASCII" \
				 -DETECT_MINAREA 5 -DETECT_THRESH 5.\
				 -ANALYSIS_THRESH 1.2 \
				 -PARAMETERS_NAME ${DATACONF}/singleastrom.ascii.param.sex \
				 -WEIGHT_IMAGE /${MAINDIR}/${WEIGHTDIR}/${BASE}.weight.fits \
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
		rm -f ${TEMPDIR}/seeing_$$.cat
	fi

	WEIGHT="-WEIGHT_IMAGE /${MAINDIR}/${WEIGHTDIR}/${BASE}.weight.fits -WEIGHT_TYPE MAP_WEIGHT"
	FLAG="-FLAG_IMAGE /${MAINDIR}/${WEIGHTDIR}/${BASE}.flag.fits"

	#adam-old# FLAG='-FLAG_IMAGE ""'
	#adam-old# if [ ${INSTRUMENT} == "SUBARU" ] && [ -f "/${MAINDIR}/${WEIGHTDIR}/${BASE}.flag.fits" ] && [ ${CONFIG} != "10_3" ] && [ ${CONFIG} != "8" ]; then
	#adam-old#     FLAG="-FLAG_IMAGE /${MAINDIR}/${WEIGHTDIR}/${BASE}.flag.fits"
	#adam-old#     WEIGHT='-WEIGHT_IMAGE ""'
	#adam-old# fi

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
        ${P_SEX2} ${file} -c ${DATACONF}/singleastrom.conf.sex\
  		       -CATALOG_NAME /${MAINDIR}/${SCIENCEDIR}/cat_scamp/${BASE}.cat\
  		       -SEEING_FWHM $fwhm \
  		       -PARAMETERS_NAME singleastrom.param.sex_noflags2 \
  		       -DETECT_MINAREA ${MINAREA} -DETECT_THRESH ${THRESH} ${WEIGHT} ${FLAG} \
	               -CHECKIMAGE_TYPE NONE
	               #-CHECKIMAGE_TYPE SEGMENTATION \
	               #-CHECKIMAGE_NAME /${MAINDIR}/${SCIENCEDIR}/cat_scamp/${BASE}.segmentation.fits
  		       #-DETECT_MINAREA ${MINAREA} -DETECT_THRESH ${THRESH} ${WEIGHT} #adam-SHNT#
      fi
    done
  }
done

test -f ${TEMPDIR}/astromimages_$$ && rm -f ${TEMPDIR}/astromimages_$$
rm ~/wtgpipeline/seeing_data_$$
