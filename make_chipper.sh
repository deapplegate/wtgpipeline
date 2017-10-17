#!/bin/bash
set -xv
#adam-SHNT# after things are moved I'll have to do some kind of change of directory names in the finish_scamp_cat_*.sh files

outdir="/nfs/slac/kipac/fs1/u/awright/batch_files/"
bsub -W 6500 -R rhel60 -o ${outdir}/OUT-finish_scamp_cat_r_chipsnum1.out -e ${outdir}/OUT-finish_scamp_cat_r_chipsnum1.err ./finish_scamp_cat_r_chipsnum1.sh
bsub -W 6500 -R rhel60 -o ${outdir}/OUT-finish_scamp_cat_r_chipsnum2.out -e ${outdir}/OUT-finish_scamp_cat_r_chipsnum2.err ./finish_scamp_cat_r_chipsnum2.sh
bsub -W 6500 -R rhel60 -o ${outdir}/OUT-finish_scamp_cat_r_chipsnum3.out -e ${outdir}/OUT-finish_scamp_cat_r_chipsnum3.err ./finish_scamp_cat_r_chipsnum3.sh
bsub -W 6500 -R rhel60 -o ${outdir}/OUT-finish_scamp_cat_r_chipsnum4.out -e ${outdir}/OUT-finish_scamp_cat_r_chipsnum4.err ./finish_scamp_cat_r_chipsnum4.sh


bsub -W 6500 -R rhel60 -o ${outdir}/OUT-finish_scamp_cat_i_chipsnum1.out -e ${outdir}/OUT-finish_scamp_cat_i_chipsnum1.err ./finish_scamp_cat_i_chipsnum1.sh
bsub -W 6500 -R rhel60 -o ${outdir}/OUT-finish_scamp_cat_i_chipsnum2.out -e ${outdir}/OUT-finish_scamp_cat_i_chipsnum2.err ./finish_scamp_cat_i_chipsnum2.sh
bsub -W 6500 -R rhel60 -o ${outdir}/OUT-finish_scamp_cat_i_chipsnum3.out -e ${outdir}/OUT-finish_scamp_cat_i_chipsnum3.err ./finish_scamp_cat_i_chipsnum3.sh


bsub -W 6500 -R rhel60 -o ${outdir}/OUT-finish_scamp_cat_g_chipsnum1.out -e ${outdir}/OUT-finish_scamp_cat_g_chipsnum1.err ./finish_scamp_cat_g_chipsnum1.sh
bsub -W 6500 -R rhel60 -o ${outdir}/OUT-finish_scamp_cat_g_chipsnum2.out -e ${outdir}/OUT-finish_scamp_cat_g_chipsnum2.err ./finish_scamp_cat_g_chipsnum2.sh
bsub -W 6500 -R rhel60 -o ${outdir}/OUT-finish_scamp_cat_g_chipsnum3.out -e ${outdir}/OUT-finish_scamp_cat_g_chipsnum3.err ./finish_scamp_cat_g_chipsnum3.sh


bsub -W 6500 -R rhel60 -o ${outdir}/OUT-finish_scamp_cat_z_chipsnum1.out -e ${outdir}/OUT-finish_scamp_cat_z_chipsnum1.err ./finish_scamp_cat_z_chipsnum1.sh
bsub -W 6500 -R rhel60 -o ${outdir}/OUT-finish_scamp_cat_z_chipsnum2.out -e ${outdir}/OUT-finish_scamp_cat_z_chipsnum2.err ./finish_scamp_cat_z_chipsnum2.sh
bsub -W 6500 -R rhel60 -o ${outdir}/OUT-finish_scamp_cat_z_chipsnum3.out -e ${outdir}/OUT-finish_scamp_cat_z_chipsnum3.err ./finish_scamp_cat_z_chipsnum3.sh
