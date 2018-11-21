#!/bin/bash
set -xv

#./do_Subaru_register_4batch.sh ${cluster} SDSS-R6 astrom "W-J-B W-C-RC W-S-Z+" 2>&1 | tee -a OUT-do_Subaru_register_4batch_${cluster}_round2.log

export cluster=RXJ2129
#./create_scamp_astrom_photom.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-J-B SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-C-RC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-S-Z+ SCIENCE SDSS-R6  2>&1 | tee -a OUT-create_scamp_astrom_photom_${cluster}_round2.log
#./get_error_log.sh OUT-create_scamp_astrom_photom_${cluster}_round2.log
#./create_scamp_astrom_photom-finish_RXJ2129.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-J-B SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-C-RC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-S-Z+ SCIENCE SDSS-R6  2>&1 | tee -a OUT-create_scamp_astrom_photom_${cluster}_round2.log2
#./get_error_log.sh OUT-create_scamp_astrom_photom_${cluster}_round2.log2
./simple_ic_SDSS.py 2>&1 | tee -a OUT-simple_ic_SDSS3_${cluster}.log
./get_error_log.sh OUT-simple_ic_SDSS3_${cluster}.log
echo "adam-look: err.OUT-simple_ic_SDSS3_${cluster}.log"

./simple_ic_PANSTARRS.py 2>&1 | tee -a OUT-simple_ic_PAN3_${cluster}.log
./get_error_log.sh OUT-simple_ic_PAN3_${cluster}.log
echo "adam-look: err.OUT-simple_ic_PAN3_${cluster}.log"
