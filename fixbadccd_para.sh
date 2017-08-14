#!/bin/bash -xv
###############
. BonnLogger.sh
. log_start
# CVSId: $Id: fixbadccd_para.sh,v 1.4 2009-08-14 20:22:30 anja Exp $
##########################################################
##########################################################
# Find images with 0 weight, make sure BADCCD is set to 1
###########################################################
. progs.ini
. bash_functions.include

rundir=$1
science=$2
weights=$3
ext=$4 #extension
chips=$5

##########################



sciencedir=${1}/${2}
weightdir=${1}/${3}

badchips=""

for chip in ${chips}; do

    imstats `ls ${weightdir}/*${chip}${ext}.weight.fits` | awk '($1 !~ /^#/) {print $1,$2,$3,$4,$5,$6}' > fixbadccd_stats_$$


    {
	while read weightfile mode lquart median uquart mean; do

	    if [ "${mode}" = "0.00" ] && [ "${lquart}" = "0.00" ] \
		&& [ "${median}" = "0.00" ] && [ "${uquart}" = "0.00" ] && [ "${mean}" = "0.00" ]; then
		
		base=`basename ${weightfile} .weight.fits`
		image=${sciencedir}/${base}.fits
		
		if [ -f  ${image} ]; then

		    badccd=`dfits ${image} | fitsort -d BADCCD | awk '{print $2}'`
		    if [ "${badccd}" != "1" ]; then
		    
			echo "Marking ${image} as  BADCCD = 1"
			value "1"
			writekey ${image} BADCCD "${VALUE}" REPLACE

			badchips="${badchips} ${image}"
		    fi
		fi
	    fi
	done
    } < fixbadccd_stats_$$

    rm fixbadccd_stats_$$

done

if [ ! -z "${badchips}" ]; then
    dfits ${badchips} | fitsort -d BADCCD > fixbadccd_check_$$
    {
	while read file badccd; do
	    if [ "${badccd}" != 1 ]; then
		log_status 2 "BADCCD not set: ${file}"
		rm fixbadccd_stats_$$
		exit 2
	    fi
	done
    } < fixbadccd_check_$$
    rm fixbadccd_check_$$
fi

log_status 0
