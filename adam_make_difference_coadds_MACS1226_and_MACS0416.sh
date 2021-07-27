#!/bin/bash
set -xv

#MACS1226
ic '%1 %2 -' /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_good/coadd.fits /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_all/coadd.fits > /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/BACKMASK/coadd_good-all.fits
ic '%1 %2 -' /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_gabodsid2619/coadd.fits /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_all/coadd.fits > /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/BACKMASK/coadd_gabodsid2619-all.fits
ic '%1 %2 -' /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_gabodsid4060/coadd.fits /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_all/coadd.fits > /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/BACKMASK/coadd_gabodsid4060-all.fits
ic '%1 %2 -' /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_gabodsid4060/coadd.fits /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_gabodsid2619/coadd.fits > /u/ki/awright/data/MACS1226+21/W-C-RC/SCIENCE/BACKMASK/coadd_gabodsid4060-gabodsid2619.fits

#MACS0416
ic '%1 %2 -' /u/ki/awright/data/MACS0416-24/W-C-RC/SCIENCE/coadd_MACS0416-24_good/coadd.fits /u/ki/awright/data/MACS0416-24/W-C-RC/SCIENCE/coadd_MACS0416-24_all/coadd.fits > /u/ki/awright/data/MACS0416-24/W-C-RC/SCIENCE/BACKMASK/coadd_good-all.fits
