#!/bin/bash
set -xv

#images of lowest seeing in each band:
#+21/W-C-IC_2010-02-12/SCIENCE/SUPA0118309_3OCF.fits   #34.5989  0.825
#filter=W-C-RC; run=2006-03-04; BASE=SUPA0046910_6   #52.9601  0.66
#filter=W-C-RC; run=2010-02-12; BASE=SUPA0118336_4   #43.0783  0.57
filter=W-J-B ; run=2010-02-12; BASE=SUPA0118323_7    #12.4808  0.66    170.0  20.0
filter=W-J-V ; run=2010-02-12; BASE=SUPA0118325_8    #27.516   0.615   133.214148132  16.3541212386
filter=W-S-G+; run=2010-04-15; BASE=SUPA0121585_9   #21.9571  0.855   159.401742489  20.4945097486
filter=W-S-I+; run=2010-04-15; BASE=SUPA0121406_2   #52.8357  0.735   66.2430894263  8.51696864052
filter=W-C-IC; run=2011-01-06; BASE=SUPA0128338_3   #45.1415  0.855   77.5339764961  9.96865412093
filter=W-S-Z+; run=2011-01-06; BASE=SUPA0128343_4   #61.3791  0.765   57.0226673249  7.33148579891

#use this command to see how the CR masker is preforming:

ds9 -tile mode column -zscale /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/${filter}_${run}/SCIENCE/${BASE}OCF.fits \
        /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_compare/BBrevised_bthresh*_BBCR_MACS1226+21_${filter}.${BASE}.fits \
	/nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/StarRMout_KeepOrRM-purified_cosmics_MACS1226+21_${filter}.${BASE}.fits \
        /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/${filter}_${run}/SCIENCE_weighted/${BASE}OCF.weighted.fits \
        -scale mode minmax /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_compare/BB_ERASED_bthresh*_BBCR_MACS1226+21_${filter}.${BASE}.fits \
        /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_KeepOrRM-starlike_cosmics_MACS1226+21_${filter}.${BASE}.fits \
        -lock frame image -geometry 2000x2000 & 

xv pltSS_NotStars-k_gt_kmax_MACS1226+21_${filter}_*_${BASE}.png  pltSS_Stars_MACS1226+21_${filter}_*_${BASE}.png &
filter=W-J-B ; run=2010-02-12; BASE=SUPA0118323_7    #12.4808  0.66    170.0  20.0
filter=W-J-V ; run=2010-02-12; BASE=SUPA0118325_8    #27.516   0.615   133.214148132  16.3541212386
filter=W-S-G+; run=2010-04-15; BASE=SUPA0121585_9   #21.9571  0.855   159.401742489  20.4945097486

ds9 -tile mode column -zscale /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/${filter}_${run}/SCIENCE/${BASE}OCF.fits \
        /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_compare/BBrevised_bthresh*_BBCR_MACS1226+21_${filter}.${BASE}.fits \
        -scale mode minmax /nfs/slac/g/ki/ki18/anja/SUBARU/eyes/CRNitschke_output/data_SCIENCE_cosmics/SEGMENTATION_KeepOrRM-starlike_cosmics_MACS1226+21_${filter}.${BASE}.fits \
        -lock frame image -geometry 2000x2000 & 

