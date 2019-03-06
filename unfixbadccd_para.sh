#!/bin/bash
set -xv
###############
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# CVSId: $Id: unfixbadccd_para.sh,v 1.2 2009-12-02 22:47:18 anja Exp $
##########################################################
##########################################################
# Find images with 0 weight, make sure BADCCD is set to 1
###########################################################
. progs.ini > /tmp/progs.out 2>&1
. bash_functions.include > /tmp/progs.out 2>&1

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

    ${P_IMSTATS} `ls ${weightdir}/*${chip}${ext}.weight.fits` | awk '($1 !~ /^#/) {print $1,$2,$3,$4,$5,$6}' > unfixbadccd_stats_$$

    {
	while read weightfile mode lquart median uquart mean; do

	    if [ "${mode}" = "0.00" ] && [ "${lquart}" = "0.00" ] \
		&& [ "${median}" = "0.00" ] && [ "${uquart}" = "0.00" ] && [ "${mean}" != "0.00" ]; then
		
		base=`basename ${weightfile} .weight.fits`
		image=${sciencedir}/${base}.fits
		
		if [ -f  ${image} ]; then

		    badccd=`dfits ${image} | fitsort -d BADCCD | awk '{print $2}'`
		    if [ "${badccd}" == "1" ]; then
		    
			echo "Un-Marking ${image} as  BADCCD = 1"
			fthedit ${image} BADCCD delete

			badchips="${badchips} ${image}"
		    fi
		fi
	    fi
	done
    } < unfixbadccd_stats_$$

    rm -f unfixbadccd_stats_$$

done

#adam-BL# log_status 0
