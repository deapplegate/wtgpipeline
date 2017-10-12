#!/bin/bash
set -xv

# $1 : run
# $2 : filter
# $3 : sciencedir

export BONN_TARGET=$1
export BONN_FILTER=$2

rundir="/nfs/slac/g/ki/ki02/xoc/anja/SUBARU/${1}_${2}"

./BonnLogger.py clear

./setup_SUBARU.sh $rundir/SCIENCE/ORIGINALS
export INSTRUMENT=SUBARU



./parallel_manager.sh process_superflat_rot_para.sh $rundir $3

./create_norm.sh $rundir $3 _rot0
./create_norm.sh $rundir $3 _rot1

for ((i=1;i<=10;i+=1))
do
    ic '%1 %2 /' $rundir/${3}_norm/${3}_norm_${i}_rot0.fits $rundir/${3}_norm/${3}_norm_${i}_rot1.fits > $rundir/${3}_norm/rot_comp_${i}.fits
done

./create_binnedmosaics.sh $rundir "$3_norm" "$3_norm" "_rot0" 8 -32
./create_binnedmosaics.sh $rundir "$3_norm" "$3_norm" "_rot1" 8 -32
./create_binnedmosaics.sh $rundir "$3_norm" rot_comp '' 8 -32