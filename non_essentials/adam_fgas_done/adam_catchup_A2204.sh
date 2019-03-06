#!/bin/bash
set -xv

#./adam_download_panstarrs_catalog.py && ./adam_combine_and_fix_panstarrs_catalog.py && ./adam_illumcorr_panstarrs_catalog.py
export cluster=A2204
./do_Subaru_register_4batch.sh ${cluster} PANSTARRS astrom "W-J-V W-S-I+" 2>&1 | tee -a OUT-do_Subaru_register_4batch_${cluster}_astrom.log
./get_error_log.sh OUT-do_Subaru_register_4batch_${cluster}_astrom.log
echo "adam-look: firefox ~/my_data/SUBARU/A2204/W-J-V/SCIENCE/astrom_photom_scamp_PANSTARRS/plots/A2204_scamp.xml &"
./simple_ic_PANSTARRS.py 2>&1 | tee -a OUT-simple_ic_PAN3_${cluster}.log
./get_error_log.sh OUT-simple_ic_PAN3_${cluster}.log
echo "adam-look: firefox ~/my_data/SUBARU/A2204/W-J-V/SCIENCE/astrom_photom_scamp_PANSTARRS/plots/A2204_scamp.xml &"
echo "adam-look: err.OUT-do_Subaru_register_4batch_${cluster}_astrom.log"
echo "adam-look: err.OUT-simple_ic_PAN3_${cluster}.log"
