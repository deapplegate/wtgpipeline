#!/bin/bash -v

#example# header_key=`${P_DFITS} ${image} | ${P_FITSORT} -d header_key | awk '{print $2}'`
#example# if [ "${header_key}" == "KEY_N/A" ]; then
#example# 	echo "header_key=" $header_key
#example# 	exit 1;
#example# fi

#START1 ##### Get from the image header file ################################
#fwhm=`${P_DFITS} ${image} | ${P_FITSORT} -d SEEING | awk '{print $2}'`
#fwhmSE=`${P_DFITS} ${image} | ${P_FITSORT} -d SEEINGSE | awk '{print $2}'`
#MYfwhm=`${P_DFITS} ${image} | ${P_FITSORT} -d MYSEEING | awk '{print $2}'`
#fwhm_gt_test=$(echo "${MYfwhm}>0.1" | bc)
#fwhm_lt_test=$(echo "${MYfwhm}<1.9" | bc)                                                                                    
#fwhm_test=$(echo "${fwhm_lt_test}*${fwhm_gt_test}" | bc)
#echo "fwhm_test=" $fwhm_test
#if [ "${fwhm_test}" = "1" ]; then
#	fwhm=$MYfwhm
#	fwhmSE=$MYfwhm
#fi

image=$1
outfile=$2

. ${INSTRUMENT:?}.ini > /tmp/INSTRUMENT.out 2>&1

fwhm=`${P_DFITS} ${image} | ${P_FITSORT} -d MYSEEING | awk '{print $2}'`
if [ "${fwhm}" == "KEY_N/A" ]; then
	echo "MYSEEING header keyword isn't in " ${image}
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#  any  # SUPA_BASE=SUPA0125912
	#  of   # SUPA_BASE=SUPA0125912_5
	# these # SUPA_BASE=SUPA0125912_5OCF
	# works # SUPA_BASE=SUPA0125912_5OCF.fits
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	basename $image .fits >> /tmp/tmp.log
	#old#SUPA_BASE=${3##${cluster}_} #$3=${cluster}_SUPA0125912 (here MACS0416-24_SUPA0125912)
	SUPA_BASE=`sed 's/_[0-9]/\ /' /tmp/tmp.log | awk '{print $1}'`
	echo "SUPA_BASE=" $SUPA_BASE
	rms_fwhm_dt_ft=( `grep -h $SUPA_BASE /u/ki/awright/bonnpipeline/CRNitschke_final_${cluster}_*_${filter}.txt | head -n 1 | awk '{print $2, $3, $4, $5}'`)
	Nelements=${#rms_fwhm_dt_ft[@]}
	if [ ${Nelements} -eq 4 ]; then
		fwhm=${rms_fwhm_dt_ft[1]}
	else
		echo "adam-Error: something wrong with rms_fwhm_dt_ft its supposed to be 4 elements long, but Nelements=" $Nelements
		echo "adam-Error: rms_fwhm_dt_ft=" ${rms_fwhm_dt_ft[@]}
		exit 1;
	fi  
	echo "MYSEEING has: fwhm=" $fwhm #if not 0.1<MYSEEING<1.9 or Nelements!=4 then use the crappy method!
fi

# IF:
# 	1.) if MYSEEING header keyword is missing
# 	or
# 	2.) if not 0.1<MYSEEING<1.9 or Nelements!=4 or if SUPA_BASE not in CRNitschke_final_${cluster}_*_${filter}.txt
# THEN: 
#	determine the seeing in the coadded image

fwhm_gt_test=$(echo "${fwhm}>0.1" | bc)
fwhm_lt_test=$(echo "${fwhm}<1.9" | bc)
fwhm_test=$(echo "${fwhm_lt_test}*${fwhm_gt_test}" | bc)
echo "fwhm_test=" $fwhm_test
if [ "${fwhm_test}" = "1" ]; then
	#SEEING=$fwhm
	echo ${fwhm} > ${outfile}
	exit 0
else
	exit 1
fi
