#!/bin/bash
#adam-BL# . BonnLogger.sh
#adam-BL# . log_start
# ----------------------------------------------------------------
# File Name:           mark_badchips.sh
# Author:              Thomas Erben (terben@astro.uni-bonn.de)
# Last modified on:    22.08.2007
# Description:         Gives specified chips the BADCCD=1 keyword
# Version:             $$VERSION$$
# ----------------------------------------------------------------

# Script history information:
# 
# 02.02.07:
# Script written
#
# 22.08.2007:
# I corrected a bug in treating the command line
# argument for missing chips. This argument can contain
# spaces and hence the variable needs to be quoted.
#
# 10.09.2007:
# The value to be put into the 'BADCCD' header keyword is
# now a command line argument.
#
# 29.10.2007:
# I checked for the wrong number of command line arguments.
# It needs to be '5', not '4'.

# File Inclusions:
. ${INSTRUMENT:?}.ini
. bash_functions.include

# function definitions
function printUsage
{
    echo "SCRIPT NAME:"
    echo -e "    mark_badchips.sh\n"
    echo "SYNOPSIS:"
    echo "    mark_badchips.sh 'main directory'"
    echo "                     'science directory'"
    echo "                     'image ending'"
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
    echo -e "    Thomas Erben (terben@astro.uni-bonn.de)\n"

}

# Handling of program interruption by CRTL-C
trap "echo 'Script $0 interrupted!! Cleaning up and exiting!'; \
      echo 'adam-look | error: Interupted'; \
      exit 1" INT
 
# check validity of command line arguments:
if [ $# -ne 5 ]; then
    printUsage
    #adam-BL# log_status 1 'Invalid Command Line'
    echo 'adam-look | error: Invalid Command Line'
    exit 1
fi

# if a text file is provided for the chips convert
# them to a string so that we can treat the text file
# and the string case in common:

if [ -f "$5" ]; then
    CHIPS=""
    while read CHIP
    do
        CHIPS="${CHIPS} ${CHIP}"
    done < $5
else
    CHIPS="$5"
fi

# and finally do the marking! 
for CHIP in ${CHIPS}
do
    FILES=`find /$1/$2/ -maxdepth 1 -name \*_${CHIP}$3.fits`
    for FILE in ${FILES}
    do
        value "$4"
        writekey ${FILE} BADCCD "${VALUE}" REPLACE
    done
done

#adam-BL# log_status $?
