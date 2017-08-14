#!/bin/bash
. BonnLogger.sh
. log_start
# CVSId: $Id: mark_badimages.sh,v 1.3 2010-04-16 23:30:54 dapple Exp $
# ----------------------------------------------------------------
# File Name:           mark_badimages.sh
# Author:              Anja von der Linden
# Last modified on:    09.02.2009
# Description:         Marks whole images with BADCCD
# Version:             $$VERSION$$
# ----------------------------------------------------------------

# This script is based on mark_badchips.sh , but marks whole
# images.

# Script history information:
# 
# 09.02.09:
# Script written

# File Inclusions:
. progs.ini
. bash_functions.include

# function definitions
function printUsage
{
    echo "SCRIPT NAME:"
    echo -e "    mark_badimags.sh\n"
    echo "SYNOPSIS:"
    echo "    mark_badimags.sh 'main directory'"
    echo "                     'science directory'"
    echo "                     'value of BADCCD keyword'"
    echo -e "                     'text file or chip list'\n"
    echo "DESCRIPTION:"
    echo "    The script marks specified chips as bad by setting the"
    echo -e "    header keyword BADCCD to the value given as third"
    echo "    command line argument."
    echo "    If the chips to be marked are given in a text file, that"
    echo "    file has to contain a chip number on each line and nothing"
    echo "    else. Alternatively the chip numbers can be given as a"
    echo -e "    simple string.\n"
    echo "EXAMPLES:"
    echo "    mark_badchips.sh /raid2/thomas/CFHTLS/ i C badchips.txt"  
    echo "    mark_badchips.sh /raid2/thomas/CFHTLS/ i C \"21 35\""  
    echo "AUTHOR"
    echo -e "    Anja von der Linden \n"

}

# Handling of program interruption by CRTL-C
trap "echo 'Script $0 interrupted!! Cleaning up and exiting!'; \
      log_status 0 'Interupted'; \
      exit 0" INT
 
# check validity of command line arguments:
if [ $# -ne 4 ]; then
    printUsage
    log_status 1 'Invalid Command Line'
    exit 1
fi

# if a text file is provided for the chips convert
# them to a string so that we can treat the text file
# and the string case in common:

if [ -f $4 ]; then
    echo "read from $4"
    IMAGES=""
    while read IMAGE
    do
        IMAGES="${IMAGES} ${IMAGE}"
    done < $4
else
    IMAGES="$4"
fi

# and finally do the marking! 
for IMAGE in ${IMAGES}
do
    FILES=`find /$1/$2/ -maxdepth 1 -name ${IMAGE}\*.fits`
    for FILE in ${FILES}
    do
        echo "Marking ${FILE} as  BADCCD = $3"
        value "$3"
        writekey ${FILE} BADCCD "${VALUE}" REPLACE
    done
done

log_status $?
