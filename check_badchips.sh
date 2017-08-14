#!/bin/bash -u
. BonnLogger.sh
. log_start
# ----------------------------------------------------------------
# File Name:           check_badchips.sh
# Author:              Thomas Erben (terben@astro.uni-bonn.de)
# Last modified on:    02.02.2007
# Description:         checks whether there are 'bad' chips in a set coaddition
# Version:             $$VERSION$$
# ----------------------------------------------------------------

# Script history information:
# 
# 02.02.07:
# Script written

# File Inclusions:
. ${INSTRUMENT:?}.ini

# function definitions
function printUsage
{
    echo "SCRIPT NAME:"
    echo -e "    check_badchips.sh\n"
    echo "SYNOPSIS:"
    echo "    check_badchips.sh 'main directory'"
    echo "                      'science directory'"
    echo "                      'image ending'"
    echo "                      'coadd identifier'"
    echo -e "                      'output file'\n"
    echo "DESCRIPTION:"
    echo "    The script identifies 'bad' chips in a set coaddition,"
    echo "    A chip is considered as bad if no image with that chip"
    echo "    is part of the coaddition. The identified chips are written"
    echo -e "    one at each line in the file specified as fith argument.\n"
    echo "    The script is mainly used to identify missing chips in"
    echo "    coadditions of our CFHTLS-Wide reference i-band image."
    echo "    Because we use the i-band to extract an astrometric"
    echo "    catalogue for the other colours we need to identify"
    echo "    missing regions in this reference frame and to subsequently"
    echo "    mark them in the other colours (script mark_badchips.sh)."
    echo "    This procedure works because all colours of a pointing"
    echo -e "    are obtained at exactly the same coordinates.\n"
    echo "EXAMPLES:"
    echo -e "    check_badchips.sh /raid2/thomas/CFHTLS/ W1p2p3 C.sub badchips.txt\n"  
    echo "AUTHOR"
    echo -e "    Thomas Erben (terben@astro.uni-bonn.de)\n"

}

# Handling of program interruption by CRTL-C
trap "echo 'Script $0 interrupted!! Cleaning up and exiting!'; log_status 0; \
      exit 0" INT
 
# check validity of command line arguments:
if [ $# -ne 5 ]; then
    printUsage
    log_status 1
    exit 1
fi

# if a file with the name of the output file is already present
# we delete it without asking!
test -f $5 && rm $5

i=1
while [ ${i} -le ${NCHIPS} ]
do
    NIMAGES=`find /$1/$2/coadd_$4/ -name \*_${i}$3.fits | wc -w`
    #
    if [ ${NIMAGES} -lt 1 ]; then
        echo ${i} >> $5
    fi
    i=$(( $i + 1 )) 
done

test -f $5 && echo "Bad chips identified in /$1/$2/coadd_$4/ !"

log_status $?


