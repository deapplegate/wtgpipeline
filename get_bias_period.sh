#! /bin/bash
#
# Usage: returns the appropriate Bias period
# -mta
#
#

FILE=$1


GABRANGEMIN=(0 902 1403 1666 1988 2525 2703)
GABRANGEMAX=(0 1252 1586 1736 2261 2562 3120)

MIDPOINTS=(0 1327 1626 1862 2393 2632)

ID=`imhead < $FILE | grep GABODSID |awk '{print $2}'`

 
NPER=${#GABRANGEMIN[*]}

for ((x=0; x <= ${NPER}; x++)); do
    if [[ $ID -le ${GABRANGEMAX[x]} && $ID -ge ${GABRANGEMIN[x]} ]]; then
	echo $x
	exit 0;
    fi
done

# WARNING: GABODS ID NOT IN ANY BIAS RANGE. Getting closest.

NPER=${#MIDPOINTS[*]}

for ((x=1; x < ${NPER}; x++)); do
    if [ $ID -le ${MIDPOINTS[x]} ]; then
	echo $x
	exit 0;
    fi
done

echo $NPER
exit 0; 