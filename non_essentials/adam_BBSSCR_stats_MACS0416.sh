#!/bin/bash
set -xv
filter=$1
run=$2
grep BBSSCR_stats-SS OUT-create_weights_raw_delink_para_CRNitschke.W-C-RC.log | sort -g -k 2 | cut -c 17- | column -t > BBSSCR_stats-SS_W-C-RC_2010-11-04.txt 
grep BBSSCR_stats-BB OUT-create_weights_raw_delink_para_CRNitschke.W-C-RC.log | sort -g -k 2 | cut -c 17- | column -t > BBSSCR_stats-BB_W-C-RC_2010-11-04.txt 
awk '{print $2}' BBSSCR_stats-SS_W-C-RC_2010-11-04.txt > ss_col.txt
paste BBSSCR_stats-BB_W-C-RC_2010-11-04.txt ss_col.txt > BBSSCR_stats-all_W-C-RC_2010-11-04.tmp.txt
cat BBSSCR_stats-header.txt BBSSCR_stats-all_W-C-RC_2010-11-04.tmp.txt | column -t > BBSSCR_stats-all_W-C-RC_2010-11-04.txt
rm -f BBSSCR_stats-all_W-C-RC_2010-11-04.tmp.txt
rm -f ss_col.txt
#ipython -i -- ~/InstallingSoftware/pythons/import_ascii.py BBSSCR_stats-all_W-C-RC_2010-11-04.txt 
