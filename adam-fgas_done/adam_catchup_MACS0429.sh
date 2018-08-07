#!/bin/bash
set -xv
export cluster=MACS0429-02
#./do_Subaru_register_4batch.sh ${cluster} PANSTARRS astrom "W-J-B W-C-RC W-S-Z+" 2>&1 | tee -a OUT-do_Subaru_register_4batch_${cluster}_round2.log


#./create_scamp_astrom_photom.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+ SCIENCE PANSTARRS  2>&1 | tee -a OUT-create_scamp_astrom_photom_${cluster}_round2.log
#./get_error_log.sh OUT-create_scamp_astrom_photom_${cluster}_round2.log

./simple_ic_PANSTARRS.py 2>%1 | tee -a OUT-simple_ic_MACS0429_PAN3.log
