#!/bin/bash
set -xv

export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU/ ; export INSTRUMENT=SUBARU
export bonn=/u/ki/awright/bonnpipeline/
export subdir=/nfs/slac/g/ki/ki18/anja/SUBARU/
export cluster=MACS0416-24
export ending="OCFR"
export filter="W-C-RC"
. progs.ini > /tmp/out 2>&1
. SUBARU.ini > /tmp/out 2>&1

# instead of : ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC SCIENCE OCFR.sub MACS0416-24_good /u/ki/awright/bonnpipeline MACS0416-24_all
#run this:
./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC SCIENCE OCFR.sub MACS0416-24_good /u/ki/awright/bonnpipeline MACS0416-24_all

