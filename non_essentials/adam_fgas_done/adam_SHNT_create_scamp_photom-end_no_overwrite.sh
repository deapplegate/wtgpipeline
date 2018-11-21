#!/bin/bash
set -xv

## just started running photom for MACS0429-02
export cluster=MACS0429-02
./create_scamp_photom-end_no_overwrite.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B_2015-12-15_CALIB SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-V SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-V_2009-01-23_CALIB SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-RC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-RC_2009-01-23_CALIB SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-IC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-C-IC_2006-12-21_CALIB SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+ SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+_2015-12-15_CALIB SCIENCE 26000 PANSTARRS 2>&1 | tee -a OUT-create_scamp_photom-end_no_overwrite_MACS0429-02.log
./get_error_log.sh OUT-create_scamp_photom-end_no_overwrite_MACS0429-02.log
exit 0;

## photom for Zw2089: I'll have to remove the images with low ZP && integrate MP data!
export cluster=Zw2089
./create_scamp_photom-end_no_overwrite.sh  /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-J-B SCIENCE  /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-J-B_2015-12-15_CALIB SCIENCE  /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-J-V SCIENCE  /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-C-RC SCIENCE  /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-C-RC_2015-12-15_CALIB SCIENCE  /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-S-I+ SCIENCE  /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-S-Z+ SCIENCE  /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-S-Z+_2015-12-15_CALIB SCIENCE  26000 SDSS-R6 2>&1 | tee -a OUT-create_scamp_photom-end_no_overwrite_Zw2089.log


## I'll have to fix the one bad data set (the one with misschip in I-band old data)
export cluster=RXJ2129
rm OUT-create_scamp_photom-end_no_overwrite_RXJ2129.log2
./create_scamp_photom-end_no_overwrite.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-J-B SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-J-V SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-C-RC SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-S-I+ SCIENCE /gpfs/slac/kipac/fs1/u/awright/SUBARU/RXJ2129/W-S-Z+ SCIENCE  26000 SDSS-R6 2>&1 | tee -a OUT-create_scamp_photom-end_no_overwrite_RXJ2129.log2
