#!/bin/bash

# adam (03/05/2015)
# this script now works with ds9 version 4.0 and 4.1 region files

for file in $@; do

    nregions=`awk '($1 !~/(#|global|physical)/){print}' $file | wc -l`

    if [ "$nregions" = "0" ]; then
	echo "Removing $file"
	rm -f $file
    fi
done
