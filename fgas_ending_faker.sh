#!/bin/bash
set -xv

# faked RXJ2129/W-J-B/ OCFI to OCFSI
# faked RXJ2129/W-C-RC/ OCFI to OCFSI
# faked Zw2089/W-S-I+/ OCFI to OCFSI
# faked MACS1115+01/W-C-RC/ OCFSI to OCFSRI (e.g. SUPA0120144_8OCFSRI.fits -> SUPA0120144_8OCFSI)

cd ~/my_data/SUBARU/Zw2089/W-S-I+/
cd WEIGHTS/
ls SUPA*OCFI.fits
\ls -1 SUPA*OCFI.flag.fits > link_from.tmp
\ls -1 SUPA*OCFI.flag.fits | sed 's/OCFI/OCFSI/g' > link_to.tmp
paste -d\  link_from.tmp link_to.tmp > fake_ending.sh
sed -i.old 's/^/ln -s /g' fake_ending.sh 
bash fake_ending.sh
\ls -1 SUPA*OCFI.weight.fits > link_from.tmp
\ls -1 SUPA*OCFI.weight.fits | sed 's/OCFI/OCFSI/g' > link_to.tmp
paste -d\  link_from.tmp link_to.tmp > fake_ending.sh
sed -i.old 's/^/ln -s /g' fake_ending.sh 
bash fake_ending.sh

cd ~/my_data/SUBARU/Zw2089/W-S-I+/
cd SCIENCE/
ls SUPA*OCFI.fits
\ls -1 SUPA*OCFI.fits > link_from.tmp
\ls -1 SUPA*OCFI.fits | sed 's/OCFI/OCFSI/g' > link_to.tmp
paste -d\  link_from.tmp link_to.tmp > fake_ending.sh
sed -i.old 's/^/ln -s /g' fake_ending.sh 
bash fake_ending.sh

