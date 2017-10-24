#!/bin/bash
set -xv
#adam-BL#. BonnLogger.sh
#adam-BL#. log_start
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


. ${INSTRUMENT:?}.ini  > /tmp/out.out 2>&1

if [ ! -d "/$1/$2/cat" ]; then
  mkdir /$1/$2/cat
fi

if [ ! -d "/$1/$2/cat" ]; then
  #adam-BL#log_status 2 "Can't write to directory!"
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
        # use myseeing!
	rms_fwhm_dt_ft=( `grep -h ${WBASE}OCF /u/ki/awright/wtgpipeline/CRNitschke_final_${cluster}_*_${filter}.txt | awk '{print $2, $3, $4, $5}'`)
	Nelements=${#rms_fwhm_dt_ft[@]}
	if [ ${Nelements} -eq 4 ]; then
		fwhm=${rms_fwhm_dt_ft[1]}
		echo "MYSEEING has: fwhm=" $fwhm
	else
		echo "adam-create_astromcats_weights_para.sh: something wrong with rms_fwhm_dt_ft its supposed to be 4 elements long, but Nelements=" $Nelements
		echo "adam-create_astromcats_weights_para.sh: rms_fwhm_dt_ft=" ${rms_fwhm_dt_ft[@]}
		echo "adam-create_astromcats_weights_para.sh: TRY GETTING THINGS FROM HEADER INSTEAD!"
		#fwhm=`${P_DFITS} ${file} | ${P_FITSORT} -d MYSEEING | awk '{print $2}'`
		#if [ "${fwhm}" == "KEY_N/A" ]; then
		#	echo "MYSEEING header keyword isn't in " ${file}
		#	fwhm=`${P_DFITS} ${file} | ${P_FITSORT} -d SEEING | awk '{print $2}'`
		#	if [ "${fwhm}" == "KEY_N/A" ]; then
		#		echo "adam-Error in create_astromcats_weights_para.sh: SEEING header keyword and MYSEEING header keyword isn't in " ${file}
		#		#exit 1;
		#	fi
		#fi
		#echo "MYSEEING (or SEEING if MYSEEING is unavailable): fwhm=" $fwhm
	fi
	if [ "${fwhm}" == "KEY_N/A" ]; then                                                                                                                                                                   
		fwhm_test="0"
	else
		echo "SEEING or MYSEEING: fwhm=" $fwhm
		fwhm_gt_test=$(echo "${fwhm}>0.1" | bc)
		fwhm_lt_test=$(echo "${fwhm}<1.9" | bc)
		fwhm_test=$(echo "${fwhm_lt_test}*${fwhm_gt_test}" | bc)
	fi
	echo "fwhm_test=" $fwhm_test

	#fwhm_gt_test=$(echo "${fwhm}>0.1" | bc)
	#fwhm_lt_test=$(echo "${fwhm}<1.9" | bc)
	#fwhm_test=$(echo "${fwhm_lt_test}*${fwhm_gt_test}" | bc)
	#echo "fwhm_test=" $fwhm_test
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
	getfwhm=`${P_GAWK} 'BEGIN {binsize=10./'${NLINES}'; 
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
	
	if [ "A${getfwhm}" = "A0.0" ]; then
	  getfwhm=1.0
	fi
	rm -f ${TEMPDIR}/seeing_$$.cat

	getfwhm_gt_test=$(echo "${getfwhm}>0.1" | bc)
	getfwhm_lt_test=$(echo "${getfwhm}<1.9" | bc)
	getfwhm_test=$(echo "${getfwhm_lt_test}*${getfwhm_gt_test}" | bc)

	## append to header
	if [ "${getfwhm_test}" == "1" ]; then
		/u/ki/awright/InstallingSoftware/pythons/header_key_add.py ${file} "GETSEEING=${getfwhm}"
	fi
	if [ "${fwhm_test}" == "1" ]; then
		/u/ki/awright/InstallingSoftware/pythons/header_key_add.py ${file} "MYSEEING=${fwhm}"
	fi

	## choose which fwhm to use
	if [ "${getfwhm_test}" == "1" ]; then
		usefwhm=${getfwhm}
		echo "adam: using get_seeing in create_astromcats_weights_para.sh: ${usefwhm} (MYSEEING=${fwhm} and GETSEEING=${getfwhm})"

	elif [ "${fwhm_test}" == "1" ]; then
		usefwhm=${fwhm}
		echo "adam: using MYSEEING in create_astromcats_weights_para.sh: ${usefwhm} (MYSEEING=${fwhm} and GETSEEING=${getfwhm})"
	else
		echo "adam-Error: neither get_seeing or MYSEEING in create_astromcats_weights_para.sh runs properly"
		exit 2;
	fi

        #now run sextractor to extract the objects
        sex ${file} -c ${DATACONF}/singleastrom.conf.sex\
  		       -CATALOG_NAME /$1/$2/cat/${BASE}.cat \
	               -FLAG_IMAGE "" \
  		       -SEEING_FWHM ${usefwhm} \
  		       -DETECT_MINAREA 3 -DETECT_THRESH 3.\
	               -FILTER N -CLEAN N \
  	               -WEIGHT_IMAGE /$1/$4/${WBASE}$5.fits\
                       -WEIGHT_TYPE MAP_WEIGHT
        
      fi
    done
  }
done

test -f ${TEMPDIR}/astromimages_$$ && rm -f ${TEMPDIR}/astromimages_$$


#adam-BL#log_status $?
