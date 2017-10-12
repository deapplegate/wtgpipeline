#!/bin/bash
set -xv
filter=$1
run=$2
grep BBSSCR_stats-SS OUT-cwrdp_CRNitschke_MACS1226+21_${filter}_${run}.log | sort -g -k 2 | cut -c 15- | column -t > BBSSCR_stats-SS_${filter}_${run}.txt 
grep BBSSCR_stats-BB OUT-cwrdp_CRNitschke_MACS1226+21_${filter}_${run}.log | sort -g -k 2 | cut -c 15- | column -t > BBSSCR_stats-BB_${filter}_${run}.txt 
awk '{print $2}' BBSSCR_stats-SS_${filter}_${run}.txt > ss_col.txt
paste BBSSCR_stats-BB_${filter}_${run}.txt ss_col.txt > BBSSCR_stats-all_${filter}_${run}.tmp.txt
cat BBSSCR_stats-header.txt BBSSCR_stats-all_${filter}_${run}.tmp.txt | column -t > BBSSCR_stats-all_${filter}_${run}.txt
rm -f BBSSCR_stats-all_${filter}_${run}.tmp.txt
rm -f ss_col.txt
#ipython -i -- ~/InstallingSoftware/pythons/import_ascii.py BBSSCR_stats-all_${filter}_${run}.txt 

