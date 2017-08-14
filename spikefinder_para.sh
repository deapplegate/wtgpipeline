#!/bin/bash
#
# Wrapper designed to run the diffraction spike finder on a 
# series of images.  -MTA
# Usage:
# ./spikefinder_para.sh  ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA OFCS
#
# $argv[1] = ${SUBARUDIR}/${run}_${filter}
# $argv[2] = SCIENCE
# $argv[3] = SUPA
# $argv[4] = OFCS
# $argv[5] = ${filter}
# ${!#}: chips to be processed
#
# Changing input to allow easy access to the filter. Sorry for the redundancy.
# CVSId : $Id: spikefinder_para.sh,v 1.9 2009-01-22 22:54:59 dapple Exp $
. BonnLogger.sh
. log_start
. ${INSTRUMENT:?}.ini

if [ ! -e ${1}/${2}/diffmask ]; then
    mkdir ${1}/${2}/diffmask
fi


for CHIP in ${!#}
do
    echo ${1}/${2}
    echo ${3}\*_${CHIP}${4}.fits
    ${P_FIND} ${1}/${2} -maxdepth 1 -name ${3}\*_${CHIP}${4}.fits \
	-print > ${TEMPDIR}/spikefinder_$$
    
    cat ${TEMPDIR}/spikefinder_$$ |\
  {
	while read file
	do
	    BASE=`basename ${file} .fits`
	    if [ ! -e ${1}/${2}/diffmask/${BASE}.sf.fits ]; then
		echo ${BASE}
		# Run sextractor for SEGMENTATION and FILDERED images
		${P_SEX} ${file} -c ${CONF}/illumfringe_back.sex -FILTER_NAME ${CONF}/gauss_1.5_3x3.conv\
		    -CHECKIMAGE_TYPE SEGMENTATION,FILTERED   -CHECKIMAGE_NAME ${TEMPDIR}/SEG_$$.fits,${TEMPDIR}/FIL_$$.fits 
		# Run the spikefinder     
		sfdir/spikefinder ${file} ${1}/${2}/diffmask/${BASE}.sp.fits ${5} 
		# prepare the sat and shadow finders    
		LINE=`${P_IMSTATS} ${TEMPDIR}/FIL_$$.fits | grep FIL`
		MEDIAN=`echo $LINE | awk '{print $4}'`
		NSIGMA=`echo $LINE | awk '{print 5*$7}'`

		# find the objects for satfinder
		${P_IC} '%1 0 %2  '${MEDIAN}' '${NSIGMA}' + > ?' $file ${TEMPDIR}/FIL_$$.fits  > ${TEMPDIR}/OBJECTS0_$$.fits
 		${P_IC} '%1 %2 +' ${TEMPDIR}/SEG_$$.fits  ${TEMPDIR}/OBJECTS0_$$.fits > ${TEMPDIR}/OBJECTS1_$$.fits
		    
		sfdir/satfinder ${TEMPDIR}/OBJECTS1_$$.fits  ${1}/${2}/diffmask/${BASE}.sa.fits 
		
		#get the background for shadowfinder...  Needs the basename...
		${P_IC} '%1 -1 %2 0 == ?' $file ${TEMPDIR}/OBJECTS1_$$.fits >   ${TEMPDIR}/BKG_${BASE}_$$.fits
		sfdir/shadowfinder ${TEMPDIR}/BKG_${BASE}_$$.fits  ${1}/${2}/diffmask/${BASE}.sh.fits 

		${P_IC} '%3 %1 %2 * *' ${1}/${2}/diffmask/${BASE}.sp.fits \
		    ${1}/${2}/diffmask/${BASE}.sa.fits\
		    ${1}/${2}/diffmask/${BASE}.sh.fits > ${1}/${2}/diffmask/${BASE}.sf.fits
		rm  ${1}/${2}/diffmask/${BASE}.{sp,sa,sh}.fits
		rm ${TEMPDIR}/{SEG,FIL,OBJECTS?,BKG_${BASE}}_$$.fits
	    fi
	done
 }

    rm ${TEMPDIR}/spikefinder_$$
done



log_status $?
