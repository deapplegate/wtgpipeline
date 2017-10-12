#!/bin/bash -xv
for dir in /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-IC_2010-02-12/SCIENCE/ /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-J-B_2010-02-12/SCIENCE/ /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-J-V_2010-02-12/SCIENCE/ /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-S-G+_2010-04-15/SCIENCE/ /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-S-I+_2010-04-15/SCIENCE/ /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-C-IC_2011-01-06/SCIENCE/ /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-S-Z+_2011-01-06/SCIENCE/
do
	mkdir ${dir}/reg
	fls=`ls ${dir}/*_5OCF.fits`
	for fl in $fls
	do
		fo=`basename ${fl} OCF.fits`
		cp ~/thiswork/drag_col/badcol_10_3_ccd5_POLYGON.reg ${dir}/reg/${fo}.reg
	done
done

