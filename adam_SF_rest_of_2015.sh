#!/bin/bash
set -xv

./adam_SF_2015-12-15_W-S-Z+-do_Subaru_preprocess_superflat_SET7.sh 2>&1 | tee -a OUT-adam_SF_2015-12-15_W-S-Z+-do_Subaru_preprocess_superflat_SET7.log
./adam_SF_2015-12-15_W-S-Z+-do_Subaru_preprocess_superflat_SET8.sh 2>&1 | tee -a OUT-adam_SF_2015-12-15_W-S-Z+-do_Subaru_preprocess_superflat_SET8.log
