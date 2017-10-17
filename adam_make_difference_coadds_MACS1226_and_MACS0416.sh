#!/bin/bash
set -xv

#MACS1226
ic '%1 %2 -' /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_good/coadd.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_all/coadd.fits > /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/BACKMASK/coadd_good-all.fits
ic '%1 %2 -' /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_gabodsid2619/coadd.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_all/coadd.fits > /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/BACKMASK/coadd_gabodsid2619-all.fits
ic '%1 %2 -' /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_gabodsid4060/coadd.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_all/coadd.fits > /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/BACKMASK/coadd_gabodsid4060-all.fits
ic '%1 %2 -' /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_gabodsid4060/coadd.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_gabodsid2619/coadd.fits > /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/BACKMASK/coadd_gabodsid4060-gabodsid2619.fits

#MACS0416
ic '%1 %2 -' /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/coadd_MACS0416-24_good/coadd.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/coadd_MACS0416-24_all/coadd.fits > /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/BACKMASK/coadd_good-all.fits
