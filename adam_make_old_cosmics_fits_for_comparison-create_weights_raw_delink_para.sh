#!/bin/bash
set -xv

# $1: main directory
# $2: science dir.
# $3: image extension (ext) on ..._iext.fits (i is the chip number)
#     note that spikefinder images have an additional .sf
# $4: weight directory
# $5: Filter to use for cosmic ray detection (OPTIONAL)
# ${!#}: chips to be processed

. ${INSTRUMENT:?}.ini

REDDIR=`pwd`

#SUPA0154711_3OCF.fits	0.55
# set cosmic ray mask to use:
MASK=${CONF}/cosmic.ret.sex

export WEIGHTSDIR="/u/ki/awright/my_data/SUBARU/Zw2701/W-C-RC/WEIGHTS/"

#adam# this actually does match the value for the 10_3 config
SATLEVEL=${SATURATION:-30000}

OUTIMAGE=oldCRmask_SUPA0154711_3OCF.fits
CHIP=3

file="/u/ki/awright/my_data/SUBARU/Zw2701/W-C-RC/SCIENCE/SUPA0154711_3OCF.fits"

BASE=`basename ${file} OCF.fits`

# first run sextractor to determine the seeing:

fwhm=0.55

conffile=${REDDIR}/cosmic.conf.sex

#adam-SHNT# I believe this is where EyE should go
# first run sextractor to identify cosmic rays:

${P_SEX} ${file} -c ${conffile} -CHECKIMAGE_NAME \
                    ${TEMPDIR}/cosmic_${CHIP}_$$.fits \
                    -FILTER_NAME ${MASK} \
                    -CATALOG_NAME ${TEMPDIR}/cosmic.cat_$$ \
                    -SEEING_FWHM ${fwhm}


# Expand the cosmc ray making:
#adam# expand_cosmics_mask only extends by one pixel (not good enough), this doesn't help the fact that we're actually missing some things entirely
sfdir/expand_cosmics_mask ${TEMPDIR}/cosmic_${CHIP}_$$.fits  ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits
mv ${TEMPDIR}/cosmic_${CHIP}_$$.2.fits  ${OUTIMAGE}
