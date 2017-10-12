#!/bin/bash
set -xv
#adam-example# ./parallel_manager.sh ./spikefinder_para.sh ${SUBARUDIR}/2009-04-29_W-S-Z+ SCIENCE SUPA OCF W-S-Z+ 2>&1 | tee -a OUT-spikefinder_2009-04-29_W-S-Z+.log
#adam-example# ./parallel_manager.sh ./spikefinder_para.sh ${SUBARUDIR}/2010-03-12_W-S-I+ SCIENCE SUPA OCF W-S-I+
#adam-example# ./spikefinder_para.sh  ${SUBARUDIR}/${run}_${filter} SCIENCE SUPA OCF
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
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start

. ${INSTRUMENT:?}.ini > /tmp/instrum.out 2>&1
. progs.ini > /tmp/progs.out 2>&1
if [ ! -e "${1}/${2}/diffmask" ]; then
    mkdir "${1}/${2}/diffmask"
fi

for CHIP in ${!#}
do
    echo "${1}/${2}"
    echo "${3}\*_${CHIP}${4}.fits"
    ${P_FIND} "${1}/${2}" -maxdepth 1 -name "${3}*_${CHIP}${4}.fits" \
	-print > ${TEMPDIR}/spikefinder_$$


    cat ${TEMPDIR}/spikefinder_$$ |\
  {
	while read file
	do
	    BASE=`basename ${file} .fits`
	    if [ ! -e "${1}/${2}/diffmask/${BASE}.sf.fits" ]; then
		echo ${BASE}
		# Run sextractor for SEGMENTATION and FILDERED images
		${P_SEX} ${file} -c ${CONF}/illumfringe_back.sex -FILTER_NAME ${CONF}/gauss_1.5_3x3.conv \
		    -CHECKIMAGE_TYPE SEGMENTATION,FILTERED   -CHECKIMAGE_NAME "${TEMPDIR}/SEG_$$.fits","${TEMPDIR}/FIL_$$.fits"
		# Run the spikefinder     
		sfdir/spikefinder "${file}" "${1}/${2}/diffmask/${BASE}.sp.fits" "${5}"
		# prepare the sat and shadow finders    
		LINE=`${P_IMSTATS} ${TEMPDIR}/FIL_$$.fits | grep FIL`
		MEDIAN=`echo $LINE | awk '{print $4}'`
		NSIGMA=`echo $LINE | awk '{print 5*$7}'`

		# find the objects for satfinder
		${P_IC} '%1 0 %2  '${MEDIAN}' '${NSIGMA}' + > ?' "${file}" "${TEMPDIR}/FIL_$$.fits"  > "${TEMPDIR}/OBJECTS0_$$.fits"
 		${P_IC} '%1 %2 +' "${TEMPDIR}/SEG_$$.fits" "${TEMPDIR}/OBJECTS0_$$.fits" > "${TEMPDIR}/OBJECTS1_$$.fits"

		sfdir/satfinder "${TEMPDIR}/OBJECTS1_$$.fits" "${1}/${2}/diffmask/${BASE}.sa.fits"

		#get the background for shadowfinder...  Needs the basename...
		if [ "${CHIP}" -gt "5" ]; then
			${P_IC} '%1 -1 %2 0 == ?' "${file}" "${TEMPDIR}/OBJECTS1_$$.fits" > "${TEMPDIR}/BKG_${BASE}_$$.fits"
			sfdir/shadowfinder "${TEMPDIR}/BKG_${BASE}_$$.fits" "${1}/${2}/diffmask/${BASE}.sh.fits"

			${P_IC} '%3 %1 %2 * *' "${1}/${2}/diffmask/${BASE}.sp.fits" \
			    "${1}/${2}/diffmask/${BASE}.sa.fits" \
			    "${1}/${2}/diffmask/${BASE}.sh.fits" > "${1}/${2}/diffmask/${BASE}.sf.fits"
			#rm -f ${1}/${2}/diffmask/${BASE}.{sp,sa}.fits
			echo "rm -f ${1}/${2}/diffmask/${BASE}.{sp,sa,sh}.fits" >> tmp_$$_rm_files.log
			echo "${1}/${2}/diffmask/${BASE}.sh.fits" >> tmp_Zband_chip6.todo
			rm -f ${TEMPDIR}/{SEG,FIL,OBJECTS?,BKG_${BASE}}_$$.fits
		else
			${P_IC} '%1 %2 *' "${1}/${2}/diffmask/${BASE}.sp.fits" \
			    "${1}/${2}/diffmask/${BASE}.sa.fits" > "${1}/${2}/diffmask/${BASE}.sf.fits"
			echo "rm -f ${1}/${2}/diffmask/${BASE}.{sp,sa}.fits" >> tmp_$$_rm_files.log
			rm -f ${TEMPDIR}/{SEG,FIL,OBJECTS?}_$$.fits
		fi
	    fi
	done
 }

    rm -f ${TEMPDIR}/spikefinder_$$
done



#adam-BL# log_status $?
