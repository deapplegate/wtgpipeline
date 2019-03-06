#!/bin/bash
set -xv

export ending=OCF
export run=2015-12-15
. SUBARU.ini
export cluster=Zw2089
#./parallel_manager.sh create_weights_raw_delink_para_CRNitschke_30sec_Z.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-S-Z+_2015-12-15/ SCIENCE OCFSF WEIGHTS
#./parallel_manager.sh create_weights_raw_delink_para_CRNitschke_30sec_Z.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-S-Z+_2015-12-15/ SCIENCE OCFSF WEIGHTS
#exit 0;
export filter=W-C-RC
./parallel_manager.sh create_weights_raw_delink_para_CRNitschke_30sec.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-C-RC_2015-12-15/ SCIENCE OCF WEIGHTS
export filter=W-J-B
./parallel_manager.sh create_weights_raw_delink_para_CRNitschke_30sec.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2089/W-J-B_2015-12-15/ SCIENCE OCF WEIGHTS
export cluster=MACS0159-08
export filter=W-J-B
./parallel_manager.sh create_weights_raw_delink_para_CRNitschke_30sec.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0159-08/W-J-B_2015-12-15/ SCIENCE OCF WEIGHTS
export cluster=Zw2701
export filter=W-J-B
./parallel_manager.sh create_weights_raw_delink_para_CRNitschke_30sec.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2701/W-J-B_2015-12-15/ SCIENCE OCF WEIGHTS
export filter=W-C-RC
./parallel_manager.sh create_weights_raw_delink_para_CRNitschke_30sec.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/Zw2701/W-C-RC_2015-12-15/ SCIENCE OCF WEIGHTS
export cluster=MACS0429-02
export filter=W-J-B
./parallel_manager.sh create_weights_raw_delink_para_CRNitschke_30sec.sh /gpfs/slac/kipac/fs1/u/awright/SUBARU/MACS0429-02/W-J-B_2015-12-15/ SCIENCE OCF WEIGHTS
