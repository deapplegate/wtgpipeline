#!/bin/bash
set -xv


## MACS0429

export ending=OCFSRI
export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU/

export cluster="MACS1115+01"
. ${cluster}.ini
export config="10_3"

export lens='pretty'
export ending="OCFI"
export filter="W-J-B"
./do_coadd_pretty.sh ${cluster} ${filter} 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a scratch/OUT-coadd_${cluster}.${filter}_pretty.log

export ending="OCFSI"
export filter="W-C-IC"
./do_coadd_pretty.sh ${cluster} ${filter} 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a scratch/OUT-coadd_${cluster}.${filter}_pretty.log

export ending="OCFSRI"
export filter="W-C-RC"
./do_coadd_pretty.sh ${cluster} ${filter} 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a scratch/OUT-coadd_${cluster}.${filter}_pretty.log

#/gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-V/SCIENCE/SUPA0043650_9OCFSI.sub.fits
export ending="OCFSI"
export filter="W-J-V"
./do_coadd_pretty.sh ${cluster} ${filter} 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a scratch/OUT-coadd_${cluster}.${filter}_pretty.log

export ending="OCFSFI"
export filter="W-S-Z+"
./do_coadd_pretty.sh ${cluster} ${filter} 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a scratch/OUT-coadd_${cluster}.${filter}_pretty.log

exit 0;
export cluster=MACS0429-02
. ${cluster}.ini
export config="10_3"

export lens='pretty'
export ending="OCFI"
export filter="W-J-B"
./do_coadd_pretty.sh ${cluster} ${filter} 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.${filter}_pretty.log
exit 0;
#./do_coadd_pretty.sh ${cluster} W-C-RC 'pretty' 'none' ${ending} 'yes' 'yes' 2>&1 | tee -a OUT-coadd_${cluster}.W-C-RC_pretty.log

export ending="OCFSFI"
export filter="W-C-IC_2006-12-21_CALIB"
./do_coadd_pretty.sh ${cluster} ${filter} 'all 3s ' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.${filter}_pretty.log

export ending="OCFSFI"
export filter="W-C-IC"
./do_coadd_pretty.sh ${cluster} ${filter} 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.${filter}_pretty.log

export ending="OCFSI"
export filter="W-C-RC_2009-01-23_CALIB"
./do_coadd_pretty.sh ${cluster} ${filter} 'all 3s ' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.${filter}_pretty.log
#/gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-RC/SCIENCE/SUPA0043342_9OCFSRI.sub.fits
export ending="OCFSRI"
export filter="W-C-RC"
./do_coadd_pretty.sh ${cluster} ${filter} 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.${filter}_pretty.log

export ending="OCFI"
export filter="W-J-B_2015-12-15_CALIB"
./do_coadd_pretty.sh ${cluster} ${filter} 'all 3s ' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.${filter}_pretty.log


#/gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-V/SCIENCE/SUPA0043650_9OCFSI.sub.fits
export ending="OCFSI"
export filter="W-J-V_2009-01-23_CALIB"
./do_coadd_pretty.sh ${cluster} ${filter} 'all 3s' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.${filter}_pretty.log
export ending="OCFSI"
export filter="W-J-V"
./do_coadd_pretty.sh ${cluster} ${filter} 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.${filter}_pretty.log

export ending="OCFSFI"
export filter="W-S-Z+_2015-12-15_CALIB"
./do_coadd_pretty.sh ${cluster} ${filter} 'all 3s' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.${filter}_pretty.log
export filter="W-S-Z+"
./do_coadd_pretty.sh ${cluster} ${filter} 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.${filter}_pretty.log


exit 0;







## RXJ2129
. RXJ2129.ini
export ending=OCFSRI
export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU/
export cluster=RXJ2129
export filter=W-C-RC
export config="10_3"

export lens='pretty'
#./do_coadd_pretty.sh ${cluster} W-C-RC 'pretty' 'none' ${ending} 'yes' 'yes' 2>&1 | tee -a OUT-coadd_${cluster}.W-C-RC_pretty.log
export ending=OCFSRI
./do_coadd_pretty.sh ${cluster} W-J-V 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.W-J-V_pretty.log
export ending=OCFSFI
./do_coadd_pretty.sh ${cluster} W-S-I+ 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.W-S-I+_pretty.log
export ending=OCFSI
./do_coadd_pretty.sh ${cluster} W-J-B 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.W-J-B_pretty.log
export ending=OCFSFI
./do_coadd_pretty.sh ${cluster} W-S-Z+ 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.W-S-Z+_pretty.log

exit 0;
export lens='pretty'
./do_coadd_pretty.sh ${cluster} W-C-RC 'pretty' 'none' ${ending} 'yes' 'yes' 2>&1 | tee -a OUT-coadd_${cluster}.W-C-RC_pretty.log

. Zw2089.ini
export cluster=Zw2089
export ending="OCFI"
#./do_coadd_pretty.sh ${cluster} W-C-RC 'pretty' 'none' ${ending} 'yes' 'yes' 2>&1 | tee -a OUT-coadd_${cluster}.W-C-RC_pretty.log
#./do_coadd_pretty.sh ${cluster} W-S-I+ 'pretty' 'none' ${ending} 'yes' 'yes' 2>&1 | tee -a OUT-coadd_${cluster}.W-S-I+_pretty.log
export ending=OCFSFI
./do_coadd_pretty.sh ${cluster} W-S-Z+ 'pretty' 'none' ${ending} 'yes' 'yes' 2>&1 | tee -a OUT-coadd_${cluster}.W-S-Z+_pretty.log
export ending="OCFI"
./do_coadd_pretty.sh ${cluster} W-J-B 'pretty' 'none' ${ending} 'yes' 'yes' 2>&1 | tee -a OUT-coadd_${cluster}.W-J-B_pretty.log
#./do_coadd_pretty.sh ${cluster} W-J-V 'pretty' 'none' ${ending} 'yes' 'yes' 2>&1 | tee -a OUT-coadd_${cluster}.W-J-V_pretty.log

exit 0;

export cluster=Zw2089
export ending="OCFSIR"
filter=W-S-I+
#./adam_pre_coadd_cleanup.sh Zw2089 W-S-I+
./do_coadd_pretty.sh Zw2089 W-S-I+ "pretty" 'none' ${ending} 2>&1 | tee -a OUT-coadd_Zw2089.${filter}.log

export cluster=Zw2089
export ending=OCFSIR
export filter=W-J-V
rm OUT-coadd_${cluster}.${filter}.log
./adam_pre_coadd_cleanup.sh ${cluster} ${filter}
./do_coadd_batch.sh Zw2089 W-J-V "all good exposure gabodsid" 'Zw2089_good_coadd_conditions.txt' ${ending} 2>&1 | tee -a OUT-coadd_${cluster}.${filter}.log

#/gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+/SCIENCE/SUPA0154653_9OCFSFI.sub.fits
export ending="OCFSFI"
export filter="W-S-Z+"
#/gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+_2015-12-15_CALIB/SCIENCE/SUPA0154638_9OCFSFI.sub.fits
#/gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+_2015-12-15_CALIB/SCIENCE/SUPA0154639_9OCFSFI.sub.fits
./do_coadd_pretty.sh ${cluster} ${filter} 'pretty' 'none' ${ending} 'no' 'no' 2>&1 | tee -a OUT-coadd_${cluster}.${filter}_pretty.log

