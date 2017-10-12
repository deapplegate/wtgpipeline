#! /bin/bash -xv
#adam-does# this code changes the coordinates of region files from physical to fk5
#adam-predecessor# this code came from /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC_2010-11-04/reg/wcs2phys.sh
#adam-call_example# ./adam_wcs2phys.sh /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/autosuppression/ /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/ OCF
#adam-comments# could be adapted to change other properties as well
regdir="/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-C-RC_2010-03-12/SCIENCE/reg"
scidir="/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1115+01/W-C-RC_2010-03-12/SCIENCE"
ending="OCFS"
mkdir ${regdir}/image_coord_regs2/


for file in $(ls -1 ${regdir}/wcs_coord_regs/SUPA0120152_*.reg)
do

base=`basename ${file}`
BASE_no_ext=`basename ${file} .reg`

ds9 ${scidir}/${BASE_no_ext}${ending}.fits &
sleep 10
xpaset -p ds9 lower
xpaset -p ds9 regions load ${file}
xpaset -p ds9 regions format ds9
sleep 1
xpaset -p ds9 regions system image
sleep 2
#xpaset -p ds9 regions skyformat sexagesimal
xpaset -p ds9 regions save ${regdir}/image_coord_regs2/${base}
sleep 2
xpaset -p ds9 regions delete all
sleep 5
wc -l ${file} ${regdir}//${base}
echo ''
done

xpaset -p ds9 exit
