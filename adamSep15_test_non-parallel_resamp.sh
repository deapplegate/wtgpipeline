#!/bin/bash
set -xv

export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU/ ; export INSTRUMENT=SUBARU
export bonn=/u/ki/awright/wtgpipeline/
export subdir=/gpfs/slac/kipac/fs1/u/awright/SUBARU/
export cluster=MACS0416-24
export ending="OCFR"
export filter="W-C-RC"
. progs.ini > /tmp/out 2>&1
. SUBARU.ini > /tmp/out 2>&1

# instead of : ./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh /u/ki/awright/data/MACS0416-24/W-C-RC SCIENCE OCFR.sub MACS0416-24_good /u/ki/awright/wtgpipeline MACS0416-24_all
#run this:
./parallel_manager.sh ./resample_coadd_swarp_chips_para.sh /u/ki/awright/data/MACS0416-24/W-C-RC SCIENCE OCFR.sub MACS0416-24_good /u/ki/awright/wtgpipeline MACS0416-24_all

