#!/bin/bash
set -xv

cd ~/my_data/SUBARU/Zw2089/W-J-V/SCIENCE/
mkdir old_rings_10_2
changed=" "
for supa in SUPA0051473 SUPA0051474 SUPA0051475 SUPA0051476 SUPA0051477
do
    for chip in 3 4 5
    do
	ic '%1 %2 + ' ${supa}_${chip}OCFSI.fits ${supa}_${chip}OCFSIR.fits > ${supa}_${chip}IandR_ave.fits
	mv ${supa}_${chip}OCFSIR.fits old_rings_10_2/
	ic '%1 2 / ' ${supa}_${chip}IandR_ave.fits > ${supa}_${chip}OCFSIR.fits
	mv ${supa}_${chip}IandR_ave.fits old_rings_10_2/

    done
    for chip in 3 4
    do
	    changed="${changed} ${supa}_${chip}OCFSIR.fits old_rings_10_2/${supa}_${chip}OCFSIR.fits "
    done
done

ds9 -frame lock image -zoom to fit -geometry 2000x2000 -cmap bb -scale limits 2150 2750 ${changed} -frame lock scale &

