#!/bin/bash
set -xv
#adam-example# ./adam_simplecat_from_image.sh ~/data/MACS1115+01/W-J-B_2009-04-29/SCIENCE/SUPA0109617_2OCF.fits SUPA0109617_2OCF.cat
. ~/bonnpipeline/progs.ini > /tmp/progs.out 2>&1
. ~/bonnpipeline/SUBARU.ini > /tmp/SUBARU.out 2>&1
sex $1 -c /u/ki/awright/InstallingSoftware/pythons/sextractimtools/seeing_clearly.sex.config \
  -PARAMETERS_NAME /u/ki/awright/data/BFcorr/2017_test/sex.params_stars \
  -CATALOG_NAME $2 \
  -CATALOG_TYPE FITS_LDAC \
  -DETECT_MINAREA 2 -ANALYSIS_THRESH 5.0 -DETECT_THRESH 5.0
