#!/bin/bash
set -xv

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
fwhm=`${P_DFITS} ${image} | ${P_FITSORT} -d MYSEEING | awk '{print $2}'`
if [ "${fwhm}" == "KEY_N/A" ]; then
	echo "MYSEEING header keyword isn't in " ${image}
	#exit 1;
fi
#END1 ####### Get from the image header file ################################


#START2 ########## use myseeing from CRNitschke pipeline ############################
SUPA_BASE=${3##${cluster}_} #$3=${cluster}_SUPA0125912 (here MACS0416-24_SUPA0125912)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  any  # SUPA_BASE=SUPA0125912
#  of   # SUPA_BASE=SUPA0125912_5
# these # SUPA_BASE=SUPA0125912_5OCF
# works # SUPA_BASE=SUPA0125912_5OCF.fits
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
#END2 ############ use myseeing from CRNitschke pipeline ############################

# IF:
# 	1.) if MYSEEING header keyword is missing
# 	or
# 	2.) if not 0.1<MYSEEING<1.9 or Nelements!=4 or if SUPA_BASE not in CRNitschke_final_${cluster}_*_${filter}.txt
# THEN: 
#	determine the seeing in the coadded image

#START3 ######### the end ##########################################################
fwhm_gt_test=$(echo "${fwhm}>0.1" | bc)
fwhm_lt_test=$(echo "${fwhm}<1.9" | bc)
fwhm_test=$(echo "${fwhm_lt_test}*${fwhm_gt_test}" | bc)
echo "fwhm_test=" $fwhm_test
if [ "${fwhm_test}" = "1" ]; then
	SEEING=$fwhm
else
	echo "adam-Error: MYSEEING header keyword cannot be found! calculating fwhm using get_seeing method."
	# first create a simple SExtractor parameter file. It
	# only contains three entries and is very special for
	# this script. Hence we do not create a new pipeline
	# config file:
	{
	    echo "NUMBER"
	    echo "FWHM_IMAGE"
	    echo "IMAFLAGS_ISO"
	} > ${TEMPDIR}/seeing_sexparam.asc_$$
	
	${P_SEX} /$1/$2/coadd_$3/$5.fits -c ${CONF}/postcoadd.conf.sex \
	           -CATALOG_NAME ${TEMPDIR}/seeing_$$.cat \
	           -FILTER_NAME ${DATACONF}/default.conv\
	           -WEIGHT_IMAGE /$1/$2/coadd_$3/$5.weight.fits \
	           -WEIGHT_TYPE MAP_WEIGHT -FLAG_IMAGE /$1/$2/coadd_$3/$5.flag.fits \
	           -FLAG_TYPE MAX \
	           -DETECT_THRESH 10 -DETECT_MINAREA 10 \
	           -ANALYSIS_THRESH 15\
	           -PARAMETERS_NAME ${TEMPDIR}/seeing_sexparam.asc_$$
	
	${P_LDACCONV}  -i ${TEMPDIR}/seeing_$$.cat -o ${TEMPDIR}/seeing_ldac.cat_$$\
	               -b 1 -c "sex" -f R
	
	${P_LDACFILTER} -i ${TEMPDIR}/seeing_ldac.cat_$$ \
	                -o ${TEMPDIR}/seeing_ldac_filt.cat_$$ -c "(IMAFLAGS_ISO<16);"
	
	${P_LDACTOASC} -b -i ${TEMPDIR}/seeing_ldac_filt.cat_$$ -t OBJECTS\
	               -k FWHM_IMAGE > ${TEMPDIR}/seeing_$$.asc
	
	NLINES=`wc ${TEMPDIR}/seeing_$$.asc | awk '{print $1}'`
	SEEING=`${P_GAWK} 'BEGIN {
	                       binsize=10./'${NLINES}';
	                       if(binsize<0.01) { binsize=0.01 } 
	          	           nbins=int(((3.0-0.3)/binsize)+0.5);
	                       for(i=1; i<=nbins; i++) { bin[i]=0 }
	                   }
	                   { 
	                       if(($1*'${PXSCALE}' > 0.3) && ($1*'${PXSCALE}' < 3.0))
	                       { 
	                           actubin=int(($1*'${PXSCALE}'-0.3)/binsize);
			                   bin[actubin]+=1; 
	                       }
	                   }
		               END {
	                       max=0; k=0 
			               for(i=1;i<=nbins; i++)
			               {
			                   if(bin[i]>max)
			                   { 
			                       max=bin[i];
			                       k=i;
			                   }
			               }
			               print 0.3+k*binsize
	                   }' ${TEMPDIR}/seeing_$$.asc`
	rm -f ${TEMPDIR}/seeing_sexparam.asc_$$
	rm -f ${TEMPDIR}/seeing_$$.cat
	rm -f ${TEMPDIR}/seeing_$$.asc
	rm -f ${TEMPDIR}/seeing_ldac.cat_$$
	rm -f ${TEMPDIR}/seeing_ldac_filt.cat_$$
fi
#END 3 ########### the end ##########################################################


#EXAMPLE: write keywords in header
# first make sure that EXPTIME, SEEING and GAINEFF are 'real' number, i.e.
# they end with a ".0" if they are represented by integers right now.
# This ensures that FITS keywords are treated as FLOATS (and not errorneously
# as ints) afterwards.
SEEING=`echo ${SEEING} | awk '{if(($1-int($1))<1.0e-06) { print $1".0" } else {print $1}}'`

value ${SEEING}
writekey /$1/$2/coadd_$3/$5.fits SEEING "${VALUE} / measured image Seeing (arcsec)" REPLACE
writekey /$1/$2/coadd_$3/$5.fits SEEINGSE "${VALUE} / measured image Seeing (arcsec)" REPLACE
writekey /$1/$2/coadd_$3/$5.fits MYSEEING "${VALUE} / measured image Seeing (arcsec)" REPLACE
