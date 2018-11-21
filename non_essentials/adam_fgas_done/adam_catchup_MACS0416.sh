#!/bin/bash
set -xv
#remove everything related to coadds/cats/etc.
./do_Subaru_register_4batch.sh "MACS0416-24" "2MASS" "astrom" "W-J-B W-C-RC W-S-Z+" 2>&1 | tee -a scratch/OUT-do_Subaru_register_4batch_MACS0416-24_astrom.log
#vi develop_simple_ic/simple_ic.py #see #adam-tmp
ipython develop_simple_ic/simple_ic.py
./do_Subaru_register_4batch.sh "MACS0416-24" "2MASS" "photom" "W-J-B W-C-RC W-S-Z+" 2>&1 | tee -a scratch/OUT-do_Subaru_register_4batch_MACS0416-24_photom.log
./adam_coadd_MACS0416-24.sh
