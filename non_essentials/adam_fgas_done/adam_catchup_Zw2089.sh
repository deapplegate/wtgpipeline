#!/bin/bash
set -xv

export cluster=Zw2089
./do_Subaru_register_4batch.sh ${cluster} SDSS-R6 astrom "W-J-B W-J-V W-C-RC W-S-I+ W-S-Z+" 2>&1 | tee -a OUT-do_Subaru_register_4batch_${cluster}_astrom.log
