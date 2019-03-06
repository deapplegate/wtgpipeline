#!/bin/bash
set -xv

#pprun="2009-09-19_W-J-V";ending="OCF"
#./distribute_sets_subaru_to_gpfs.sh ${SUBARUDIR} ${pprun}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list WEIGHTS

#pprun="2009-03-28_W-S-I+";ending="OCFS"
#pprun="2010-03-12_W-J-V";ending="OCF"
#pprun="2010-03-12_W-S-I+";ending="OCFS"
#pprun="2010-11-04_W-J-B";ending="OCF"
#pprun="2010-11-04_W-S-Z+";ending="OCFSF"
#./distribute_sets_subaru_to_gpfs.sh ${SUBARUDIR} ${pprun}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list WEIGHTS
#pprun="2010-12-05_W-J-V";ending="OCFS"
#pprun="2012-07-23_W-C-RC";ending="OCF"

./distribute_sets_subaru_to_gpfs.sh ${SUBARUDIR} ${pprun}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list WEIGHTS 2>&1 | tee -a OUT-${pprun}_distribute.log

#pprun="2013-06-10_W-S-Z+";ending="OCFSF"
#./distribute_sets_subaru_to_gpfs.sh ${SUBARUDIR} ${pprun}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list WEIGHTS
#pprun="2015-12-15_W-C-RC";ending="OCF"
#./distribute_sets_subaru_to_gpfs.sh ${SUBARUDIR} ${pprun}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list WEIGHTS
#pprun="2015-12-15_W-J-B";ending="OCF"
#./distribute_sets_subaru_to_gpfs.sh ${SUBARUDIR} ${pprun}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list WEIGHTS
#pprun="2015-12-15_W-S-Z+";ending="OCFSF"
#./distribute_sets_subaru_to_gpfs.sh ${SUBARUDIR} ${pprun}/SCIENCE ${ending} 1000 ${SUBARUDIR}/SUBARU.list WEIGHTS
#rsync ~/data/MACS1115+01/ /gpfs/slac/kipac/fs1/u/awright/SUBARU/
