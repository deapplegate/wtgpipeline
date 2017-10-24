#!/bin/bash
set -xv
#1# first split the 10_3 and 10_2 data in the W-C-RC directory into 10_3_W-C-RC and 10_2_W-C-RC

########mv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/SUPA01*.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/SCIENCE/
########mv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/SUPA00*.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/SCIENCE/
########mv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/WEIGHTS/SUPA01*.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/WEIGHTS/
########mv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/WEIGHTS/SUPA00*.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/WEIGHTS/

#2# then link the stuff from 10_3_W-C-RC back into the W-C-RC directory 
#ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/WEIGHTS/*.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/WEIGHTS/
#ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/SCIENCE/*.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/

#see /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/out_history-B4.log for details
export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU
export cluster=MACS1226+21
export INSTRUMENT=SUBARU
export ending="OCF"


#3# setup SUBARU to 10_3 config and do the 10_3 coadds
cd ~/wtgpipeline
export run=2010-02-12 ;export filter="W-C-RC";export BONN_TARGET=${cluster} ;export BONN_FILTER=${filter}_${run}
./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
./do_coadd_batch.sh ${cluster} ${filter} "all exposure good gabodsid rotation" 2>&1 | tee -a OUT-do_coadd_batch_${filter}_${cluster}-10_3.log

#4# move the 10_3 coadds to 10_3_W-C-RC directory and remove links to 10_3 data
mv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/cat/ /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/SCIENCE/
mv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/plots/ /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/SCIENCE/
mv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_*/ /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/SCIENCE/
mv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/MACS1226+21_*.cat /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/SCIENCE/
rm -f /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/*.fits
rm -f /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/WEIGHTS/*.fits 
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/WEIGHTS/*.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/WEIGHTS/
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/SCIENCE/*.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/

#5# setup SUBARU to 10_2 config and do the 10_2 coadds
cd ~/wtgpipeline
export run=2006-03-04 ;export filter="W-C-RC" ; export BONN_TARGET=${cluster}; export BONN_FILTER=${filter}_${run}
./setup_SUBARU.sh ${SUBARUDIR}/${run}_${filter}/SCIENCE/ORIGINALS
./do_coadd_batch.sh ${cluster} ${filter} "all exposure good gabodsid rotation" 2>&1 | tee -a OUT-do_coadd_batch_${filter}_${cluster}-10_2.log

#6# move the 10_2 coadds to 10_2_W-C-RC directory and remove links to 10_2 data
mv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/cat/ /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/SCIENCE/
mv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/plots/ /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/SCIENCE/
mv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/coadd_MACS1226+21_*/ /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/SCIENCE/
mv /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/MACS1226+21_*.cat /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/SCIENCE/

#7# restore the /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/ directory to have links to all necessary 10_2 and 10_3 data
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/WEIGHTS/*.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/WEIGHTS/
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/SCIENCE/*.fits /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/
cd /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-RC/SCIENCE/
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/cat/ ./cat10_3
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/plots/ ./plots10_3
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/coadd_MACS1226+21_good/ ./coadd_MACS1226+21_good10_3
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/coadd_MACS1226+21_all/ ./coadd_MACS1226+21_all10_3
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/coadd_MACS1226+21_SUPA* .
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/coadd_MACS1226+21_gab* .
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/MACS1226+21_good.cat ./MACS1226+21_good10_3.cat
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/MACS1226+21_all.cat ./MACS1226+21_all10_3.cat
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/MACS1226+21_SUPA*.cat .
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_3_W-C-RC/MACS1226+21_gab*.cat .
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/cat/ ./cat10_2
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/plots/ ./plots10_2
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/coadd_MACS1226+21_good/ ./coadd_MACS1226+21_good10_2
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/coadd_MACS1226+21_all/ ./coadd_MACS1226+21_all10_2
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/coadd_MACS1226+21_SUPA* .
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/coadd_MACS1226+21_gab* .
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/MACS1226+21_good.cat ./MACS1226+21_good10_2.cat
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/MACS1226+21_all.cat ./MACS1226+21_all10_2.cat
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/MACS1226+21_SUPA*.cat .
ln -s /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/10_2_W-C-RC/MACS1226+21_gab*.cat .
