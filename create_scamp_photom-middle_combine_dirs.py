#!/bin/bash
set -xv

#cd ~/data/MACS1115+01/W-C-RC/SCIENCE/
#ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-C-RC/SCIENCE/SUPA*I.fits .
#ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-C-RC/SCIENCE/SUPA*I.sub.fits .
#cd cat_scampIC/
#ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-C-RC/SCIENCE/cat_scampIC/SUPA*I.cat .
##rename 's/OCFSI/OCFSRI/g' SUPA0019*.cat
#cd ../headers_scamp_SDSS-R6/
#cp /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-C-RC/SCIENCE/headers_scamp_SDSS-R6/SUPA*.head .

## now combine the astrom_photom_scamp_SDSS-R6 stuff!
#find . -name "astrom_photom_scamp_SDSS-R6"

#ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-J-V/SCIENCE/astrom_photom_scamp_SDSS-R6/cat_photom/SUPA* ~/data/MACS1115+01/W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6
#ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-J-V/SCIENCE/astrom_photom_scamp_SDSS-R6/headers/SUPA* ~/data/MACS1115+01/W-J-B/SCIENCE/astrom_photom_scamp_SDSS-R6

## what about for distinct filters in the old, but not in the new?
cd ~/data/MACS1115+01/
mkdir -p /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-J-V/SCIENCE/headers_scamp_SDSS-R6/
mkdir -p /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-C-IC/SCIENCE/headers_scamp_SDSS-R6/
mkdir -p /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-J-V/SCIENCE/headers_scamp_photom_SDSS-R6/
mkdir -p /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-C-IC/SCIENCE/headers_scamp_photom_SDSS-R6/
mkdir -p /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-J-V/SCIENCE/cat_scampIC
mkdir -p /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-C-IC/SCIENCE/cat_scampIC
mkdir -p /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-J-V/WEIGHTS
mkdir -p /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-C-IC/WEIGHTS
cp /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-J-V/WEIGHTS/SUPA*_*I.weight.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-J-V/WEIGHTS/
cp /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-J-V/WEIGHTS/SUPA*_*I.flag.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-J-V/WEIGHTS/
ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-J-V/SCIENCE/SUPA*I.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-J-V/SCIENCE/
ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-J-V/SCIENCE/SUPA*I.sub.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-J-V/SCIENCE/
cp /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-J-V/SCIENCE/headers_scamp_SDSS-R6/SUPA*.head /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-J-V/SCIENCE/headers_scamp_SDSS-R6/
ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-J-V/SCIENCE/cat_scampIC/SUPA*I.cat /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-J-V/SCIENCE/cat_scampIC/

cp /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-C-IC/WEIGHTS/SUPA*_*I.weight.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-C-IC/WEIGHTS/
cp /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-C-IC/WEIGHTS/SUPA*_*I.flag.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-C-IC/WEIGHTS/
ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-C-IC/SCIENCE/SUPA*I.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-C-IC/SCIENCE/
ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-C-IC/SCIENCE/SUPA*I.sub.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-C-IC/SCIENCE/
cp /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-C-IC/SCIENCE/headers_scamp_SDSS-R6/SUPA*.head /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-C-IC/SCIENCE/headers_scamp_SDSS-R6/
ln -s /nfs/slac/g/ki/ki05/anja/SUBARU/MACS1115+01/W-C-IC/SCIENCE/cat_scampIC/SUPA*I.cat /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-C-IC/SCIENCE/cat_scampIC/



