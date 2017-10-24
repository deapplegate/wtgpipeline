#!/bin/bash
set -xv
## running "astrom", "photom", and coadd for MACS0416 in the S-OCFR_W-OCF mode
#./do_Subaru_register_4batch.sh ${cluster} 2MASS astrom "W-J-B W-C-RC W-S-Z+" 2>&1 | tee -a scratch/S-OCFR_W-OCF/OUT-do_Subaru_register_4batch_astrom-MACS0416-24.log 
#./do_Subaru_register_4batch.sh ${cluster} 2MASS photom "W-J-B W-C-RC W-S-Z+" 2>&1 | tee -a scratch/S-OCFR_W-OCF/OUT-do_Subaru_register_4batch_photom-MACS0416-24.log 
bsub -q long -R rhel60 -o /u/ki/awright/wtgpipeline/scratch/S-OCFR_W-OCF/OUT-do_coadd_batch-MACS0416-24_W-C-RC.out -e /u/ki/awright/wtgpipeline/scratch/S-OCFR_W-OCF/OUT-do_coadd_batch-MACS0416-24_W-C-RC.err ./do_coadd_batch.sh ${cluster} W-C-RC "all exposure good"
bsub -q long -R rhel60 -o /u/ki/awright/wtgpipeline/scratch/S-OCFR_W-OCF/OUT-do_coadd_batch-MACS0416-24_W-J-B.out -e /u/ki/awright/wtgpipeline/scratch/S-OCFR_W-OCF/OUT-do_coadd_batch-MACS0416-24_W-J-B.err ./do_coadd_batch.sh ${cluster} W-J-B "all"
bsub -q long -R rhel60 -o /u/ki/awright/wtgpipeline/scratch/S-OCFR_W-OCF/OUT-do_coadd_batch-MACS0416-24_W-S-Z+.out -e /u/ki/awright/wtgpipeline/scratch/S-OCFR_W-OCF/OUT-do_coadd_batch-MACS0416-24_W-S-Z+.err ./do_coadd_batch.sh ${cluster} W-S-Z+ "all"
