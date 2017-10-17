#!/bin/bash
set -xv
# splits Subaru Fits extension images into the
# ten chips. Uses the eclipse utilities
# and also updates the image headers

. SUBARU.ini > /tmp/out.tmp 2>&1
. progs.ini > /tmp/out.tmp 2>&1

FILE=$1
OUTPUTDIR=$2
if [ -z ${OUTPUTDIR} ] ; then
	OUTPUTDIR=`dirname $FILE`
fi

BASE=`basename ${FILE} .fits`

if [ -e ${OUTPUTDIR}/${BASE}_2.fits ]; then
	echo "already there...if you want to overwrite, then comment out the exit on the next line"
	exit 0;
fi

${P_FITSSPLIT_ECL} \
    -OUTPUT_DIR ${OUTPUTDIR} \
    ${FILE}
