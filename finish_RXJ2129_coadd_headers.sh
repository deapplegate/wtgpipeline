#!/bin/bash
set -xv
export ending=OCFSRI
export INSTRUMENT=SUBARU
export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU/
export cluster=RXJ2129
export filter=W-C-RC
export config="10_3"


cp SUBARU_10_2.ini SUBARU.ini
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_gabodsid2025 STATS coadd -1.0 AB '(GABODSID=2025);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0032911 STATS coadd -1.0 AB '(EXPOSURE=1);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0032912 STATS coadd -1.0 AB '(EXPOSURE=2);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0032913 STATS coadd -1.0 AB '(EXPOSURE=3);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0032914 STATS coadd -1.0 AB '(EXPOSURE=4);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0032915 STATS coadd -1.0 AB '(EXPOSURE=5);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0032916 STATS coadd -1.0 AB '(EXPOSURE=6);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0032917 STATS coadd -1.0 AB '(EXPOSURE=7);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0032918 STATS coadd -1.0 AB '(EXPOSURE=8);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0032919 STATS coadd -1.0 AB '(EXPOSURE=9);'



cp SUBARU_10_3.ini SUBARU.ini
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_all STATS coadd -1.0 AB '((((RA>(322.41625000-0.5))AND(RA<(322.41625000+0.5)))AND((DEC>(0.08888889-0.5))AND(DEC<(0.08888889+0.5))))AND(SEEING<1.9));'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_good CHIPS_STATS coadd -1.0 AB '(((EXPOSURE>9))AND((EXPOSURE<23)OR(EXPOSURE>24)));'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135155 STATS coadd -1.0 AB '(EXPOSURE=10);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135156 STATS coadd -1.0 AB '(EXPOSURE=11);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135157 STATS coadd -1.0 AB '(EXPOSURE=12);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135158 STATS coadd -1.0 AB '(EXPOSURE=13);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135159 STATS coadd -1.0 AB '(EXPOSURE=14);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135160 STATS coadd -1.0 AB '(EXPOSURE=15);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135161 STATS coadd -1.0 AB '(EXPOSURE=16);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135162 STATS coadd -1.0 AB '(EXPOSURE=17);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135163 STATS coadd -1.0 AB '(EXPOSURE=18);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135164 STATS coadd -1.0 AB '(EXPOSURE=19);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135165 STATS coadd -1.0 AB '(EXPOSURE=20);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135166 STATS coadd -1.0 AB '(EXPOSURE=21);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135167 STATS coadd -1.0 AB '(EXPOSURE=22);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135168 STATS coadd -1.0 AB '(EXPOSURE=23);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135169 STATS coadd -1.0 AB '(EXPOSURE=24);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135170 STATS coadd -1.0 AB '(EXPOSURE=25);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_SUPA0135171 STATS coadd -1.0 AB '(EXPOSURE=26);'
./update_coadd_header.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU//RXJ2129/W-C-RC SCIENCE RXJ2129_gabodsid4952 STATS coadd -1.0 AB '(GABODSID=4952);'
