#!/bin/bash
set -xv



## Zw2089 lensing vars:
cluster=Zw2089
filter=W-J-V
ending=OCFSI
config="10_3"
#./adam_make_autosuppression_ims.py ~/my_data/SUBARU/${cluster}/${filter}/SCIENCE/ ${ending} ${config}
#./adam_make_backmask_ims.py ~/my_data/SUBARU/${cluster}/${filter}/SCIENCE/ ${ending}

cluster=RXJ2129
filter=W-C-RC
ending=OCFSI
config="10_3"
./adam_make_autosuppression_ims.py ~/my_data/SUBARU/${cluster}/${filter}/SCIENCE/ ${ending} ${config}
./adam_make_backmask_ims.py ~/my_data/SUBARU/${cluster}/${filter}/SCIENCE/ ${ending}
