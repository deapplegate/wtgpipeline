#!/bin/bash
set -xv
echo "1 $1: main directory"
echo "2 $2: science dir."
echo "3 $3: image extension (ext) on ..._iext.fits (i is the chip number) note that spikefinder images have an additional .sf"
echo "4 $4: weight directory"
echo "5 $5: Filter to use for cosmic ray detection (OPTIONAL)"
echo "!# ${!#}: chips to be processed"
