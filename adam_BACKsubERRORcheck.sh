#!/bin/bash
set -xv
#adam-example# ./adam_BACKsubERRORcheck.sh ${cluster}
#adam-example# ./adam_BACKsubERRORcheck.sh RXJ2129
cluster=$1
ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale -title ${cluster}_W-J-B_BACKsubERRORcheck /gpfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}/coadds_together_${cluster}/coadd_${cluster}_SUPA*.W-J-B.fits -zoom to fit &
ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale -title ${cluster}_W-J-V_BACKsubERRORcheck /gpfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}/coadds_together_${cluster}/coadd_${cluster}_SUPA*.W-J-V.fits -zoom to fit &
ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale -title ${cluster}_W-C-RC_BACKsubERRORcheck /gpfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}/coadds_together_${cluster}/coadd_${cluster}_SUPA*.W-C-RC.fits -zoom to fit &
if [ -d /gpfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}/W-S-I+/SCIENCE/ ]; then
    ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale -title ${cluster}_W-S-I+_BACKsubERRORcheck /gpfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}/coadds_together_${cluster}/coadd_${cluster}_SUPA*.W-S-I+.fits -zoom to fit &
fi
if [ -d /gpfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}/W-C-IC/SCIENCE/ ]; then
    ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale -title ${cluster}_W-C-IC_BACKsubERRORcheck /gpfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}/coadds_together_${cluster}/coadd_${cluster}_SUPA*.W-C-IC.fits -zoom to fit &
fi
if [ -d /gpfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}/W-S-Z+/SCIENCE/ ]; then
    ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -zscale -title ${cluster}_W-S-Z+_BACKsubERRORcheck /gpfs/slac/kipac/fs1/u/awright/SUBARU/${cluster}/coadds_together_${cluster}/coadd_${cluster}_SUPA*.W-S-Z+.fits -zoom to fit &
fi
exit 0;
