#!/bin/bash
set -xv
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

