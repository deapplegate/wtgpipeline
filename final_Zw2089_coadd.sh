#!/bin/bash
set -xv
export cluster=Zw2089
ending="OCFSI"
filter=W-S-I+
./adam_pre_coadd_cleanup.sh Zw2089 W-S-I+
./do_coadd_batch.sh Zw2089 W-S-I+ "all exposure " 'none' ${ending} 2>&1 | tee -a OUT-coadd_Zw2089.${filter}.log
exit 0;

export cluster=Zw2089
export ending=OCFSIR
export filter=W-J-V
rm OUT-coadd_${cluster}.${filter}.log
./adam_pre_coadd_cleanup.sh ${cluster} ${filter}
./do_coadd_batch.sh Zw2089 W-J-V "all good exposure gabodsid" 'Zw2089_good_coadd_conditions.txt' ${ending} 2>&1 | tee -a OUT-coadd_${cluster}.${filter}.log

